# SPDX-License-Identifier: Apache-2.0
"""Wiki page generator — the loop-closing artifact for ethnographers (§6.1).

Produces a hyperlinked, GitHub-Pages-compatible Markdown wiki under ``wiki/``.
Per the user's note, this is expected to evolve to fit ethnographer use —
the layout below is a starting point, not a polished design.

Pages produced:

- ``Home.md`` — landing: cases (with embedded summary), perspectives,
  actants grouped by case, translations, concept glossary
- ``Cases/<slug>.md`` — RICH case page: network description, translations
  inline, characterization table (§4.1.1 surface), actants, perspectives,
  inscriptions, programs of action
- ``Translations/<slug>.md`` — the four Callon moments rendered narratively
  (reuses the TranslationTrace logic)
- ``Actants/<case>--<slug>.md`` — per-actant: description, characterizations
  targeting this actant (the §4.1.1 surface again), enrols-relations,
  inscriptions produced, programs of action carried
- ``Perspectives/<case>--<slug>.md`` — disambiguated by case prefix to
  avoid collisions when two cases both have a ``_default`` perspective
- ``Concepts/<term>.md`` — one page per ontology term with founding-text
  citation; the ontology rendered as a navigable glossary
"""

from __future__ import annotations

from collections.abc import Iterable
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
ABSTRACT_PATH = REPO_ROOT / "abstract.md"

# Canonical Callon moment order, used in case + translation rendering.
_MOMENT_ORDER = ["Problematization", "Interessement", "Enrolment", "Mobilization"]


# ---------------------------------------------------------------------------
# Federated front-matter pages
# ---------------------------------------------------------------------------
#
# abstract.md at the repo root is the canonical socio-material reading of
# the project (≈1500 words). Putting all of it at the top of the wiki Home
# page buried the navigation surface, so we federate: each H2 section of
# abstract.md becomes its own top-level wiki page (About.md, Theoretical-
# Frame.md, Lineage.md), and Home gets a ~200-word hand-curated summary
# with links out to the federated pages.
#
# This keeps abstract.md as the single source of truth — no duplicated
# content — while making the wiki Home page scannable in seconds.

# Maps the H2 heading-prefix (case-insensitive) to the federated page stem.
# The order here is also the rendering order in the About-page footer.
_FEDERATED_PAGES: list[tuple[str, str]] = [
    ("theoretical frame", "Theoretical-Frame"),
    ("lineage", "Lineage"),
]

# Hand-curated Home summary. Kept under 200 words to honour the
# "shrink the home page front matter" constraint. Links to the federated
# pages carry the positioning/lineage detail.
_HOME_SUMMARY = """\
`ant-rdf` is a docs-as-code semantic-web vocabulary and authoring toolkit \
for **actor-network / material-semiotic analysis**, synthesising Callon, \
Latour, Law, and Mol. Records are RDF (canonical); compilers render \
reviewable Markdown briefs and this hyperlinked wiki; a Python CLI authors \
records, callable directly or via an LLM-mediated catechism.

The move worth naming up front is reflexive: **`ant-rdf` is itself an \
assemblage of the kind material-semiotic analysis is built to interrogate** \
— ethnographers, toolchain, LLM mediator, deterministic Turtle, SHACL, this \
wiki, and the cases studied are all actants whose webs of relations produce \
what gets attributed downstream to "the ethnographer's reading." The toolkit \
is therefore a **prosthesis**, not a neutral instrument, and the project \
treats it that way.

**Read further (positioning and lineage pages):**

- **[About](About.md)** — the full socio-material reading: four operational \
consequences (toolkit as prosthesis; three-tier validation; comparison \
studies; git/RDF complementarity).
- **[Theoretical Frame](Theoretical-Frame.md)** — Artificial Organisational \
Intelligence (AOI) and "building the loop"; DSG as a self-infrastructuring \
organisation (Rennie et al. 2026).
- **[Lineage](Lineage.md)** — *intellectual* (Callon / Latour / Law / Mol — the founding-text moves each ontology term inherits) and *technical* (the small pattern language `ant-rdf` extends).

Below: navigation across the cases, actants, translations, perspectives, and \
the ontology as a glossary.
"""


