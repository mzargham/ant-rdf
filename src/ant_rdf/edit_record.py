# SPDX-License-Identifier: Apache-2.0
"""In-place record editing and removal for the ``ant`` CLI.

``new-record`` is append-only (pure add semantics). Changing a field previously
required deleting the kind-file and re-authoring every record it held. These
helpers close that gap:

- :func:`edit_record` — set-replace the *provided* fields on one record, in
  place, leaving untouched fields and every other record byte-identical (the
  determinism invariant holds via the same :func:`write_turtle` serializer).
- :func:`remove_record` — delete one record's triples from its file, after a
  cross-reference pre-check (refuse unless ``force=True``; never cascade).

The store is one flat graph in v1, so these operate on the per-``(case,
perspective)`` kind-file. Perspectival content lives in Characterizations; a
shared actant's *identity* fields (label/description) should be edited in
every frame that declares it, so they stay identical.

The ``_EDIT_SPEC`` table mirrors ``serialize._add_*`` exactly. If a model gains
an editable field there, add it here too (same atomicity discipline as the
``ant-gvrn`` skill demands for the ontology).
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS

from ant_rdf import ANT
from ant_rdf.graph import SHARED_DIR, load_case, new_dataset
from ant_rdf.new_record import _file_for_kind, _perspective_dir
from ant_rdf.serialize import write_turtle

IRI = "iri"
LIT = "literal"

# kind -> flag -> (predicate, value-mode, multi-valued). Mirrors serialize._add_*.
_EDIT_SPEC: dict[str, dict[str, tuple[URIRef, str, bool]]] = {
    "actant": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
        "participates_in": (ANT.participatesIn, IRI, True),
        "corresponds_to": (ANT.correspondsTo, IRI, True),
        "internalizes": (ANT.internalizes, IRI, True),
        "inscribes": (ANT.inscribes, IRI, True),
        "draws_on": (ANT.drawsOn, IRI, True),
        "manifests_as": (ANT.manifestsAs, IRI, True),
        "has_program": (ANT.hasProgram, IRI, True),
        "enrols": (ANT.enrols, IRI, True),
    },
    "inscription": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
        "source": (DCTERMS.source, LIT, False),
        # class = the inscription's rdf:type (ant:Inscription / ImmutableMobile /
        # FluidObject).
        # Set-replace: exactly one type triple, mirroring new-record.
        "class": (RDF.type, IRI, False),
    },
    "characterization": {
        "target": (ANT.characterizes, IRI, False),
        "within_network": (ANT.withinNetwork, IRI, False),
        "assigns_role": (ANT.assignsRole, IRI, False),
        "per_practice": (ANT.perPractice, IRI, False),
        "invariance": (ANT.invarianceCriterion, LIT, False),
        "description": (DCTERMS.description, LIT, False),
    },
    "network": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
        "scope": (ANT.scopeIri, IRI, False),
        "from_construct": (ANT.fromConstruct, LIT, False),
    },
    "translation": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
        "has_moment": (ANT.hasMoment, IRI, True),
        "reads_same_program_as": (ANT.readsSameProgramAs, IRI, True),
        "traces_to_passage": (ANT.tracesToPassage, IRI, True),
        "has_durability": (ANT.hasDurability, IRI, False),
        "has_status": (ANT.hasStatus, IRI, False),
        "authored_under": (ANT.authoredUnder, IRI, False),
    },
    "moment": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
    },
    "program": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
        "opposes": (ANT.opposes, IRI, True),
    },
    "practice": {
        "label": (RDFS.label, LIT, False),
        "description": (DCTERMS.description, LIT, False),
    },
}


class EditError(Exception):
    """Editing/removal problem the CLI should surface cleanly (not a traceback)."""


def editable_fields(kind: str) -> list[str]:
    return sorted(_EDIT_SPEC.get(kind, {}))


def supported_kinds() -> list[str]:
    return sorted(_EDIT_SPEC)


def _kind_file(
    kind: str, case: str | None, perspective: str | None, target: Path | None
) -> Path:
    if target is not None:
        return Path(target)
    if kind == "practice":
        return SHARED_DIR / "practices.ttl"
    if case is None or perspective is None:
        raise EditError("case and perspective are required to locate the record file.")
    return _file_for_kind(case, perspective, kind)


def _coerce(value: str, mode: str) -> URIRef | Literal:
    return URIRef(value) if mode == IRI else Literal(value)


def edit_record(
    kind: str,
    iri: str,
    updates: dict[str, object],
    *,
    case: str | None = None,
    perspective: str | None = None,
    target: Path | None = None,
) -> Path:
    """Set-replace the given fields on record ``iri`` in its kind-file.

    ``updates`` maps a field flag (see ``_EDIT_SPEC``) to a value (str) or list
    of str for multi-valued fields. An empty string / empty list clears the
    field. Only provided fields change; others are untouched. Returns the
    file written.
    """
    if kind not in _EDIT_SPEC:
        raise EditError(
            f"edit-record does not support kind {kind!r}; supported: {supported_kinds()}"
        )
    spec = _EDIT_SPEC[kind]
    unknown = [f for f in updates if f not in spec]
    if unknown:
        raise EditError(
            f"{kind} has no editable field(s) {unknown}; editable: {editable_fields(kind)}"
        )
    if not updates:
        raise EditError("no fields to edit were provided.")

    path = _kind_file(kind, case, perspective, target)
    if not path.exists():
        raise EditError(f"no {kind} file at {path}")

    ds = new_dataset()
    ds.parse(path, format="turtle")
    g = ds.default_graph
    s = URIRef(iri)
    if (s, RDF.type, None) not in g:
        raise EditError(f"no record {iri} found in {path}")

    for flag, value in updates.items():
        pred, mode, _multi = spec[flag]
        g.remove((s, pred, None))
        values = value if isinstance(value, (list, tuple)) else [value]
        for v in values:
            if v is None or v == "":
                continue
            g.add((s, pred, _coerce(str(v), mode)))
    write_turtle(ds, path)
    return path


def find_referrers(graph: Graph, s: URIRef) -> list[str]:
    """Distinct subjects (other than ``s``) that point at ``s`` — inbound refs."""
    return sorted(
        {
            str(x)
            for x, _p, _o in graph.triples((None, None, s))
            if isinstance(x, URIRef) and x != s
        }
    )


def _locate_in_perspective(case: str, perspective: str, s: URIRef) -> Path | None:
    pdir = _perspective_dir(case, perspective)
    if not pdir.exists():
        return None
    for f in sorted(pdir.glob("*.ttl")):
        g = Graph()
        g.parse(f, format="turtle")
        if (s, RDF.type, None) in g:
            return f
    return None


def remove_record(
    iri: str,
    *,
    case: str,
    perspective: str,
    force: bool = False,
    target: Path | None = None,
    scan: Dataset | None = None,
) -> tuple[Path, list[str]]:
    """Remove record ``iri`` from its kind-file in ``perspective``.

    Pre-checks inbound cross-references across the whole case; if any exist and
    ``force`` is False, raises without modifying anything. Returns
    ``(file_written, referrers)``; with ``force`` the referrers are returned so
    the caller can warn that they now dangle (``ant verify`` will flag them).
    """
    s = URIRef(iri)
    path = (
        Path(target)
        if target is not None
        else _locate_in_perspective(case, perspective, s)
    )
    if path is None or not path.exists():
        raise EditError(
            f"no record {iri} found in perspective {perspective!r} of case {case!r}"
        )

    scan_ds = scan if scan is not None else load_case(case)
    refs = find_referrers(scan_ds.default_graph, s)
    if refs and not force:
        listed = "\n".join(f"  - {r}" for r in refs)
        raise EditError(
            f"{iri} is referenced by {len(refs)} record(s); refusing to remove.\n"
            f"{listed}\n"
            "Re-run with --force to remove anyway "
            "(leaves dangling refs for `ant verify` to flag)."
        )

    ds = new_dataset()
    ds.parse(path, format="turtle")
    g = ds.default_graph
    if (s, RDF.type, None) not in g:
        raise EditError(f"no record {iri} found in {path}")
    g.remove((s, None, None))
    write_turtle(ds, path)
    return path, refs
