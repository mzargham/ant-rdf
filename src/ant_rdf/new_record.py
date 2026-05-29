# SPDX-License-Identifier: Apache-2.0
"""Record creation: flag-driven (LLM-callable) and interactive (catechism) modes.

All paths produce structurally correct RDF; ethnographer-validation of
content is out-of-scope here (per C7). Per C8, the same ``create_*`` helpers
are reachable from the catechism skill, direct CLI invocation, and (via
``ingest.py``) note-import — one mechanism, multiple front-ends.

File layout per §4.5 quad-readiness:

    instances/cases/<case>/perspectives/<perspective>/<kind>s.ttl

Each file accumulates records of a given kind for that (case, perspective)
pair. If the file exists, the new record's triples are merged in and the
file is re-serialized deterministically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdflib import Dataset
from rdflib.namespace import RDF

from ant_rdf.graph import CASES_DIR, SHARED_DIR, new_dataset
from ant_rdf.models import (
    Actant,
    AntModel,
    Characterization,
    Network,
    Perspective,
    Practice,
    Problematization,
    Translation,
)
from ant_rdf.serialize import add, write_turtle

# ---------------------------------------------------------------------------
# File-routing
# ---------------------------------------------------------------------------


def _perspective_dir(case: str, perspective: str) -> Path:
    return CASES_DIR / case / "perspectives" / perspective


def _file_for_kind(case: str, perspective: str, kind: str) -> Path:
    return _perspective_dir(case, perspective) / f"{kind}s.ttl"


def _merge_into(target: Path, obj: AntModel | Characterization) -> None:
    """Add ``obj`` to the file at ``target`` (creating or merging) and
    re-serialize deterministically."""
    ds = new_dataset()
    if target.exists():
        ds.parse(target, format="turtle")
    add(ds, obj)
    write_turtle(ds, target)


def _ensure_perspective_record(case: str, perspective: str) -> None:
    """If ``_perspective.ttl`` doesn't exist for this (case, perspective),
    write a minimal stub recording that the perspective exists. This keeps
    the file-system convention honest: every perspective subdir has its
    perspective metadata file.

    For the special ``_default`` slug, the stub uses a synthesized IRI and
    a placeholder holder; the ethnographer should run ``ant new-record
    perspective`` to record actual metadata when they have it.
    """
    pdir = _perspective_dir(case, perspective)
    perspective_file = pdir / "_perspective.ttl"
    if perspective_file.exists():
        return
    pdir.mkdir(parents=True, exist_ok=True)
    iri = f"https://w3id.org/ant/cases/{case}/perspectives/{perspective}"
    holder = "https://w3id.org/ant/agent/_unspecified"
    obj = Perspective(
        iri=iri,
        label=f"Auto-created perspective stub: {perspective}",
        description=(
            f"Auto-created stub for perspective '{perspective}' in case '{case}'. "
            "Run `ant new-record perspective` to record the actual holder, "
            "grounding practices, and tracked invariances."
        ),
        held_by=holder,
        case=case,
        grounded_in=[],
        tracks_invariance=[],
    )
    ds = new_dataset()
    add(ds, obj)
    write_turtle(ds, perspective_file)


# ---------------------------------------------------------------------------
# Flag-driven creators
# ---------------------------------------------------------------------------


def create_network(
    iri: str,
    label: str,
    description: str,
    case: str,
    perspective: str = "_default",
    scope: str | None = None,
    from_construct: str | None = None,
    out: str | None = None,
) -> Path:
    _ensure_perspective_record(case, perspective)
    obj = Network(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, scope=scope, from_construct=from_construct,
    )
    target = Path(out) if out else _file_for_kind(case, perspective, "network")
    _merge_into(target, obj)
    return target


def create_actant(
    iri: str,
    label: str,
    description: str,
    case: str,
    perspective: str = "_default",
    participates_in: list[str] | None = None,
    out: str | None = None,
) -> Path:
    _ensure_perspective_record(case, perspective)
    obj = Actant(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, participates_in=list(participates_in or []),
    )
    target = Path(out) if out else _file_for_kind(case, perspective, "actant")
    _merge_into(target, obj)
    return target


def create_translation(
    iri: str,
    label: str,
    description: str,
    case: str,
    perspective: str = "_default",
    has_moment: list[str] | None = None,
    out: str | None = None,
) -> Path:
    _ensure_perspective_record(case, perspective)
    obj = Translation(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, has_moment=list(has_moment or []),
    )
    target = Path(out) if out else _file_for_kind(case, perspective, "translation")
    _merge_into(target, obj)
    return target


def create_perspective(
    iri: str,
    label: str,
    held_by: str,
    case: str,
    grounded_in: list[str] | None = None,
    tracks_invariance: list[str] | None = None,
    description: str | None = None,
) -> Path:
    obj = Perspective(
        iri=iri,
        label=label,
        description=description or f"Perspective: {label}",
        held_by=held_by,
        case=case,
        grounded_in=list(grounded_in or []),
        tracks_invariance=list(tracks_invariance or []),
    )
    # Derive the perspective slug from the IRI's last path segment.
    perspective_slug = iri.rstrip("/").rsplit("/", 1)[-1]
    target = _perspective_dir(case, perspective_slug) / "_perspective.ttl"
    target.parent.mkdir(parents=True, exist_ok=True)
    # Overwrite (a perspective's metadata file is the canonical record;
    # not appended-to like instance kinds).
    ds = new_dataset()
    add(ds, obj)
    write_turtle(ds, target)
    return target


def create_practice(
    iri: str,
    label: str,
    description: str,
    out: str | None = None,
) -> Path:
    """Create an ant:Practice record.

    Practices are perspective-agnostic shared vocabulary; they live under
    instances/shared/ (default: practices.ttl), not under a case/perspective.
    They back the ant:perPractice (Characterization) and
    ant:perspectiveGroundedIn (Perspective) cross-references.
    """
    obj = Practice(iri=iri, label=label, description=description)
    target = Path(out) if out else SHARED_DIR / "practices.ttl"
    _merge_into(target, obj)
    return target


def create_characterization(
    iri: str,
    target: str,
    within_network: str,
    assigns_role: str,
    case: str,
    perspective: str = "_default",
    per_practice: str | None = None,
    invariance: str | None = None,
    description: str | None = None,
) -> Path:
    """Create an ant:Characterization (§4.1.1)."""
    _ensure_perspective_record(case, perspective)
    obj = Characterization(
        iri=iri,
        characterizes=target,
        within_network=within_network,
        per_practice=per_practice,
        invariance=invariance,
        assigns_role=assigns_role,  # type: ignore[arg-type]  # Literal validated at runtime
        case=case,
        perspective=perspective,
        description=description,
    )
    target_path = _file_for_kind(case, perspective, "characterization")
    _merge_into(target_path, obj)
    return target_path


# Convenience for the four moments (used by interactive mode)


def create_moment(
    moment_kind: str,
    iri: str,
    label: str,
    description: str,
    case: str,
    perspective: str = "_default",
    out: str | None = None,
) -> Path:
    """Create one of the four Callon moments."""
    _ensure_perspective_record(case, perspective)
    cls_map = {
        "problematization": Problematization,
        "interessement": __import__("ant_rdf.models", fromlist=["Interessement"]).Interessement,
        "enrolment": __import__("ant_rdf.models", fromlist=["Enrolment"]).Enrolment,
        "mobilization": __import__("ant_rdf.models", fromlist=["Mobilization"]).Mobilization,
    }
    cls = cls_map.get(moment_kind.lower())
    if cls is None:
        raise ValueError(
            f"Unknown moment kind {moment_kind!r}; expected one of {sorted(cls_map)}"
        )
    obj = cls(
        iri=iri, label=label, description=description, case=case, perspective=perspective,
    )
    target = Path(out) if out else _file_for_kind(case, perspective, "moment")
    _merge_into(target, obj)
    return target


# ---------------------------------------------------------------------------
# Interactive (catechism) mode
# ---------------------------------------------------------------------------


def interactive_create(kind: str) -> None:
    """Walk-me-through prompts for a record kind (conversational catechism).

    Per C8, the conversational path is *one* ingestion mode; for note-import
    or upload paths the user should run ``ant ingest …`` instead. We offer
    an early off-ramp before any required field is collected.
    """
    import typer

    typer.echo("(Catechism mode — one ingestion path among several; see `ant ingest --help` for others.)")
    typer.echo("Press Ctrl-C to abort at any time.")
    typer.echo()

    if kind not in {"network", "actant", "translation", "perspective", "characterization"}:
        raise typer.BadParameter(
            f"Unknown kind {kind!r}; expected network, actant, translation, perspective, or characterization."
        )

    case = typer.prompt("Case slug")
    perspective = typer.prompt("Perspective slug", default="_default")

    if kind == "network":
        iri = typer.prompt("IRI for the network")
        label = typer.prompt("Short label (rdfs:label)")
        description = typer.prompt("Description (dcterms:description; narrative paragraph)")
        path = create_network(iri=iri, label=label, description=description,
                              case=case, perspective=perspective)
    elif kind == "actant":
        iri = typer.prompt("IRI for the actant")
        label = typer.prompt("Short label (no human/non-human pre-classification needed)")
        description = typer.prompt("Description")
        participates = _prompt_list("Network IRI this actant participates in (blank to finish)")
        path = create_actant(iri=iri, label=label, description=description,
                             case=case, perspective=perspective,
                             participates_in=participates)
    elif kind == "translation":
        iri = typer.prompt("IRI for the translation")
        label = typer.prompt("Short label")
        description = typer.prompt("Description")
        moments = _prompt_list("Moment IRI this translation has (blank to finish; ≥1 required)")
        if not moments:
            typer.echo("⚠ A translation needs at least one moment (Tier-1 SHACL).")
            return
        path = create_translation(iri=iri, label=label, description=description,
                                  case=case, perspective=perspective,
                                  has_moment=moments)
    elif kind == "perspective":
        iri = typer.prompt("IRI for the perspective")
        label = typer.prompt("Short label")
        description = typer.prompt("Description")
        held_by = typer.prompt("Perspective held by (prov:Agent IRI)")
        grounded = _prompt_list("Practice IRI this perspective is grounded in (blank to finish)")
        tracks = _prompt_list("Invariance tracked by this perspective (free text, blank to finish)")
        path = create_perspective(iri=iri, label=label, description=description,
                                  held_by=held_by, case=case,
                                  grounded_in=grounded, tracks_invariance=tracks)
    elif kind == "characterization":
        iri = typer.prompt("IRI for the characterization")
        target = typer.prompt("Target actant IRI (what is being characterized)")
        within_network = typer.prompt("Within which network IRI")
        assigns_role = typer.prompt(
            "Assigns role IRI (e.g., https://w3id.org/ant#Mediator)"
        )
        per_practice = typer.prompt(
            "Per practice IRI (recommended; blank to skip and let Tier-2 warn)",
            default="",
        ) or None
        invariance = typer.prompt(
            "Invariance criterion (recommended; blank to skip and let Tier-2 warn)",
            default="",
        ) or None
        description = typer.prompt("Description (optional)", default="") or None
        path = create_characterization(
            iri=iri, target=target, within_network=within_network,
            assigns_role=assigns_role, case=case, perspective=perspective,
            per_practice=per_practice, invariance=invariance, description=description,
        )
    else:  # pragma: no cover
        raise typer.BadParameter(f"Unhandled kind {kind!r}")

    typer.echo(f"✓ wrote {path}")
    typer.echo("Run `ant verify` to check SHACL conformance.")


def _prompt_list(prompt_text: str) -> list[str]:
    """Collect a list by repeatedly prompting until the user enters an empty line."""
    import typer

    out: list[str] = []
    while True:
        value = typer.prompt(prompt_text, default="", show_default=False)
        if not value:
            break
        out.append(value)
    return out