def _split_abstract() -> dict[str, str] | None:
    """Split abstract.md into federated wiki pages.

    Returns ``{page_stem: page_markdown}`` for ``About``, ``Theoretical-Frame``,
    ``Lineage`` (and any other H2-bounded section in abstract.md whose
    heading is in ``_FEDERATED_PAGES``). The ``Further reading`` H2 is folded
    into ``About`` as its footer.

    Returns ``None`` if abstract.md isn't present.
    """
    if not ABSTRACT_PATH.exists():
        return None

    text = ABSTRACT_PATH.read_text(encoding="utf-8")

    # Strip SPDX header comment and leading H1 (the doc-level title is
    # replaced per-page below)
    body_lines: list[str] = []
    seen_h1 = False
    for line in text.splitlines():
        if line.startswith("<!--") and "SPDX" in line:
            continue
        if not seen_h1 and line.startswith("# "):
            seen_h1 = True
            continue
        if seen_h1 or body_lines:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()

    # Split by H2 markers. The text before the first H2 is the "prelude".
    sections: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_heading is not None or current_buf:
                sections.append((current_heading, "\n".join(current_buf).strip()))
            current_heading = line[3:].strip()
            current_buf = []
        else:
            current_buf.append(line)
    if current_heading is not None or current_buf:
        sections.append((current_heading, "\n".join(current_buf).strip()))

    # First section may be the prelude (heading=None)
    prelude = ""
    h2_sections: list[tuple[str, str]] = []
    for heading, content in sections:
        if heading is None:
            prelude = content
        else:
            h2_sections.append((heading, content))

    pages: dict[str, str] = {}

    # Federated H2 pages
    further_reading_body: str | None = None
    for heading, content in h2_sections:
        page_stem = _match_federated(heading)
        if page_stem:
            breadcrumb = "[← Home](Home.md) · [← About](About.md)"
            pages[page_stem] = (
                f"# {heading}\n\n"
                f"{breadcrumb}\n\n"
                f"{content}\n"
            )
        elif heading.lower().startswith("further reading"):
            further_reading_body = content
        # Unknown H2: silently fold into About at the end so nothing is dropped
        else:
            further_reading_body = (
                (further_reading_body or "")
                + f"\n\n## {heading}\n\n{content}"
            )

    # About: prelude + (footer with cross-links and further-reading)
    about_lines = [
        "# About ant-rdf — a material-semiotic reading of this repository",
        "",
        "[← Home](Home.md)",
        "",
        prelude,
        "",
        "---",
        "",
        "## Where this continues",
        "",
        "- [Theoretical Frame](Theoretical-Frame.md) — AOI / building-the-loop framing and DSG's self-infrastructuring",
        "- [Lineage](Lineage.md) — *intellectual* (Callon/Latour/Law/Mol) and *technical* (the docs-as-code pattern family) lineages",
    ]
    if further_reading_body:
        about_lines += [
            "",
            "## Further reading",
            "",
            further_reading_body,
        ]
    pages["About"] = "\n".join(about_lines) + "\n"

    return pages


def _match_federated(heading: str) -> str | None:
    """Return the federated page stem for an H2 heading, or None if unmatched."""
    h = heading.lower()
    for prefix, stem in _FEDERATED_PAGES:
        if h.startswith(prefix):
            return stem
    return None


# ---------------------------------------------------------------------------
# Slug helpers — case-disambiguated for things that live under a case
# ---------------------------------------------------------------------------


def _case_slug_of(iri: str) -> str | None:
    """Extract the case slug from an IRI like .../cases/<slug>/..."""
    marker = "/cases/"
    if marker not in iri:
        return None
    rest = iri.split(marker, 1)[1]
    slug = rest.split("/", 1)[0].split("#", 1)[0]
    return slug or None


def _disambiguated_slug(iri: str) -> str:
    """For records that live inside a case, produce a ``<case>--<slug>``
    filesystem-safe name so two cases' ``_default`` perspectives (etc.)
    don't collide. Records not inside a case fall through to plain slugify.
    Always prefix when a case is detectable, even when tail == case_slug,
    so the naming is uniform across the Actants/, Translations/, and
    Perspectives/ subdirectories."""
    case = _case_slug_of(iri)
    tail = slugify(iri)
    if case and tail:
        return f"{case}--{tail}"
    return tail or slugify(iri)


