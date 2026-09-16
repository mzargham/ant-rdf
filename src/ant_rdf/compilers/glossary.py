# SPDX-License-Identifier: Apache-2.0
"""Glossary compiler — the vocabulary a reader may want to check, in two parts.

First the **material-semiotics (ANT) terms** the case actually uses, rendered
live from the ontology (``rdfs:comment`` for the definition, ``dcterms:source``
for the founding citation) — no definitions are authored here. Then the
**load-bearing terms from other fields** the reading leans on: ``skos:Concept``
records authored with ``ant new-record glossary-term`` into
``instances/shared/glossary.ttl``, each a concise definition taken faithfully
from a cited source, a hook to how the reading uses the word, and links to
check the source.

Scope: per-case (loads the shared glossary)::

    ant compile koi Glossary -o briefs/koi-glossary.md
"""

from __future__ import annotations

import re

from rdflib import Dataset, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS

from ant_rdf import ANT
from ant_rdf.compilers._common import (
    case_slug_of,
    description_of,
    label_of,
    see_also_footer,
)

REFRESH_SUFFIX = "glossary"
REQUIRES_GROUNDED = True

_SKOS = "http://www.w3.org/2004/02/skos/core#"
SKOS_Concept = URIRef(_SKOS + "Concept")
SKOS_altLabel = URIRef(_SKOS + "altLabel")
SKOS_scopeNote = URIRef(_SKOS + "scopeNote")

_URL = re.compile(r"(https?://\S+)")

# Ontology comments/sources carry maintainer cross-references (plan sections, ADR
# and R/C rule numbers, "Synthesized …" design notes) that are meaningless to an
# external glossary reader. Strip them from the rendered ANT vocabulary only; the
# ontology keeps its annotations. These patterns are internal-ref-specific so they
# never touch real citations like "(Callon 1986)".
_INTERNAL_REF = re.compile(
    r"\s*\(\s*per\s+[RC]\d[a-z]?[^)]*\)"      # (per C2), (per R6), (per R9a)
    r"|\s*\(\s*(?:see\s+)?\u00a7[\d.]+[^)]*\)"     # legacy section refs in parentheses
    r"|\s*See \u00a7[\d.]+\.?"                     # legacy "See <section>."
    r"|\s*See R\d+[a-z]?\.?"                  # See R4.
    r"|\s*\b(?:See\s+)?plan \u00a7[\d.]+\.?"       # legacy "plan <section>"
    r"|\s*\u00a7[\d.]+"                            # legacy bare section ref
    r"|\s*\b(?:See\s+)?ADR-\d+\b\.?"          # ADR-0002. / See ADR-0006.
)
_SYNTH_NOTE = re.compile(r"^\s*Synthesized[^;,.]*[;,.]\s*", re.IGNORECASE)

# House style is straight quotes; some source strings carry curly quotes.
# Normalize on emit (presentation only; sources keep their bytes).
_SMART = {"“": '"', "”": '"', "‘": "'", "’": "'"}


def _straight_quotes(text: str) -> str:
    for k, v in _SMART.items():
        text = text.replace(k, v)
    return text


