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


_STATUS_TOKENS = {
    "stabilized": "Stabilized",
    "precarious": "Precarious",
    "unravelled": "Unravelled",
    "unraveled": "Unravelled",
}


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


def query_traffic(g: Graph, passage: URIRef) -> list[dict]:
    """Translations that must clear (``tracesToPassage``) or pass through
    (``passesThrough``) an obligatory passage point actant."""
    rows: list[dict] = []
    for pred, via in ((ANT.tracesToPassage, "traces"), (ANT.passesThrough, "passes-through")):
        for t in g.subjects(pred, passage):
            if not isinstance(t, URIRef):
                continue
            au = next(iter(g.objects(t, ANT.authoredUnder)), None)
            rows.append({
                "translation": label_of(g, t),
                "via": via,
                "frame": frame_label(g, au) if isinstance(au, URIRef) else "",
            })
    return sorted(rows, key=lambda r: r["translation"])


def query_status(g: Graph, status: str) -> list[dict]:
    """Translations by behavioral status. ``forming`` = no ``hasStatus`` triple
    (a deliberate 'not yet assessable' state, not missing data)."""
    token = status.lower()
    forming = token == "forming"
    want = None if forming else _STATUS_TOKENS.get(token)
    if not forming and want is None:
        raise QueryError(
            f"unknown status {status!r}; expected one of "
            "stabilized / precarious / unravelled / forming"
        )
    rows: list[dict] = []
    for t in g.subjects(RDF.type, ANT.Translation):
        if not isinstance(t, URIRef):
            continue
        st = next(iter(g.objects(t, ANT.hasStatus)), None)
        st_name = local_name(str(st)) if isinstance(st, URIRef) else None
        hit = (st_name is None) if forming else (st_name == want)
        if not hit:
            continue
        du = next(iter(g.objects(t, ANT.hasDurability)), None)
        au = next(iter(g.objects(t, ANT.authoredUnder)), None)
        rows.append({
            "translation": label_of(g, t),
            "frame": frame_label(g, au) if isinstance(au, URIRef) else "",
            "durability": local_name(str(du)) if isinstance(du, URIRef) else "",
        })
    return sorted(rows, key=lambda r: r["translation"])


def query_same_program(g: Graph, of: URIRef | None = None) -> list[list[str]]:
    """Clusters of translations linked by ``readsSameProgramAs`` (a symmetric
    relation). If ``of`` is given, only the cluster containing it."""
    adj: dict[URIRef, set[URIRef]] = {}
    for s, o in g.subject_objects(ANT.readsSameProgramAs):
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            adj.setdefault(s, set()).add(o)
            adj.setdefault(o, set()).add(s)
    seen: set[URIRef] = set()
    clusters: list[list[URIRef]] = []
    for node in sorted(adj, key=str):
        if node in seen:
            continue
        stack, comp = [node], []
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            comp.append(n)
            stack.extend(adj[n] - seen)
        clusters.append(sorted(comp, key=str))
    if of is not None:
        clusters = [c for c in clusters if of in c]
    return [[label_of(g, n) for n in c] for c in clusters]


def query_anti_programs(g: Graph) -> list[dict]:
    """The ``opposes`` edges: program of action -> the translation/program it
    runs against."""
    rows = [
        {"program": label_of(g, s), "opposes": label_of(g, o)}
        for s, o in g.subject_objects(ANT.opposes)
        if isinstance(s, URIRef) and isinstance(o, URIRef)
    ]
    return sorted(rows, key=lambda r: r["program"])


def query_manifests(g: Graph) -> list[dict]:
    """The ``manifestsAs`` edges: an actant -> the inscription it also is (C9)."""
    rows = [
        {
            "actant": label_of(g, s),
            "inscription": label_of(g, o),
            "inscription_type": _type_name(g, o),
        }
        for s, o in g.subject_objects(ANT.manifestsAs)
        if isinstance(s, URIRef) and isinstance(o, URIRef)
    ]
    return sorted(rows, key=lambda r: (r["actant"], r["inscription"]))


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


def run_traffic(passage: str, as_json: bool = False) -> None:
    g = load_graph()
    s = resolve(g, passage)
    rows = query_traffic(g, s)

    def render(rows: list[dict]) -> None:
        console.print(f"[bold]{label_of(g, s)}[/bold] — traffic ({len(rows)})")
        for r in rows:
            console.print(f"  {r['translation']} {escape('[' + r['frame'] + ']')} ({r['via']})")
        if not rows:
            console.print("  (nothing traces to or passes through this passage yet)")
    _emit(rows, as_json, render)


def run_status(status: str, as_json: bool = False) -> None:
    g = load_graph()
    rows = query_status(g, status)

    def render(rows: list[dict]) -> None:
        console.print(f"[bold]{status.capitalize()}[/bold] translations ({len(rows)})")
        for r in rows:
            dur = f" · {r['durability']}" if r["durability"] else ""
            console.print(f"  {r['translation']} {escape('[' + r['frame'] + ']')}{dur}")
    _emit(rows, as_json, render)


def run_same_program(of: str | None = None, as_json: bool = False) -> None:
    g = load_graph()
    subj = resolve(g, of) if of else None
    clusters = query_same_program(g, subj)

    def render(clusters: list[list[str]]) -> None:
        console.print(f"[bold]Same-program clusters[/bold] ({len(clusters)})")
        for i, c in enumerate(clusters, 1):
            console.print(f"  {i}. " + " ↔ ".join(c))
    _emit(clusters, as_json, render)


def run_anti_programs(as_json: bool = False) -> None:
    g = load_graph()
    rows = query_anti_programs(g)

    def render(rows: list[dict]) -> None:
        console.print(f"[bold]Anti-programs[/bold] ({len(rows)})")
        for r in rows:
            console.print(f"  {r['program']} — opposes → {r['opposes']}")
    _emit(rows, as_json, render)


def run_manifests(as_json: bool = False) -> None:
    g = load_graph()
    rows = query_manifests(g)

    def render(rows: list[dict]) -> None:
        console.print(
            f"[bold]Manifestations[/bold] (an actant that is also an inscription) ({len(rows)})"
        )
        for r in rows:
            console.print(
                f"  {r['actant']} — manifests as → {r['inscription']} "
                f"{escape('[' + r['inscription_type'] + ']')}"
            )
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
