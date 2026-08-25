# SPDX-License-Identifier: Apache-2.0
"""Tests for in-place edit-record / remove-record (edit_record.py).

Fake content only (https://w3id.org/ant/test); nothing under instances/.
Operates on tmp files via the ``target=`` / ``scan=`` overrides so no case
directory is touched.
"""

from __future__ import annotations

import pytest
from rdflib import URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS

from ant_rdf import ANT
from ant_rdf.edit_record import (
    EditError,
    edit_record,
    find_referrers,
    remove_record,
)
from ant_rdf.graph import new_dataset
from ant_rdf.models import Actant, Characterization, ImmutableMobile, Inscription, ProgramOfAction
from ant_rdf.serialize import build_dataset, write_turtle

T = "https://w3id.org/ant/test"
Z = f"{T}/actant/z"


def _actant(slug: str, desc: str = "orig", nets: list[str] | None = None) -> Actant:
    return Actant(
        iri=f"{T}/actant/{slug}",
        label=slug.title(),
        description=desc,
        case="test",
        perspective="p",
        participates_in=nets or [f"{T}/network/n"],
    )


def _char(slug: str, target: str) -> Characterization:
    return Characterization(
        iri=f"{T}/char/{slug}",
        characterizes=target,
        within_network=f"{T}/network/n",
        assigns_role="https://w3id.org/ant#Mediator",
        case="test",
        perspective="p",
        description="d",
    )


def _write(path, *objs):
    ds = build_dataset(*objs)
    write_turtle(ds, path)
    return path


def _reload(path):
    ds = new_dataset()
    ds.parse(path, format="turtle")
    return ds.default_graph


