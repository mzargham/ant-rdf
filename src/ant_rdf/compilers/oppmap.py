# SPDX-License-Identifier: Apache-2.0
"""OPPMap compiler — the obligatory passage points and their traffic.

An OPP (Callon 1986) is a passage every relevant actant/commitment must clear. In the
graph an OPP is a Characterization assigning role ant:ObligatoryPassagePoint to an actant.
This compiler collects every OPP across frames, names the passage (the actant), the frame
that reads it as an OPP, and the *traffic*: what traces to it (ant:tracesToPassage) or
passes through it (ant:passesThrough).

Scope: whole-case::

    ant compile koi OPPMap -o briefs/koi-opp-map.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    description_of,
    label_of,
    local_name,
    many_iris,
    md_table,
    perspective_index,
    see_also_footer,
)

REFRESH_SUFFIX = "opp-map"
REQUIRES_GROUNDED = True


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject
    _frames, practice_to_persp = perspective_index(g)
    frame_label = {p: label_of(g, p).split(" · ")[0].strip() for p in set(practice_to_persp.values())}

    # Group OPP characterizations by the actant (the passage). An actant read as
    # an OPP in more than one frame becomes ONE section whose Frame merges the
    # frames, rather than a duplicate `## <actant>` per characterization.
    by_actant: dict[URIRef, dict[str, list[str]]] = {}
    order: list[URIRef] = []
    for c in sorted(g.subjects(ANT.assignsRole, ANT.ObligatoryPassagePoint), key=str):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        prac = next(iter(g.objects(c, ANT.perPractice)), None)
        inv = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
        if not isinstance(actant, URIRef):
            continue
        persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
        frame = frame_label.get(persp, "") if persp is not None else ""
        if actant not in by_actant:
            by_actant[actant] = {"frames": [], "invs": [], "glosses": []}
            order.append(actant)
        d = by_actant[actant]
        if frame not in d["frames"]:
            d["frames"].append(frame)
        if inv and str(inv) not in d["invs"]:
            d["invs"].append(str(inv))
        gloss = description_of(g, c)
        if gloss and gloss not in d["glosses"]:
            d["glosses"].append(gloss)

    case = next((case_slug_of(str(a)) for a in order), None)
    lines: list[str] = [f"# OPP map: {case}" if case else "# OPP map", ""]
    lines += [
        f"{len(by_actant)} obligatory passage point(s) across the frames, the passages "
        "commitments must clear. Traffic is what must clear each passage; passages that "
        "are the same across frames (ant:correspondsTo) share it, so a flow tagged 'via X' "
        "clears this passage through its cross-frame twin.",
        "",
    ]

    if not by_actant:
        lines += ["_No ObligatoryPassagePoint characterizations in the loaded scope._", ""]
        lines.append(see_also_footer(case))
        return "\n".join(lines)

    # Summary table
    rows = []
    for actant in sorted(order, key=str):
        d = by_actant[actant]
        flows = _passage_flows(g, actant)
        rows.append([label_of(g, actant), " · ".join(d["frames"]), str(len(flows))])
    lines.append(md_table(["Passage (actant)", "Frame", "Traffic"], rows))
    lines.append("")

    # Per-OPP detail
    for actant in sorted(order, key=str):
        d = by_actant[actant]
        lines += [f"## {label_of(g, actant)}", "", f"<!-- {actant} -->", ""]
        lines.append(f"- **Frame:** {' · '.join(d['frames'])}")
        if d["invs"]:
            lines.append(f"- **Invariance:** {'; '.join(d['invs'])}")
        corr = many_iris(g, actant, ANT.correspondsTo)
        if corr:
            twins = []
            for o in corr:
                fr = " · ".join(by_actant[o]["frames"]) if o in by_actant else ""
                twins.append(f"{label_of(g, o)}" + (f" ({fr})" if fr else ""))
            lines.append(f"- **Corresponds to** (same passage across frames): {', '.join(twins)}")
        if (actant, RDF.type, ANT.BlackBox) in g:
            lines.append(
                "- **Also a black box** (punctualization): the whole treated as a single "
                "actant, so essentially every formal interaction passes through it. An "
                "aggregate passage, not a selective bottleneck, which is why little traces to "
                "it as a specific gate."
            )
        lines.append("")
        if d["glosses"]:
            lines += ["\n\n".join(d["glosses"]), ""]
        flows = _passage_flows(g, actant)
        if flows:
            lines.append("**Must clear it:**")
            for t in sorted(flows, key=str):
                nodes = flows[t]
                tag = "" if actant in nodes else (
                    " (via " + ", ".join(label_of(g, n) for n in sorted(nodes, key=str)) + ")"
                )
                lines.append(f"- {label_of(g, t)} (`{local_name(str(t))}`){tag}")
        else:
            lines.append("_No traffic recorded yet (nothing is wired to clear this passage)._")
        lines.append("")

    lines.append(see_also_footer(case))
    return "\n".join(lines)


def _traffic(g, actant: URIRef) -> list[URIRef]:
    """Records that trace to or pass through this OPP actant (deduped, sorted)."""
    seen = {
        s for s in g.subjects(ANT.tracesToPassage, actant) if isinstance(s, URIRef)
    } | {s for s in g.subjects(ANT.passesThrough, actant) if isinstance(s, URIRef)}
    return sorted(seen, key=str)


def _passage_flows(g, actant: URIRef) -> dict[URIRef, set[URIRef]]:
    """Traffic for the whole passage, aggregated across ant:correspondsTo twins.

    An OPP read under two frames is one passage; its traffic should not fragment
    across the twin nodes. Returns ``{flow (translation) -> the passage-node(s) it
    traces to}`` over the actant and its correspondsTo twins, so the caller can
    tag a flow that enters via a twin and the count is the passage's.
    """
    nodes = [actant, *many_iris(g, actant, ANT.correspondsTo)]
    flows: dict[URIRef, set[URIRef]] = {}
    for n in nodes:
        for t in _traffic(g, n):
            flows.setdefault(t, set()).add(n)
    return flows
