# SPDX-License-Identifier: Apache-2.0
"""Reader-oriented vantage points: PositionalityLedger, TensionsView,
ReadingGuide, Glossary, CaseSynopsis, plus the PerspectiveComparison
translations-by-frame section and the NetworkBrief positionality header.

Synthetic fixtures only (https://w3id.org/ant/cases/test); nothing under instances/.
"""

from __future__ import annotations

import re

from rdflib import URIRef

from ant_rdf.compilers import (
    casesynopsis,
    durabilitydashboard,
    glossary,
    networkbrief,
    perspectivecomparison,
    positionalityledger,
    readingguide,
    tensionsview,
)
from ant_rdf.models import (
    Actant,
    Agent,
    Characterization,
    GlossaryTerm,
    Mobilization,
    Network,
    Perspective,
    Practice,
    ProgramOfAction,
    Translation,
)
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"
P = "https://w3id.org/ant/practices"
AG = "https://w3id.org/ant/agent/holder"
A = "https://w3id.org/ant#"


def _case():
    return [
        Agent(iri=AG, label="Dr. Holder", description="the analyst"),
        Practice(iri=f"{P}/pa", label="Practice A", description="the A practice does A"),
        Practice(iri=f"{P}/pb", label="Practice B", description="the B practice does B"),
        Perspective(iri=f"{T}/perspectives/alpha", label="Alpha frame", description="alpha reads it",
                    held_by=AG, case="test", grounded_in=[f"{P}/pa"], tracks_invariance=["stays A"]),
        Perspective(iri=f"{T}/perspectives/beta", label="Beta frame", description="beta reads it",
                    held_by=AG, case="test", grounded_in=[f"{P}/pb"], tracks_invariance=["stays B"]),
        Network(iri=f"{T}/network/alpha", label="Alpha reading", description="the alpha reading", case="test"),
        Network(iri=f"{T}/network/beta", label="Beta reading", description="the beta reading", case="test"),
        Actant(iri=f"{T}/actant/x", label="Shared X", description="d", case="test",
               participates_in=[f"{T}/network/alpha", f"{T}/network/beta"]),
        Actant(iri=f"{T}/actant/y", label="Shared Y", description="d", case="test",
               participates_in=[f"{T}/network/alpha", f"{T}/network/beta"]),
        # x flips (Mediator / Intermediary); y agrees (Intermediary in both)
        Characterization(iri=f"{T}/char/x-a", characterizes=f"{T}/actant/x", within_network=f"{T}/network/alpha",
                         assigns_role=f"{A}Mediator", per_practice=f"{P}/pa", invariance="stays A",
                         case="test", description="x as mediator"),
        Characterization(iri=f"{T}/char/x-b", characterizes=f"{T}/actant/x", within_network=f"{T}/network/beta",
                         assigns_role=f"{A}Intermediary", per_practice=f"{P}/pb", invariance="stays B",
                         case="test", description="x as intermediary"),
        Characterization(iri=f"{T}/char/y-a", characterizes=f"{T}/actant/y", within_network=f"{T}/network/alpha",
                         assigns_role=f"{A}Intermediary", per_practice=f"{P}/pa", case="test"),
        Characterization(iri=f"{T}/char/y-b", characterizes=f"{T}/actant/y", within_network=f"{T}/network/beta",
                         assigns_role=f"{A}Intermediary", per_practice=f"{P}/pb", case="test"),
        Mobilization(iri=f"{T}/moment/m1", label="M1", description="m", case="test"),
        Mobilization(iri=f"{T}/moment/m2", label="M2", description="m", case="test"),
        Translation(iri=f"{T}/translation/ta", label="Program A", description="da", case="test",
                    has_moment=[f"{T}/moment/m1"], has_status=f"{A}Precarious",
                    authored_under=f"{T}/perspectives/alpha"),
        Translation(iri=f"{T}/translation/tb", label="Program B", description="db", case="test",
                    has_moment=[f"{T}/moment/m2"], has_status=f"{A}Stabilized",
                    authored_under=f"{T}/perspectives/beta"),
    ]


def test_positionality_ledger():
    md = positionalityledger.compile_(build_dataset(*_case()))
    assert "# Positionality ledger: test" in md
    assert "Dr. Holder" in md                       # holder label from the Agent record
    assert "the A practice does A" in md             # practice description rendered
    assert "1 network · 1 translations · 2 characterizations" in md
    assert "**See also:**" in md and "(test-positionality.md)" not in md  # hub excludes itself


def test_positionality_renders_internalizes():
    models = _case() + [
        Actant(iri=f"{T}/actant/persona-a", label="Persona A", description="d", case="test",
               participates_in=[f"{T}/network/alpha"], internalizes=[f"{T}/perspectives/alpha"]),
    ]
    md = positionalityledger.compile_(build_dataset(*models))
    assert "**Internalized by:**" in md and "Persona A" in md


def test_tensions_view():
    md = tensionsview.compile_(build_dataset(*_case()))
    assert "## Role flips" in md
    assert "Shared X" in md and "Mediator" in md and "Intermediary" in md
    assert "Shared Y" not in md.split("## Precarious")[0]  # agreement is not a flip
    assert "## Precarious & unravelling" in md
    fragile = md.split("Precarious & unravelling")[1].split("##")[0]
    assert "Program A" in fragile and "Program B" not in fragile


