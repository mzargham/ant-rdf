# SPDX-License-Identifier: Apache-2.0
"""Tests for the ADR-0002 cross-perspective compilers.

Synthetic fixtures only (https://w3id.org/ant/cases/test); nothing under instances/.
Since ADR-0004, SameProgramTrace / DurabilityDashboard derive a translation's frame from
the graph (ant:authoredUnder), not the filesystem — so these in-memory tests DO assert
frame labels.
"""

from __future__ import annotations

from rdflib import URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.compilers import (
    actantacrossframes,
    characterizationcoverage,
    durabilitydashboard,
    oppmap,
    sameprogramtrace,
)
from ant_rdf.models import (
    Actant,
    Characterization,
    FluidObject,
    Mobilization,
    Network,
    Perspective,
    Practice,
    Translation,
)
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"
P = "https://w3id.org/ant/practices"
AG = "https://w3id.org/ant/agent/x"
A = "https://w3id.org/ant#"


def _two_frames():
    return [
        Practice(iri=f"{P}/pa", label="Practice A", description="a"),
        Practice(iri=f"{P}/pb", label="Practice B", description="b"),
        Perspective(iri=f"{T}/perspectives/alpha", label="Alpha frame", description="a",
                    held_by=AG, case="test", grounded_in=[f"{P}/pa"], tracks_invariance=["inv a"]),
        Perspective(iri=f"{T}/perspectives/beta", label="Beta frame", description="b",
                    held_by=AG, case="test", grounded_in=[f"{P}/pb"], tracks_invariance=["inv b"]),
        Network(iri=f"{T}/network/alpha", label="Alpha net", description="a", case="test", perspective="alpha"),
        Network(iri=f"{T}/network/beta", label="Beta net", description="b", case="test", perspective="beta"),
    ]


def _char(slug, actant, net, role, prac, inv, desc="d"):
    return Characterization(iri=f"{T}/char/{slug}", characterizes=f"{T}/actant/{actant}",
                            within_network=f"{T}/network/{net}", assigns_role=f"{A}{role}",
                            per_practice=f"{P}/{prac}", invariance=inv, case="test", description=desc)


def test_actant_across_frames_detects_divergence():
    models = _two_frames() + [
        Actant(iri=f"{T}/actant/x", label="Shared X", description="d", case="test",
               participates_in=[f"{T}/network/alpha", f"{T}/network/beta"]),
        _char("x-a", "x", "alpha", "Mediator", "pa", "inv a", "x as mediator"),
        _char("x-b", "x", "beta", "Intermediary", "pb", "inv b", "x as intermediary"),
    ]
    md = actantacrossframes.compile_(build_dataset(*models))
    assert "# Actants across frames: test" in md
    assert "## Shared X" in md
    assert "Diverges" in md
    assert "regulates to preserve: inv a" in md and "passes through: inv b" in md


def test_actantacrossframes_single_frame_multirole_and_correspondsto():
    models = _two_frames() + [
        Actant(iri=f"{T}/actant/y", label="Solo Y", description="d", case="test",
               participates_in=[f"{T}/network/alpha"], corresponds_to=[f"{T}/actant/twin"]),
        Actant(iri=f"{T}/actant/twin", label="Twin", description="d", case="test",
               participates_in=[f"{T}/network/alpha"]),
        _char("y-med", "y", "alpha", "Mediator", "pa", "inv"),
        _char("y-spoke", "y", "alpha", "Spokesperson", "pa", "inv"),
    ]
    md = actantacrossframes.compile_(build_dataset(*models))
    solo = md.split("## Read in only one frame")[1]
    assert "Solo Y" in solo
    assert "Mediator" in solo and "Spokesperson" in solo  # both roles, not just the first
    assert "corresponds to Twin" in solo


def test_actantacrossframes_renders_manifests_as():
    models = _two_frames() + [
        FluidObject(iri=f"{T}/inscription/repo", label="Living Repo", description="d", case="test"),
        Actant(iri=f"{T}/actant/x", label="Shared X", description="d", case="test",
               participates_in=[f"{T}/network/alpha", f"{T}/network/beta"],
               manifests_as=[f"{T}/inscription/repo"]),
        _char("x-a", "x", "alpha", "Mediator", "pa", "inv a"),
        _char("x-b", "x", "beta", "Intermediary", "pb", "inv b"),
    ]
    md = actantacrossframes.compile_(build_dataset(*models))
    assert "Manifested as" in md and "Living Repo" in md


def test_characterization_coverage_splits_interpreted_from_bare():
    models = _two_frames() + [
        Actant(iri=f"{T}/actant/read", label="Read Actant", description="d", case="test",
               participates_in=[f"{T}/network/alpha"]),
        Actant(iri=f"{T}/actant/bare", label="Bare Actant", description="d", case="test",
               participates_in=[f"{T}/network/alpha"]),
        _char("read-a", "read", "alpha", "Mediator", "pa", "inv a"),
    ]
    md = characterizationcoverage.compile_(build_dataset(*models))
    assert "1 of 2 actants carry a characterization" in md
    assert "Read Actant" in md
    bare = md.split("## Bare actants")[1]
    assert "Bare Actant" in bare


def _one_frame_opp():
    return [
        Practice(iri=f"{P}/pa", label="Practice A", description="a"),
        Perspective(iri=f"{T}/perspectives/alpha", label="Alpha frame", description="a",
                    held_by=AG, case="test", grounded_in=[f"{P}/pa"], tracks_invariance=["inv"]),
        Network(iri=f"{T}/network/alpha", label="Alpha net", description="a", case="test"),
    ]


