# SPDX-License-Identifier: Apache-2.0
"""ADR-0004: NetworkBrief reads a translation's frame from ``ant:authoredUnder``
so a whole-case compile no longer lists every frame's translation under one
network. Un-attributed translations are kept (backward-compatible)."""

from __future__ import annotations

from rdflib import URIRef

from ant_rdf.compilers import networkbrief
from ant_rdf.models import Mobilization, Network, Perspective, Translation
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"
AG = "https://w3id.org/ant/agent/x"


def _models():
    return [
        Perspective(iri=f"{T}/perspectives/alpha", label="Alpha", description="a", held_by=AG, case="test"),
        Perspective(iri=f"{T}/perspectives/beta", label="Beta", description="b", held_by=AG, case="test"),
        Network(iri=f"{T}/network/alpha", label="Alpha net", description="a", case="test"),
        Network(iri=f"{T}/network/beta", label="Beta net", description="b", case="test"),
        Mobilization(iri=f"{T}/moment/m", label="M", description="m", case="test"),
        Translation(iri=f"{T}/translation/alpha", label="Alpha reading", description="d",
                    case="test", has_moment=[f"{T}/moment/m"],
                    authored_under=f"{T}/perspectives/alpha"),
        Translation(iri=f"{T}/translation/beta", label="Beta reading", description="d",
                    case="test", has_moment=[f"{T}/moment/m"],
                    authored_under=f"{T}/perspectives/beta"),
        Translation(iri=f"{T}/translation/legacy", label="Legacy reading", description="d",
                    case="test", has_moment=[f"{T}/moment/m"]),
    ]


def test_whole_case_compile_scopes_translations_by_authored_under():
    ds = build_dataset(*_models())
    md = networkbrief.compile_(ds, subject=URIRef(f"{T}/network/alpha"))
    assert "### Alpha reading" in md
    assert "### Beta reading" not in md
    assert "### Legacy reading" in md  # un-attributed: kept


def test_default_perspective_keeps_its_translation():
    """Regression: a single-frame case whose perspective is the ``_default``
    stub (tail never equals the network slug) must still render its
    translation — the frame resolves to the lone perspective."""
    models = [
        Perspective(iri=f"{T}/perspectives/_default", label="stub", description="d",
                    held_by="https://w3id.org/ant/agent/_unspecified", case="test"),
        Network(iri=f"{T}/network", label="The net", description="d", case="test"),
        Mobilization(iri=f"{T}/moment/m", label="M", description="m", case="test"),
        Translation(iri=f"{T}/translation/main", label="The chain", description="d",
                    case="test", has_moment=[f"{T}/moment/m"],
                    authored_under=f"{T}/perspectives/_default"),
    ]
    md = networkbrief.compile_(build_dataset(*models), subject=URIRef(f"{T}/network"))
    assert "### The chain" in md
    assert "No translations recorded" not in md
