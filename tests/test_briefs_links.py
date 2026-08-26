# SPDX-License-Identifier: Apache-2.0
"""No brief is an island: every relative link inside the committed briefs/
resolves to a file in briefs/ (the hub footers and the reading guide link by
the `<case>-<suffix>.md` convention `ant refresh` writes)."""

from __future__ import annotations

import re

from ant_rdf.graph import REPO_ROOT

_LINK_RE = re.compile(r"\[[^\]]*\]\(<?([^)>\s]+)>?\)")


def test_every_relative_brief_link_resolves():
    briefs = REPO_ROOT / "briefs"
    names = {p.name for p in briefs.glob("*.md")}
    dangling = []
    for p in sorted(briefs.glob("*.md")):
        for tgt in _LINK_RE.findall(p.read_text(encoding="utf-8")):
            if tgt.startswith(("http://", "https://", "#")):
                continue
            if tgt.split("#", 1)[0] not in names:
                dangling.append((p.name, tgt))
    assert not dangling, f"dangling links in briefs/: {dangling}"
