<!-- SPDX-License-Identifier: CC-BY-4.0 -->

---
name: ant-refresh
description: |
  Regenerate the compiled briefs (and optionally the wiki) so the rendered
  artifacts stay in sync with the graph. Use after any new-record /
  edit-record / remove-record / ingest --commit, or whenever a brief disagrees
  with the graph. Briefs are derived — never hand-edited; only recompiled.
---

# ant-refresh — regenerate the deliverable

You are helping keep the compiled **briefs** (and the wiki) in sync with the RDF graph. The files in `briefs/` are **derived** — rendered deterministically from the graph — so the same graph always yields the same brief. They are **never hand-edited**; when the graph changes, you recompile.

## When to run

- After any authoring step that wrote triples: `new-record`, `edit-record`, `remove-record`, or `ingest … --commit`.
- Whenever a brief disagrees with a fresh `ant query` (the briefs are stale, not wrong-by-hand).
- Before a reader trusts the briefs as current (e.g. before sharing, before opening a PR).

## The command

One command regenerates the whole canonical brief set for a case — every compiler in the registry that declares a refresh output (one network brief per perspective, the perspective comparison when the case has two or more frames) plus the cross-case catalog:

```bash
uv run ant refresh koi --verify --wiki
```

- `--verify` runs `ant verify` at the end (SHACL Tier-1 + Tier-2 + cross-refs) and fails if the graph does not conform.
- `--wiki` also regenerates `wiki/` (the whole-graph hyperlinked traversal; spans every case, unlike the per-case briefs).
- Omit both flags to just recompile the briefs.

What gets written follows one naming rule: a case whose only perspective is `_default` writes `briefs/<case>-network.md`; a case with named perspectives writes `briefs/<case>-<perspective>-network.md` for each, plus `briefs/<case>-comparison.md`. The catalog is always `briefs/case-catalog.md`. To see the plan without writing anything:

```bash
uv run python -c "from ant_rdf.compilers import refresh_plan; print(refresh_plan('koi'))"
```

Per-subject views (`ActantProfile`, `TranslationTrace`) are not part of a refresh; render those on demand with `ant compile`.

**Determinism check:** on an **unchanged** graph, `ant refresh <case>` leaves `briefs/` byte-identical (a clean `git diff`). A non-empty diff means the graph changed since the briefs were last built — which is exactly what you want to review and commit. CI enforces the same check for every case (`.github/workflows/compile.yml`).

## Critical rules

- **Never hand-edit a brief or a TTL.** Briefs come from `ant compile` / `ant refresh`; the graph changes only through the CLI (C7; see [CLAUDE.md](../../CLAUDE.md)). If you catch yourself editing a `.md` in `briefs/`, stop and recompile instead.
- **Refresh, then review, then commit.** Regenerate, read the rendered result, and only then commit — the ethnographer accepts the rendered artifact, not the raw triples.
- **Verify before you trust.** Run with `--verify` after any authoring change; do not present briefs as current if verify is failing.
- **The wiki spans all cases.** `--wiki` rebuilds the whole-graph wiki, not just this case — expect other cases' pages to move too.