def _actant_page(actant: URIRef) -> str:
    return f"../Actants/{_disambiguated_slug(str(actant))}.md"


def _case_page(case_slug: str) -> str:
    return f"../Cases/{case_slug}.md"


def _translation_page(t: URIRef) -> str:
    return f"../Translations/{_disambiguated_slug(str(t))}.md"


def _perspective_page(p: URIRef) -> str:
    return f"../Perspectives/{_disambiguated_slug(str(p))}.md"


def _concept_page(term: str) -> str:
    return f"../Concepts/{slugify(term)}.md"


# ---------------------------------------------------------------------------
# Gather
# ---------------------------------------------------------------------------


def _gather_by_type(g: Graph, cls: URIRef) -> list[URIRef]:
    return sorted(s for s in g.subjects(RDF.type, cls) if isinstance(s, URIRef))


def _is_top_level_translation(g: Graph, t: URIRef) -> bool:
    """A Translation is top-level (rendered with its own page) iff it has
    ``ant:hasMoment`` links. The four moment subclasses are themselves
    rdf:type ant:Translation but they are *steps*, not standalone records."""
    return any(True for _ in g.objects(t, ANT.hasMoment))


def _moment_kind(g: Graph, moment: URIRef) -> str:
    for t in g.objects(moment, RDF.type):
        if isinstance(t, URIRef) and str(t).startswith(str(ANT)):
            kind = local_name(str(t))
            if kind != "Translation":
                return kind
    return "Translation"


def _ants_namespace_str() -> str:
    return str(ANT)


def _gather_cases(g: Graph) -> dict[str, dict]:
    """Discover cases via IRIs containing ``/cases/<slug>/``. For each:
    networks, perspectives, actants, top-level translations, characterizations.
    """
    cases: dict[str, dict] = {}

    def bucket(slug: str) -> dict:
        return cases.setdefault(slug, {
            "networks": set(),
            "perspectives": set(),
            "actants": set(),
            "translations": set(),
            "characterizations": set(),
            "inscriptions": set(),
            "programs": set(),
        })

    for s in g.subjects():
        if not isinstance(s, URIRef):
            continue
        slug = _case_slug_of(str(s))
        if not slug:
            continue
        b = bucket(slug)
        types = list(g.objects(s, RDF.type))
        for t in types:
            if t == ANT.Network:
                b["networks"].add(s)
            elif t == ANT.Actant:
                b["actants"].add(s)
            elif t == ANT.Translation and _is_top_level_translation(g, s):
                b["translations"].add(s)
            elif t == ANT.Perspective:
                b["perspectives"].add(s)
            elif t == ANT.Characterization:
                b["characterizations"].add(s)
            elif t == ANT.Inscription or t == ANT.ImmutableMobile:
                b["inscriptions"].add(s)
            elif t == ANT.ProgramOfAction or t == ANT.AntiProgram:
                b["programs"].add(s)
    return cases


def _gather_concepts(ont: Graph) -> dict[str, dict]:
    """Every ant: ontology term, with its label, comment, source, and kind."""
    concepts: dict[str, dict] = {}
    ant_str = _ants_namespace_str()
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
# Top-level driver
# ---------------------------------------------------------------------------


