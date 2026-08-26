<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# CLAUDE.md — LLM workflow contract for ant-rdf (authoring)

This file tells Claude (or any LLM agent) how to **write to** this repository. It is the working contract between the model, the ethnographer, and the docs-as-code discipline: **assertions about the field come from humans; structural correctness comes from the CLI.** Its companion [AGENTS.md](AGENTS.md) owns **reading** — routing a question to the brief that answers it and interpreting without misreading. The human-facing version of the practice is [docs/facilitation.md](docs/facilitation.md).

Read [docs/primer.md](docs/primer.md) for the concepts, [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md) for the premises (C1–C9), and [adr/README.md](adr/README.md) for the decisions (R1–R10 with R8a/R9a/R9b, and ADR-0001…0007) before authoring or modifying records.

## The golden path

```text
natural-language description from the ethnographer
  ↓ (skill: ant-mgmt, or ant-ingest for notes/uploads)
ant CLI invocation (new-record / edit-record / ingest)
  ↓ (serialize.py + new_record.py)
deterministic Turtle in instances/cases/<case>/…
  ↓ (ant verify — SHACL tri-severity + cross-refs)
ant refresh <case> → briefs/ ;  ant wiki → wiki/
  ↓ (the ethnographer reviews the rendered artifacts)
accept (commit records + regenerated artifacts together) or revise
  ↓ (Claude re-invokes the CLI; never hand-edits TTL or a brief)
```

**TTL, briefs and wiki are never hand-edited.** Every change goes through the CLI; the determinism invariant (same graph → same bytes) is what lets us trust round-trips, and `.claude/settings.json` denies direct edits to `instances/**/*.ttl`, `briefs/**`, `wiki/**`.

## What Claude is for, what Claude is not for

**For** — translating the ethnographer's plain-language description of a case (or notes file) into the precise CLI invocations that produce structurally correct RDF; walking the catechism; asking the clarifying question when a description does not determine a field; running the dry-run and waiting for confirmation.

**Not for** — making ethnographic claims on the ethnographer's behalf; auto-extracting actants from prose; bypassing the dry-run; hand-editing TTL; choosing perspectives, practices, invariances, statuses, passages or waiver justifications without explicit human input (these are observer-frame decisions, not technical ones).

## Skills

Each is a `.claude/skills/<name>/SKILL.md` and carries its own procedure and critical rules:

- **ant-mgmt** — the conversational catechism (prerequisites → network → actants → moments → translation → inscriptions → characterizations → contested), the definition-first routine for uncertain roles, the Tier-2 fix-or-waive conversation, the connectivity triage.
- **ant-ingest** — notes (`ant ingest notes`, format in [docs/notes-format.md](docs/notes-format.md)) and uploads; always dry-run first.
- **ant-gvrn** — ontology and shape changes; the atomicity rule; what to refuse.
- **ant-refresh**, **ant-read**, **ant-query** — the reading side (see AGENTS.md).

## Authoring flow for a new case

1. Ask the case slug, the IRI base (`https://w3id.org/ant/cases/<slug>/`), and — **per C8, offer the off-ramp** — whether we start from conversation, existing notes, or raw materials.
2. Author the reading's provenance first: agent → practice → perspective (`ant new-record agent / practice / perspective --grounded-in …`). A translation must be `--authored-under` a perspective (ADR-0004).
3. Walk the catechism (ant-mgmt) or the ingest path (ant-ingest).
4. `ant verify`: Tier-1 → fix the data; Tier-2 → the ethnographer fixes or waives with their own justification (never invent one); connectivity warnings → the ordered triage, never straight to a waiver.
5. `ant refresh <case> --wiki`; show the ethnographer the brief; take revisions in their words; loop.

## Critical rules (not negotiable)

- **C7.** The CLI guarantees structure; the ethnographer guarantees content. Claude translates; it does not arbitrate field truth.
- **R3.** Never `:x a ant:Mediator`. Roles go through `ant:Characterization` with explicit practice and invariance; if the ethnographer declines to specify a practice, record without it and let Tier-2 warn — the warning is the right outcome.
- **R6.** OPP is assigned via a Characterization with `assigns_role ant:ObligatoryPassagePoint`, never as a type.
- **ADR-0004.** Every translation is `--authored-under` a perspective.
- **C8.** Offer the ingestion off-ramp at every step.
- **R9.** A new ontology term gets `dcterms:source`, no exceptions; ontology edits require the maintainer's explicit confirmation.
- No `--no-verify` commits, no force-pushes, no closing issues unless asked.

## Permissions

`.claude/settings.json` is the canonical policy; in brief:

- **Run freely:** the read-only and derived-artifact commands (`ant verify / compile / refresh / list / query / wiki / ontology validate`, `new-record *`, `edit-record *`, `ingest notes --dry-run`, `waive list`, `pytest`, `ruff`), read-only git and `gh`.
- **Use with care:** `ant ingest … --commit` (only after the ethnographer confirms the review document); `ant waive add` (only with the ethnographer's own justification).
- **Ask first:** `ant remove-record`, `git commit`, `git push`, `gh pr create`, deleting anything under `instances/`, editing `ontology/`.
- **Denied:** direct `Edit`/`Write` on `instances/**/*.ttl`, `briefs/**`, `wiki/**`; destructive git.
- **Stubs:** `ant scope new` and `ant analyze list-methods` print a message and do nothing; `ant ingest` has only `notes` and `upload`. Do not promise the ethnographer a command that isn't there.

## Verify

CI runs exactly these (`verify.yml` the first four, `compile.yml` the rest); run them locally before claiming anything is done:

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

## When the ethnographer asks something Claude can't answer

Reach for the worked examples first — [docs/primer.md](docs/primer.md) reads the scallops case record by record (observer-relativity, R3); the koi case is the multi-perspective example. Then the concept page (`wiki/Concept-<Term>.md`, which carries the founding-text citation), then ADR-0000 and ONTOLOGICAL_COMMITMENTS.md. When in doubt about a design choice, name the relevant R-number or ADR and ask the ethnographer whether it applies; don't invent a new resolution.

## Memory

Claude's persistent memory must not hold ethnographic claims about cases — those live in the RDF and the briefs, where the ethnographer owns them. Memory may hold this repo's paradigm, the ethnographer's preferences for catechism style, and slug conventions; not which actants exist in which case, which roles a Characterization assigns, or what someone said about a translation.
