# SPDX-License-Identifier: Apache-2.0
"""PositionalityLedger compiler — the reader's key to the frames as provenance.

The perspectives are not neutral accounts; they are *positions* — each held by
someone, grounded in a practice, tracking a particular invariance. Every
characterization and network reading is authored *from* one of them. This
ledger makes that provenance legible up front: who holds each frame, the
practice it reasons from (with the practice's own description), the invariance
it holds constant, and how much of the field site it authors.

Scope: per-case::

    ant compile koi PositionalityLedger -o briefs/koi-positionality.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    description_of,
    label_of,
    md_table,
    network_for_perspective,
    see_also_footer,
)

REFRESH_SUFFIX = "positionality"
REQUIRES_GROUNDED = True


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject

    perspectives = sorted(
        p for p in g.subjects(RDF.type, ANT.Perspective)
        if isinstance(p, URIRef)
        and next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None) is not None
    )
    case = next((case_slug_of(str(p)) for p in perspectives), None)
    lines: list[str] = [f"# Positionality ledger: {case}" if case else "# Positionality ledger", ""]

    if not perspectives:
        lines += ["_No grounded perspectives in the loaded scope._", ""]
        return "\n".join(lines)

    lines += [
        f"The {case or 'this'} field site is read from {len(perspectives)} "
        f"position{'s' if len(perspectives) != 1 else ''}. Each is provenance, not neutral fact: a reading is authored "
        "*from* a frame, by whoever holds it, reasoning from a practice, holding "
        "one invariance constant. This ledger is the key to who is speaking.",
        "",
    ]

    # A compact overview first.
    rows = []
    for p in perspectives:
        net = network_for_perspective(g, p)
        holder = next(iter(g.objects(p, ANT.perspectiveHeldBy)), None)
        practices = sorted(g.objects(p, ANT.perspectiveGroundedIn), key=str)
        rows.append([
            label_of(g, p),
            label_of(g, holder) if isinstance(holder, URIRef) else "",
            " · ".join(label_of(g, pr) for pr in practices) or "",
            str(_authored_count(g, p, net)),
        ])
    lines += ["## At a glance", ""]
    lines.append(md_table(
        ["Position", "Held by", "Grounding practice(s)", "Authors (records)"], rows
    ))
    lines.append("")

    # Then a section per position.
    for p in perspectives:
        net = network_for_perspective(g, p)
        holder = next(iter(g.objects(p, ANT.perspectiveHeldBy)), None)
        practices = sorted(g.objects(p, ANT.perspectiveGroundedIn), key=str)
        invariance = next(iter(g.objects(p, ANT.perspectiveTracksInvariance)), None)
        n_trans = sum(1 for _ in _translations_under(g, p))
        n_chars = sum(1 for _ in g.subjects(ANT.withinNetwork, net)) if net else 0

        lines += [f"## {label_of(g, p)}", ""]
        if holder is not None:
            lines.append(f"- **Held by:** {label_of(g, holder)}")
        if net is not None:
            lines.append(f"- **Reading:** {label_of(g, net)}")
        if invariance is not None:
            lines.append(f"- **Holds invariant:** {invariance}")
        lines.append(f"- **Authors:** 1 network · {n_trans} translations · {n_chars} characterizations")
        internalizers = sorted(g.subjects(ANT.internalizes, p), key=str)
        if internalizers:
            lines.append("- **Internalized by:** " + ", ".join(label_of(g, s) for s in internalizers))
        lines.append("")
        if description_of(g, p):
            lines += [description_of(g, p), ""]
        for pr in practices:
            lines += [f"**Practice · {label_of(g, pr)}:**", "", description_of(g, pr) or "_(no description)_", ""]

    lines.append(see_also_footer(case, exclude=f"{case}-positionality.md"))
    return "\n".join(lines)


def _translations_under(g, p: URIRef):
    for t in g.subjects(RDF.type, ANT.Translation):
        if isinstance(t, URIRef) and (t, ANT.authoredUnder, p) in g:
            yield t


def _authored_count(g, p: URIRef, net: URIRef | None) -> int:
    n = 1 if net is not None else 0  # the network
    n += sum(1 for _ in _translations_under(g, p))
    if net is not None:
        n += sum(1 for _ in g.subjects(ANT.withinNetwork, net))
    return n

