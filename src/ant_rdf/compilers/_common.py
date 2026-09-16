# SPDX-License-Identifier: Apache-2.0
"""Shared helpers used across compilers."""

from __future__ import annotations

from collections.abc import Iterable

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS

from ant_rdf import ANT


def case_slug_of(iri: str) -> str | None:
    """Extract the case slug from a ``.../cases/<slug>/...`` IRI."""
    marker = "/cases/"
    if marker not in iri:
        return None
    return iri.split(marker, 1)[1].split("/", 1)[0].split("#", 1)[0] or None


def perspective_index(g: Graph) -> tuple[list[dict], dict[URIRef, URIRef]]:
    """Return ``(frames, practice_to_persp)`` for a whole-case graph.

    ``frames`` is a per-perspective list (sorted by IRI) of dicts with keys
    ``iri, slug, label, practices, network``. ``practice_to_persp`` maps EVERY
    grounding practice → its perspective IRI, so a perspective grounded in
    several practices is matched by all of them (a characterization made
    ``perPractice`` any of them lands in that frame). Only grounded
    perspectives are included (the auto-created ``_default`` stub drops out).
    """
    frames: list[dict] = []
    practice_to_persp: dict[URIRef, URIRef] = {}
    persps = sorted(
        p
        for p in g.subjects(RDF.type, ANT.Perspective)
        if isinstance(p, URIRef)
        and next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None) is not None
    )
    for p in persps:
        practices = sorted(
            pr for pr in g.objects(p, ANT.perspectiveGroundedIn) if isinstance(pr, URIRef)
        )
        for pr in practices:
            practice_to_persp[pr] = p
        slug = local_name(str(p))
        network = next(
            (
                s
                for s in sorted(g.subjects(RDF.type, ANT.Network))
                if isinstance(s, URIRef) and local_name(str(s)) == slug
            ),
            None,
        )
        frames.append(
            {"iri": p, "slug": slug, "label": label_of(g, p),
             "practices": practices, "network": network}
        )
    return frames, practice_to_persp


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


def frame_label(g: Graph, perspective: URIRef) -> str:
    """A compact human label for a perspective, for a table's Frame column:
    the perspective's rdfs:label trimmed at the first ' · ' (a convention for
    long qualifying tails), falling back to the IRI slug when unlabelled."""
    return label_of(g, perspective).split(" · ")[0].strip()


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
