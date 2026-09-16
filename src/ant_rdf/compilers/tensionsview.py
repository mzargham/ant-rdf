# SPDX-License-Identifier: Apache-2.0
"""TensionsView compiler — where the network is under strain.

A reader-vantage on the fragile and the contested, pulled from the whole graph:
actants the frames *flip* on (read as different roles by different practices),
translations read as Precarious or Unravelled, anti-programs, and obligatory
passage points that nothing yet clears (latent bottlenecks). What is stable is
elsewhere; this brief is only the strain.

Scope: per-case::

    ant compile koi TensionsView -o briefs/koi-tensions.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    frame_label,
    label_of,
    local_name,
    md_table,
    perspective_index,
    see_also_footer,
)

REFRESH_SUFFIX = "tensions"
REQUIRES_GROUNDED = True

_FRAGILE = {"Precarious", "Unravelled"}


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject
    frames, practice_to_persp = perspective_index(g)
    frame_label_by_iri = {f["iri"]: f["label"].split(" · ")[0].strip() for f in frames}

    case = None
    for f in frames:
        case = case_slug_of(str(f["iri"]))
        if case:
            break
    lines: list[str] = [f"# Tensions & contested: {case}" if case else "# Tensions & contested", ""]
    lines += [
        "The fragile and the contested only. Role flips are where practices "
        "disagree about what an actant is; precarious and unravelling "
        "translations are behavioral regularities that have not held; "
        "bottlenecks are passages nothing has yet cleared.",
        "",
    ]

    # --- Role flips ---------------------------------------------------------
    roles: dict[URIRef, dict[URIRef, set[str]]] = {}
    for c in g.subjects(RDF.type, ANT.Characterization):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        prac = next(iter(g.objects(c, ANT.perPractice)), None)
        persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
        if not (isinstance(actant, URIRef) and isinstance(role, URIRef) and persp is not None):
            continue
        roles.setdefault(actant, {}).setdefault(persp, set()).add(local_name(str(role)))

    lines += ["## Role flips: the frames disagree", ""]
    flips = [
        (label_of(g, a), by)
        for a, by in roles.items()
        if len(by) >= 2 and len({r for rs in by.values() for r in rs}) > 1
    ]
    if flips:
        for name, by in sorted(flips, key=lambda t: t[0]):
            parts = [
                f"{frame_label_by_iri.get(pi, local_name(str(pi)))} = {'/'.join(sorted(rs))}"
                for pi, rs in by.items()
            ]
            lines.append(f"- **{name}**: {', '.join(sorted(parts))}")
        lines.append("")
    else:
        lines += ["_No role flips: every shared actant is read the same way._", ""]

    # --- Precarious / unravelling translations ------------------------------
    lines += ["## Precarious & unravelling", ""]
    fragile = []
    for t in g.subjects(RDF.type, ANT.Translation):
        if not isinstance(t, URIRef):
            continue
        status = next(iter(g.objects(t, ANT.hasStatus)), None)
        sname = local_name(str(status)) if isinstance(status, URIRef) else None
        if sname in _FRAGILE:
            au = next(iter(g.objects(t, ANT.authoredUnder)), None)
            fragile.append([label_of(g, t), frame_label(g, au) if isinstance(au, URIRef) else "", sname])
    if fragile:
        lines.append(
            f"{len(fragile)} translation(s) have not stabilized "
            "(delivery is not durable use):"
        )
        lines.append("")
        lines.append(md_table(["Translation", "Frame", "Status"], sorted(fragile)))
        lines.append("")
    else:
        lines += ["_No precarious or unravelling translations._", ""]

    # --- Anti-programs ------------------------------------------------------
    opposed = sorted(g.subject_objects(ANT.opposes), key=lambda so: str(so[0]))
    if opposed:
        lines += ["## Anti-programs", ""]
        for s, o in opposed:
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                lines.append(f"- **{label_of(g, s)}** opposes **{label_of(g, o)}**")
        lines.append("")

    # --- Bottlenecks: OPPs with no traffic ----------------------------------
    lines += ["## Bottlenecks: passages nothing clears yet", ""]
    idle = []
    for c in g.subjects(ANT.assignsRole, ANT.ObligatoryPassagePoint):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        if not isinstance(actant, URIRef):
            continue
        traffic = set(g.subjects(ANT.tracesToPassage, actant)) | set(g.subjects(ANT.passesThrough, actant))
        if not traffic:
            prac = next(iter(g.objects(c, ANT.perPractice)), None)
            persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
            idle.append([label_of(g, actant), frame_label_by_iri.get(persp, "")])
    if idle:
        lines.append(
            "Obligatory passage points with nothing tracing to them, either "
            "latent bottlenecks or passages the model has not yet wired up:"
        )
        lines.append("")
        lines.append(md_table(["Passage (actant)", "Frame"], sorted(idle)))
        lines.append("")
    else:
        lines += ["_Every OPP has traffic._", ""]

    lines.append(see_also_footer(case))
    return "\n".join(lines)
