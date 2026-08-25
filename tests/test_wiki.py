# SPDX-License-Identifier: Apache-2.0
"""Integration tests for the wiki generator (``ant_rdf.wiki``).

``run_wiki`` loads the real dataset (``load_full_dataset``), so these run
against the public cases committed in ``instances/``. Every run targets an
explicit ``output_dir`` under tmp so the repo's own ``wiki/`` is never
clobbered.

Guarantees exercised:

- **Key pages exist** — Home, a concept page, the canonical scallops case.
- **Link integrity** — every internal wiki link (a ``[text](Target)`` whose
  target is not an absolute URL or a fragment) must resolve to a produced
  page. This is what catches abstract.md links that survive flattening.
- **Determinism** — two independent runs produce byte-identical file sets and
  contents (the compile-and-diff CI gate relies on this).
"""

from __future__ import annotations

import re
from pathlib import Path

from ant_rdf.wiki import run_wiki

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _md_files(d: Path) -> set[str]:
    return {p.name for p in d.glob("*.md")}


def _internal_targets(text: str) -> list[str]:
    targets = []
    for tgt in _LINK_RE.findall(text):
        if tgt.startswith(("http://", "https://", "#")):
            continue
        targets.append(tgt.split("#", 1)[0])
    return targets


def test_key_pages_exist(tmp_path: Path) -> None:
    run_wiki(output_dir=str(tmp_path))
    files = _md_files(tmp_path)
    assert "Home.md" in files
    assert "Concept-Actant.md" in files
    assert "Case-scallops.md" in files


def test_link_integrity(tmp_path: Path) -> None:
    run_wiki(output_dir=str(tmp_path))
    files = _md_files(tmp_path)

    dangling: list[tuple[str, str]] = []
    for md in sorted(files):
        text = (tmp_path / md).read_text(encoding="utf-8")
        for tgt in _internal_targets(text):
            if f"{tgt}.md" not in files and tgt not in files:
                dangling.append((md, tgt))

    assert not dangling, f"dangling internal wiki links: {dangling}"


def test_determinism(tmp_path: Path) -> None:
    a = tmp_path / "run_a"
    b = tmp_path / "run_b"
    a.mkdir()
    b.mkdir()
    run_wiki(output_dir=str(a))
    run_wiki(output_dir=str(b))

    files_a = _md_files(a)
    files_b = _md_files(b)
    assert files_a == files_b

    for name in sorted(files_a):
        assert (a / name).read_bytes() == (b / name).read_bytes(), (
            f"non-deterministic content for {name}"
        )