def test_oppmap_lists_passage_and_traffic():
    models = _one_frame_opp() + [
        Actant(iri=f"{T}/actant/gate", label="The Gate", description="d", case="test",
               participates_in=[f"{T}/network/alpha"]),
        _char("gate-opp", "gate", "alpha", "ObligatoryPassagePoint", "pa", "inv",
              "the passage all must clear"),
        Mobilization(iri=f"{T}/moment/m", label="M", description="m", case="test"),
        Translation(iri=f"{T}/translation/t", label="A commitment", description="d", case="test",
                    has_moment=[f"{T}/moment/m"], traces_to_passage=[f"{T}/actant/gate"]),
    ]
    md = oppmap.compile_(build_dataset(*models))
    assert "## The Gate" in md
    assert "the passage all must clear" in md
    assert "A commitment" in md  # traffic surfaced


def test_oppmap_notes_black_box_punctualization():
    models = _one_frame_opp() + [
        Actant(iri=f"{T}/actant/whole", label="The Whole", description="d", case="test",
               participates_in=[f"{T}/network/alpha"]),
        _char("whole-opp", "whole", "alpha", "ObligatoryPassagePoint", "pa", "inv"),
    ]
    ds = build_dataset(*models)
    ds.default_graph.add((URIRef(f"{T}/actant/whole"), RDF.type, ANT.BlackBox))
    assert "Also a black box" in oppmap.compile_(ds)


def test_oppmap_aggregates_traffic_across_twins():
    # Two OPPs that are the same passage (ant:correspondsTo) share their traffic:
    # a translation tracing to ONE twin shows on BOTH (tagged "via" on the other).
    models = _two_frames() + [
        Actant(iri=f"{T}/actant/gate-a", label="Gate A", description="d", case="test",
               participates_in=[f"{T}/network/alpha"], corresponds_to=[f"{T}/actant/gate-b"]),
        Actant(iri=f"{T}/actant/gate-b", label="Gate B", description="d", case="test",
               participates_in=[f"{T}/network/beta"], corresponds_to=[f"{T}/actant/gate-a"]),
        _char("gate-a-opp", "gate-a", "alpha", "ObligatoryPassagePoint", "pa", "inv a"),
        _char("gate-b-opp", "gate-b", "beta", "ObligatoryPassagePoint", "pb", "inv b"),
        Mobilization(iri=f"{T}/moment/m", label="M", description="m", case="test"),
        Translation(iri=f"{T}/translation/t", label="Only flow", description="d", case="test",
                    has_moment=[f"{T}/moment/m"], traces_to_passage=[f"{T}/actant/gate-a"]),
    ]
    md = oppmap.compile_(build_dataset(*models))
    assert "**Corresponds to**" in md and "Gate B (Beta frame)" in md
    gate_b = md.split("## Gate B")[1].split("## ")[0]
    assert "Only flow" in gate_b and "via Gate A" in gate_b
    assert "No traffic recorded" not in gate_b


def test_sameprogramtrace_clusters_linked_translations():
    models = [
        Mobilization(iri=f"{T}/moment/m1", label="M1", description="mob one", case="test"),
        Mobilization(iri=f"{T}/moment/m2", label="M2", description="mob two", case="test"),
        Translation(iri=f"{T}/translation/a", label="Prog A", description="da", case="test",
                    has_moment=[f"{T}/moment/m1"], reads_same_program_as=[f"{T}/translation/b"],
                    has_status=f"{A}Precarious", authored_under=f"{T}/perspectives/alpha"),
        Translation(iri=f"{T}/translation/b", label="Prog B", description="db", case="test",
                    has_moment=[f"{T}/moment/m2"], reads_same_program_as=[f"{T}/translation/a"],
                    has_status=f"{A}Stabilized", authored_under=f"{T}/perspectives/beta"),
    ]
    md = sameprogramtrace.compile_(build_dataset(*models))
    assert "1 program(s)" in md
    assert "Prog A" in md and "Prog B" in md
    assert "mob one" in md  # Mobilization moment surfaced
    assert "alpha" in md and "beta" in md  # frame from ant:authoredUnder
    assert "different **statuses**" in md


def test_durabilitydashboard_buckets_by_status_including_forming():
    models = [
        Mobilization(iri=f"{T}/moment/m1", label="M1", description="m", case="test"),
        Translation(iri=f"{T}/translation/a", label="Stable one", description="d", case="test",
                    has_moment=[f"{T}/moment/m1"], has_status=f"{A}Stabilized",
                    has_durability=f"{A}StrategicDurability", authored_under=f"{T}/perspectives/alpha"),
        Translation(iri=f"{T}/translation/b", label="Shaky one", description="d", case="test",
                    has_moment=[f"{T}/moment/m1"], has_status=f"{A}Precarious",
                    authored_under=f"{T}/perspectives/beta"),
        Translation(iri=f"{T}/translation/c", label="Forming one", description="d", case="test",
                    has_moment=[f"{T}/moment/m1"], authored_under=f"{T}/perspectives/alpha"),
        Translation(iri=f"{T}/translation/d", label="Momentless one", description="d", case="test",
                    has_status=f"{A}Unravelled", authored_under=f"{T}/perspectives/alpha"),
    ]
    md = durabilitydashboard.compile_(build_dataset(*models))
    assert "4 translation(s)" in md
    assert "## Stabilized (1)" in md and "## Precarious (1)" in md and "## Unravelled (1)" in md
    assert "## Forming / not yet assessed (1)" in md and "Forming: 1" in md
    assert "StrategicDurability" in md
    assert "Momentless one" in md  # not filtered by moment presence