def run_wiki(output_dir: str | None = None) -> None:
    out = Path(output_dir) if output_dir else DEFAULT_WIKI_DIR
    out.mkdir(parents=True, exist_ok=True)
    (out / "Cases").mkdir(exist_ok=True)
    (out / "Actants").mkdir(exist_ok=True)
    (out / "Translations").mkdir(exist_ok=True)
    (out / "Perspectives").mkdir(exist_ok=True)
    (out / "Concepts").mkdir(exist_ok=True)

    ds = load_full_dataset()
    g = ds.default_graph
    ont = load_ontology().default_graph

    cases = _gather_cases(g)
    perspectives = _gather_by_type(g, ANT.Perspective)
    concepts = _gather_concepts(ont)

    # Map each actant / translation / perspective to its case for cross-linking
    pages_written = 0

    # Sweep wiki/ subdirs of stale generated content so removed records don't
    # leave orphan pages behind.
    for sub in ("Cases", "Actants", "Translations", "Perspectives", "Concepts"):
        for f in (out / sub).glob("*.md"):
            f.unlink()
    # Also sweep the federated front-matter pages and Home so abstract changes
    # don't leave stale top-level pages.
    for stem in ("Home", "About", *(stem for _, stem in _FEDERATED_PAGES)):
        p = out / f"{stem}.md"
        if p.exists():
            p.unlink()

    # Home
    (out / "Home.md").write_text(_render_home(g, cases, perspectives, concepts), encoding="utf-8")
    pages_written += 1

    # Federated front-matter pages (About, Theoretical-Frame, Lineage)
    # split out of abstract.md so Home stays scannable.
    federated = _split_abstract()
    if federated:
        for stem, body in federated.items():
            (out / f"{stem}.md").write_text(body, encoding="utf-8")
            pages_written += 1

    # Cases
    for case_slug in sorted(cases):
        page = _render_case(g, case_slug, cases[case_slug])
        (out / "Cases" / f"{case_slug}.md").write_text(page, encoding="utf-8")
        pages_written += 1

    # Actants — disambiguated by case to avoid collisions
    seen_actant_pages: set[str] = set()
    for slug in sorted(cases):
        for a in sorted(cases[slug]["actants"]):
            stem = _disambiguated_slug(str(a))
            if stem in seen_actant_pages:
                continue
            seen_actant_pages.add(stem)
            (out / "Actants" / f"{stem}.md").write_text(
                _render_actant(g, a), encoding="utf-8",
            )
            pages_written += 1

    # Translations
    seen_t_pages: set[str] = set()
    for slug in sorted(cases):
        for t in sorted(cases[slug]["translations"]):
            stem = _disambiguated_slug(str(t))
            if stem in seen_t_pages:
                continue
            seen_t_pages.add(stem)
            (out / "Translations" / f"{stem}.md").write_text(
                _render_translation(g, t), encoding="utf-8",
            )
            pages_written += 1

    # Perspectives — disambiguated by case so two ``_default``s don't collide
    seen_p_pages: set[str] = set()
    for p in perspectives:
        stem = _disambiguated_slug(str(p))
        if stem in seen_p_pages:
            continue
        seen_p_pages.add(stem)
        (out / "Perspectives" / f"{stem}.md").write_text(
            _render_perspective(g, p), encoding="utf-8",
        )
        pages_written += 1

    # Concepts (the ontology as a glossary)
    for term, data in sorted(concepts.items()):
        (out / "Concepts" / f"{slugify(term)}.md").write_text(
            _render_concept(g, term, data, concepts), encoding="utf-8",
        )
        pages_written += 1

    console.print(f"[green]✓ wrote {pages_written} wiki pages to {out}[/green]")


# ---------------------------------------------------------------------------
# Render — Home
# ---------------------------------------------------------------------------


