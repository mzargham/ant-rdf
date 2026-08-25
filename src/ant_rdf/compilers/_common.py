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


def network_for_perspective(g: Graph, p: URIRef) -> URIRef | None:
    """The ant:Network a perspective authors, by the repo convention
    ``perspectives/<x>`` ↔ ``network/<x>``; when no tail matches and the graph
    holds exactly one network (a single-frame case whose perspective is the
    ``_default`` stub), that network."""
    nets = sorted(s for s in g.subjects(RDF.type, ANT.Network) if isinstance(s, URIRef))
    slug = local_name(str(p))
    for n in nets:
        if local_name(str(n)) == slug:
            return n
    return nets[0] if len(nets) == 1 else None


def perspective_for_network(g: Graph, network: URIRef) -> URIRef | None:
    """Inverse of :func:`network_for_perspective`: tail match first, else the
    lone grounded perspective when the graph has exactly one."""
    persps = sorted(p for p in g.subjects(RDF.type, ANT.Perspective) if isinstance(p, URIRef))
    tail = local_name(str(network))
    for p in persps:
        if local_name(str(p)) == tail:
            return p
    grounded = [
        p for p in persps
        if next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None) is not None
    ]
    return grounded[0] if len(grounded) == 1 else None


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
        network = network_for_perspective(g, p)
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


def invariance_display(role: str, inv: str) -> str:
    """Render an ant:invarianceCriterion through its role (ADR-0006).

    The criterion names the invariant the characterization is about. The two
    roles hold it in structurally different ways: an Intermediary **passes it
    through** (transmits that dimension-set unchanged), whereas a Mediator
    **regulates to preserve** it — varies *other* dimensions in order to keep
    this invariant (requisite variety). Other roles show the criterion as is.
    """
    if not inv:
        return ""
    if role == "Mediator":
        return f"regulates to preserve: {inv}"
    if role == "Intermediary":
        return f"passes through: {inv}"
    return inv


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


# Navigation hubs a reader can always jump back to. A per-brief footer links to
# these so no brief is an island (the reading guide links everything in full).
# They are compiled by `ant refresh` for every case with a grounded perspective;
# a case without one gets no footer (see `see_also_footer`).
_FOOTER_HUBS = [
    ("guide.md", "Reading guide"),
    ("synopsis.md", "Synopsis"),
    ("positionality.md", "Positionality"),
    ("glossary.md", "Glossary"),
]


def has_grounded_perspective(g: Graph) -> bool:
    """Whether any ant:Perspective in the graph is grounded in a practice — the
    condition under which the reader-vantage briefs (and the hub footer) render."""
    return any(
        next(iter(g.objects(p, ANT.perspectiveGroundedIn)), None) is not None
        for p in g.subjects(RDF.type, ANT.Perspective)
    )


def see_also_footer(case: str | None, exclude: str | None = None, g: Graph | None = None) -> str:
    """A '---' + 'See also:' block linking to the orientation hubs.

    Links are relative to ``briefs/`` (all briefs live there) and named by the
    ``<case>-<suffix>.md`` convention `ant refresh` uses. ``exclude`` skips the
    current brief's own filename so a hub does not link to itself. When ``g``
    is given and has no grounded perspective, the hubs are not compiled for
    that case, so only the rule is emitted.
    """
    if not case or (g is not None and not has_grounded_perspective(g)):
        return "---\n"
    links = [
        f"[{title}]({case}-{suffix})"
        for suffix, title in _FOOTER_HUBS
        if f"{case}-{suffix}" != exclude
    ]
    return "---\n\n**See also:** " + " · ".join(links) + "\n"


def _join_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _escape_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()
