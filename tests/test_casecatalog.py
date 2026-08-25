# SPDX-License-Identifier: Apache-2.0
"""Tests for the CaseCatalog compiler — one row per case (not per network)."""

from __future__ import annotations

from ant_rdf.compilers import casecatalog
from ant_rdf.models import Actant, Network
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/cases/test"


def _one_case_two_networks():
    return [
        Network(iri=f"{T}/network/alpha", label="Alpha net", description="a",
                case="test", perspective="alpha"),
        Network(iri=f"{T}/network/beta", label="Beta net", description="b",
                case="test", perspective="beta"),
        Actant(iri=f"{T}/actant/x", label="X", description="d", case="test",
               perspective="alpha", participates_in=[f"{T}/network/alpha"]),
        Actant(iri=f"{T}/actant/y", label="Y", description="d", case="test",
               perspective="beta", participates_in=[f"{T}/network/beta"]),
    ]


def test_catalog_one_row_per_case_not_per_network():
    md = casecatalog.compile_(build_dataset(*_one_case_two_networks()))
    # exactly one table data row for the case, even though it has two networks
    data_rows = [ln for ln in md.splitlines() if ln.startswith("| test ")]
    assert len(data_rows) == 1
    # the row reports the networks *count* (2), not a single network name
    assert "| test | 2 |" in md
    # both networks are still named + described in the sections below
    assert "Alpha net" in md and "Beta net" in md
