# SPDX-License-Identifier: Apache-2.0
"""Wiki page generator — the loop-closing artifact for ethnographers (§6.1).

Produces a hyperlinked, GitHub-Pages-compatible Markdown wiki under ``wiki/``.
Per the user's note, this is expected to evolve to fit ethnographer use —
the v1 layout is a starting point, not a polished design.

Initial pages:
- ``Home.md`` — landing page listing cases and concepts
- ``Cases/<slug>.md`` — one page per case linking out to its actants,
  translations, characterizations, perspectives
- ``Actants/<slug>.md`` — one page per actant (cross-case where shared)
- ``Concepts/<term>.md`` — one page per ontology term with founding-text
  citations (turns the vocabulary itself into a navigable glossary)
- ``Perspectives/<slug>.md`` — one page per perspective
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS
from rich.console import Console

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    description_of,
    label_of,
    local_name,
    slugify,
)
from ant_rdf.graph import REPO_ROOT, load_full_dataset, load_ontology

console = Console()

DEFAULT_WIKI_DIR = REPO_ROOT / "wiki"


def run_wiki(output_dir: str | None = None) -> None:
    """Generate all wiki pages to ``output_dir`` (default: ``<repo>/wiki``)."""
    out = Path(output_dir) if output_dir else DEFAULT_WIKI_DIR
    out.mkdir(parents=True, exist_ok=True)

    ds = load_full_dataset()
    g = ds.default_graph

    # Subdirectories
    (out / "Cases").mkdir(exist_ok=True)
    (out / "Actants").mkdir(exist_ok=True)
    (out / "Concepts").mkdir(exist_ok=True)
    (out / "Perspectives").mkdir(exist_ok=True)

    cases = _gather_cases(g)
    actants = _gather_by_type(g, ANT.Actant)
    perspectives = _gather_by_type(g, ANT.Perspective)
    concepts = _gather_concepts(load_ontology().default_graph)

    pages_written = 0

    # Home
    (out / "Home.md").write_text(
        _render_home(cases, actants, perspectives, concepts), encoding="utf-8"
    )
    pages_written += 1

    # Cases
    for case_slug, case_data in sorted(cases.items()):
        page = _render_case(g, case_slug, case_data)
        (out / "Cases" / f"{case_slug}.md").write_text(page, encoding="utf-8")
        pages_written += 1

    # Actants
    for a in actants:
        page = _render_actant(g, a)
        (out / "Actants" / f"{slugify(str(a))}.md").write_text(page, encoding="utf-8")
        pages_written += 1

    # Perspectives
    for p in perspectives:
        page = _render_perspective(g, p)
        (out / "Perspectives" / f"{slugify(str(p))}.md").write_text(page, encoding="utf-8")
        pages_written += 1

    # Concepts
    for term, data in sorted(concepts.items()):
        page = _render_concept(term, data)
        (out / "Concepts" / f"{slugify(term)}.md").write_text(page, encoding="utf-8")
        pages_written += 1

    console.print(f"[green]✓ wrote {pages_written} wiki pages to {out}[/green]")


# ---------------------------------------------------------------------------
# Gather
# ---------------------------------------------------------------------------


def _gather_by_type(g: Graph, cls: URIRef) -> list[URIRef]:
    return sorted(s for s in g.subjects(RDF.type, cls) if isinstance(s, URIRef))


def _gather_cases(g: Graph) -> dict[str, dict]:
    """Heuristic v1: derive case slugs from network IRIs of the form
    ``https://w3id.org/ant/cases/<slug>/network`` (or any IRI containing
    ``/cases/<slug>/``). Returns ``{slug: {networks, perspectives}}``."""
    cases: dict[str, dict[str, set]] = {}
    for s in g.subjects():
        if not isinstance(s, URIRef):
            continue
        slug = _case_slug(str(s))
        if not slug:
            continue
        cases.setdefault(slug, {"networks": set(), "perspectives": set(), "actants": set()})
        for t in g.objects(s, RDF.type):
            if t == ANT.Network:
                cases[slug]["networks"].add(s)
            elif t == ANT.Perspective:
                cases[slug]["perspectives"].add(s)
            elif t == ANT.Actant:
                cases[slug]["actants"].add(s)
    return {k: v for k, v in cases.items() if any(v.values())}


def _case_slug(iri: str) -> str | None:
    marker = "/cases/"
    if marker not in iri:
        return None
    rest = iri.split(marker, 1)[1]
    slug = rest.split("/", 1)[0].split("#", 1)[0]
    return slug or None


def _gather_concepts(ont: Graph) -> dict[str, dict]:
    """Every ant: ontology term, with its label, comment, and dcterms:source."""
    concepts: dict[str, dict] = {}
    ant_str = str(ANT)
    for term in sorted(set(ont.subjects())):
        if not isinstance(term, URIRef) or not str(term).startswith(ant_str):
            continue
        types = list(ont.objects(term, RDF.type))
        if not any(t in {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty} for t in types):
            continue
        concepts[str(term)] = {
            "label": label_of(ont, term),
            "comment": str(next(iter(ont.objects(term, RDFS.comment)), "")),
            "source": str(next(iter(ont.objects(term, DCTERMS.source)), "")),
            "kind": _term_kind(types),
        }
    return concepts


def _term_kind(types: list) -> str:
    if OWL.Class in types:
        return "Class"
    if OWL.ObjectProperty in types:
        return "Object property"
    if OWL.DatatypeProperty in types:
        return "Datatype property"
    return "Term"


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def _render_home(cases, actants, perspectives, concepts) -> str:
    lines = [
        "# ant-rdf wiki",
        "",
        "Generated from the canonical RDF in `instances/`. Each page is regenerated by `ant wiki`.",
        "",
        "## Cases",
        "",
    ]
    if cases:
        for slug in sorted(cases):
            lines.append(f"- [{slug}](Cases/{slug}.md)")
    else:
        lines.append("_No cases recorded yet._")
    lines += ["", "## Perspectives", ""]
    if perspectives:
        for p in perspectives:
            lines.append(f"- [{local_name(str(p))}](Perspectives/{slugify(str(p))}.md)")
    else:
        lines.append("_No perspectives recorded yet._")
    lines += ["", "## Actants (cross-case)", ""]
    if actants:
        for a in actants:
            lines.append(f"- [{local_name(str(a))}](Actants/{slugify(str(a))}.md)")
    else:
        lines.append("_No actants recorded yet._")
    lines += ["", "## Concepts (the ontology as a glossary)", ""]
    if concepts:
        for term in sorted(concepts):
            lines.append(f"- [{local_name(term)}](Concepts/{slugify(term)}.md) ({concepts[term]['kind']})")
    return "\n".join(lines) + "\n"


def _render_case(g: Graph, slug: str, case: dict) -> str:
    lines = [f"# Case: {slug}", "", "[← Home](../Home.md)", ""]
    for net in sorted(case["networks"]):
        lines += [
            f"## Network — {label_of(g, net)}",
            "",
            f"<!-- {net} -->",
            "",
            description_of(g, net) or "_(no description)_",
            "",
        ]
    if case["perspectives"]:
        lines += ["## Perspectives", ""]
        for p in sorted(case["perspectives"]):
            lines.append(f"- [{label_of(g, p)}](../Perspectives/{slugify(str(p))}.md)")
        lines.append("")
    if case["actants"]:
        lines += ["## Actants in this case", ""]
        for a in sorted(case["actants"]):
            lines.append(f"- [{label_of(g, a)}](../Actants/{slugify(str(a))}.md)")
        lines.append("")
    return "\n".join(lines) + "\n"


def _render_actant(g: Graph, actant: URIRef) -> str:
    lines = [
        f"# Actant: {label_of(g, actant)}",
        "",
        "[← Home](../Home.md)",
        "",
        f"<!-- {actant} -->",
        "",
        description_of(g, actant) or "_(no description)_",
        "",
        "## Participates in",
        "",
    ]
    nets = sorted(o for o in g.objects(actant, ANT.participatesIn) if isinstance(o, URIRef))
    if nets:
        for n in nets:
            lines.append(f"- [{label_of(g, n)}]({_relative_link_to_network(n)})")
    else:
        lines.append("_(no networks listed)_")
    lines.append("")
    # Characterizations targeting this actant
    chars = sorted(c for c in g.subjects(ANT.characterizes, actant) if isinstance(c, URIRef))
    if chars:
        lines += ["## Characterizations of this actant", ""]
        for c in chars:
            role = next(iter(g.objects(c, ANT.assignsRole)), None)
            net = next(iter(g.objects(c, ANT.withinNetwork)), None)
            practice = next(iter(g.objects(c, ANT.perPractice)), None)
            inv = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
            lines.append(
                f"- **{local_name(str(role)) if role else '?'}** "
                f"in network `{local_name(str(net)) if net else '?'}` — "
                f"practice: `{local_name(str(practice)) if practice else 'unspecified'}`, "
                f"invariance: {str(inv) if inv else '_unspecified_'}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def _render_perspective(g: Graph, p: URIRef) -> str:
    lines = [
        f"# Perspective: {label_of(g, p)}",
        "",
        "[← Home](../Home.md)",
        "",
        f"<!-- {p} -->",
        "",
        description_of(g, p) or "_(no description)_",
        "",
    ]
    held_by = next(iter(g.objects(p, ANT.perspectiveHeldBy)), None)
    if held_by:
        lines.append(f"**Held by:** `{held_by}`")
    grounded = sorted(g.objects(p, ANT.perspectiveGroundedIn))
    if grounded:
        lines.append("")
        lines.append("**Grounded in practices:**")
        for prac in grounded:
            lines.append(f"- `{prac}`")
    tracks = sorted(str(o) for o in g.objects(p, ANT.perspectiveTracksInvariance))
    if tracks:
        lines.append("")
        lines.append("**Tracks invariances:**")
        for inv in tracks:
            lines.append(f"- {inv}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_concept(term: str, data: dict) -> str:
    lines = [
        f"# {local_name(term)} _({data['kind']})_",
        "",
        "[← Home](../Home.md)",
        "",
        f"**IRI:** `{term}`",
        "",
        f"**Label:** {data['label']}",
        "",
        "## Definition",
        "",
        data["comment"] or "_(no rdfs:comment)_",
        "",
        "## Source",
        "",
        data["source"] or "_(no dcterms:source recorded)_",
        "",
    ]
    return "\n".join(lines) + "\n"


def _relative_link_to_network(net_iri: URIRef) -> str:
    """Best-effort link from an Actant page to its Network page (a Case page)."""
    slug = _case_slug(str(net_iri)) or "unknown"
    return f"../Cases/{slug}.md"
