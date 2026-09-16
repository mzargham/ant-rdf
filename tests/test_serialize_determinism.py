# SPDX-License-Identifier: Apache-2.0
"""The determinism invariant: same model → same Turtle, byte for byte.

The whole docs-as-code loop (compile-and-diff CI, edit-record round-trips,
reviewable git diffs) rests on ``write_turtle`` producing byte-stable output
regardless of how the triples were assembled. Fake content only.
"""

from __future__ import annotations

from _fixtures import core_models
from rdflib import Graph

from ant_rdf.serialize import build_dataset, write_turtle


def test_same_models_twice_are_byte_identical(tmp_path):
    a = tmp_path / "a.ttl"
    b = tmp_path / "b.ttl"
    write_turtle(build_dataset(*core_models()), a)
    write_turtle(build_dataset(*core_models()), b)
    assert a.read_bytes() == b.read_bytes()


def test_insertion_order_does_not_matter(tmp_path):
    a = tmp_path / "a.ttl"
    b = tmp_path / "b.ttl"
    write_turtle(build_dataset(*core_models()), a)
    write_turtle(build_dataset(*reversed(core_models())), b)
    assert a.read_bytes() == b.read_bytes()


def test_round_trip_is_isomorphic(tmp_path):
    src = build_dataset(*core_models())
    p = tmp_path / "rt.ttl"
    write_turtle(src, p)
    back = Graph()
    back.parse(p, format="turtle")
    assert set(back) == set(src.default_graph)
    # and re-serializing the parsed graph reproduces the same bytes
    from ant_rdf.graph import new_dataset

    ds = new_dataset()
    ds.parse(p, format="turtle")
    q = tmp_path / "rt2.ttl"
    write_turtle(ds, q)
    assert p.read_bytes() == q.read_bytes()
