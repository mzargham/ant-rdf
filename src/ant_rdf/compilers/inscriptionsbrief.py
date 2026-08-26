# SPDX-License-Identifier: Apache-2.0
"""InscriptionsBrief compiler — the case's material carry-forward.

An inscription (Latour) is a material trace that circulates between actors. This
brief renders every inscription in the case with its **type** (an ant:ImmutableMobile
holds form / an ant:FluidObject persists by mutation), who **produced** it
(ant:inscribes) and who **draws on** it (ant:drawsOn). Produce vs consume is the
material analogue of the invariance/variance axis: an immutable mobile is unaltered
when drawn on (intermediary-like), a fluid object may be altered (mediator-like).

Scope: whole-case::

    ant compile koi InscriptionsBrief -o briefs/koi-inscriptions.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import DCTERMS, RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    description_of,
    label_of,
    local_name,
    md_table,
    one_literal,
    see_also_footer,
)

REFRESH_SUFFIX = "inscriptions"
REQUIRES_GROUNDED = True

_TYPE_LABEL = {
    ANT.FluidObject: "Fluid object",
    ANT.ImmutableMobile: "Immutable mobile",
    ANT.Inscription: "Inscription",
}


def _inscription_type(g, i: URIRef) -> URIRef | None:
    """The most specific inscription class declared on i (fluid/immutable/plain)."""
    types = set(g.objects(i, RDF.type))
    for t in (ANT.FluidObject, ANT.ImmutableMobile, ANT.Inscription):
        if t in types:
            return t
    return None


def _reverse(g, pred: URIRef, obj: URIRef) -> list[URIRef]:
    return sorted((s for s in g.subjects(pred, obj) if isinstance(s, URIRef)), key=str)


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject

    inscriptions: list[URIRef] = sorted(
        {
            s
            for cls in (ANT.ImmutableMobile, ANT.FluidObject, ANT.Inscription)
            for s in g.subjects(RDF.type, cls)
            if isinstance(s, URIRef)
        },
        key=str,
    )
    case = next((case_slug_of(str(i)) for i in inscriptions), None) or next(
        (case_slug_of(str(p)) for p in g.subjects(RDF.type, ANT.Perspective) if case_slug_of(str(p))),
        None,
    )

    lines: list[str] = [f"# Inscriptions: {case}" if case else "# Inscriptions", ""]
    lines += [
        f"{len(inscriptions)} inscription(s): the case's material carry-forward. Each is **produced** "
        "by an origin (`ant:inscribes`) and **drawn on** by consumers (`ant:drawsOn`). The shared object "
        "is the thread that persists even when a producing site is wound down.",
        "",
        "> **Type = how it persists.** An *immutable mobile* holds form constant and is **unaltered** when "
        "drawn on (the invariant, intermediary-like pole); a *fluid object* persists through mutation and "
        "may be **altered** when drawn on: a consumer keeps developing the living object (the varied, "
        "mediator-like pole).",
        "",
    ]

    if not inscriptions:
        lines += ["_No inscriptions in the loaded scope._", ""]
        lines.append(see_also_footer(case))
        return "\n".join(lines)

    # Master table.
    rows = []
    for i in inscriptions:
        t = _inscription_type(g, i)
        producers = _reverse(g, ANT.inscribes, i)
        consumers = _reverse(g, ANT.drawsOn, i)
        rows.append([
            label_of(g, i),
            _TYPE_LABEL.get(t, "Inscription"),
            " · ".join(label_of(g, p) for p in producers) or "(none)",
            " · ".join(label_of(g, c) for c in consumers) or "(none)",
        ])
    lines.append(md_table(["Inscription", "Type", "Produced by", "Drawn on by"], rows))
    lines.append("")

    # Reverse index: per consumer → what it draws on.
    consumers_all = sorted(
        {s for s in g.subjects(ANT.drawsOn, None) if isinstance(s, URIRef)}, key=str
    )
    if consumers_all:
        lines += ["## What each consumer draws on", ""]
        crows = []
        for c in consumers_all:
            drawn = sorted(g.objects(c, ANT.drawsOn), key=str)
            crows.append([
                label_of(g, c),
                " · ".join(label_of(g, d) for d in drawn),
            ])
        lines.append(md_table(["Consumer", "Draws on"], crows))
        lines.append("")

    # Per-inscription detail.
    lines += ["## Detail", ""]
    for i in inscriptions:
        t = _inscription_type(g, i)
        lines += [f"### {label_of(g, i)}", "", f"<!-- {i} -->", ""]
        lines.append(f"- **Type:** {_TYPE_LABEL.get(t, 'Inscription')}")
        src = one_literal(g, i, DCTERMS.source, "")
        if src:
            lines.append(f"- **Source:** {src}")
        producers = _reverse(g, ANT.inscribes, i)
        consumers = _reverse(g, ANT.drawsOn, i)
        lines.append(
            "- **Produced by:** "
            + (" · ".join(f"{label_of(g, p)} (`{local_name(str(p))}`)" for p in producers) or "_unknown_")
        )
        lines.append(
            "- **Drawn on by:** "
            + (" · ".join(f"{label_of(g, c)} (`{local_name(str(c))}`)" for c in consumers) or "_none recorded_")
        )
        manifested = _reverse(g, ANT.manifestsAs, i)
        if manifested:
            lines.append(
                "- **Also an actant** (manifested from, C9): "
                + " · ".join(f"{label_of(g, a)} (`{local_name(str(a))}`)" for a in manifested)
            )
        desc = description_of(g, i)
        if desc:
            lines += ["", desc]
        lines.append("")

    lines.append(see_also_footer(case))
    return "\n".join(lines)
