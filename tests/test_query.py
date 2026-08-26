# SPDX-License-Identifier: Apache-2.0
"""Tests for the read-only `ant query` graph queries (query.py).

Synthetic fixtures only (https://w3id.org/ant/cases/test); nothing under
instances/. Every role must surface *inside* its Characterization with the
frame that scopes it (R3/R6) — that fidelity is what these tests pin.
"""

from __future__ import annotations

import pytest

from ant_rdf.models import (
    Actant,
    Characterization,
    FluidObject,
    Mobilization,
    Network,
    Perspective,
    Practice,
    ProgramOfAction,
    Translation,
)
from ant_rdf.query import (
    QueryError,
    query_anti_programs,
    query_flips,
    query_manifests,
    query_roles,
    query_same_program,
    query_search,
    query_show,
    query_sparql,
    query_status,
    query_traffic,
    resolve,
)
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"
P = "https://w3id.org/ant/practices"
A = "https://w3id.org/ant#"


def _models(*, beta_practices: list[str] | None = None) -> list:
    return [
        Practice(iri=f"{P}/pa", label="Practice A", description="a"),
        Practice(iri=f"{P}/pb", label="Practice B", description="b"),
        Practice(iri=f"{P}/pc", label="Practice C", description="c"),
        Perspective(iri=f"{T}/perspectives/alpha", label="Alpha frame", description="a",
                    held_by=f"{T}/agent/h", case="test", grounded_in=[f"{P}/pa"],
                    tracks_invariance=["stays A"]),
        Perspective(iri=f"{T}/perspectives/beta", label="Beta frame", description="b",
                    held_by=f"{T}/agent/h", case="test",
                    grounded_in=beta_practices or [f"{P}/pb"],
                    tracks_invariance=["stays B"]),
        Network(iri=f"{T}/network/alpha", label="Alpha net", description="a", case="test", perspective="alpha"),
        Network(iri=f"{T}/network/beta", label="Beta net", description="b", case="test", perspective="beta"),
        # a flip: Mediator in alpha, Intermediary in beta
        Actant(iri=f"{T}/actant/x", label="Shared X", description="d", case="test",
               perspective="alpha", participates_in=[f"{T}/network/alpha", f"{T}/network/beta"]),
        Characterization(iri=f"{T}/char/x-a", characterizes=f"{T}/actant/x", within_network=f"{T}/network/alpha",
                         assigns_role=f"{A}Mediator", per_practice=f"{P}/pa", invariance="stays A",
                         case="test", perspective="alpha", description="x as mediator"),
        Characterization(iri=f"{T}/char/x-b", characterizes=f"{T}/actant/x", within_network=f"{T}/network/beta",
                         assigns_role=f"{A}Intermediary", per_practice=f"{P}/pb", invariance="stays B",
                         case="test", perspective="beta", description="x as intermediary"),
        Actant(iri=f"{T}/actant/gate", label="The Gate", description="a passage", case="test",
               perspective="alpha", participates_in=[f"{T}/network/alpha"]),
        Mobilization(iri=f"{T}/moment/m1", label="M1", description="m", case="test"),
        Translation(iri=f"{T}/translation/t1", label="Prog One", description="d1", case="test",
                    has_moment=[f"{T}/moment/m1"], has_status=f"{A}Precarious",
                    traces_to_passage=[f"{T}/actant/gate"], reads_same_program_as=[f"{T}/translation/t2"],
                    authored_under=f"{T}/perspectives/alpha"),
        Translation(iri=f"{T}/translation/t2", label="Prog Two", description="d2", case="test",
                    has_moment=[f"{T}/moment/m1"], has_status=f"{A}Stabilized",
                    authored_under=f"{T}/perspectives/beta"),
        Translation(iri=f"{T}/translation/t-forming", label="Prog Forming", description="d3", case="test",
                    has_moment=[f"{T}/moment/m1"], authored_under=f"{T}/perspectives/alpha"),
        ProgramOfAction(iri=f"{T}/program/anti", label="The Anti", description="opposes one",
                        case="test", opposes=[f"{T}/translation/t1"]),
        FluidObject(iri=f"{T}/inscription/repo", label="Living Repo", description="d", case="test"),
        Actant(iri=f"{T}/actant/platform", label="Platform", description="d", case="test",
               participates_in=[f"{T}/network/alpha"], manifests_as=[f"{T}/inscription/repo"]),
    ]


