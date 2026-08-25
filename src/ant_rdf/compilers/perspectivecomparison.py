# SPDX-License-Identifier: Apache-2.0
"""PerspectiveComparison compiler — reads one field site through every
perspective recorded for it, side by side.

Where NetworkBrief renders a single ``ant:Network``, this compiler is for the
case the rest of the toolchain is otherwise silent about: *the same field site
characterized from two or more observer-frames*. It pivots on the actant — the
unit both perspectives share — and asks, for each, what role every perspective
assigns it. Convergence (the same actant read as the same role by independent
practices) and divergence (the "flips") are each findings in their own right,
so they lead; the per-frame network narratives sit at the end for reference.

Scope: per-case. Run with a case slug so the loader pulls every perspective's
TTL into one graph::

    ant compile koi PerspectiveComparison -o briefs/koi-comparison.md

Perspectives are joined to their content by the graph, not the filesystem:

- networks       → by shared IRI tail (``perspectives/<x>`` ↔ ``network/<x>``)
- characterizations → by ``ant:perPractice`` matching any of a perspective's
  ``ant:perspectiveGroundedIn`` practices. Characterizations whose practice
  grounds no compared perspective surface separately as additional lenses.
- translations   → by ``ant:authoredUnder`` (ADR-0004): each perspective's
  translations, listed with behavioral status and durability.
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
    md_table,
    network_for_perspective,
    see_also_footer,
)

# `ant refresh` contract: one comparison per case, only when there is
# something to compare.
REFRESH_SUFFIX = "comparison"
MIN_PERSPECTIVES = 2


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject  # comparison spans all perspectives in the loaded case

    # Perspectives worth comparing carry a grounding practice. The auto-created
    # `_default` stub has none, so it drops out naturally.
    perspectives = sorted(
        p
        for p in g.subjects(RDF.type, ANT.Perspective)
        if isinstance(p, URIRef)
        and next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None) is not None
    )

    lines: list[str] = ["# Perspective Comparison", ""]

    if len(perspectives) < 2:
        lines += [
            "_Fewer than two grounded perspectives are present in the loaded "
            "scope — there is nothing to compare. Run this against a case slug "
            "whose field site is read from multiple observer-frames._",
            "",
        ]
        return "\n".join(lines)

    # Per-perspective bundle: holder, practices, matched network. Every
    # grounding practice maps to the perspective so no characterization is
    # misfiled as an "extra lens" just because it cites the second practice.
    frames: list[dict] = []
    practice_to_persp: dict[URIRef, URIRef] = {}
    for p in perspectives:
        practices = sorted(
            pr for pr in g.objects(p, ANT.perspectiveGroundedIn) if isinstance(pr, URIRef)
        )
        holder = next(iter(g.objects(p, ANT.perspectiveHeldBy)), None)
        tail = local_name(str(p))
        network = network_for_perspective(g, p)
        for pr in practices:
            practice_to_persp[pr] = p
        frames.append({
            "iri": p,
            "tail": tail,
            "label": label_of(g, p),
            "practices": practices,
            "holder": holder,
            "network": network,
            "invariance": str(next(iter(g.objects(p, ANT.perspectiveTracksInvariance)), "")),
        })

    case_slug = case_slug_of(str(perspectives[0]))
    lines[0] = f"# Perspective Comparison: {case_slug}" if case_slug else lines[0]
    lines += [
        f"The {case_slug or 'this'} field site read through "
        f"{len(frames)} perspectives, side by side. The comparison pivots on "
        "the actant (the unit the frames share), so that where they converge "
        "and where they diverge each become visible.",
        "",
    ]

    # --- Perspectives at a glance -------------------------------------------
    lines += ["## Perspectives at a glance", ""]
    rows = []
    for f in frames:
        rows.append([
            f["label"],
            label_of(g, f["holder"]) if f["holder"] else "",
            " · ".join(local_name(str(pr)) for pr in f["practices"]) or "",
            f["invariance"] or "",
            label_of(g, f["network"]) if f["network"] else "_(no network)_",
        ])
    lines.append(md_table(
        ["Perspective", "Held by", "Grounded in (practice)", "Invariance tracked", "Network"], rows
    ))
    lines.append("")

    # --- Actants characterized across perspectives (the finding — leads) -----
    # Each cell is (role, invariance, characterization) so the invariance can be
    # rendered once per frame (in the glance table above) and shown per-cell only
    # where an actant carries more than one reading in a frame.
    actant_cells: dict[URIRef, dict[URIRef, list[tuple[str, str, URIRef]]]] = {}
    extra_lens: list[tuple[URIRef, URIRef, URIRef, str, URIRef | None]] = []
    for c in g.subjects(RDF.type, ANT.Characterization):
        if not isinstance(c, URIRef):
            continue
        actant = next(iter(g.objects(c, ANT.characterizes)), None)
        role = next(iter(g.objects(c, ANT.assignsRole)), None)
        practice = next(iter(g.objects(c, ANT.perPractice)), None)
        invariance = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
        net = next(iter(g.objects(c, ANT.withinNetwork)), None)
        if not isinstance(actant, URIRef) or not isinstance(role, URIRef):
            continue
        persp = practice_to_persp.get(practice) if isinstance(practice, URIRef) else None
        if persp is None:
            extra_lens.append((actant, role, practice, str(invariance or ""), net))
            continue
        actant_cells.setdefault(actant, {}).setdefault(persp, []).append(
            (local_name(str(role)), str(invariance or ""), c)
        )

    lines += ["## Actants characterized across perspectives", ""]
    lines += [
        "Roles per actant per frame. Each frame tracks one invariance (in the table "
        "above), so a per-cell invariance appears only where an actant carries more "
        "than one reading in a frame, to tell those readings apart.",
        "",
    ]
    if actant_cells:
        headers = ["Actant"] + [f["label"] for f in frames] + ["Reading"]
        rows = []
        converge: list[tuple[str, str]] = []
        diverge: list[str] = []
        for actant in sorted(actant_cells, key=str):
            by_persp = actant_cells[actant]
            row = [label_of(g, actant)]
            roles_seen: set[str] = set()
            covered = 0
            for f in frames:
                cells = by_persp.get(f["iri"])
                if cells:
                    covered += 1
                    row.append("<br>".join(_render_cells(g, cells)))
                    for role, _inv, _ch in cells:
                        roles_seen.add(role)
                else:
                    row.append("")
            if covered >= 2:
                if len(roles_seen) == 1:
                    verdict = "converge"
                    converge.append((label_of(g, actant), next(iter(roles_seen))))
                else:
                    verdict = "**diverge**"
                    diverge.append(label_of(g, actant))
            else:
                verdict = "single frame"
            row.append(verdict)
            rows.append(row)
        lines.append(md_table(headers, rows))
        lines.append("")

        lines += ["### Where the frames converge", ""]
        if converge:
            lines.append(
                "Independent practices reading the same actant as the same "
                "role: agreement that is itself a finding, not a redundancy:"
            )
            lines.append("")
            for name, role in sorted(converge):
                lines.append(f"- **{name}**: {role} in every frame that characterizes it")
            lines.append("")
        else:
            lines += ["_No actant is read as the same role by two or more frames._", ""]

        lines += ["### Where the frames diverge", ""]
        if diverge:
            lines.append(
                "The flips: the same actant carries a different role depending "
                "on the practice doing the reading."
            )
            lines.append("")
            for name in sorted(set(diverge)):
                lines.append(f"- **{name}**")
            lines.append("")
        else:
            lines += ["_No role flips between the frames._", ""]
    else:
        lines += ["_No characterizations recorded in the loaded scope._", ""]

    # --- Additional lenses ---------------------------------------------------
    if extra_lens:
        lines += ["## Readings beyond the grounding practices", ""]
        lines.append(
            "Characterizations whose practice grounds none of the compared "
            "perspectives, extra texture layered over the field site:"
        )
        lines.append("")
        rows = []
        for actant, role, practice, invariance, net in sorted(
            extra_lens, key=lambda t: (str(t[0]), str(t[1]))
        ):
            rows.append([
                label_of(g, actant),
                local_name(str(role)),
                local_name(str(practice)) if practice else "",
                invariance_display(local_name(str(role)), invariance or ""),
                label_of(g, net) if isinstance(net, URIRef) else "",
            ])
        lines.append(md_table(
            ["Actant", "Role", "Practice", "Invariance", "Within network"], rows
        ))
        lines.append("")

    # --- Translations by frame (ADR-0004: grouped by ant:authoredUnder) ------
    by_frame: dict[URIRef, list[URIRef]] = {}
    for t in g.subjects(RDF.type, ANT.Translation):
        if not isinstance(t, URIRef):
            continue
        au = next(iter(g.objects(t, ANT.authoredUnder)), None)
        if isinstance(au, URIRef):
            by_frame.setdefault(au, []).append(t)

    lines += ["## Translations, by frame", ""]
    if any(by_frame.get(f["iri"]) for f in frames):
        lines.append(
            "Each perspective's programs of action, with the behavioral status "
            "(is the new regularity holding?) and durability it is read to have."
        )
        lines.append("")
        for f in frames:
            ts = sorted(by_frame.get(f["iri"], []), key=str)
            lines += [f"### {f['label']}", ""]
            if not ts:
                lines += ["_No translations authored under this frame._", ""]
                continue
            rows = [
                [label_of(g, t), _one(g, t, ANT.hasStatus), _one(g, t, ANT.hasDurability)]
                for t in ts
            ]
            lines.append(md_table(["Translation", "Status", "Durability"], rows))
            lines.append("")
    else:
        lines += ["_No translations carry ant:authoredUnder in the loaded scope._", ""]

    # --- The networks, side by side (narratives — reference, at the end) -----
    lines += ["## The readings, side by side", ""]
    for f in frames:
        net = f["network"]
        lines += [f"### {f['label']}", ""]
        if net is not None:
            lines += [
                f"**{label_of(g, net)}**",
                "",
                f"<!-- {net} -->",
                "",
                description_of(g, net) or "_(no description)_",
                "",
            ]
        else:
            lines += ["_No network matched to this perspective._", ""]

    lines.append(see_also_footer(case_slug, exclude=f"{case_slug}-comparison.md"))
    return "\n".join(lines)


def _render_cells(g, cells: list[tuple[str, str, URIRef]]) -> list[str]:
    """Render an actant's cell(s) for one frame, disambiguating progressively. A
    single characterization shows just the role (the frame's invariance is in the
    glance table). Multiple characterizations show the role; the per-cell
    invariance is added only where it actually tells the readings apart; any
    remaining tie is broken by the characterization slug."""
    ordered = sorted(cells, key=lambda t: (t[0], local_name(str(t[2]))))
    if len(ordered) == 1:
        return [ordered[0][0]]
    roles = [role for role, _inv, _ch in ordered]
    with_inv = [
        f"{role} · _{invariance_display(role, inv)}_" if inv else role
        for role, inv, _ch in ordered
    ]
    # Use the invariance only if it distinguishes more than the bare role does.
    base = with_inv if len(set(with_inv)) > len(set(roles)) else roles
    out = []
    for s, (_role, _inv, ch) in zip(base, ordered, strict=True):
        if base.count(s) > 1:
            s += f" (`{local_name(str(ch))}`)"
        out.append(s)
    return out


def _one(g, s: URIRef, pred: URIRef) -> str:
    o = next(iter(g.objects(s, pred)), None)
    return local_name(str(o)) if isinstance(o, URIRef) else ""

