<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# CLAUDE.md — LLM workflow contract for ant-rdf

This file tells Claude (or any LLM agent) how to interact with this repository. It is the working contract between the model, the ethnographer, and the discipline of the docs-as-code paradigm. The repo's expectation: **assertions about the field come from humans; structural correctness comes from the CLI**.

Read [README.md](README.md) first for the architecture, [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md) for the philosophical premises (C1–C9), and [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md) for the foundational decisions (R1–R10) before authoring or modifying records.

## The golden path

```
natural-language description from ethnographer
  ↓ (Claude skill: ant-mgmt or ant-ingest)
ant CLI invocation (flag-driven or interactive)
  ↓ (serialize.py + new_record.py)
deterministic Turtle in instances/cases/<case>/perspectives/<slug>/
  ↓ (ant verify — SHACL tri-severity + cross-refs)
ant compile → Markdown brief in briefs/
ant wiki    → hyperlinked navigation in wiki/
  ↓ (human reviews the rendered artifacts)
ethnographer either accepts (commit) or requests revision
  ↓ (Claude re-invokes the CLI; never hand-edits the TTL)
```

**TTL is never hand-edited.** Every change goes through the CLI. The determinism invariant (same model → same TTL) is what lets us trust round-trips.

## What Claude is for, what Claude is not for

**Claude is for** — translating the ethnographer's plain-language description of a case (or notes file) into the precise CLI invocations that produce structurally correct RDF. Walking the catechism. Asking clarifying questions when the ethnographer's description doesn't determine a specific field. Generating dry-run review documents and waiting for confirmation.

**Claude is not for** — making ethnographic claims on the ethnographer's behalf. Auto-extracting actants from text without confirmation. Bypassing dry-run for `ant ingest notes`. Hand-editing TTL files. Choosing perspectives or invariances without explicit human input (these are observer-frame decisions, not technical ones).

## Authoring flow for a new case

1. **Ask the ethnographer:**
   - What is the case slug (kebab-case)?
   - What's the IRI base (typically `https://w3id.org/ant/cases/<slug>/`)?
   - Are we starting from a blank conversation, existing notes, or raw materials? *(Per C8 — offer the off-ramp.)*

2. **If conversational** — walk the [ant-mgmt skill](.claude/skills/ant-mgmt.md) catechism:
   - Network (label, narrative description)
   - Actants (resist asking "human or non-human?" — that pre-categorizes)
   - Translations + their moments (which of the four are visible? If fewer than four, plan a waiver naming the moment of failure)
   - Inscriptions / immutable mobiles
   - From whose practice are you describing this? (optional but encouraged — captures the observer-frame for any Characterization)
   - Where is the configuration holding (Material / Strategic / Discursive durability)?
   - What's contested or unraveling?

3. **If note-import** — switch to the [ant-ingest skill](.claude/skills/ant-ingest.md):
   - Help structure the ethnographer's existing notes into the YAML-frontmatter format `ant ingest notes` expects
   - Run dry-run first; show the generated `/tmp/ant-review-*.md`
   - Walk through each candidate; revise the notes file as needed
   - Commit only after the ethnographer confirms

4. **If upload** — register each raw material via `ant ingest upload`, then circle back to characterization (which is what the ethnographer actually has interpretive claims about — the upload alone is perspective-agnostic).

5. **After the records land:**
   - Run `ant verify`
   - Tier-1 violations: fix the data (not the shape, unless governance has decided otherwise)
   - Tier-2 warnings: either fix the data or run `ant waive add` with a justification the ethnographer explicitly supplies — never invent justifications
   - `ant refresh <case>` regenerates every brief the case supports (the network brief(s); for a case with a grounded perspective also the reader set — guide, synopsis, positionality, glossary, OPP map, inscriptions, durability, coverage, tensions; for two or more frames also comparison, actants-across-frames, same-program-trace); `ant wiki` to regenerate navigation
   - Show the ethnographer the brief; ask for revision in their words; loop

## Critical rules (these are not negotiable)

