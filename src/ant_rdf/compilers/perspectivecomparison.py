# SPDX-License-Identifier: Apache-2.0
"""PerspectiveComparison compiler — reads one field site through every
perspective recorded for it, side by side.

Where NetworkBrief renders a single ``ant:Network``, this compiler is for the
case the rest of the toolchain is otherwise silent about: *the same field site
characterized from two or more observer-frames*. It pivots on the actant — the
unit both perspectives share — and asks, for each, what role every perspective
assigns it. Convergence (the same actant read as the same role by independent
practices) and divergence (the "flips") are each findings in their own right.

Scope: per-case. Run with a case slug so the loader pulls every perspective's
TTL into one graph::

    ant compile koi PerspectiveComparison -o briefs/koi-comparison.md

Perspectives are joined to their content structurally:

- networks / translations  → by shared IRI tail (the repo's filesystem
  convention: ``perspectives/<x>``, ``network/<x>``, ``translation/<x>``)
- characterizations         → by ``ant:perPractice`` matching a perspective's
  ``ant:perspectiveGroundedIn``. Characterizations whose practice is *not* any
  perspective's grounding practice are surfaced separately as additional
  lenses (e.g. a data-stewardship reading layered over an ethnographic one).
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    description_of,
    label_of,
    local_name,
    md_table,
)

# Callon's four moments, in canonical order, for the translation comparison.
_MOMENT_ORDER = [
    ("Problematization", ANT.Problematization),
    ("Interessement", ANT.Interessement),
    ("Enrolment", ANT.Enrolment),
    ("Mobilization", ANT.Mobilization),
]


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

    # Per-perspective bundle: holder, practice, matched network + translation.
    frames: list[dict] = []
    practice_to_persp: dict[URIRef, URIRef] = {}
    for p in perspectives:
        practice = next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None)
        holder = next(iter(g.objects(p, ANT.perspectiveHeldBy)), None)
        tail = local_name(str(p))
        network = _by_tail(g, ANT.Network, tail)
        translation = _translation_by_tail(g, tail)
        if isinstance(practice, URIRef):
            practice_to_persp[practice] = p
        frames.append({
            "iri": p,
            "tail": tail,
            "label": label_of(g, p),
            "practice": practice,
            "holder": holder,
            "network": network,
            "translation": translation,
        })

    case_slug = _case_slug(str(perspectives[0]))
    lines[0] = f"# Perspective Comparison: {case_slug}" if case_slug else lines[0]
    lines += [
        f"The {case_slug or 'this'} field site read through "
        f"{len(frames)} perspectives, side by side. The comparison pivots on "
        "the actant — the unit the frames share — so that where they converge "
        "and where they diverge each become visible.",
        "",
    ]

    # --- Perspectives at a glance -------------------------------------------
    lines += ["## Perspectives at a glance", ""]
    rows = []
    for f in frames:
        rows.append([
            f["label"],
            local_name(str(f["holder"])) if f["holder"] else "—",
            local_name(str(f["practice"])) if f["practice"] else "—",
            label_of(g, f["network"]) if f["network"] else "_(no network)_",
        ])
    lines.append(md_table(
        ["Perspective", "Held by", "Grounded in (practice)", "Network"], rows
    ))
    lines.append("")

    # --- The networks, side by side -----------------------------------------
    lines += ["## The networks, side by side", ""]
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

    # --- Actants characterized across perspectives --------------------------
    # Group every characterization by the actant it characterizes, then by the
    # perspective its practice grounds. Cells carry role + invariance.
    actant_cells: dict[URIRef, dict[URIRef, list[str]]] = {}
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
        cell = local_name(str(role))
        if invariance:
            cell += f" — _{invariance}_"
        actant_cells.setdefault(actant, {}).setdefault(persp, []).append(cell)

    lines += ["## Actants characterized across perspectives", ""]
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
                    row.append("<br>".join(sorted(cells)))
                    for cell in cells:
                        roles_seen.add(cell.split(" — ", 1)[0])
                else:
                    row.append("—")
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
                "role — agreement that is itself a finding, not a redundancy:"
            )
            lines.append("")
            for name, role in sorted(converge):
                lines.append(f"- **{name}** — {role} in every frame that characterizes it")
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
            "perspectives — extra texture layered over the field site:"
        )
        lines.append("")
        rows = []
        for actant, role, practice, invariance, net in sorted(
            extra_lens, key=lambda t: (str(t[0]), str(t[1]))
        ):
            rows.append([
                label_of(g, actant),
                local_name(str(role)),
                local_name(str(practice)) if practice else "—",
                invariance or "—",
                label_of(g, net) if isinstance(net, URIRef) else "—",
            ])
        lines.append(md_table(
            ["Actant", "Role", "Practice", "Invariance", "Within network"], rows
        ))
        lines.append("")

    # --- Translations, side by side -----------------------------------------
    lines += ["## Translations, side by side", ""]
    have_translation = any(f["translation"] for f in frames)
    if have_translation:
        for f in frames:
            t = f["translation"]
            if t is None:
                continue
            lines += [
                f"**{f['label']}** — {label_of(g, t)}",
                "",
                description_of(g, t) or "_(no description)_",
                "",
            ]
        # Moment-by-moment matrix across the canonical Callon arc.
        lines += ["### The translation arcs, moment by moment", ""]
        headers = ["Moment"] + [f["label"] for f in frames]
        rows = []
        for moment_label, moment_type in _MOMENT_ORDER:
            row = [moment_label]
            for f in frames:
                t = f["translation"]
                cell = "—"
                if t is not None:
                    for m in g.objects(t, ANT.hasMoment):
                        if (m, RDF.type, moment_type) in g:
                            cell = label_of(g, m)
                            break
                row.append(cell)
            rows.append(row)
        lines.append(md_table(headers, rows))
        lines.append("")
    else:
        lines += ["_No translations matched to the compared perspectives._", ""]

    lines += ["---", ""]
    return "\n".join(lines)


def _by_tail(g, rdf_type: URIRef, tail: str) -> URIRef | None:
    """Subject of ``rdf_type`` whose IRI tail matches ``tail`` (repo convention)."""
    for s in g.subjects(RDF.type, rdf_type):
        if isinstance(s, URIRef) and local_name(str(s)) == tail:
            return s
    return None


def _translation_by_tail(g, tail: str) -> URIRef | None:
    """Top-level translation (has moments) whose IRI tail matches ``tail``."""
    for s in g.subjects(RDF.type, ANT.Translation):
        if (
            isinstance(s, URIRef)
            and local_name(str(s)) == tail
            and next(iter(g.objects(s, ANT.hasMoment)), None) is not None
        ):
            return s
    return None


def _case_slug(iri: str) -> str | None:
    marker = "/cases/"
    if marker not in iri:
        return None
    rest = iri.split(marker, 1)[1]
    return rest.split("/", 1)[0].split("#", 1)[0] or None
