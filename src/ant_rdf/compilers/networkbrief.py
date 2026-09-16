# SPDX-License-Identifier: Apache-2.0
"""NetworkBrief compiler — renders one Network as a Markdown brief.

Deterministic output (sorted IRIs). Per §6, the brief shows:
- Network name, narrative description
- Participating actants (table)
- Translations within this network's case (with their moments)
- Characterizations grounded in this network (Mediator/Intermediary/OPP/etc.)
- Provenance: the perspective the network is authored under (if known)
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
    perspective_for_network,
    see_also_footer,
)

# `ant refresh` contract: one network brief per grounded perspective.
REFRESH_SUFFIX = "network"
PER_PERSPECTIVE = True


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    """Render NetworkBrief for ``subject`` (or first ant:Network found)."""
    g = ds.default_graph

    # Locate the Network instance
    if subject is None:
        candidates = sorted(
            s for s in g.subjects(RDF.type, ANT.Network) if isinstance(s, URIRef)
        )
        if not candidates:
            raise ValueError("No ant:Network instances in the loaded graph.")
        subject = candidates[0]

    name = label_of(g, subject)
    desc = description_of(g, subject)

    lines: list[str] = [
        f"# Network Brief: {name}",
        "",
        f"<!-- compiled from {subject} -->",
        "",
    ]

    # Positionality: whose reading this is, and from which practice/invariance.
    # The authorial frame is provenance, not neutral fact — surface it up front
    # (only when the perspective is grounded; an auto-created stub says nothing).
    persp = perspective_for_network(g, subject)
    if persp is not None and next(iter(g.objects(persp, ANT.perspectiveGroundedIn)), None) is not None:
        holder = next(iter(g.objects(persp, ANT.perspectiveHeldBy)), None)
        practices = many_iris(g, persp, ANT.perspectiveGroundedIn)
        invariance = next(iter(g.objects(persp, ANT.perspectiveTracksInvariance)), None)
        lines += ["## Positionality", ""]
        lines.append(f"_This is one frame's reading ({label_of(g, persp)}), not a neutral account._")
        lines.append("")
        if holder is not None:
            lines.append(f"- **Held by:** {label_of(g, holder)}")
        if practices:
            lines.append(f"- **Grounding practice:** {' · '.join(label_of(g, pr) for pr in practices)}")
        if invariance is not None:
            lines.append(f"- **Invariance tracked:** {invariance}")
        lines.append("")

    lines += [
        "## Description",
        "",
        desc or "_(no description)_",
        "",
    ]

    # Participating actants
    actants = sorted(
        s for s in g.subjects(ANT.participatesIn, subject) if isinstance(s, URIRef)
    )
    lines += ["## Participating actants", ""]
    if actants:
        rows = [
            [label_of(g, a), description_of(g, a), local_name(str(a))]
            for a in actants
        ]
        lines.append(md_table(["Actant", "Description", "Local name"], rows))
    else:
        lines.append("_No participating actants recorded for this network._")
    lines.append("")

    # Translations for this frame. The frame is read from the graph via
    # ant:authoredUnder: a translation explicitly authored under a *different*
    # perspective is excluded, so a whole-case compile (no --perspective) no
    # longer lists every frame's translation under one network. The network's
    # own perspective is the one whose IRI tail matches the network's (repo
    # convention), else the lone perspective of a single-frame case (whose
    # `_default` stub never matches a network slug). Un-attributed
    # translations, and every translation when the frame cannot be resolved,
    # are kept. Under --perspective the loader already admits only this
    # frame's TTL.
    frame = perspective_for_network(g, subject)

    def _in_frame(s: URIRef) -> bool:
        au = next(iter(g.objects(s, ANT.authoredUnder)), None)
        return au is None or frame is None or au == frame

    translations = sorted(
        s
        for s in g.subjects(RDF.type, ANT.Translation)
        if isinstance(s, URIRef) and _in_frame(s)
    )
    lines += ["## Translations", ""]
    if translations:
        for t in translations:
            t_label = label_of(g, t)
            t_desc = description_of(g, t)
            lines += [
                f"### {t_label}",
                "",
                f"<!-- {t} -->",
                "",
                t_desc or "_(no description)_",
                "",
            ]
            moments = many_iris(g, t, ANT.hasMoment)
            if moments:
                rows = []
                for m in moments:
                    moment_type = next(
                        (
                            local_name(str(o))
                            for o in g.objects(m, RDF.type)
                            if isinstance(o, URIRef) and str(o).startswith(str(ANT))
                            and local_name(str(o)) != "Translation"
                        ),
                        "Translation",
                    )
                    rows.append([moment_type, label_of(g, m), description_of(g, m)])
                lines.append(md_table(["Moment", "Label", "Description"], rows))
            else:
                lines.append("_(no moments — Tier-1 SHACL would flag this)_")
            lines.append("")
    else:
        lines.append("_No translations recorded in the loaded scope._")
        lines.append("")

    # Characterizations within this network
    chars = sorted(
        c for c in g.subjects(ANT.withinNetwork, subject) if isinstance(c, URIRef)
    )
    lines += ["## Characterizations within this network", ""]
    if chars:
        rows = []
        for c in chars:
            target = next(iter(g.objects(c, ANT.characterizes)), None)
            role = next(iter(g.objects(c, ANT.assignsRole)), None)
            practice = next(iter(g.objects(c, ANT.perPractice)), None)
            invariance = next(iter(g.objects(c, ANT.invarianceCriterion)), None)
            role_name = local_name(str(role)) if role else "?"
            rows.append([
                label_of(g, target) if target else "?",
                role_name,
                local_name(str(practice)) if practice else "_(unspecified)_",
                invariance_display(role_name, str(invariance)) if invariance else "_(unspecified)_",
                description_of(g, c),
            ])
        lines.append(md_table(
            ["Target", "Role", "Per practice", "Invariance", "Description"], rows,
        ))
    else:
        lines.append("_No characterizations recorded within this network._")
    lines.append("")

    lines += [f"<!-- generated by ant-rdf; see {subject} -->", ""]
    lines.append(see_also_footer(case_slug_of(str(subject)), g=g))
    return "\n".join(lines)
