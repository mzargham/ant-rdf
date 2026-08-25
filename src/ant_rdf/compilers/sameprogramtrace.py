# SPDX-License-Identifier: Apache-2.0
"""SameProgramTrace compiler — one program read across its frames.

Some programs are enacted once but read differently by each perspective.
ant:readsSameProgramAs (symmetric, ADR-0002) links those translations. This
compiler finds each connected cluster and lays the members side by side —
frame, status, durability, reading, and the Mobilization (behavioral) moment.

Scope: whole-case::

    ant compile koi SameProgramTrace -o briefs/koi-same-program-trace.md
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    description_of,
    frame_label,
    label_of,
    local_name,
    md_table,
    see_also_footer,
)

REFRESH_SUFFIX = "same-program-trace"
MIN_PERSPECTIVES = 2


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject

    # Symmetric adjacency over readsSameProgramAs.
    adj: dict[URIRef, set[URIRef]] = {}
    nodes: set[URIRef] = set()
    for s, o in g.subject_objects(ANT.readsSameProgramAs):
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            adj.setdefault(s, set()).add(o)
            adj.setdefault(o, set()).add(s)
            nodes.add(s)
            nodes.add(o)

    # Connected components.
    seen: set[URIRef] = set()
    components: list[list[URIRef]] = []
    for n in sorted(nodes, key=str):
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.add(x)
            stack.extend(adj.get(x, ()))
        components.append(sorted(comp, key=str))

    case = next((case_slug_of(str(n)) for n in nodes), None) or next(
        (case_slug_of(str(p)) for p in g.subjects(RDF.type, ANT.Perspective) if case_slug_of(str(p))),
        None,
    )
    lines: list[str] = [f"# Same-program traces: {case}" if case else "# Same-program traces", ""]
    lines += [
        f"{len(components)} program(s) are read across more than one frame "
        "(linked by ant:readsSameProgramAs). Each is one enactment seen several ways.",
        "",
    ]
    if not components:
        lines += ["_No ant:readsSameProgramAs clusters in the loaded scope._", ""]
        lines.append(see_also_footer(case))
        return "\n".join(lines)

    for comp in components:
        title = " · ".join(sorted(local_name(str(t)) for t in comp))
        lines += [f"## {title}", ""]
        rows = []
        statuses: set[str] = set()
        for t in comp:
            st = _one(g, t, ANT.hasStatus)
            statuses.add(st or "Forming")
            rows.append([
                _frame(g, t),
                label_of(g, t),
                st,
                _one(g, t, ANT.hasDurability),
            ])
        lines.append(md_table(["Frame", "Translation", "Status", "Durability"], rows))
        lines.append("")
        if len(statuses) > 1:
            lines += [
                "> The frames read different **statuses** for this one program. That is an "
                "honest divergence on the time scale, not a contradiction: the standing "
                "pattern can be stabilized over the long run while any individual enactment "
                "of it stays precarious until it re-stabilizes.",
                "",
            ]
        for t in comp:
            lines += [f"### {label_of(g, t)} · {_frame(g, t)}", "", f"<!-- {t} -->", ""]
            if description_of(g, t):
                lines += [description_of(g, t), ""]
            mob = _mobilization(g, t)
            if mob:
                lines += [f"*Mobilization:* {description_of(g, mob)}", ""]

    lines.append(see_also_footer(case))
    return "\n".join(lines)


def _one(g, s: URIRef, pred: URIRef) -> str:
    o = next(iter(g.objects(s, pred)), None)
    return local_name(str(o)) if isinstance(o, URIRef) else ""


def _frame(g, t: URIRef) -> str:
    au = next(iter(g.objects(t, ANT.authoredUnder)), None)
    return frame_label(g, au) if isinstance(au, URIRef) else ""


def _mobilization(g, t: URIRef) -> URIRef | None:
    for m in g.objects(t, ANT.hasMoment):
        if isinstance(m, URIRef) and (m, RDF.type, ANT.Mobilization) in g:
            return m
    return None
