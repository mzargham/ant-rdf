# SPDX-License-Identifier: Apache-2.0
"""Shared helpers used across compilers."""

from __future__ import annotations

from collections.abc import Iterable

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDFS


def slugify(iri: str) -> str:
    """Filesystem-safe slug from an IRI's tail segment."""
    tail = iri.rstrip("/").rsplit("/", 1)[-1]
    if "#" in tail:
        tail = tail.rsplit("#", 1)[-1]
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in tail).strip("-") or "untitled"


def local_name(iri: str) -> str:
    """Human-readable last-segment of an IRI for in-text references."""
    tail = iri.rstrip("/").rsplit("/", 1)[-1]
    if "#" in tail:
        tail = tail.rsplit("#", 1)[-1]
    return tail


def one_literal(g: Graph, subject: URIRef, predicate: URIRef, default: str = "") -> str:
    """Pull a single literal property (returns ``default`` if not found)."""
    for obj in g.objects(subject, predicate):
        if isinstance(obj, Literal):
            return str(obj)
    return default


def label_of(g: Graph, subject: URIRef) -> str:
    """rdfs:label of a subject; falls back to local_name(iri)."""
    lit = one_literal(g, subject, RDFS.label, "")
    return lit or local_name(str(subject))


def description_of(g: Graph, subject: URIRef) -> str:
    return one_literal(g, subject, DCTERMS.description, "")


def many_iris(g: Graph, subject: URIRef, predicate: URIRef) -> list[URIRef]:
    """All IRI objects of a predicate, sorted for determinism."""
    return sorted(o for o in g.objects(subject, predicate) if isinstance(o, URIRef))


def md_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    """Render a GitHub-flavored markdown table.

    Each cell is escaped for ``|`` and newlines (replaced with space). The
    ``headers`` row defines column count; rows are zipped to fit.
    """
    sep = ["---"] * len(headers)
    materialized = [list(r) for r in rows]
    lines = [_join_row(headers), _join_row(sep)]
    for r in materialized:
        # Truncate/extend to header width
        cells = [_escape_cell(c) for c in r[: len(headers)]]
        while len(cells) < len(headers):
            cells.append("")
        lines.append(_join_row(cells))
    return "\n".join(lines) + "\n"


def _join_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _escape_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()
