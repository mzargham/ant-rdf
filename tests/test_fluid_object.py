# SPDX-License-Identifier: Apache-2.0
"""ant:FluidObject (ADR-0005) and the actant→inscription edges
(``inscribes`` produces, ``drawsOn`` consumes, ``manifestsAs`` is-also; C9).

Fake content only (https://w3id.org/ant/test); nothing under instances/.
"""

from __future__ import annotations

from pyshacl import validate as _pyshacl_validate
from rdflib import URIRef
from rdflib.namespace import DCTERMS, RDF

from ant_rdf import ANT
from ant_rdf.edit_record import edit_record
from ant_rdf.graph import load_shapes, new_dataset
from ant_rdf.models import Actant, FluidObject, ImmutableMobile, Inscription
from ant_rdf.serialize import build_dataset, write_turtle

T = "https://w3id.org/ant/test"


def _reload(path):
    ds = new_dataset()
    ds.parse(path, format="turtle")
    return ds.default_graph


def _write(path, *objs):
    write_turtle(build_dataset(*objs), path)
    return path


def test_fluid_object_serializes_with_type_and_source(tmp_path):
    fo = FluidObject(
        iri=f"{T}/inscription/repo", label="Repo", description="a living repo",
        case="test", perspective="p", source="https://example.com/repo",
    )
    g = _reload(_write(tmp_path / "inscriptions.ttl", fo))
    s = URIRef(f"{T}/inscription/repo")
    assert (s, RDF.type, ANT.FluidObject) in g
    assert str(next(g.objects(s, DCTERMS.source))) == "https://example.com/repo"


def test_fluid_and_immutable_get_distinct_types(tmp_path):
    fo = FluidObject(iri=f"{T}/i/fo", label="FO", description="d", case="test", perspective="p")
    im = ImmutableMobile(iri=f"{T}/i/im", label="IM", description="d", case="test", perspective="p")
    g = _reload(_write(tmp_path / "inscriptions.ttl", fo, im))
    assert (URIRef(f"{T}/i/fo"), RDF.type, ANT.FluidObject) in g
    assert (URIRef(f"{T}/i/im"), RDF.type, ANT.ImmutableMobile) in g


def test_fluid_object_is_inscription_subclass():
    assert issubclass(FluidObject, Inscription)
    assert not issubclass(FluidObject, ImmutableMobile)


def test_inscription_source_shape_fires_on_subclasses_too():
    # ADR-0005 noted the Tier-2 InscriptionSourceShape missed ImmutableMobile /
    # FluidObject under direct typing; the targets are now listed explicitly.
    shapes = load_shapes(("warnings",))
    for cls in (Inscription, ImmutableMobile, FluidObject):
        data = build_dataset(cls(iri=f"{T}/i/x", label="X", description="d", case="test")).default_graph
        _c, _g, report = _pyshacl_validate(data_graph=data, shacl_graph=shapes,
                                           ont_graph=None, inference="none", advanced=False)
        assert "should have dcterms:source" in report, cls.__name__


def test_actant_inscribes_draws_on_and_manifests_as_are_distinct(tmp_path):
    a = Actant(
        iri=f"{T}/actant/stream", label="Stream", description="d",
        case="test", perspective="p", participates_in=[f"{T}/network/n"],
        inscribes=[f"{T}/i/made"], draws_on=[f"{T}/i/used-a", f"{T}/i/used-b"],
        manifests_as=[f"{T}/i/self"],
    )
    g = _reload(_write(tmp_path / "actants.ttl", a))
    s = URIRef(f"{T}/actant/stream")
    assert {str(o) for o in g.objects(s, ANT.inscribes)} == {f"{T}/i/made"}
    assert {str(o) for o in g.objects(s, ANT.drawsOn)} == {f"{T}/i/used-a", f"{T}/i/used-b"}
    assert {str(o) for o in g.objects(s, ANT.manifestsAs)} == {f"{T}/i/self"}


