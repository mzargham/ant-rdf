# SPDX-License-Identifier: Apache-2.0
"""Tests for the InscriptionsBrief compiler (material carry-forward).

Synthetic fixtures only (https://w3id.org/ant/cases/test); nothing under instances/.
"""

from __future__ import annotations

from ant_rdf.compilers import inscriptionsbrief
from ant_rdf.models import Actant, FluidObject, ImmutableMobile
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"


def _fixtures():
    repo = FluidObject(iri=f"{T}/inscription/repo", label="Repo", description="a living repo",
                       case="test", perspective="_shared", source="https://example.com/repo")
    paper = ImmutableMobile(iri=f"{T}/inscription/paper", label="Paper", description="a fixed paper",
                            case="test", perspective="_shared", source="Author (2024). Paper.")
    worksite = Actant(iri=f"{T}/actant/worksite", label="Worksite", description="produced the repo",
                      case="test", participates_in=[f"{T}/network/n"],
                      inscribes=[f"{T}/inscription/repo", f"{T}/inscription/paper"])
    stream = Actant(iri=f"{T}/actant/stream", label="Stream", description="draws on both",
                    case="test", participates_in=[f"{T}/network/n"],
                    draws_on=[f"{T}/inscription/repo", f"{T}/inscription/paper"])
    platform = Actant(iri=f"{T}/actant/platform", label="Platform", description="repos live here",
                      case="test", participates_in=[f"{T}/network/n"],
                      manifests_as=[f"{T}/inscription/repo"])
    return build_dataset(repo, paper, worksite, stream, platform)


def test_brief_renders_types_counts_and_source():
    md = inscriptionsbrief.compile_(_fixtures())
    assert "# Inscriptions: test" in md
    assert "2 inscription(s)" in md
    assert "Fluid object" in md and "Immutable mobile" in md
    assert "https://example.com/repo" in md
    assert "unaltered" in md and "altered" in md  # the immutable/fluid variance note


def test_brief_splits_produce_from_consume_and_surfaces_manifests():
    md = inscriptionsbrief.compile_(_fixtures())
    assert "**Produced by:** Worksite" in md
    assert "**Drawn on by:** Stream" in md
    assert "What each consumer draws on" in md
    assert "Also an actant" in md and "Platform" in md


def test_empty_scope_is_graceful():
    assert "No inscriptions" in inscriptionsbrief.compile_(build_dataset())
