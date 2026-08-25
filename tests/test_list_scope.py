# SPDX-License-Identifier: Apache-2.0
"""``ant list --case/--perspective`` scoping is a file-path fact, so it is
exercised against the public cases in ``instances/`` (read-only)."""

from __future__ import annotations

from rdflib import URIRef
from rdflib.namespace import RDF

from ant_rdf import ANT
from ant_rdf.verify import _scoped_data_dataset


def _subjects(ds, rdf_type):
    return {str(s) for s in ds.default_graph.subjects(RDF.type, rdf_type) if isinstance(s, URIRef)}


def test_case_scope_excludes_other_cases_but_keeps_shared():
    ds = _scoped_data_dataset("scallops", None)
    actants = _subjects(ds, ANT.Actant)
    assert actants and all("/cases/scallops/" in a for a in actants)
    assert not any("/cases/koi/" in a for a in actants)
    # shared reference (practices) still loads
    assert _subjects(ds, ANT.Practice)


def test_perspective_scope_excludes_sibling_frames():
    ds = _scoped_data_dataset("koi", "architectural")
    nets = _subjects(ds, ANT.Network)
    assert any(n.endswith("/architectural") for n in nets)
    assert not any(n.endswith("/ethnographic") for n in nets)


def test_no_scope_is_the_full_graph():
    full = _subjects(_scoped_data_dataset(None, None), ANT.Actant)
    assert any("/cases/koi/" in a for a in full)
    assert any("/cases/scallops/" in a for a in full)
