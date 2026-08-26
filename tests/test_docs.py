# SPDX-License-Identifier: Apache-2.0
"""The documentation drift gate.

Iterative editing lets README, contracts, skills and reference docs fall
behind the tool. These checks pin the facts that drifted before:

1. every relative markdown link in the hand-written docs resolves;
2. every registered DocumentKind is documented in docs/toolchain.md;
3. every `ant` command and subcommand is documented in docs/toolchain.md;
4. no reference to a section of a plan that is not in the repo (`§n`,
   `.claude/plans`) survives in tracked md/py/ttl;
5. every skill is `.claude/skills/<name>/SKILL.md` with frontmatter first;
6. ONTOLOGICAL_COMMITMENTS.md's H1 count matches its `## C` headings;
7. every command in CLAUDE.md's Verify block is run by a workflow;
8. the generated CLI reference in docs/toolchain.md is current.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import click
import typer.main

from ant_rdf.cli import app
from ant_rdf.compilers import REGISTRY
from ant_rdf.graph import REPO_ROOT

_LINK_RE = re.compile(r"\[[^\]]*\]\(<?([^)>\s]*)>?\)")
_ROOT_DOCS = ["README.md", "AGENTS.md", "CLAUDE.md", "ONTOLOGICAL_COMMITMENTS.md",
              "FUTURE_WORK.md", "abstract.md", "LICENSE.md"]


def _docs() -> list[Path]:
    out = [REPO_ROOT / d for d in _ROOT_DOCS]
    out += sorted((REPO_ROOT / "adr").glob("*.md"))
    out += sorted((REPO_ROOT / "docs").glob("*.md"))
    out += sorted((REPO_ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    return [p for p in out if p.exists()]


def _resolves(src: Path, target: str) -> bool:
    target = target.split("#", 1)[0]
    if not target:
        return False  # an empty target `[x]()` is always a defect
    candidates = [src.parent / target]
    if src.name == "abstract.md":  # flattened into wiki/ by wiki.py
        candidates.append(REPO_ROOT / "wiki" / target)
    return any(c.resolve().exists() for c in candidates)


def test_relative_links_resolve():
    bad = []
    for doc in _docs():
        for tgt in _LINK_RE.findall(doc.read_text(encoding="utf-8")):
            if tgt.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not _resolves(doc, tgt):
                bad.append((str(doc.relative_to(REPO_ROOT)), tgt))
    assert not bad, f"dangling links: {bad}"


def test_every_document_kind_documented():
    text = (REPO_ROOT / "docs" / "toolchain.md").read_text(encoding="utf-8")
    missing = [k for k in REGISTRY if f"`{k}`" not in text]
    assert not missing, missing


def _commands(cmd: click.Command, path: str):
    if isinstance(cmd, click.Group):
        for name, sub in cmd.commands.items():
            yield from _commands(sub, f"{path} {name}")
    else:
        yield path


def test_every_cli_command_documented():
    text = (REPO_ROOT / "docs" / "toolchain.md").read_text(encoding="utf-8")
    missing = [p for p in _commands(typer.main.get_command(app), "ant") if f"`{p}`" not in text]
    assert not missing, missing


def _tracked(*globs: str) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "--", *globs], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.split("\n")
    return [REPO_ROOT / f for f in out if f]


def test_no_references_to_the_absent_plan():
    pat = re.compile(r"§\s*[0-9]|\.claude/plans")
    hits = []
    for f in _tracked("*.md", "*.py", "*.ttl"):
        if f.name == "test_docs.py":
            continue  # this file names the pattern it forbids
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if pat.search(line) and "\\u00a7" not in line:  # the glossary regex spells it escaped
                hits.append((str(f.relative_to(REPO_ROOT)), i))
    assert not hits, hits


def test_skills_are_directories_with_frontmatter_first():
    skills_dir = REPO_ROOT / ".claude" / "skills"
    flat = sorted(skills_dir.glob("*.md"))
    assert not flat, f"flat skill files are not discovered by Claude Code: {flat}"
    skills = sorted(skills_dir.glob("*/SKILL.md"))
    assert len(skills) >= 6
    bad = [s for s in skills if s.read_text(encoding="utf-8").splitlines()[0].strip() != "---"]
    assert not bad, f"frontmatter must start on line 1: {bad}"


def test_commitment_count_matches_h1():
    t = (REPO_ROOT / "ONTOLOGICAL_COMMITMENTS.md").read_text(encoding="utf-8")
    n = int(re.search(r"^# .*\(C1[–-]C(\d+)\)", t, re.M).group(1))
    assert len(re.findall(r"^## C\d+ ", t, re.M)) == n
    assert "eight explicit commitments" not in t


def test_claude_verify_block_matches_ci():
    t = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    block = re.search(r"## Verify.*?```bash\n(.*?)```", t, re.S).group(1)
    ci = re.sub(r"\s+", " ", "\n".join(
        p.read_text(encoding="utf-8") for p in (REPO_ROOT / ".github" / "workflows").glob("*.yml")
    ))
    missing = []
    for line in block.splitlines():
        for cmd in re.findall(r"uv run [^;#\"]+", line):
            if re.sub(r"\s+", " ", cmd.strip()) not in ci:
                missing.append(cmd.strip())
    assert not missing, missing
    assert "git diff --quiet briefs/ wiki/" in ci


def test_cli_reference_is_current():
    r = subprocess.run(
        ["uv", "run", "python", "tools/gen_cli_reference.py", "--check"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
