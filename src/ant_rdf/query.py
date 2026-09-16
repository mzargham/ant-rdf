# SPDX-License-Identifier: Apache-2.0
"""Read-only graph queries for navigating the field — the reader's counterpart
to authoring (``new-record`` / ``edit-record``).

Every function here is READ-ONLY. The curated queries **bake in fidelity**: a
role is always reported as a value assigned *inside* an ``ant:Characterization``
(with its ``perPractice`` / ``withinNetwork`` / ``invarianceCriterion``), never
as an ``rdf:type`` on the actant (per R3/R6/C2/C3). The pure ``query_*``
functions take a graph and return plain data (unit-testable); the ``run_*``
wrappers load the full instance graph and print (Rich text, or ``--json``).

Wired into the CLI as the ``ant query`` subgroup (see cli.py).
"""

from __future__ import annotations

import json as _json
from collections.abc import Callable
from typing import Any

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS
from rich.console import Console
from rich.markup import escape

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    description_of,
    frame_label,
    label_of,
    local_name,
    perspective_index,
)

console = Console()


class QueryError(ValueError):
    """A query could not be resolved (bad slug, unknown token, …)."""


# --------------------------------------------------------------------------- #
# Loading + resolution
# --------------------------------------------------------------------------- #

def load_graph() -> Graph:
    """The full instance graph (shared + every case + waivers); no ontology,
    so instance queries are not polluted by term definitions."""
    from ant_rdf.verify import _build_data_dataset
    return _build_data_dataset(None).default_graph


def resolve(g: Graph, token: str) -> URIRef:
    """A bare slug (``larvae-collectors``, ``fishermen``) or a full IRI to a
    subject that exists in the graph. Slugs match on IRI local-name; when the
    same slug exists in several cases the lowest IRI wins — pass the full IRI
    to disambiguate."""
    if token.startswith("http"):
        return URIRef(token)
    matches = sorted(
        {s for s in g.subjects() if isinstance(s, URIRef) and local_name(str(s)) == token}
    )
    if not matches:
        raise QueryError(f"no record found for slug/IRI {token!r}")
    return matches[0]


# --------------------------------------------------------------------------- #
# Pure queries (graph -> data)
# --------------------------------------------------------------------------- #

def query_roles(g: Graph, actant: URIRef) -> list[dict]:
    """Every role the actant is assigned, one row per Characterization, with the
    frame/practice/network/invariance that scopes it."""
    _, practice_to_persp = perspective_index(g)
    rows: list[dict] = []
    for c in g.subjects(ANT.characterizes, actant):
        if not isinstance(c, URIRef):
            continue
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        prac = next(iter(g.objects(c, ANT.perPractice)), None)
        net = next(iter(g.objects(c, ANT.withinNetwork)), None)
        inv = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
        persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
        rows.append({
            "characterization": local_name(str(c)),
            "frame": frame_label(g, persp) if isinstance(persp, URIRef)
            else (local_name(str(prac)) if isinstance(prac, URIRef) else "(no practice)"),
            "role": local_name(str(role)) if isinstance(role, URIRef) else "(no role)",
            "network": label_of(g, net) if isinstance(net, URIRef) else "",
            "invariance": str(inv) if inv is not None else "",
            "practice": local_name(str(prac)) if isinstance(prac, URIRef) else "",
        })
    return sorted(rows, key=lambda r: (r["frame"], r["role"], r["characterization"]))


def _roles_by_actant(g: Graph) -> dict[URIRef, dict[URIRef, set[str]]]:
    _, practice_to_persp = perspective_index(g)
    out: dict[URIRef, dict[URIRef, set[str]]] = {}
    for c in g.subjects(RDF.type, ANT.Characterization):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        prac = next(iter(g.objects(c, ANT.perPractice)), None)
        persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
        if not (isinstance(actant, URIRef) and isinstance(role, URIRef) and persp is not None):
            continue
        out.setdefault(actant, {}).setdefault(persp, set()).add(local_name(str(role)))
    return out


def query_flips(g: Graph) -> list[dict]:
    """Actants read as different roles by different frames (the role-flip set)."""
    rows: list[dict] = []
    for actant, by_persp in _roles_by_actant(g).items():
        if len(by_persp) < 2:
            continue
        if len({r for rs in by_persp.values() for r in rs}) <= 1:
            continue
        rows.append({
            "actant": label_of(g, actant),
            "by_frame": {
                frame_label(g, p): sorted(rs) for p, rs in by_persp.items()
            },
        })
    return sorted(rows, key=lambda r: r["actant"])


def query_search(g: Graph, text: str) -> list[dict]:
    """Case-insensitive substring over rdfs:label and dcterms:description."""
    needle = text.lower()
    hits: dict[URIRef, dict] = {}
    for pred, field in ((RDFS.label, "label"), (DCTERMS.description, "description")):
        for s, o in g.subject_objects(pred):
            if not isinstance(s, URIRef):
                continue
            if needle in str(o).lower():
                entry = hits.setdefault(s, {"iri": str(s), "type": _type_name(g, s),
                                            "label": label_of(g, s), "fields": set()})
                entry["fields"].add(field)
    out = [
        {"iri": h["iri"], "type": h["type"], "label": h["label"],
         "fields": sorted(h["fields"])}
        for h in hits.values()
    ]
    return sorted(out, key=lambda r: (r["type"], r["label"]))


