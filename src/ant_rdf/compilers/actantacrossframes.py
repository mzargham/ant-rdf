# SPDX-License-Identifier: Apache-2.0
"""ActantAcrossFrames compiler — the many faces of one actant, read frame by frame.

Where ActantProfile renders a single actant's characterizations as an undifferentiated
list, this compiler is cross-perspective: for every actant characterized in two or more
frames (the payoff of shared actant IRIs), it lays out the frame-by-frame reading — role,
practice, invariance, the characterization's gloss — and a converge/diverge verdict, plus
any ant:correspondsTo cross-frame twins and ant:manifestsAs coexistence.

Scope: whole-case. Run with a case slug (no --perspective, so every frame loads)::

    ant compile koi ActantAcrossFrames -o briefs/koi-actants-across-frames.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    description_of,
    invariance_display,
    label_of,
    local_name,
    many_iris,
    md_table,
    perspective_index,
    see_also_footer,
)

REFRESH_SUFFIX = "actants-across-frames"
MIN_PERSPECTIVES = 2


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject  # whole-case; ignores subject
    frames, practice_to_persp = perspective_index(g)
    frame_order = [f["iri"] for f in frames]
    frame_label = {f["iri"]: f["label"].split(" · ")[0].strip() for f in frames}

    # actant -> {perspective_iri -> [(role, invariance, char_desc)]}
    by_actant: dict[URIRef, dict[URIRef, list[tuple[str, str, str]]]] = {}
    for c in g.subjects(RDF.type, ANT.Characterization):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        prac = next(iter(g.objects(c, ANT.perPractice)), None)
        inv = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
        if not isinstance(actant, URIRef) or not isinstance(role, URIRef):
            continue
        persp = practice_to_persp.get(prac) if isinstance(prac, URIRef) else None
        if persp is None:
            continue
        by_actant.setdefault(actant, {}).setdefault(persp, []).append(
            (local_name(str(role)), str(inv or ""), description_of(g, c))
        )

    case = next((case_slug_of(str(a)) for a in by_actant), None)
    lines: list[str] = [f"# Actants across frames: {case}" if case else "# Actants across frames", ""]

    multi = {a: d for a, d in by_actant.items() if len(d) >= 2}
    single = {a: d for a, d in by_actant.items() if len(d) == 1}

    lines += [
        f"{len(multi)} actant(s) are characterized in two or more of the "
        f"{len(frames)} frames: the same entity read several ways. Each section "
        "gives the frame-by-frame roles and whether they converge or diverge.",
        "",
        "> **Reading the roles.** The *invariant* column names what the characterization "
        "holds constant. An **Intermediary** *passes it through*: it transmits that one "
        "dimension-set unchanged. A **Mediator** *regulates to preserve* it: it varies *other* "
        "dimensions in order to keep that invariant (cybernetic requisite variety). Both serve an "
        "invariant; the role is the *shape*. An actant can be a Mediator on the dimensions it "
        "regulates and an Intermediary on the ones it passes through, and the frame (perspective) "
        "selects which dimensions are coded.",
        "",
    ]

    for actant in sorted(multi, key=str):
        by_persp = multi[actant]
        lines += [f"## {label_of(g, actant)}", "", f"<!-- {actant} -->", ""]
        roles_seen: set[str] = set()
        rows = []
        for f_iri in frame_order:
            if f_iri not in by_persp:
                continue
            for role, inv, gloss in by_persp[f_iri]:
                roles_seen.add(role)
                rows.append([frame_label[f_iri], role, invariance_display(role, inv), gloss or ""])
        lines.append(md_table(["Frame", "Role", "Invariant (how held)", "Reading"], rows))
        verdict = (
            f"**Converges**: read as {next(iter(roles_seen))} in every frame that characterizes it."
            if len(roles_seen) == 1
            else f"**Diverges**: {' / '.join(sorted(roles_seen))} depending on the frame."
        )
        lines += ["", verdict, ""]
        corr = many_iris(g, actant, ANT.correspondsTo)
        if corr:
            lines.append(
                "Cross-frame correspondents: "
                + ", ".join(f"{label_of(g, o)} (`{local_name(str(o))}`)" for o in corr)
            )
            lines.append("")
        manif = many_iris(g, actant, ANT.manifestsAs)
        if manif:
            lines.append(
                "Manifested as (also inscriptions, C9): "
                + ", ".join(f"{label_of(g, o)} (`{local_name(str(o))}`)" for o in manif)
            )
            lines.append("")

    if single:
        lines += ["## Read in only one frame", ""]
        for actant in sorted(single, key=str):
            f_iri = next(iter(single[actant]))
            roles = " / ".join(dict.fromkeys(r for r, _inv, _g in single[actant][f_iri]))
            line = f"- **{label_of(g, actant)}**: {roles} ({frame_label.get(f_iri, '?')})"
            corr = many_iris(g, actant, ANT.correspondsTo)
            if corr:
                line += "; corresponds to " + ", ".join(label_of(g, o) for o in corr)
            manif = many_iris(g, actant, ANT.manifestsAs)
            if manif:
                line += "; manifested as " + ", ".join(label_of(g, o) for o in manif)
            lines.append(line)
        lines.append("")

    lines.append(see_also_footer(case))
    return "\n".join(lines)
