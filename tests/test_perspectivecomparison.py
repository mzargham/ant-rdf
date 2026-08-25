# SPDX-License-Identifier: Apache-2.0
"""PerspectiveComparison: a perspective grounded in several practices owns
the characterizations made under any of them (not just the first)."""

from __future__ import annotations

from ant_rdf.compilers import perspectivecomparison
from ant_rdf.models import Actant, Characterization, Network, Perspective, Practice
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"
P = "https://w3id.org/ant/practices"
A = "https://w3id.org/ant#"


def _models():
    return [
        Practice(iri=f"{P}/pa", label="Practice A", description="a"),
        Practice(iri=f"{P}/pb", label="Practice B", description="b"),
        Practice(iri=f"{P}/pc", label="Practice C", description="c"),
        Perspective(iri=f"{T}/perspectives/alpha", label="Alpha frame", description="a",
                    held_by=f"{T}/agent/h", case="test", grounded_in=[f"{P}/pa"]),
        # beta is grounded in TWO practices; the characterization cites the second
        Perspective(iri=f"{T}/perspectives/beta", label="Beta frame", description="b",
                    held_by=f"{T}/agent/h", case="test", grounded_in=[f"{P}/pc", f"{P}/pb"]),
        Network(iri=f"{T}/network/alpha", label="Alpha net", description="a", case="test"),
        Network(iri=f"{T}/network/beta", label="Beta net", description="b", case="test"),
        Actant(iri=f"{T}/actant/x", label="Shared X", description="d", case="test",
               participates_in=[f"{T}/network/alpha", f"{T}/network/beta"]),
        Characterization(iri=f"{T}/char/x-a", characterizes=f"{T}/actant/x",
                         within_network=f"{T}/network/alpha", assigns_role=f"{A}Mediator",
                         per_practice=f"{P}/pa", case="test"),
        Characterization(iri=f"{T}/char/x-b", characterizes=f"{T}/actant/x",
                         within_network=f"{T}/network/beta", assigns_role=f"{A}Intermediary",
                         per_practice=f"{P}/pb", case="test"),
    ]


def test_second_grounding_practice_lands_in_its_frame_column():
    md = perspectivecomparison.compile_(build_dataset(*_models()))
    row = next(ln for ln in md.splitlines() if ln.startswith("| Shared X"))
    # both frames covered → a divergence verdict, not "single frame"
    assert "diverge" in row
    assert "single frame" not in row
    # nothing was misfiled as an extra lens
    assert "Readings beyond the grounding practices" not in md
    # the glance table lists both of beta's practices
    assert "pb · pc" in md or "pc · pb" in md
