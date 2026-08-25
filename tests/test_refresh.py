# SPDX-License-Identifier: Apache-2.0
"""``ant refresh <case>`` reproduces exactly the committed briefs/ layout.

Runs in a tmp working directory so the repo's ``briefs/`` is never written;
the produced files must match the committed ones byte for byte (this pins
both the naming rule and compiler determinism against the public cases).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ant_rdf.compilers import refresh_case, refresh_plan
from ant_rdf.graph import REPO_ROOT

_READER = {"guide", "synopsis", "positionality", "opp-map", "inscriptions",
           "durability", "coverage", "tensions", "glossary"}
_CROSS = {"comparison", "actants-across-frames", "same-program-trace"}
EXPECTED = {
    # no grounded perspective → only the network brief + catalog
    "scallops": {"scallops-network.md", "case-catalog.md"},
    # one grounded frame → the reader set, no cross-frame views
    "pi-learning": {"pi-learning-network.md", "case-catalog.md"}
    | {f"pi-learning-{s}.md" for s in _READER},
    # two grounded frames → everything
    "koi": {"koi-architectural-network.md", "koi-ethnographic-network.md", "case-catalog.md"}
    | {f"koi-{s}.md" for s in _READER | _CROSS},
}


def test_refresh_plan_respects_frame_count_and_grounding():
    kinds = {k for k, _, _ in refresh_plan("scallops")}
    assert kinds == {"NetworkBrief", "CaseCatalog"}  # ungrounded: no reader views
    pi = {k for k, _, _ in refresh_plan("pi-learning")}
    assert "ReadingGuide" in pi and "PerspectiveComparison" not in pi
    assert {k for k, _, _ in refresh_plan("koi")} >= {"NetworkBrief", "PerspectiveComparison", "ActantAcrossFrames"}


@pytest.mark.parametrize("case", sorted(EXPECTED))
def test_refresh_reproduces_committed_briefs(case: str, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    refresh_case(case)
    produced = {p.name for p in (tmp_path / "briefs").glob("*.md")}
    assert produced == EXPECTED[case]
    for name in produced:
        committed = REPO_ROOT / "briefs" / name
        assert (tmp_path / "briefs" / name).read_bytes() == committed.read_bytes(), name