def query_show(g: Graph, subject: URIRef) -> dict:
    """A fidelity-aware record view: its type, label, description, and a grouped
    predicate->object map (labels resolved for IRI objects). A Characterization
    additionally renders as target -> role within network per practice."""
    out: dict = {
        "iri": str(subject),
        "type": _type_name(g, subject),
        "label": label_of(g, subject),
        "description": description_of(g, subject),
        "properties": {},
    }
    for p, o in g.predicate_objects(subject):
        if p in (RDF.type, RDFS.label, DCTERMS.description):
            continue
        key = local_name(str(p))
        val = label_of(g, o) if isinstance(o, URIRef) else str(o)
        out["properties"].setdefault(key, []).append(val)
    for k in out["properties"]:
        out["properties"][k] = sorted(out["properties"][k])
    if out["type"] == "Characterization":
        tgt = next(iter(g.objects(subject, ANT.characterizes)), None)
        role = next(iter(g.objects(subject, ANT.assignsRole)), None)
        net = next(iter(g.objects(subject, ANT.withinNetwork)), None)
        prac = next(iter(g.objects(subject, ANT.perPractice)), None)
        inv = next(iter(g.objects(subject, ANT.invarianceCriterion)), None)
        out["reading"] = (
            f"{label_of(g, tgt) if isinstance(tgt, URIRef) else '?'} "
            f"→ {local_name(str(role)) if isinstance(role, URIRef) else '?'} "
            f"within {label_of(g, net) if isinstance(net, URIRef) else '?'} "
            f"per {local_name(str(prac)) if isinstance(prac, URIRef) else '?'}"
            + (f" tracking '{inv}'" if inv is not None else "")
        )
    return out


def query_sparql(g: Graph, query: str) -> list[dict]:
    """Escape hatch: run an arbitrary SPARQL SELECT/ASK over the instance graph."""
    rows: list[dict] = []
    for row in g.query(query):
        if hasattr(row, "labels") and row.labels:
            rows.append({
                str(k): (str(v) if v is not None else None)
                for k, v in zip(row.labels, row, strict=False)
            })
        else:  # ASK
            rows.append({"result": str(row)})
    return rows


def _type_name(g: Graph, s: URIRef) -> str:
    t = next((o for o in g.objects(s, RDF.type) if isinstance(o, URIRef)), None)
    return local_name(str(t)) if t is not None else "(untyped)"


# --------------------------------------------------------------------------- #
# CLI wrappers (load + print)
# --------------------------------------------------------------------------- #

def _emit(data: Any, as_json: bool, render: Callable[[Any], None]) -> None:
    if as_json:
        # sets are pre-sorted to lists by the pure funcs; default=str is a guard
        print(_json.dumps(data, indent=2, default=str))
    else:
        render(data)


def run_roles(actant: str, as_json: bool = False) -> None:
    g = load_graph()
    s = resolve(g, actant)
    rows = query_roles(g, s)

    def render(rows: list[dict]) -> None:
        console.print(f"[bold]{label_of(g, s)}[/bold] — roles across frames")
        if not rows:
            console.print("  (no characterizations — this actant is given no role in any frame)")
        for r in rows:
            extra = f" · tracks '{r['invariance']}'" if r["invariance"] else ""
            # escape(): a literal "[frame]" would otherwise be eaten as Rich markup
            console.print(
                f"  {escape('[' + r['frame'] + ']')} {r['role']} — within "
                f"{r['network']}{extra} ([dim]{r['characterization']}[/dim])"
            )
    _emit(rows, as_json, render)


def run_flips(as_json: bool = False) -> None:
    g = load_graph()
    rows = query_flips(g)

    def render(rows: list[dict]) -> None:
        console.print(
            f"[bold]Role flips[/bold] ({len(rows)} actants read differently across frames)"
        )
        for r in rows:
            parts = ", ".join(
                f"{fr} = {'/'.join(roles)}" for fr, roles in sorted(r["by_frame"].items())
            )
            console.print(f"  {r['actant']}: {parts}")
    _emit(rows, as_json, render)


def run_search(text: str, as_json: bool = False) -> None:
    g = load_graph()
    rows = query_search(g, text)

    def render(rows: list[dict]) -> None:
        console.print(f"[bold]Search[/bold] '{text}' ({len(rows)} records)")
        for r in rows:
            console.print(f"  [{r['type']}] {r['label']}  ({'/'.join(r['fields'])})")
    _emit(rows, as_json, render)


def run_show(token: str, as_json: bool = False) -> None:
    g = load_graph()
    s = resolve(g, token)
    data = query_show(g, s)

    def render(d: dict) -> None:
        console.print(f"[bold]{d['label']}[/bold] — {d['type']}")
        console.print(f"  {d['iri']}")
        if d["description"]:
            console.print(f"  {d['description']}")
        if "reading" in d:
            console.print(f"  reading: {d['reading']}")
        for k, vals in d["properties"].items():
            console.print(f"  {k}: " + ", ".join(vals))
    _emit(data, as_json, render)


def run_sparql(query: str, as_json: bool = False) -> None:
    g = load_graph()
    rows = query_sparql(g, query)

    def render(rows: list[dict]) -> None:
        console.print(f"[bold]SPARQL[/bold] — {len(rows)} row(s)")
        for r in rows:
            console.print("  " + " · ".join(f"{k}={v}" for k, v in r.items()))
    _emit(rows, as_json, render)