def _reader_clean(text: str) -> str:
    text = _SYNTH_NOTE.sub("", text)
    text = _INTERNAL_REF.sub("", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([.;,])", r"\1", text)
    return text.strip()


def compile_(ds: Dataset, subject: URIRef | None = None) -> str:
    g = ds.default_graph
    _ = subject
    terms = [t for t in g.subjects(RDF.type, SKOS_Concept) if isinstance(t, URIRef)]
    case = next((case_slug_of(str(p)) for p in g.subjects(RDF.type, ANT.Perspective)
                 if case_slug_of(str(p))), None)

    lines: list[str] = [f"# Glossary: {case}" if case else "# Glossary", ""]
    lines += [
        "Two vocabularies a reader may want to check, kept apart. First the "
        "**material-semiotics (Actor-Network Theory) terms** the reading is built "
        "from (actant, mediator, translation, and so on). Then any **load-bearing "
        "terms from other fields** the reading leans on. Every definition is taken "
        "faithfully from a cited source, never the ethnographer's own.",
        "",
    ]

    # --- Section 1: the method's own vocabulary (from the ontology) ----------
    lines += _ant_section(g)

    # --- Section 2: load-bearing terms from other fields (skos:Concept) ------
    lines += ["# Load-bearing terms from other fields", ""]
    if terms:
        lines += [
            "Terms that are **not** part of the ANT vocabulary but that the reading "
            "uses; *In this reading* notes how each word is used here.",
            "",
        ]
        buckets: dict[str, list[URIRef]] = {}
        for t in terms:
            cat = next((str(o) for o in g.objects(t, DCTERMS.subject)), "Other")
            buckets.setdefault(cat, []).append(t)
        for cat in sorted(buckets):
            lines += [f"## {cat}", ""]
            for t in sorted(buckets[cat], key=lambda x: label_of(g, x).lower()):
                acr = next((str(o) for o in g.objects(t, SKOS_altLabel)), None)
                head = f"**{label_of(g, t)}**" + (f" ({acr})" if acr else "")
                lines.append(f"{head}: {description_of(g, t)}")
                used = next((str(o) for o in g.objects(t, SKOS_scopeNote)), None)
                if used:
                    lines.append(f"*In this reading:* {used}")
                srcs = sorted(str(o) for o in g.objects(t, DCTERMS.source))
                if srcs:
                    lines.append("Sources: " + " · ".join(_linkify(s) for s in srcs))
                lines.append("")
    else:
        lines += [
            "_No external terms recorded. Author one with "
            "`ant new-record glossary-term` when the reading leans on a word from "
            "another field._",
            "",
        ]

    lines.append(see_also_footer(case, exclude=f"{case}-glossary.md" if case else None))
    return _straight_quotes("\n".join(lines))


def _ant_section(g) -> list[str]:
    """Render the ANT vocabulary this case actually uses, from the ontology
    (rdfs:comment for the definition, dcterms:source for the founding citation).
    No definitions are authored here."""
    from ant_rdf.graph import load_ontology

    onto = load_ontology().default_graph
    ant_ns = str(ANT)
    roles = {o for _, _, o in g.triples((None, ANT.assignsRole, None))
             if isinstance(o, URIRef) and str(o).startswith(ant_ns)}
    types = {o for _, _, o in g.triples((None, RDF.type, None))
             if isinstance(o, URIRef) and str(o).startswith(ant_ns)}

    def defined(t: URIRef) -> bool:
        return onto.value(t, RDFS.comment) is not None

    roles = sorted((t for t in roles if defined(t)), key=lambda t: label_of(onto, t).lower())
    concepts = sorted(
        (t for t in types - set(roles) if defined(t)), key=lambda t: label_of(onto, t).lower()
    )

    out = ["# Material semiotics (Actor-Network Theory) vocabulary", ""]
    if not (roles or concepts):
        return out + ["_No ANT terms in the loaded scope._", ""]
    out += [
        "The method's own terms, as this case uses them. Definitions are the "
        "ontology's; sources are the founding texts of the tradition.",
        "",
    ]

    def entry(t: URIRef) -> None:
        out.append(f"**{label_of(onto, t)}**: {_reader_clean(str(onto.value(t, RDFS.comment)))}")
        src = onto.value(t, DCTERMS.source)
        clean = _reader_clean(str(src)) if src else ""
        if clean:
            out.append(f"Source: {_linkify(clean)}")
        out.append("")

    if roles:
        out += ["## Roles a characterization can assign", ""]
        for t in roles:
            entry(t)
    if concepts:
        out += ["## Core concepts", ""]
        for t in concepts:
            entry(t)
    return out


def _linkify(src: str) -> str:
    m = _URL.search(src)
    if not m:
        return src
    url = m.group(1).rstrip(".,;")  # keep ')' — some glossary URLs end in "(glossary)"
    text = src[: m.start()].rstrip(" ,") or url
    return f"[{text}](<{url}>)"  # angle brackets: robust to parentheses in the URL
