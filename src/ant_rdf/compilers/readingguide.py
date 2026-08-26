# SPDX-License-Identifier: Apache-2.0
"""ReadingGuide compiler — the 'start here' index for a case's briefs.

No brief should be an island. This one gives a first-time reader an order to
read in and a link to every other brief, grouped: orient yourself, read the
frames, then the cross-frame analyses, then reference. The per-frame briefs
are derived from the graph (one ant:Network per perspective) so their titles
and links stay correct, and the cross-frame briefs are listed only when the
case has more than one frame (which is when `ant refresh` compiles them).

Scope: per-case::

    ant compile koi ReadingGuide -o briefs/koi-guide.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef

from ant_rdf.compilers._common import case_slug_of, label_of, perspective_index

REFRESH_SUFFIX = "guide"
REQUIRES_GROUNDED = True


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject
    frames, _ = perspective_index(g)
    case = next((case_slug_of(str(f["iri"])) for f in frames if case_slug_of(str(f["iri"]))), None)
    c = case or "case"
    multi = len(frames) >= 2

    def link(title: str, suffix: str, gloss: str) -> str:
        return f"- [{title}]({c}-{suffix}): {gloss}"

    lines: list[str] = [
        f"# {c}: reading guide", "",
        "Start here. These briefs are compiled from one RDF graph that reads the "
        f"{c} field site from {len(frames)} position{'s' if multi else ''}. The perspectives are provenance "
        "(who is speaking, from which practice); read the positionality ledger "
        "first if you want the key, or the synopsis if you want the gist.",
        "",
        "## Orient yourself", "",
        link("Positionality ledger", "positionality.md",
             "who holds each frame, the practice it reasons from, the invariance it keeps"),
        link("Synopsis", "synopsis.md",
             "the whole case at a glance: each frame's reading and where they agree or flip"),
        "",
        "## The readings" if multi else "## The reading", "",
        "The same field site, each frame in full (positionality header up top):"
        if multi else "The frame's reading in full (positionality header up top):",
        "",
    ]
    for f in sorted(frames, key=lambda f: str(f["iri"])):
        net = f.get("network")
        gloss = label_of(g, net) if isinstance(net, URIRef) else "the frame's reading"
        target = f"{c}-{f['slug']}-network.md" if f["slug"] != "_default" else f"{c}-network.md"
        lines.append(f"- [{f['label']}]({target}): {gloss}")
    lines += ["", "## Analyses", ""]
    if multi:
        lines += [
            link("Perspective comparison", "comparison.md",
                 "the frames side by side, pivoted on the actant; where they converge and diverge"),
            link("Actants across frames", "actants-across-frames.md",
                 "the many faces of each shared actant, role by role, frame by frame"),
            link("Same-program trace", "same-program-trace.md",
                 "one program read across all the frames at once"),
        ]
    lines += [
        link("OPP map", "opp-map.md",
             "the obligatory passage points every commitment must clear, and their traffic"),
        link("Inscriptions", "inscriptions.md",
             "material carry-forward: who produces each inscription and who draws on it, "
             "immutable mobiles vs fluid objects"),
        link("Durability dashboard", "durability.md",
             "every translation by behavioral status: what is stabilized, precarious, unravelling"),
        link("Characterization coverage", "coverage.md",
             "which actants are given a role reading, and which are left bare"),
        link("Tensions & contested", "tensions.md",
             "the strain only: role flips, precarity, anti-programs, and bottlenecks"),
        "",
        "## Reference", "",
        link("Glossary", "glossary.md",
             "the ANT vocabulary this case uses, from the ontology, plus any load-bearing "
             "terms from other fields with citable definitions"),
        "- [Case catalog](case-catalog.md): the cross-case index (counts per case)",
        "",
    ]
    return "\n".join(lines)