def test_tensions_renders_anti_programs_and_idle_opps():
    models = _case() + [
        ProgramOfAction(iri=f"{T}/program/anti", label="The counter-move", description="d",
                        case="test", opposes=[f"{T}/translation/ta"]),
        Actant(iri=f"{T}/actant/gate", label="Idle Gate", description="d", case="test",
               participates_in=[f"{T}/network/alpha"]),
        Characterization(iri=f"{T}/char/gate-opp", characterizes=f"{T}/actant/gate",
                         within_network=f"{T}/network/alpha", assigns_role=f"{A}ObligatoryPassagePoint",
                         per_practice=f"{P}/pa", case="test"),
    ]
    md = tensionsview.compile_(build_dataset(*models))
    assert "## Anti-programs" in md and "The counter-move" in md and "opposes" in md
    assert "Idle Gate" in md.split("## Bottlenecks")[1]


def test_reading_guide_links_only_what_refresh_compiles():
    md = readingguide.compile_(build_dataset(*_case()))
    assert "reading guide" in md.lower()
    for target in ("test-positionality.md", "test-synopsis.md", "test-alpha-network.md",
                   "test-beta-network.md", "test-comparison.md", "test-actants-across-frames.md",
                   "test-glossary.md", "case-catalog.md"):
        assert f"({target})" in md, target
    # a single-frame case gets no cross-frame links
    single = [m for m in _case() if not (isinstance(m, Perspective) and m.iri.endswith("beta"))]
    md1 = readingguide.compile_(build_dataset(*single))
    assert "comparison.md" not in md1 and "actants-across-frames" not in md1
    assert "(test-alpha-network.md)" in md1


def test_perspective_comparison_translations_by_frame_and_invariance():
    md = perspectivecomparison.compile_(build_dataset(*_case()))
    assert "## Translations, by frame" in md
    assert "Program A" in md and "Program B" in md and "Precarious" in md
    assert "Invariance tracked" in md and "stays A" in md
    assert "Dr. Holder" in md  # holder label, not slug
    assert "(test-comparison.md)" not in md and "(test-guide.md)" in md  # footer excludes itself


def test_durability_frame_column_is_labelled():
    md = durabilitydashboard.compile_(build_dataset(*_case()))
    assert "Alpha frame" in md and "Beta frame" in md


def test_glossary_sections():
    ds = build_dataset(*_case(), GlossaryTerm(
        iri="https://w3id.org/ant/glossary/verification", label="Verification",
        description="Objective evidence that a system meets its requirements.",
        acronym="V&V", used_as="the conformance side of the V&V.",
        category="Systems engineering & assurance",
        sources=["SEBoK: Verification, https://sebokwiki.org/wiki/Verification_(glossary)"],
    ))
    md = glossary.compile_(ds)
    assert "# Material semiotics (Actor-Network Theory) vocabulary" in md
    assert "## Roles a characterization can assign" in md
    assert "**Mediator" in md and "**Intermediary" in md and "TRANSFORMING" in md
    ant = md.split("# Load-bearing terms")[0]
    assert not re.search(r"per [RC]\d|See §|§\d|ADR-\d|Synthesized", ant)
    assert "## Systems engineering & assurance" in md
    assert "**Verification** (V&V)" in md
    assert "*In this reading:* the conformance side" in md
    assert "(<https://sebokwiki.org/wiki/Verification_(glossary)>)" in md


def test_glossary_without_external_terms_is_graceful():
    md = glossary.compile_(build_dataset(*_case()))
    assert "No external terms recorded" in md


def test_synopsis_flip_agreement_and_multi_practice():
    md = casesynopsis.compile_(build_dataset(*_case()))
    assert md.startswith("# Synopsis: test")
    flip = md.split("They flip")[1].split("They agree")[0]
    agree = md.split("They agree")[1]
    assert "Shared X" in flip and "Shared Y" in agree and "Shared Y" not in flip
    assert "Alpha reading | 2 | 2 |" in md  # actants read (x, y) · characterizations
    # a perspective grounded in two practices groups characterizations from either
    models = [m for m in _case() if not (isinstance(m, Perspective) and m.iri.endswith("beta"))]
    models += [
        Practice(iri=f"{P}/pc", label="Practice C", description="c"),
        Perspective(iri=f"{T}/perspectives/beta", label="Beta frame", description="b",
                    held_by=AG, case="test", grounded_in=[f"{P}/pc", f"{P}/pb"]),
    ]
    md2 = casesynopsis.compile_(build_dataset(*models))
    assert "pb · pc" in md2
    assert "Shared X" in md2.split("They flip")[1].split("They agree")[0]


def test_synopsis_no_grounded_perspectives():
    md = casesynopsis.compile_(build_dataset(
        Actant(iri=f"{T}/actant/lonely", label="Lonely", description="d", case="test")
    ))
    assert "No grounded perspectives" in md


def test_network_brief_positionality_header_and_footer():
    ds = build_dataset(*_case())
    md = networkbrief.compile_(ds, subject=URIRef(f"{T}/network/alpha"))
    assert "## Positionality" in md and "Dr. Holder" in md and "Practice A" in md
    assert "stays A" in md
    assert "**See also:**" in md
    # an ungrounded stub perspective gets neither header nor footer
    bare = build_dataset(
        Perspective(iri=f"{T}/perspectives/_default", label="stub", description="d",
                    held_by=AG, case="test"),
        Network(iri=f"{T}/network/_default", label="N", description="d", case="test"),
    )
    md2 = networkbrief.compile_(bare, subject=URIRef(f"{T}/network/_default"))
    assert "## Positionality" not in md2 and "See also" not in md2
