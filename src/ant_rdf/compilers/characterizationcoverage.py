# SPDX-License-Identifier: Apache-2.0
"""CharacterizationCoverage compiler — which actants are read in which frames.

A standing lens on the "mass of records vs interpretation" question. The graph
holds many actants, but only some carry a Characterization (a role/practice/
invariance reading from a frame); the rest are context that situates the network
without a role reading. This view makes the ratio legible: a per-frame count, a
coverage matrix over the characterized actants, and a compact roll of the bare
actants, so bare-vs-interpreted is visible at a glance (elucidate, not inundate).

Scope: whole-case::

    ant compile koi CharacterizationCoverage -o briefs/koi-coverage.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    label_of,
    local_name,
    md_table,
    perspective_index,
    see_also_footer,
)

REFRESH_SUFFIX = "coverage"
REQUIRES_GROUNDED = True


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject
    frames, practice_to_persp = perspective_index(g)
    frame_order = [f["iri"] for f in frames]
    frame_short = {f["iri"]: f["label"].split(" · ")[0].strip() for f in frames}

    # actant -> {perspective -> set(role local-names)}
    coverage: dict[URIRef, dict[URIRef, set[str]]] = {}
    for c in g.subjects(RDF.type, ANT.Characterization):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        prac = next(iter(g.objects(c, ANT.perPractice)), None)
        persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
        if not isinstance(actant, URIRef) or not isinstance(role, URIRef) or persp is None:
            continue
        coverage.setdefault(actant, {}).setdefault(persp, set()).add(local_name(str(role)))

    all_actants = sorted(
        (a for a in g.subjects(RDF.type, ANT.Actant) if isinstance(a, URIRef)), key=str
    )
    case = next((case_slug_of(str(a)) for a in all_actants), None)
    characterized = [a for a in all_actants if a in coverage]
    bare = [a for a in all_actants if a not in coverage]

    title = f"# Characterization coverage: {case}" if case else "# Characterization coverage"
    lines: list[str] = [title, ""]
    lines += [
        f"{len(characterized)} of {len(all_actants)} actants carry a characterization "
        f"(a role read from a frame) in at least one of the {len(frames)} frame(s); "
        f"{len(bare)} are bare. A bare actant is context that situates the network (a "
        "person, an external org, a platform, an output) without being given a role "
        "reading; that is expected, not a gap. This view keeps the balance legible.",
        "",
    ]

    lines += ["## Coverage by frame", ""]
    crows = [
        [frame_short[f["iri"]], str(sum(1 for a in characterized if f["iri"] in coverage[a]))]
        for f in frames
    ]
    lines.append(md_table(["Frame", "Actants characterized"], crows))
    lines.append("")

    lines += ["## Characterized actants, by frame", ""]
    if characterized:
        headers = ["Actant"] + [frame_short[i] for i in frame_order]
        rows = []
        for a in sorted(characterized, key=lambda x: label_of(g, x).lower()):
            row = [label_of(g, a)]
            for i in frame_order:
                roles = coverage[a].get(i)
                row.append(" / ".join(sorted(roles)) if roles else "")
            rows.append(row)
        lines.append(md_table(headers, rows))
        lines.append("")
    else:
        lines += ["_No characterized actants in the loaded scope._", ""]

    if bare:
        lines += ["## Bare actants (context, no role reading)", ""]
        lines += [
            "They situate the network as participants and are left uncharacterized by "
            "design (elucidate, not inundate).",
            "",
            " · ".join(label_of(g, a) for a in sorted(bare, key=lambda x: label_of(g, x).lower())),
            "",
        ]

    lines.append(see_also_footer(case))
    return "\n".join(lines)