def _render_home(
    g: Graph,
    cases: dict[str, dict],
    perspectives: list[URIRef],
    concepts: dict[str, dict],
) -> str:
    lines: list[str] = [
        "# ant-rdf wiki",
        "",
        _HOME_SUMMARY,
        "",
        "_Source for the federated front-matter pages: [`abstract.md`](https://github.com/mzargham/ant-rdf/blob/main/abstract.md) in the main repo. Pages are regenerated by `ant wiki`._",
        "",
        "---",
        "",
    ]

    lines += [
        "## Navigation",
        "",
        "Hyperlinked traversal of the canonical RDF in `instances/`. Every actant, translation, characterization, and perspective is a click away — and every concept on the right is a glossary entry with a citation to its founding text.",
        "",
        "## Cases",
        "",
    ]
    if cases:
        for slug in sorted(cases):
            c = cases[slug]
            nets = sorted(c["networks"])
            if nets:
                label = label_of(g, nets[0])
                lines.append(f"- **[{slug}](Cases/{slug}.md)** — {label}")
                desc = description_of(g, nets[0])
                if desc:
                    lines.append(f"  > {desc[:240]}{'…' if len(desc) > 240 else ''}")
            else:
                lines.append(f"- [{slug}](Cases/{slug}.md)")
    else:
        lines.append("_No cases recorded yet._")
    lines.append("")

    # Actants grouped by case (rather than flat cross-case dump)
    lines += ["## Actants by case", ""]
    if not cases:
        lines.append("_(no actants yet)_")
    for slug in sorted(cases):
        actants = sorted(cases[slug]["actants"])
        if not actants:
            continue
        lines.append(f"### {slug}")
        lines.append("")
        for a in actants:
            lines.append(f"- [{label_of(g, a)}](Actants/{_disambiguated_slug(str(a))}.md)")
        lines.append("")

    # Translations
    all_translations = [t for slug in cases for t in cases[slug]["translations"]]
    lines += ["## Translations", ""]
    if all_translations:
        for t in sorted(all_translations):
            slug = _case_slug_of(str(t)) or "?"
            lines.append(
                f"- [{label_of(g, t)}](Translations/{_disambiguated_slug(str(t))}.md) "
                f"_(case: [{slug}](Cases/{slug}.md))_"
            )
    else:
        lines.append("_No translations recorded yet._")
    lines.append("")

    # Perspectives (disambiguated by case prefix)
    lines += ["## Perspectives", ""]
    if perspectives:
        for p in perspectives:
            case = _case_slug_of(str(p))
            slug = local_name(str(p))
            stem = _disambiguated_slug(str(p))
            display = f"{case}::{slug}" if case else slug
            lines.append(f"- [{display}](Perspectives/{stem}.md)")
    else:
        lines.append("_No perspectives recorded yet._")
    lines.append("")

    # Concepts glossary (compact)
    lines += [
        "## Concepts (the ontology as a glossary)",
        "",
        "Every term below renders as a page with `rdfs:comment` and `dcterms:source` to a founding text.",
        "",
        "**Classes**",
        "",
    ]
    classes = [t for t, d in concepts.items() if d["kind"] == "Class"]
    for term in sorted(classes):
        lines.append(f"- [{local_name(term)}](Concepts/{slugify(term)}.md)")
    lines += ["", "**Properties**", ""]
    props = [t for t, d in concepts.items() if d["kind"] in {"Object property", "Datatype property"}]
    for term in sorted(props):
        lines.append(f"- [{local_name(term)}](Concepts/{slugify(term)}.md)")
    lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Render — Case (rich)
# ---------------------------------------------------------------------------