def _g(**kw):
    return build_dataset(*_models(**kw)).default_graph


def test_resolve_slug_and_iri():
    g = _g()
    assert resolve(g, "gate") == resolve(g, f"{T}/actant/gate")
    with pytest.raises(QueryError):
        resolve(g, "does-not-exist")


def test_roles_reports_each_characterization_with_frame_and_scope():
    g = _g()
    rows = query_roles(g, resolve(g, "x"))
    assert len(rows) == 2
    by_role = {r["role"]: r for r in rows}
    assert set(by_role) == {"Mediator", "Intermediary"}
    assert by_role["Mediator"]["frame"] == "Alpha frame"
    assert by_role["Mediator"]["invariance"] == "stays A"
    assert by_role["Mediator"]["characterization"] == "x-a"   # identity surfaced (disambiguates duplicates)
    assert by_role["Intermediary"]["network"] == "Beta net"


def test_roles_multi_practice_perspective():
    """A perspective grounded in two practices claims characterizations made
    under *either* (regression: only the first grounding practice used to map)."""
    g = _g(beta_practices=[f"{P}/pc", f"{P}/pb"])  # pb is the SECOND practice
    rows = query_roles(g, resolve(g, "x"))
    by_role = {r["role"]: r for r in rows}
    assert by_role["Intermediary"]["frame"] == "Beta frame"
    flips = query_flips(g)
    assert len(flips) == 1 and set(flips[0]["by_frame"]) == {"Alpha frame", "Beta frame"}


def test_flips_detects_cross_frame_divergence():
    g = _g()
    flips = query_flips(g)
    assert len(flips) == 1
    assert flips[0]["actant"] == "Shared X"
    assert set(flips[0]["by_frame"]) == {"Alpha frame", "Beta frame"}


def test_search_hits_labels_and_descriptions():
    g = _g()
    hits = {r["label"] for r in query_search(g, "passage")}   # in the Gate's description
    assert "The Gate" in hits
    hits2 = {r["label"] for r in query_search(g, "prog one")}  # in a label
    assert "Prog One" in hits2


def test_show_narrates_a_characterization():
    g = _g()
    d = query_show(g, resolve(g, "x-a"))
    assert d["type"] == "Characterization"
    assert "Shared X" in d["reading"] and "Mediator" in d["reading"] and "pa" in d["reading"]
    assert "stays A" in d["reading"]


def test_sparql_escape_hatch():
    g = _g()
    rows = query_sparql(
        g,
        "PREFIX ant: <https://w3id.org/ant#> "
        "SELECT ?c WHERE { ?c a ant:Characterization ; ant:assignsRole ant:Mediator }",
    )
    assert [r["c"] for r in rows] == [f"{T}/char/x-a"]


def test_traffic_lists_translations_clearing_a_passage():
    g = _g()
    rows = query_traffic(g, resolve(g, "gate"))
    assert [r["translation"] for r in rows] == ["Prog One"]
    assert rows[0]["via"] == "traces" and rows[0]["frame"] == "Alpha frame"


def test_status_including_forming_as_absent_status():
    g = _g()
    assert [r["translation"] for r in query_status(g, "precarious")] == ["Prog One"]
    assert [r["translation"] for r in query_status(g, "stabilized")] == ["Prog Two"]
    assert [r["translation"] for r in query_status(g, "forming")] == ["Prog Forming"]
    with pytest.raises(QueryError):
        query_status(g, "bogus")


def test_same_program_clusters_and_filter():
    g = _g()
    assert query_same_program(g) == [["Prog One", "Prog Two"]]
    assert query_same_program(g, resolve(g, "t1")) == [["Prog One", "Prog Two"]]


def test_anti_programs_and_manifests():
    g = _g()
    assert query_anti_programs(g) == [{"program": "The Anti", "opposes": "Prog One"}]
    assert query_manifests(g) == [
        {"actant": "Platform", "inscription": "Living Repo", "inscription_type": "FluidObject"}
    ]
