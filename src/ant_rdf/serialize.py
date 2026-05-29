# SPDX-License-Identifier: Apache-2.0
"""Pydantic models → RDF Dataset → deterministic Turtle.

Same model → byte-identical Turtle output (the determinism invariant from
RIME's D15). That's what lets CI diff-compare compiled artifacts against
their source.

The dispatch table at the bottom maps every Pydantic model class to its
``_add_*`` helper. Adding a new model requires (a) the model class,
(b) the ``_add_*`` helper, (c) the dispatch entry — all in the same commit
(atomicity rule per plan §4 RIME-inheritance).
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable

from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD

from ant_rdf import ANT
from ant_rdf.graph import new_dataset
from ant_rdf.models import (
    Actant,
    Analysis,
    AnalysisReport,
    AntModel,
    Characterization,
    ConstraintWaiver,
    Enrolment,
    ImmutableMobile,
    Inscription,
    Interessement,
    Mobilization,
    Network,
    Perspective,
    Practice,
    Problematization,
    ProgramOfAction,
    Scope,
    Translation,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _iri(value: str) -> URIRef:
    return URIRef(value)


def _ant(local: str) -> URIRef:
    return getattr(ANT, local)


def _lit(value: Any, datatype: URIRef | None = None) -> Literal:
    if isinstance(value, datetime):
        return Literal(value.isoformat(), datatype=XSD.dateTime)
    if isinstance(value, date):
        return Literal(value.isoformat(), datatype=XSD.date)
    return Literal(value, datatype=datatype)


def _add_base(g: Graph, subject: URIRef, obj: AntModel, class_iri: URIRef) -> None:
    """Add the rdf:type, rdfs:label, dcterms:description triples every record carries."""
    g.add((subject, RDF.type, class_iri))
    g.add((subject, RDFS.label, _lit(obj.label)))
    g.add((subject, DCTERMS.description, _lit(obj.description)))


# ---------------------------------------------------------------------------
# Per-class adders — alphabetical
# ---------------------------------------------------------------------------


def _add_actant(g: Graph, obj: Actant) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Actant"))
    for net_iri in sorted(obj.participates_in):
        g.add((s, _ant("participatesIn"), _iri(net_iri)))
    return s


def _add_analysis(g: Graph, obj: Analysis) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Analysis"))
    g.add((s, _ant("scopeIri"), _iri(obj.scope_iri)))
    g.add((s, _ant("analysisMethod"), _lit(obj.method)))
    if obj.query:
        g.add((s, _ant("analysisQuery"), _lit(obj.query)))
    if obj.results:
        g.add((s, _ant("analysisResults"), _lit(obj.results)))
    return s


def _add_analysis_report(g: Graph, obj: AnalysisReport) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("AnalysisReport"))
    g.add((s, _ant("scopeIri"), _iri(obj.scope_iri)))
    if obj.analysis_iri:
        g.add((s, _ant("analysisIri"), _iri(obj.analysis_iri)))
    if obj.network_iri:
        g.add((s, _ant("networkIri"), _iri(obj.network_iri)))
    return s


def _add_characterization(g: Graph, obj: Characterization) -> URIRef:
    s = _iri(obj.iri)
    g.add((s, RDF.type, _ant("Characterization")))
    g.add((s, _ant("characterizes"), _iri(obj.characterizes)))
    g.add((s, _ant("withinNetwork"), _iri(obj.within_network)))
    g.add((s, _ant("assignsRole"), _iri(obj.assigns_role)))
    if obj.per_practice:
        g.add((s, _ant("perPractice"), _iri(obj.per_practice)))
    if obj.invariance:
        g.add((s, _ant("invarianceCriterion"), _lit(obj.invariance)))
    if obj.description:
        g.add((s, DCTERMS.description, _lit(obj.description)))
    return s


def _add_constraint_waiver(g: Graph, obj: ConstraintWaiver) -> URIRef:
    s = _iri(obj.iri)
    g.add((s, RDF.type, _ant("ConstraintWaiver")))
    g.add((s, _ant("waivesShape"), _iri(obj.waives_shape)))
    g.add((s, _ant("waivesForTarget"), _iri(obj.waives_for_target)))
    g.add((s, _ant("waivedBy"), _iri(obj.waived_by)))
    g.add((s, DCTERMS.date, _lit(obj.date, datatype=XSD.date)))
    g.add((s, _ant("waiverJustification"), _lit(obj.justification)))
    if obj.expires:
        g.add((s, _ant("waiverExpires"), _lit(obj.expires, datatype=XSD.date)))
    return s


def _add_enrolment(g: Graph, obj: Enrolment) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Enrolment"))
    return s


def _add_immutable_mobile(g: Graph, obj: ImmutableMobile) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("ImmutableMobile"))
    if obj.source:
        g.add((s, DCTERMS.source, _lit(obj.source)))
    return s


def _add_inscription(g: Graph, obj: Inscription) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Inscription"))
    if obj.source:
        g.add((s, DCTERMS.source, _lit(obj.source)))
    return s


def _add_interessement(g: Graph, obj: Interessement) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Interessement"))
    return s


def _add_mobilization(g: Graph, obj: Mobilization) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Mobilization"))
    return s


def _add_network(g: Graph, obj: Network) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Network"))
    if obj.scope:
        g.add((s, _ant("scopeIri"), _iri(obj.scope)))
    if obj.from_construct:
        g.add((s, _ant("fromConstruct"), _lit(obj.from_construct)))
    return s


def _add_perspective(g: Graph, obj: Perspective) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Perspective"))
    g.add((s, _ant("perspectiveHeldBy"), _iri(obj.held_by)))
    for prac in sorted(obj.grounded_in):
        g.add((s, _ant("perspectiveGroundedIn"), _iri(prac)))
    for inv in sorted(obj.tracks_invariance):
        g.add((s, _ant("perspectiveTracksInvariance"), _lit(inv)))
    return s


def _add_practice(g: Graph, obj: Practice) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Practice"))
    return s


def _add_problematization(g: Graph, obj: Problematization) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Problematization"))
    return s


def _add_program_of_action(g: Graph, obj: ProgramOfAction) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("ProgramOfAction"))
    for opp in sorted(obj.opposes):
        g.add((s, _ant("opposes"), _iri(opp)))
    return s


def _add_scope(g: Graph, obj: Scope) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Scope"))
    for c in sorted(obj.cases):
        g.add((s, _ant("scopeCase"), _lit(c)))
    for p in sorted(obj.perspectives):
        g.add((s, _ant("scopePerspective"), _iri(p)))
    for f in sorted(obj.filters):
        g.add((s, _ant("scopeFilter"), _lit(f)))
    return s


def _add_translation(g: Graph, obj: Translation) -> URIRef:
    s = _iri(obj.iri)
    _add_base(g, s, obj, _ant("Translation"))
    for moment_iri in sorted(obj.has_moment):
        g.add((s, _ant("hasMoment"), _iri(moment_iri)))
    return s


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_DISPATCH: dict[type, Callable[[Graph, Any], URIRef]] = {
    Actant: _add_actant,
    Analysis: _add_analysis,
    AnalysisReport: _add_analysis_report,
    Characterization: _add_characterization,
    ConstraintWaiver: _add_constraint_waiver,
    Enrolment: _add_enrolment,
    ImmutableMobile: _add_immutable_mobile,
    Inscription: _add_inscription,
    Interessement: _add_interessement,
    Mobilization: _add_mobilization,
    Network: _add_network,
    Perspective: _add_perspective,
    Practice: _add_practice,
    Problematization: _add_problematization,
    ProgramOfAction: _add_program_of_action,
    Scope: _add_scope,
    Translation: _add_translation,
}


def add(graph_or_ds: Graph | Dataset, obj: Any) -> URIRef:
    """Dispatch on the model's class; add triples to the (default) graph."""
    cls = type(obj)
    adder = _DISPATCH.get(cls)
    if adder is None:
        raise TypeError(
            f"No serialize adder registered for {cls.__name__}. "
            f"Add a _add_{cls.__name__.lower()} helper and a dispatch entry."
        )
    g = graph_or_ds if isinstance(graph_or_ds, Graph) else graph_or_ds.default_graph
    return adder(g, obj)


def build_dataset(*objs: Any) -> Dataset:
    """Build a fresh Dataset with all given model instances added."""
    ds = new_dataset()
    for obj in objs:
        add(ds, obj)
    return ds


def write_turtle(ds: Dataset, path: Path) -> None:
    """Write the dataset's default graph to ``path`` as deterministic Turtle.

    rdflib's Turtle serializer has stable ordering when ``encoding='utf-8'``
    is used with a fresh graph; we further normalize line endings.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = ds.default_graph.serialize(format="turtle", encoding="utf-8")
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    # Normalize trailing whitespace + ensure single trailing newline.
    normalized = "\n".join(line.rstrip() for line in data.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8")
