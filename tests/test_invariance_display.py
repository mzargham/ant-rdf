# SPDX-License-Identifier: Apache-2.0
"""ADR-0006: an invariance criterion is rendered through its role — the
criterion is the invariant in both cases; the role says how it is held."""

from __future__ import annotations

from ant_rdf.compilers import networkbrief
from ant_rdf.compilers._common import invariance_display
from ant_rdf.models import Actant, Characterization, Network
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"
A = "https://w3id.org/ant#"


def test_invariance_display_by_role():
    assert invariance_display("Mediator", "X") == "regulates to preserve: X"
    assert invariance_display("Intermediary", "X") == "passes through: X"
    assert invariance_display("ObligatoryPassagePoint", "X") == "X"
    assert invariance_display("Mediator", "") == ""


def test_network_brief_renders_role_aware_invariance():
    models = [
        Network(iri=f"{T}/network/n", label="N", description="d", case="test"),
        Actant(iri=f"{T}/actant/a", label="A", description="d", case="test",
               participates_in=[f"{T}/network/n"]),
        Characterization(iri=f"{T}/char/a-med", characterizes=f"{T}/actant/a",
                         within_network=f"{T}/network/n", assigns_role=f"{A}Mediator",
                         invariance="rhythm", case="test"),
        Characterization(iri=f"{T}/char/a-int", characterizes=f"{T}/actant/a",
                         within_network=f"{T}/network/n", assigns_role=f"{A}Intermediary",
                         invariance="substrate", case="test"),
    ]
    md = networkbrief.compile_(build_dataset(*models))
    assert "regulates to preserve: rhythm" in md
    assert "passes through: substrate" in md
