# SPDX-License-Identifier: Apache-2.0
"""CaseCatalog compiler — renders all cases as a single Markdown index.

Walks every Network instance in the loaded graph and groups them by case
slug (derived from IRI). For each case: name the network(s), count
actants and translations, list perspectives.
"""

from __future__ import annotations

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    description_of,
    label_of,
    md_table,
)


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject  # CaseCatalog ignores subject — it's an index over all cases

    cases: dict[str, dict] = {}
    for s in g.subjects():
        if not isinstance(s, URIRef):
            continue
        slug = _case_slug(str(s))
        if not slug:
            continue
        bucket = cases.setdefault(slug, {
            "networks": set(),
            "actants": set(),
            "translations": set(),
            "perspectives": set(),
            "characterizations": set(),
        })
        for t in g.objects(s, RDF.type):
            if t == ANT.Network:
                bucket["networks"].add(s)
            elif t == ANT.Actant:
                bucket["actants"].add(s)
            elif t == ANT.Translation and list(g.objects(s, ANT.hasMoment)):
                # Only top-level translations (with moments), not moment subclasses
                bucket["translations"].add(s)
            elif t == ANT.Perspective:
                bucket["perspectives"].add(s)
            elif t == ANT.Characterization:
                bucket["characterizations"].add(s)

    lines = [
        "# Case Catalog",
        "",
        f"All ant:Network records across {len(cases)} case(s) in the loaded graph.",
        "",
    ]

    if not cases:
        lines.append("_(no cases recorded)_")
        return "\n".join(lines) + "\n"

    rows = []
    for slug in sorted(cases):
        c = cases[slug]
        for net in sorted(c["networks"]):
            rows.append([
                slug,
                label_of(g, net),
                str(len(c["actants"])),
                str(len(c["translations"])),
                str(len(c["perspectives"])),
                str(len(c["characterizations"])),
            ])
    lines.append(md_table(
        ["Case", "Network", "Actants", "Translations", "Perspectives", "Characterizations"],
        rows,
    ))
    lines.append("")

    for slug in sorted(cases):
        c = cases[slug]
        lines.append(f"## {slug}")
        lines.append("")
        for net in sorted(c["networks"]):
            lines.append(f"### {label_of(g, net)}")
            lines.append("")
            lines.append(f"<!-- {net} -->")
            lines.append("")
            lines.append(description_of(g, net) or "_(no description)_")
            lines.append("")

    lines += ["---", ""]
    return "\n".join(lines)


def _case_slug(iri: str) -> str | None:
    marker = "/cases/"
    if marker not in iri:
        return None
    rest = iri.split(marker, 1)[1]
    slug = rest.split("/", 1)[0].split("#", 1)[0]
    return slug or None