def test_edit_replaces_only_provided_field(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z", "old desc", [f"{T}/network/exec"]))
    edit_record("actant", Z, {"description": "new desc"}, target=p)
    g = _reload(p)
    s = URIRef(Z)
    # description replaced (exactly one value, not appended)
    assert [str(d) for d in g.objects(s, DCTERMS.description)] == ["new desc"]
    # untouched fields survive
    assert str(next(g.objects(s, RDFS.label))) == "Z"
    assert str(next(g.objects(s, ANT.participatesIn))) == f"{T}/network/exec"


def test_edit_multivalue_set_replace(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z", "d", [f"{T}/network/a"]))
    edit_record(
        "actant", Z, {"participates_in": [f"{T}/network/a", f"{T}/network/b"]}, target=p
    )
    g = _reload(p)
    nets = {str(o) for o in g.objects(URIRef(Z), ANT.participatesIn)}
    assert nets == {f"{T}/network/a", f"{T}/network/b"}


def test_edit_empty_list_clears_multivalue_field(tmp_path):
    # The --clear-participates-in path: an empty list removes every edge.
    p = _write(tmp_path / "actants.ttl", _actant("z", "d", [f"{T}/network/a"]))
    edit_record("actant", Z, {"participates_in": []}, target=p)
    g = _reload(p)
    assert list(g.objects(URIRef(Z), ANT.participatesIn)) == []
    assert str(next(g.objects(URIRef(Z), RDFS.label))) == "Z"  # untouched field survives


def test_edit_program_label_desc_and_opposes(tmp_path):
    prog = ProgramOfAction(iri=f"{T}/program/anti", label="Old", description="old",
                           case="test", perspective="p", opposes=[f"{T}/translation/x"])
    p = _write(tmp_path / "programs.ttl", prog)
    edit_record("program", f"{T}/program/anti",
                {"label": "New", "description": "new", "opposes": [f"{T}/translation/y"]}, target=p)
    g = _reload(p)
    s = URIRef(f"{T}/program/anti")
    assert str(next(g.objects(s, RDFS.label))) == "New"
    assert [str(d) for d in g.objects(s, DCTERMS.description)] == ["new"]
    assert {str(o) for o in g.objects(s, ANT.opposes)} == {f"{T}/translation/y"}


def test_edit_inscription_source_label_and_class(tmp_path):
    # Editing --class set-replaces the single rdf:type; untouched fields survive.
    ins = ImmutableMobile(iri=f"{T}/inscription/paper", label="Paper", description="d",
                          case="test", perspective="p", source="Old citation")
    p = _write(tmp_path / "inscriptions.ttl", ins)
    edit_record(
        "inscription", f"{T}/inscription/paper",
        {"source": "New citation", "class": "https://w3id.org/ant#Inscription"}, target=p
    )
    g = _reload(p)
    s = URIRef(f"{T}/inscription/paper")
    assert [str(x) for x in g.objects(s, DCTERMS.source)] == ["New citation"]
    assert list(g.objects(s, RDF.type)) == [ANT.Inscription]
    assert str(next(g.objects(s, RDFS.label))) == "Paper"


def test_edit_inscription_equals_fresh_author(tmp_path):
    p = _write(tmp_path / "inscriptions.ttl",
               Inscription(iri=f"{T}/inscription/p", label="P", description="d",
                           case="test", perspective="p", source="old"))
    edit_record("inscription", f"{T}/inscription/p", {"source": "final"}, target=p)
    fresh = _write(tmp_path / "fresh.ttl",
                   Inscription(iri=f"{T}/inscription/p", label="P", description="d",
                               case="test", perspective="p", source="final"))
    assert p.read_bytes() == fresh.read_bytes()


def test_edit_equals_fresh_author(tmp_path):
    """Editing a field yields byte-identical output to authoring it fresh
    (the determinism invariant — same triple set → same Turtle)."""
    p = _write(tmp_path / "actants.ttl", _actant("z", "old", [f"{T}/network/n"]))
    edit_record("actant", Z, {"description": "final"}, target=p)
    fresh = _write(tmp_path / "fresh.ttl", _actant("z", "final", [f"{T}/network/n"]))
    assert p.read_bytes() == fresh.read_bytes()


def test_edit_is_idempotent(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z", "old"))
    edit_record("actant", Z, {"description": "changed"}, target=p)
    once = p.read_bytes()
    edit_record("actant", Z, {"description": "changed"}, target=p)
    assert p.read_bytes() == once


def test_edit_unknown_field_raises(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z"))
    with pytest.raises(EditError):
        edit_record("actant", Z, {"bogus": "x"}, target=p)


def test_edit_missing_subject_raises(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z"))
    with pytest.raises(EditError):
        edit_record("actant", f"{T}/actant/nope", {"description": "x"}, target=p)


def test_edit_unsupported_kind_raises(tmp_path):
    p = _write(tmp_path / "x.ttl", _actant("z"))
    with pytest.raises(EditError):
        edit_record("unicorn", Z, {"label": "x"}, target=p)


def test_find_referrers(tmp_path):
    ds = build_dataset(_actant("z"), _char("c", Z))
    refs = find_referrers(ds.default_graph, URIRef(Z))
    assert refs == [f"{T}/char/c"]
    # a subject with no inbound refs
    assert find_referrers(ds.default_graph, URIRef(f"{T}/char/c")) == []


def test_remove_refuses_when_referenced_then_force(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z"))
    scan = build_dataset(_actant("z"), _char("c", Z))
    with pytest.raises(EditError):
        remove_record(Z, case="test", perspective="p", target=p, scan=scan)
    # nothing removed yet
    assert (URIRef(Z), None, None) in _reload(p)
    # force removes and reports the danglers
    path, refs = remove_record(
        Z, case="test", perspective="p", target=p, scan=scan, force=True
    )
    assert refs == [f"{T}/char/c"]
    assert (URIRef(Z), None, None) not in _reload(path)


def test_remove_clean_no_refs(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z"))
    scan = build_dataset(_actant("z"))
    path, refs = remove_record(Z, case="test", perspective="p", target=p, scan=scan)
    assert refs == []
    assert (URIRef(Z), None, None) not in _reload(path)


def test_remove_missing_subject_raises(tmp_path):
    p = _write(tmp_path / "actants.ttl", _actant("z"))
    scan = build_dataset(_actant("z"))
    with pytest.raises(EditError):
        remove_record(f"{T}/actant/nope", case="test", perspective="p", target=p, scan=scan)
