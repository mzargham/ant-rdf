# SPDX-License-Identifier: Apache-2.0
"""DurabilityDashboard compiler — what is holding vs. unravelling across the case.

Read behaviorally, a translation is 'done' when a new regularity stabilizes; success is its
durability, failure its unravelling. This board groups every translation by ant:hasStatus
(Stabilized / Precarious / Unravelled / forming) and shows its ant:hasDurability (material /
strategic / discursive) and frame — the honest at-a-glance of the case's precariousness.

Scope: whole-case::

    ant compile koi DurabilityDashboard -o briefs/koi-durability.md
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
    see_also_footer,
)

REFRESH_SUFFIX = "durability"
REQUIRES_GROUNDED = True

# Display order for status buckets.
_STATUS_ORDER = ["Stabilized", "Precarious", "Unravelled", ""]


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject

    # Every ant:Translation (not filtered by moment presence — the board claims
    # to cover them all). Frame is read from the graph via ant:authoredUnder,
    # whose local-name is the perspective slug (ADR-0004).
    translations = sorted(
        (t for t in g.subjects(RDF.type, ANT.Translation) if isinstance(t, URIRef)),
        key=str,
    )
    case = next((case_slug_of(str(t)) for t in translations), None)

    # bucket -> [(label, frame, durability, iri)]
    buckets: dict[str, list[tuple[str, str, str, URIRef]]] = {}
    for t in translations:
        status = _one(g, t, ANT.hasStatus)
        durab = _one(g, t, ANT.hasDurability)
        au = next(iter(g.objects(t, ANT.authoredUnder)), None)
        frame = frame_label(g, au) if isinstance(au, URIRef) else ""
        buckets.setdefault(status, []).append((label_of(g, t), frame, durab, t))

    lines: list[str] = [f"# Durability dashboard: {case}" if case else "# Durability dashboard", ""]
    total = len(translations)
    counts = " · ".join(
        f"{s or 'Forming'}: {len(buckets.get(s, []))}"
        for s in _STATUS_ORDER
        if buckets.get(s)
    )
    lines += [
        f"{total} translation(s) by behavioral status. {counts}." if total else "_No translations._",
        "",
    ]
    if not total:
        lines.append(see_also_footer(case))
        return "\n".join(lines)

    for status in _STATUS_ORDER:
        rows_src = sorted(buckets.get(status, []))
        if not rows_src:
            continue
        heading = status if status != "" else "Forming / not yet assessed"
        lines += [f"## {heading} ({len(rows_src)})", ""]
        rows = [[label, frame, durab] for (label, frame, durab, _iri) in rows_src]
        lines.append(md_table(["Translation", "Frame", "Durability"], rows))
        lines.append("")

    # Durability cross-tab.
    lines += ["## By durability", ""]
    dur_counts: dict[str, int] = {}
    for t in translations:
        d = _one(g, t, ANT.hasDurability)
        dur_counts[d] = dur_counts.get(d, 0) + 1
    rows = [[k if k != "" else "_(unset)_", str(v)] for k, v in sorted(dur_counts.items())]
    lines.append(md_table(["Durability", "Count"], rows))
    lines += ["", see_also_footer(case)]
    return "\n".join(lines)


def _one(g, s: URIRef, pred: URIRef) -> str:
    o = next(iter(g.objects(s, pred)), None)
    return local_name(str(o)) if isinstance(o, URIRef) else ""
