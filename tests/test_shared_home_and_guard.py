# SPDX-License-Identifier: Apache-2.0
"""ADR-0003: the frame-neutral shared home + the cross-frame identity guard.

- ``_shared`` routes actant identity to ``instances/cases/<case>/shared/`` (outside
  ``perspectives/``) and declares no ant:Perspective node.
- The Tier-1 ActantShape (sh:maxCount 1 on label/description) turns a drifted
  shared-actant identity into a hard error over the union graph.

Fake content only (https://w3id.org/ant/cases/test); nothing under instances/.
"""

from __future__ import annotations

from ant_rdf.new_record import (
    SHARED_PERSPECTIVE,
    _ensure_perspective_record,
    _file_for_kind,
    _perspective_dir,
)
from ant_rdf.verify import run_verify

ACTANT = """\
@prefix ant: <https://w3id.org/ant#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://w3id.org/ant/cases/test/actant/x> a ant:Actant ;
    rdfs:label "Shared X" ;
%s .
"""
ONE_DESC = '    dcterms:description "canonical identity"'
TWO_DESC = (
    '    dcterms:description "canonical identity" ;\n'
    '    dcterms:description "drifted identity"'
)


def test_shared_perspective_routes_outside_perspectives():
    d = _perspective_dir("acme", SHARED_PERSPECTIVE)
    assert d.name == "shared"
    assert "perspectives" not in d.parts  # → included in every frame-scoped compile
    f = _file_for_kind("acme", SHARED_PERSPECTIVE, "actant")
    assert f.parts[-3:] == ("acme", "shared", "actants.ttl")


def test_shared_home_declares_no_perspective():
    # The shared home is not an observer frame: no _perspective.ttl stub is
    # written (and nothing under instances/ is touched — the call is a no-op).
    _ensure_perspective_record("acme", SHARED_PERSPECTIVE)
    assert not (_perspective_dir("acme", SHARED_PERSPECTIVE)).exists()


def test_actant_identity_agreement_passes(tmp_path):
    p = tmp_path / "ok.ttl"
    p.write_text(ACTANT % ONE_DESC, encoding="utf-8")
    assert run_verify(graph=str(p)) == 0


def test_actant_identity_drift_fails(tmp_path):
    # Two divergent descriptions on one shared actant (the union-graph bleed)
    # is a Tier-1 violation: the guard fires, exit code is non-zero.
    p = tmp_path / "drift.ttl"
    p.write_text(ACTANT % TWO_DESC, encoding="utf-8")
    assert run_verify(graph=str(p)) != 0