def _render_case(g: Graph, slug: str, case: dict) -> str:
    lines = [f"# Case: {slug}", "", "[← Home](../Home.md)", ""]

    # Networks (usually one per case)
    for net in sorted(case["networks"]):
        lines += [
            f"## Network — {label_of(g, net)}",
            "",
            f"<!-- {net} -->",
            "",
            description_of(g, net) or "_(no description)_",
            "",
        ]

    # Translations — embed their four moments inline, link to full page
    translations = sorted(case["translations"])
    if translations:
        lines += ["## Translations", ""]
        for t in translations:
            lines += [
                f"### [{label_of(g, t)}]({_translation_page(t)})",
                "",
                description_of(g, t) or "_(no description)_",
                "",
            ]
            # Inline the four moments compactly
            moments = sorted(o for o in g.objects(t, ANT.hasMoment) if isinstance(o, URIRef))
            by_kind: dict[str, list[URIRef]] = {}
            for m in moments:
                by_kind.setdefault(_moment_kind(g, m), []).append(m)
            for kind in _MOMENT_ORDER:
                for m in by_kind.get(kind, []):
                    snippet = description_of(g, m)
                    snippet_short = (snippet[:200] + "…") if len(snippet) > 200 else snippet
                    lines += [
                        f"**{kind}.** {label_of(g, m)} — {snippet_short or '_(no description)_'}",
                        "",
                    ]
            lines += [f"_See the full trace: [{label_of(g, t)}]({_translation_page(t)})_", ""]

    # Characterizations — the §4.1.1 surface (this is the whole point!)
    case_chars = sorted(case["characterizations"])
    if case_chars:
        lines += [
            "## Characterizations (observer-relative role assignments)",
            "",
            "Each row records an analyst's claim *within a context*: the (target, network, practice, invariance) tuple grounds the role assignment. The same actant may appear with different roles across rows — that's not contradiction, it's [§4.1.1 observer-relativity](../Concepts/Characterization.md).",
            "",
        ]
        rows = []
        for c in case_chars:
            target = next(iter(g.objects(c, ANT.characterizes)), None)
            role = next(iter(g.objects(c, ANT.assignsRole)), None)
            net = next(iter(g.objects(c, ANT.withinNetwork)), None)
            practice = next(iter(g.objects(c, ANT.perPractice)), None)
            invariance = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
            desc = description_of(g, c)
            target_link = (
                f"[{label_of(g, target)}]({_actant_page(target)})"
                if isinstance(target, URIRef) else "?"
            )
            role_link = (
                f"[{local_name(str(role))}]({_concept_page(str(role))})"
                if isinstance(role, URIRef) else "?"
            )
            net_label = label_of(g, net) if isinstance(net, URIRef) else "?"
            net_slug = _case_slug_of(str(net)) if isinstance(net, URIRef) else None
            net_cell = (
                f"[{net_label}]({_case_page(net_slug)})" if net_slug else net_label
            )
            rows.append([
                target_link,
                role_link,
                net_cell,
                local_name(str(practice)) if practice else "_(unspecified)_",
                str(invariance) if invariance else "_(unspecified)_",
                (desc[:120] + "…") if len(desc) > 120 else desc,
            ])
        lines.append(_md_table(
            ["Target", "Role", "Network", "Practice", "Invariance", "Note"], rows,
        ))
        lines.append("")

    # Actants
    actants = sorted(case["actants"])
    if actants:
        lines += ["## Actants in this case", ""]
        for a in actants:
            adesc = description_of(g, a)
            snippet = (adesc[:200] + "…") if len(adesc) > 200 else adesc
            lines.append(
                f"- **[{label_of(g, a)}]({_actant_page(a)})** — {snippet or '_(no description)_'}"
            )
        lines.append("")

    # Inscriptions (if any)
    inscriptions = sorted(case["inscriptions"])
    if inscriptions:
        lines += ["## Inscriptions / immutable mobiles", ""]
        for i in inscriptions:
            src = list(g.objects(i, DCTERMS.source))
            src_str = f" — source: `{src[0]}`" if src else ""
            lines.append(f"- **{label_of(g, i)}**{src_str}")
            d = description_of(g, i)
            if d:
                lines.append(f"  > {d[:240]}{'…' if len(d) > 240 else ''}")
        lines.append("")

    # Programs of action (if any)
    programs = sorted(case["programs"])
    if programs:
        lines += ["## Programs of action", ""]
        for p in programs:
            lines.append(f"- **{label_of(g, p)}**")
            d = description_of(g, p)
            if d:
                lines.append(f"  > {d[:240]}{'…' if len(d) > 240 else ''}")
            opposes = sorted(o for o in g.objects(p, ANT.opposes) if isinstance(o, URIRef))
            for opp in opposes:
                lines.append(f"  - opposes: *{label_of(g, opp)}*")
        lines.append("")

    # Perspectives in this case
    if case["perspectives"]:
        lines += ["## Perspectives", ""]
        for p in sorted(case["perspectives"]):
            display = local_name(str(p))
            lines.append(f"- [{display}]({_perspective_page(p)})")
        lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Render — Translation (new)
# ---------------------------------------------------------------------------


def _render_translation(g: Graph, t: URIRef) -> str:
    case_slug = _case_slug_of(str(t)) or "?"
    lines = [
        f"# Translation: {label_of(g, t)}",
        "",
        f"[← Home](../Home.md) · [Case: {case_slug}]({_case_page(case_slug)})",
        "",
        f"<!-- {t} -->",
        "",
        description_of(g, t) or "_(no description)_",
        "",
        "## Moments (in canonical order)",
        "",
    ]

    moments = sorted(o for o in g.objects(t, ANT.hasMoment) if isinstance(o, URIRef))
    by_kind: dict[str, list[URIRef]] = {}
    for m in moments:
        by_kind.setdefault(_moment_kind(g, m), []).append(m)

    for kind in _MOMENT_ORDER:
        items = by_kind.get(kind, [])
        lines.append(f"### {kind}")
        lines.append("")
        if not items:
            lines.append(f"_(no {kind.lower()} recorded — Tier-2 SHACL warns unless waived)_")
            lines.append("")
            continue
        for m in items:
            lines.append(f"**{label_of(g, m)}**")
            lines.append("")
            lines.append(f"<!-- {m} -->")
            lines.append("")
            lines.append(description_of(g, m) or "_(no description)_")
            lines.append("")

    # Any other moments not in the canonical four kinds
    other_kinds = sorted(k for k in by_kind if k not in _MOMENT_ORDER)
    if other_kinds:
        lines += ["### Other moments", ""]
        for kind in other_kinds:
            for m in by_kind[kind]:
                lines += [
                    f"**{kind}: {label_of(g, m)}**",
                    "",
                    f"<!-- {m} -->",
                    "",
                    description_of(g, m) or "_(no description)_",
                    "",
                ]

    lines.append("---")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Render — Actant (rich)
