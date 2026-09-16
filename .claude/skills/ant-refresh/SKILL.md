---
name: ant-refresh
description: |
  Regenerate the compiled briefs (and optionally the wiki) so the rendered
  artifacts stay in sync with the graph. Use after any new-record /
  edit-record / remove-record / ingest --commit, whenever a brief disagrees
  with the graph, or before sharing or opening a PR. Briefs are derived —
  never hand-edited; only recompiled.
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-refresh — regenerate the deliverable

You are keeping the compiled **briefs** (and the wiki) in sync with the RDF graph. Files in `briefs/` and `wiki/` are **derived** — rendered deterministically from the graph, so the same graph always yields the same bytes. They are **never hand-edited**; when the graph changes, you recompile. Which briefs a case gets, and why, is in [docs/toolchain.md](../../../docs/toolchain.md) §"DocumentKinds".

## When to use

- After any authoring step that wrote triples (`new-record`, `edit-record`, `remove-record`, `ingest … --commit`).
- When a brief disagrees with `ant query` (the brief is stale, not wrong-by-hand).
- Before a reader trusts the briefs as current, and before a PR (CI enforces byte-identity).

## Procedure

```bash
uv run ant refresh <case> --plan             # what would be written; no files touched
uv run ant refresh <case> --verify --wiki    # regenerate + tri-severity check + wiki
```

- `--verify` runs `ant verify` at the end and fails if the graph does not conform.
- `--wiki` also regenerates `wiki/` — the whole-graph traversal, so other cases' pages may move too.

What gets written is decided by the case's perspectives:

- **Always:** one network brief per perspective (`briefs/<case>-network.md` for a lone `_default`; `briefs/<case>-<perspective>-network.md` otherwise) and the cross-case `briefs/case-catalog.md`.
- **If at least one perspective is grounded in a practice:** the reader set — `guide` (start here), `synopsis`, `positionality`, `glossary` (the four hubs every footer links), plus `opp-map`, `inscriptions`, `durability`, `coverage`, `tensions`.
- **If two or more perspectives:** the cross-frame views — `comparison`, `actants-across-frames`, `same-program-trace`.

Per-subject views (`ActantProfile`, `TranslationTrace`) are not part of a refresh; render them on demand with `ant compile <case> <Kind>`.

**Determinism check:** on an **unchanged** graph, `ant refresh <case>` leaves `briefs/` byte-identical (a clean `git diff`). A non-empty diff means the graph changed since the briefs were last built — which is exactly what to review and commit. CI runs the same check for every case (`.github/workflows/compile.yml`).

## Critical rules

- **Never hand-edit a brief or a TTL.** If you catch yourself editing a `.md` in `briefs/`, stop and recompile.
- **Refresh, then review, then commit.** The ethnographer accepts the rendered artifact, not the raw triples; regenerated briefs and wiki are committed together with the change that moved them.
- **Verify before you trust.** Do not present briefs as current if `verify` is failing.

## Handoffs

- Read and interpret the result → [ant-read](../ant-read/SKILL.md).
- The graph needs changing → [ant-mgmt](../ant-mgmt/SKILL.md).
