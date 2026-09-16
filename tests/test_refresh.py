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

EXPECTED = {
    "scallops": {"scallops-network.md", "case-catalog.md"},
    "koi": {
        "koi-architectural-network.md",
        "koi-ethnographic-network.md",
        "koi-comparison.md",
        "case-catalog.md",
    },
}


def test_refresh_plan_skips_comparison_for_single_frame_cases():
    kinds = {k for k, _, _ in refresh_plan("scallops")}
    assert "PerspectiveComparison" not in kinds
    assert {k for k, _, _ in refresh_plan("koi")} >= {"NetworkBrief", "PerspectiveComparison"}


@pytest.mark.parametrize("case", sorted(EXPECTED))
def test_refresh_reproduces_committed_briefs(case: str, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    refresh_case(case)
    produced = {p.name for p in (tmp_path / "briefs").glob("*.md")}
    assert produced == EXPECTED[case]
    for name in produced:
        committed = REPO_ROOT / "briefs" / name
        assert (tmp_path / "briefs" / name).read_bytes() == committed.read_bytes(), name