# ---------------------------------------------------------------------------


def _render_actant(g: Graph, actant: URIRef) -> str:
    case_slug = _case_slug_of(str(actant))
    breadcrumb = "[← Home](../Home.md)"
    if case_slug:
        breadcrumb += f" · [Case: {case_slug}]({_case_page(case_slug)})"
    lines = [
        f"# Actant: {label_of(g, actant)}",
        "",
        breadcrumb,
        "",
        f"<!-- {actant} -->",
        "",
        description_of(g, actant) or "_(no description)_",
        "",
    ]

    # Participates in
    nets = sorted(o for o in g.objects(actant, ANT.participatesIn) if isinstance(o, URIRef))
    lines += ["## Participates in", ""]
    if nets:
        for n in nets:
            slug = _case_slug_of(str(n)) or "?"
            lines.append(f"- [{label_of(g, n)}]({_case_page(slug)})")
    else:
        lines.append("_(no networks listed)_")
    lines.append("")

    # Characterizations targeting this actant — the §4.1.1 surface
    chars = sorted(c for c in g.subjects(ANT.characterizes, actant) if isinstance(c, URIRef))
    if chars:
        lines += [
            "## Characterizations of this actant",
            "",
            "This actant has been characterized in the role(s) below, under specified practices and invariance criteria. Where multiple rows appear with different roles, that's [§4.1.1 observer-relativity](../Concepts/Characterization.md), not contradiction.",
            "",
        ]
        rows = []
        for c in chars:
            role = next(iter(g.objects(c, ANT.assignsRole)), None)
            net = next(iter(g.objects(c, ANT.withinNetwork)), None)
            prac = next(iter(g.objects(c, ANT.perPractice)), None)
            inv = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
            d = description_of(g, c)
            role_link = (
                f"[{local_name(str(role))}]({_concept_page(str(role))})"
                if isinstance(role, URIRef) else "?"
            )
            net_label = label_of(g, net) if isinstance(net, URIRef) else "?"
            net_slug = _case_slug_of(str(net)) if isinstance(net, URIRef) else None
            net_cell = (
                f"[{net_label}]({_case_page(net_slug)})" if net_slug else net_label
            )
            rows.append([
                role_link,
                net_cell,
                local_name(str(prac)) if prac else "_(unspecified)_",
                str(inv) if inv else "_(unspecified)_",
                (d[:140] + "…") if len(d) > 140 else d,
            ])
        lines.append(_md_table(
            ["Role", "Within network", "Per practice", "Invariance", "Note"], rows,
        ))
        lines.append("")

    # Enrols / Enrolled-by
    enrolled_by = sorted(s for s in g.subjects(ANT.enrols, actant) if isinstance(s, URIRef))
    enrols_others = sorted(o for o in g.objects(actant, ANT.enrols) if isinstance(o, URIRef))
    if enrolled_by or enrols_others:
        lines += ["## Enrolment relations", ""]
        if enrolled_by:
            lines.append("**Enrolled by:**")
            for s in enrolled_by:
                lines.append(f"- [{label_of(g, s)}]({_actant_page(s)})")
            lines.append("")
        if enrols_others:
            lines.append("**Enrols:**")
            for o in enrols_others:
                lines.append(f"- [{label_of(g, o)}]({_actant_page(o)})")
            lines.append("")

    # Inscriptions produced
    inscr = sorted(o for o in g.objects(actant, ANT.inscribes) if isinstance(o, URIRef))
    if inscr:
        lines += ["## Inscriptions this actant produces", ""]
        for i in inscr:
            lines.append(f"- {label_of(g, i)}")
        lines.append("")

    # Programs carried
    progs = sorted(o for o in g.objects(actant, ANT.hasProgram) if isinstance(o, URIRef))
    if progs:
        lines += ["## Programs of action", ""]
        for p in progs:
            lines.append(f"- {label_of(g, p)}")
            d = description_of(g, p)
            if d:
                lines.append(f"  > {d[:200]}{'…' if len(d) > 200 else ''}")
        lines.append("")

    # Speaks for
    speaks_for = sorted(o for o in g.objects(actant, ANT.speaksFor) if isinstance(o, URIRef))
    if speaks_for:
        lines += ["## Speaks for", ""]
        for o in speaks_for:
            lines.append(f"- [{label_of(g, o)}]({_actant_page(o)})")
        lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Render — Perspective