def test_edit_record_rewires_produce_to_consume(tmp_path):
    """The re-wire path: move a stream from inscribes (produce) to drawsOn (consume)."""
    a = Actant(iri=f"{T}/actant/s", label="S", description="d", case="test",
               perspective="p", participates_in=[f"{T}/network/n"], inscribes=[f"{T}/i/x"])
    p = _write(tmp_path / "actants.ttl", a)
    edit_record("actant", f"{T}/actant/s", {"draws_on": [f"{T}/i/x"], "inscribes": []}, target=p)
    g = _reload(p)
    s = URIRef(f"{T}/actant/s")
    assert list(g.objects(s, ANT.inscribes)) == []
    assert {str(o) for o in g.objects(s, ANT.drawsOn)} == {f"{T}/i/x"}


def test_inscribes_edit_equals_fresh_author(tmp_path):
    """Determinism invariant: editing inscribes → byte-identical to authoring fresh."""
    def mk(inscribes):
        return Actant(iri=f"{T}/actant/w", label="W", description="d", case="test",
                      perspective="p", participates_in=[f"{T}/network/n"], inscribes=inscribes)
    p = _write(tmp_path / "actants.ttl", mk([f"{T}/i/1"]))
    edit_record("actant", f"{T}/actant/w", {"inscribes": [f"{T}/i/2"]}, target=p)
    fresh = _write(tmp_path / "fresh.ttl", mk([f"{T}/i/2"]))
    assert p.read_bytes() == fresh.read_bytes()


def test_edit_inscription_class_to_fluid(tmp_path):
    im = ImmutableMobile(iri=f"{T}/i/paper", label="Paper", description="d",
                         case="test", perspective="p", source="old")
    p = _write(tmp_path / "inscriptions.ttl", im)
    edit_record("inscription", f"{T}/i/paper", {"class": str(ANT.FluidObject)}, target=p)
    assert list(_reload(p).objects(URIRef(f"{T}/i/paper"), RDF.type)) == [ANT.FluidObject]


def test_create_inscription_helper_types_and_sources(tmp_path):
    """Exercises the CLI authoring helper end-to-end."""
    import pytest

    from ant_rdf.new_record import create_inscription

    out = tmp_path / "inscriptions.ttl"
    create_inscription(
        iri=f"{T}/inscription/repo", label="Repo", description="a living repo",
        case="test", perspective="_shared", klass="ant:FluidObject",
        source="https://example.com/repo", out=str(out),
    )
    g = _reload(out)
    s = URIRef(f"{T}/inscription/repo")
    assert (s, RDF.type, ANT.FluidObject) in g
    assert str(next(g.objects(s, DCTERMS.source))) == "https://example.com/repo"
    with pytest.raises(ValueError):
        create_inscription(iri=f"{T}/i/bad", label="B", description="d", case="test",
                           perspective="_shared", klass="ant:Unicorn", out=str(out))


def test_translation_status_durability_and_frame_round_trip(tmp_path):
    from ant_rdf.models import Mobilization, Translation

    tr = Translation(iri=f"{T}/translation/t", label="T", description="d", case="test",
                     perspective="p", has_moment=[f"{T}/moment/m"],
                     has_status=str(ANT.Precarious), has_durability=str(ANT.StrategicDurability),
                     authored_under=f"{T}/perspectives/p", traces_to_passage=[f"{T}/actant/gate"])
    mob = Mobilization(iri=f"{T}/moment/m", label="M", description="d", case="test")
    p = _write(tmp_path / "translations.ttl", tr, mob)
    g = _reload(p)
    s = URIRef(f"{T}/translation/t")
    assert (s, ANT.hasStatus, ANT.Precarious) in g
    assert (s, ANT.hasDurability, ANT.StrategicDurability) in g
    assert (s, ANT.authoredUnder, URIRef(f"{T}/perspectives/p")) in g
    # --clear-status: the "forming / not yet assessed" state removes the triple
    edit_record("translation", str(s), {"has_status": ""}, target=p)
    g = _reload(p)
    assert list(g.objects(s, ANT.hasStatus)) == []
    assert list(g.objects(s, ANT.hasMoment)) == [URIRef(f"{T}/moment/m")]
