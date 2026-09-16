# SPDX-License-Identifier: Apache-2.0
"""Negative controls for the Wave-2 shapes: each one must FIRE on the bad case
and stay quiet on the good case.

- Tier-2 ``TranslationFrameShape`` (ADR-0004): a Translation should carry
  exactly one ``ant:authoredUnder``.
- Tier-2 anchoring shapes: a Translation should anchor into the graph
  (``tracesToPassage`` or ``readsSameProgramAs``, either direction); a
  ProgramOfAction should be carried by an actant (inverse ``hasProgram``).

Fake content only (https://w3id.org/ant/test); nothing under instances/.
Mirrors run_verify's pyshacl call (advanced=False, direct typing — Callon
moment subclasses must NOT inherit the Translation targeting).
"""

from __future__ import annotations

from pyshacl import validate as _pyshacl_validate

from ant_rdf.graph import load_shapes
from ant_rdf.models import Actant, Problematization, ProgramOfAction, Translation
from ant_rdf.serialize import build_dataset

T = "https://w3id.org/ant/test"
P = f"{T}/perspectives/p"


def _warnings_for(*models) -> str:
    data = build_dataset(*models).default_graph
    shapes = load_shapes(("warnings",))
    _conforms, _report_g, report_text = _pyshacl_validate(
        data_graph=data, shacl_graph=shapes,
        ont_graph=None, inference="none", advanced=False,
    )
    return report_text


def test_translation_without_frame_warns_and_with_frame_does_not():
    bare = Translation(iri=f"{T}/translation/bare", label="Bare", description="d", case="test",
                       traces_to_passage=[f"{T}/actant/gate"])
    # Property-shape results report the blank node, not the named parent, so
    # assert on the message text.
    assert "ant:authoredUnder" in _warnings_for(bare)
    framed = Translation(iri=f"{T}/translation/framed", label="Framed", description="d",
                         case="test", authored_under=P, traces_to_passage=[f"{T}/actant/gate"])
    assert "ant:authoredUnder" not in _warnings_for(framed)


def test_unanchored_translation_warns():
    t = Translation(iri=f"{T}/translation/floating", label="Floating", description="d",
                    case="test", authored_under=P)
    assert "TranslationAnchoredShape" in _warnings_for(t)


def test_anchored_translation_does_not_warn_on_anchoring():
    t = Translation(iri=f"{T}/translation/wired", label="Wired", description="d",
                    case="test", authored_under=P, traces_to_passage=[f"{T}/actant/gate"])
    assert "TranslationAnchoredShape" not in _warnings_for(t)
    t2 = Translation(iri=f"{T}/translation/wired2", label="Wired2", description="d",
                     case="test", authored_under=P,
                     reads_same_program_as=[f"{T}/translation/other"])
    assert "TranslationAnchoredShape" not in _warnings_for(t2)


def test_incoming_reads_same_program_as_anchors_too():
    # ant:readsSameProgramAs is symmetric: a translation pointed AT by another
    # is anchored even when the edge is asserted from the other side only.
    pointer = Translation(iri=f"{T}/translation/pointer", label="Pointer",
                          description="d", case="test", authored_under=P,
                          traces_to_passage=[f"{T}/actant/gate"],
                          reads_same_program_as=[f"{T}/translation/pointee"])
    pointee = Translation(iri=f"{T}/translation/pointee", label="Pointee",
                          description="d", case="test", authored_under=P)
    assert "TranslationAnchoredShape" not in _warnings_for(pointer, pointee)


def test_moment_subclasses_are_exempt():
    # Direct typing only (run_verify uses advanced=False): a Problematization is
    # typed as its subclass, so the Translation-targeted shapes must not fire.
    m = Problematization(iri=f"{T}/moment/p1", label="P1", description="d", case="test")
    report = _warnings_for(m)
    assert "TranslationAnchoredShape" not in report
    assert "ant:authoredUnder" not in report


def test_uncarried_program_warns_and_carried_does_not():
    prog = ProgramOfAction(iri=f"{T}/program/floating", label="Floating prog",
                           description="d", case="test",
                           opposes=[f"{T}/translation/x"])
    assert "never standalone" in _warnings_for(prog)

    carrier = Actant(iri=f"{T}/actant/carrier", label="Carrier", description="d",
                     case="test", participates_in=[f"{T}/network/n"],
                     has_program=[f"{T}/program/carried"])
    carried = ProgramOfAction(iri=f"{T}/program/carried", label="Carried prog",
                              description="d", case="test")
    assert "never standalone" not in _warnings_for(carrier, carried)