# ---------------------------------------------------------------------------


def _render_perspective(g: Graph, p: URIRef) -> str:
    case_slug = _case_slug_of(str(p))
    breadcrumb = "[← Home](../Home.md)"
    if case_slug:
        breadcrumb += f" · [Case: {case_slug}]({_case_page(case_slug)})"
    lines = [
        f"# Perspective: {label_of(g, p)}",
        "",
        breadcrumb,
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
        lines += ["", "**Grounded in practices:**"]
        for prac in grounded:
            lines.append(f"- `{prac}`")
    tracks = sorted(str(o) for o in g.objects(p, ANT.perspectiveTracksInvariance))
    if tracks:
        lines += ["", "**Tracks invariances:**"]
        for inv in tracks:
            lines.append(f"- {inv}")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Render — Concept (with back-references)
# ---------------------------------------------------------------------------


def _render_concept(
    g: Graph, term: str, data: dict, all_concepts: dict[str, dict],
) -> str:
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

    # Back-references: which records use this term (as type, predicate, or role value).
    term_uri = URIRef(term)
    examples = sorted({
        s for s in g.subjects(RDF.type, term_uri) if isinstance(s, URIRef)
    })
    if examples:
        lines += ["## Examples (records typed with this term)", ""]
        for e in examples[:12]:  # cap to keep the page readable
            link = _example_link(e)
            lines.append(f"- [{label_of(g, e) or local_name(str(e))}]({link})")
        if len(examples) > 12:
            lines.append(f"- … and {len(examples) - 12} more")
        lines.append("")

    role_uses = sorted({
        s for s in g.subjects(ANT.assignsRole, term_uri) if isinstance(s, URIRef)
    })
    if role_uses:
        lines += ["## Characterizations that assign this role", ""]
        for c in role_uses[:12]:
            net = next(iter(g.objects(c, ANT.withinNetwork)), None)
            prac = next(iter(g.objects(c, ANT.perPractice)), None)
            target = next(iter(g.objects(c, ANT.characterizes)), None)
            target_link = (
                f"[{label_of(g, target)}]({_actant_page(target)})"
                if isinstance(target, URIRef) else "?"
            )
            net_str = local_name(str(net)) if net else "?"
            prac_str = local_name(str(prac)) if prac else "_(unspecified)_"
            lines.append(f"- {target_link} *(in {net_str}, per {prac_str})*")
        if len(role_uses) > 12:
            lines.append(f"- … and {len(role_uses) - 12} more")
        lines.append("")

    return "\n".join(lines) + "\n"


def _example_link(record: URIRef) -> str:
    """Best-effort link from a Concept page to the page for a record."""
    iri = str(record)
    case = _case_slug_of(iri)
    if "/actant/" in iri:
        return _actant_page(record)
    if "/translation/" in iri:
        return _translation_page(record)
    if "/perspectives/" in iri:
        return _perspective_page(record)
    if "/network" in iri and case:
        return _case_page(case)
    if case:
        return _case_page(case)
    return f"#{slugify(iri)}"  # graceful fallback


# ---------------------------------------------------------------------------
# Markdown table (local to wiki.py — _common.md_table is similar but the wiki
# wants un-truncated cells with full markdown link syntax preserved)
# ---------------------------------------------------------------------------


def _md_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    sep = ["---"] * len(headers)
    materialized = [list(r) for r in rows]
    lines = [_join(headers), _join(sep)]
    for r in materialized:
        cells = [_cell(c) for c in r[: len(headers)]]
        while len(cells) < len(headers):
            cells.append("")
        lines.append(_join(cells))
    return "\n".join(lines) + "\n"


def _join(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()
