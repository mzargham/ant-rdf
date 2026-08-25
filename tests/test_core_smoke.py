# SPDX-License-Identifier: Apache-2.0
"""Core-infrastructure smoke tests: a minimal fake graph verifies and compiles.

Fake content only (https://w3id.org/ant/test); nothing under instances/.
"""

from __future__ import annotations

from _fixtures import core_models

from ant_rdf.compilers import networkbrief
from ant_rdf.serialize import build_dataset, write_turtle
from ant_rdf.verify import run_verify


def test_core_graph_conforms(tmp_path):
    ds = build_dataset(*core_models())
    p = tmp_path / "core.ttl"
    write_turtle(ds, p)
    assert run_verify(graph=str(p)) == 0


def test_network_brief_renders():
    ds = build_dataset(*core_models())
    md = networkbrief.compile_(ds)
    assert md.startswith("# Network Brief")
    assert "Alice Example" in md
    assert "Widget Example" in md
    # all four Callon moments render in the translation table
    for moment in ("Problematization", "Interessement", "Enrolment", "Mobilization"):
        assert moment in md
