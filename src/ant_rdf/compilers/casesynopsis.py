# SPDX-License-Identifier: Apache-2.0
"""CaseSynopsis compiler — a short, high-level overview of one case.

Where ``NetworkBrief`` renders one perspective in full and
``PerspectiveComparison`` tabulates every shared actant, this compiler is the
*synopsis*: the case, its perspectives at a glance (grounding practice ·
invariance · network · counts), each frame's authored reading (the network
narrative), and the headline cross-frame finding — which actants the frames
read the *same*, and which they *flip* on.

Scope: per-case (spans all perspectives). Run with a case slug::

    ant compile koi CaseSynopsis -o briefs/koi-synopsis.md

Everything is derived from the graph; no prose is authored here.
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
    md_table,
    network_for_perspective,
    see_also_footer,
)

REFRESH_SUFFIX = "synopsis"
REQUIRES_GROUNDED = True


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject  # a synopsis spans all perspectives of the loaded case

    perspectives = sorted(
        p
        for p in g.subjects(RDF.type, ANT.Perspective)
        if isinstance(p, URIRef)
        and next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None) is not None
    )
    case = case_slug_of(str(perspectives[0])) if perspectives else None
    lines: list[str] = [f"# Synopsis: {case}" if case else "# Synopsis", ""]

    if not perspectives:
        lines += ["_No grounded perspectives in the loaded scope._", ""]
        return "\n".join(lines)

    practice_to_persp: dict[URIRef, URIRef] = {}
    frames: list[dict] = []
    for p in perspectives:
        practices = sorted(
            (pr for pr in g.objects(p, ANT.perspectiveGroundedIn) if isinstance(pr, URIRef)),
            key=str,
        )
        invariance = next(iter(g.objects(p, ANT.perspectiveTracksInvariance)), None)
        holder = next(iter(g.objects(p, ANT.perspectiveHeldBy)), None)
        network = network_for_perspective(g, p)
        for pr in practices:  # a perspective may be grounded in more than one practice
            practice_to_persp[pr] = p
        frames.append({
            "iri": p,
            "label": label_of(g, p),
            "holder": holder,
            "practices": practices,
            "invariance": str(invariance) if invariance else "",
            "network": network,
            # Interpretive footprint, not bare network membership: how many
            # distinct actants this frame actually *characterizes*.
            "n_actants_read": len({
                o
                for c in g.subjects(ANT.withinNetwork, network)
                for o in g.objects(c, ANT.characterizes)
                if isinstance(o, URIRef)
            }) if network else 0,
            "n_chars": len(set(g.subjects(ANT.withinNetwork, network))) if network else 0,
        })

    holders = {f["holder"] for f in frames if f["holder"] is not None}
    held_note = (
        f" All {len(frames)} readings are authored by {label_of(g, next(iter(holders)))}. "
        "The perspectives are provenance (positionality), not neutral fact."
        if len(holders) == 1 and len(frames) > 1 else ""
    )
    plural = "perspectives" if len(frames) != 1 else "perspective"
    lines += [
        f"The **{case or 'this'}** field site read through {len(frames)} "
        f"{plural}: the actants, characterized from each. "
        "This synopsis gives each frame's reading and where the frames agree or "
        "flip; the per-frame briefs and the perspective comparison carry the "
        f"full detail.{held_note}",
        "",
    ]

    # --- At a glance ---------------------------------------------------------
    lines += ["## At a glance", ""]
    rows = [[
        f["label"],
        " · ".join(local_name(str(pr)) for pr in f["practices"]) or "",
        f["invariance"] or "",
        label_of(g, f["network"]) if f["network"] else "",
        str(f["n_actants_read"]),
        str(f["n_chars"]),
    ] for f in frames]
    lines.append(md_table(
        ["Perspective", "Grounded in", "Invariance tracked", "Network",
         "Actants read", "Characterizations"], rows,
    ))
    lines.append("")

    # --- The readings (authored network narratives) --------------------------
    lines += ["## The readings", ""]
    for f in frames:
        net = f["network"]
        lines += [f"### {f['label']}", ""]
        if net is not None:
            lines += [
                f"**{label_of(g, net)}**", "",
                description_of(g, net) or "_(no description)_", "",
            ]
        else:
            lines += ["_No network matched to this perspective._", ""]

    # --- Across the frames (flips vs agreements) -----------------------------
    actant_roles: dict[URIRef, dict[URIRef, set[str]]] = {}
    for c in g.subjects(RDF.type, ANT.Characterization):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        practice = next(iter(g.objects(c, ANT.perPractice)), None)
        if not isinstance(actant, URIRef) or not isinstance(role, URIRef):
            continue
        persp = practice_to_persp.get(practice) if isinstance(practice, URIRef) else None
        if persp is None:
            continue
        actant_roles.setdefault(actant, {}).setdefault(persp, set()).add(local_name(str(role)))

    diverge: list[tuple[str, dict[URIRef, set[str]]]] = []
    converge: list[tuple[str, str]] = []
    for actant, by_persp in actant_roles.items():
        if len(by_persp) < 2:
            continue
        roles: set[str] = set().union(*by_persp.values())
        if len(roles) == 1:
            converge.append((label_of(g, actant), next(iter(roles))))
        else:
            diverge.append((label_of(g, actant), by_persp))

    lines += ["## Across the frames", ""]
    shared = sum(1 for by in actant_roles.values() if len(by) >= 2)
    lines += [f"{shared} actant(s) are characterized in more than one frame.", ""]

    lines += ["**They flip**, same actant, different role by frame:", ""]
    if diverge:
        for name, by_persp in sorted(diverge, key=lambda t: t[0]):
            parts = [
                f"{f['label'].split(' ')[0]} = {'/'.join(sorted(by_persp[f['iri']]))}"
                for f in frames if f["iri"] in by_persp
            ]
            lines.append(f"- **{name}**: {', '.join(parts)}")
    else:
        lines.append("_No role flips between the frames._")
    lines.append("")

    lines += ["**They agree**, same role across the frames that read them:", ""]
    if converge:
        for name, role in sorted(converge):
            lines.append(f"- **{name}**: {role}")
    else:
        lines.append("_No cross-frame agreements._")
    lines.append("")

    # --- Totals --------------------------------------------------------------
    n_actants = len(set(g.subjects(RDF.type, ANT.Actant)))
    n_trans = len([
        t for t in g.subjects(RDF.type, ANT.Translation)
        if next(iter(g.objects(t, ANT.hasMoment)), None) is not None
    ])
    n_chars = len(set(g.subjects(RDF.type, ANT.Characterization)))
    lines += [
        "---", "",
        f"_{case or 'case'}: {n_actants} actants · {n_trans} translations · "
        f"{n_chars} characterizations · {len(frames)} {plural}._",
        "",
        see_also_footer(case, exclude=f"{case}-synopsis.md"),
    ]
    return "\n".join(lines)