- **C7 (verification vs validation).** The CLI guarantees structural correctness. The ethnographer guarantees content correctness. Claude is the translator between natural language and CLI invocations — it does not arbitrate field truth.
- **R3 (Mediator/Intermediary observer-relative).** Never write `:x a ant:Mediator` as a direct typing on an actant — always go through `ant:Characterization` with explicit `per_practice` and `invariance_criterion`. If the ethnographer hasn't specified a practice, ask. If they decline to specify, record the Characterization without `per_practice` and let Tier-2 warn (the warning is the right outcome).
- **R6 (OPP as emergent attribute).** OPP is assigned via `ant:Characterization` with `assigns_role https://w3id.org/ant#ObligatoryPassagePoint`. Never as `:x a ant:ObligatoryPassagePoint` directly.
- **C8 (plural ingestion).** Offer the ingestion off-ramp at every step. Don't assume conversational is the right path.
- **R9 (provenance per term).** When adding new ontology terms, every term gets `dcterms:source`. No exceptions.
- **No `--no-verify` git commits.** No `git push --force`. No `gh issue close` unless the user explicitly requests. Standard Claude Code safety rules.

## Reading vs authoring

This file owns **authoring** (writing to the graph). [AGENTS.md](AGENTS.md) owns **reading** — how to route a question to the brief that answers it, the interpretive pitfalls (roles are not types; a reading is provenance), and the read-only `ant query` / `ant list` surface. Reach for AGENTS.md and the `ant-read` / `ant-query` skills when the ethnographer is asking *what the graph says*; reach for this file and `ant-mgmt` / `ant-ingest` when they want to *change* it. After any change, `ant refresh <case>` regenerates the briefs (the `ant-refresh` skill).

## Allowed commands

See [.claude/settings.json](.claude/settings.json) for the canonical allowlist. In brief:

- **Always allowed:** `ant verify`, `ant compile`, `ant refresh`, `ant list`, `ant query *`, `ant wiki`, `ant ontology validate`, `ant new-record *`, `ant edit-record *` (set-replaces only the fields you pass; byte-identical elsewhere), `ant ingest notes --dry-run`, `ant analyze list-methods`, `ant waive list`, `uv run pytest`, `uv run ruff`, `uv sync`, git read-only commands, `gh` read-only commands.
- **Allowed but use with care:** `ant ingest * --commit` (writes triples — but reversible via git), `ant waive add` (writes a waiver — should reflect an explicit ethnographer-supplied justification).
- **Require explicit confirmation:** `ant remove-record` (deletes a record; refuses while other records reference it unless `--force`), `git commit`, `git push`, `gh pr create`, file deletions in `instances/`, ontology edits in `ontology/`.
- **Stubs, not features:** `ant scope new` exists but raises `NotImplementedError` (v1.1); `ant ingest` has only `notes` and `upload`. Don't promise the ethnographer a command that isn't there.

## Verify

CI runs exactly these; run them locally before claiming anything is done:

```bash
uv run ant ontology validate
uv run ant verify                    # Tier-1 breaks; Tier-2 surfaces (R9b)
uv run ruff check src tests
uv run pytest -x
for c in instances/cases/*/; do uv run ant refresh "$(basename "$c")"; done
uv run ant wiki
git diff --quiet briefs/ wiki/       # determinism gate: regenerated == committed
```

If the last line fails, the briefs or wiki are stale: commit the regenerated artifacts alongside the change that moved them (never hand-edit them back).

## When the ethnographer asks a question Claude can't answer

Reach for the canonical case in [instances/cases/scallops/](instances/cases/scallops/) first — the Callon 1986 scallops example demonstrates every v1 commitment. Then ADR-0000, then ONTOLOGICAL_COMMITMENTS.md. If the question is about a term, the wiki concept page (`wiki/Concept-<term>.md`) carries the founding-text citation.

When in doubt about a design choice, name the relevant R-number (R1–R10) from ADR-0000 and ask the ethnographer whether the current resolution applies to their situation. Don't invent new resolutions.

## Memory and context

Claude's persistent memory should NOT include ethnographic claims about cases — those live in the RDF and the wiki, where the ethnographer owns them. Memory can include: this repo's paradigm (already in CLAUDE.md), the ethnographer's preferences for catechism style, recurring case-slug conventions the team uses. Memory should *not* include: which actants exist in which case (read the graph), which roles a Characterization assigns (read the Characterization), or what someone said about a specific translation (that's a field claim).
