---
name: ant-ingest
description: |
  Note-and-upload ingestion for ant-rdf. Use when the ethnographer has existing
  material — markdown notes with a YAML `ant:` block, or raw files (PDFs,
  photos, recordings) — rather than starting from a blank conversation. Walks
  the dry-run → review-document → confirm → commit round-trip; never
  auto-commits triples and never extracts records from free prose.
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-ingest — note-and-upload ingestion

You are helping an ethnographer bring **existing material** into the graph: structured notes (markdown with a YAML `ant:` block) or raw uploads. The workflow is always: parse → propose candidates → write the review document → the human confirms → commit. **Never bypass the review document.** The canonical notes format is [docs/notes-format.md](../../../docs/notes-format.md).

## When to use

- The ethnographer already has notes, a paper, a recording, a photo.
- The [ant-mgmt](../ant-mgmt/SKILL.md) off-ramp (C8) was taken with option (b) or (c).

## Procedure

### A. Structured notes (`ant ingest notes`)

1. Ask: "Which case does this belong to? Which perspective (default `_default`)?"
2. Check the file has a YAML frontmatter `ant:` block. Its shape — every block, every key name, and the six kinds ingest can commit (`networks`, `actants`, `translations`, `perspectives`, `characterizations`, `moments`, plus `inscriptions` and `programs`) — is specified in [docs/notes-format.md](../../../docs/notes-format.md). Key names are the `create_*` argument names (snake_case): `has_status` not `status`, `has_durability` not `durability`, `assigns_role`, `within_network`, `moment_kind`.
3. If the file has no frontmatter yet, help the ethnographer add it using the same catechism questions as ant-mgmt, translating answers into YAML instead of running the CLI. Practices, agents and glossary terms are not ingestable from notes — author them with `new-record practice` / `agent` / `glossary-term` first.
4. Dry-run:
   ```bash
   uv run ant ingest notes <path/to/notes.md> --case <slug> [--perspective <p>] --dry-run [--review-out <path>]
   ```
5. Read the review document (`/tmp/ant-review-<stem>.md` unless `--review-out`). Walk through each candidate with the ethnographer; to change anything, edit the notes file and re-run the dry-run.
   - **Role fit uncertain?** Run ant-mgmt's definition-first routine; hand the deciding question to the ethnographer rather than resolving it in the YAML.
   - **Connectivity check now, not later:** a candidate translation with no `traces_to_passage` / `reads_same_program_as`, or a candidate program no actant carries (`has_program`), will draw a Tier-2 warning after commit. Run ant-mgmt's connectivity triage on the candidate before it lands.
6. Only on an **explicit** "yes, commit these":
   ```bash
   uv run ant ingest notes <path/to/notes.md> --case <slug> --commit
   ```
7. Then `uv run ant refresh <slug> --verify --wiki` ([ant-refresh](../ant-refresh/SKILL.md)).

### B. Raw materials (`ant ingest upload`)

1. Ask: "Which case does this belong to?"
2. `uv run ant ingest upload <path/to/file> --case <slug> [--as ant:ImmutableMobile]`
3. The file is registered as an inscription with sha256 provenance in `dcterms:source`; the file itself stays where it is, only the metadata TTL is written under `instances/cases/<slug>/uploads/`.
4. **Characterization is a separate step.** Ask: "Characterize this now, within a network and perspective, or later?" If now, switch to ant-mgmt step 7.

> **Not a file? Use `new-record inscription`.** `ingest upload` is for uploaded files. Material that lives elsewhere and is cited by URL — a repository, a hosted service, a published paper — is authored with `ant new-record inscription --class {inscription|immutable|fluid} --source <url-or-citation>` (ant-mgmt step 6). Fluid objects (things that persist by mutation) belong on that path.

> **An inscription may later be recognized as an actant.** Registration is perspective-agnostic and does not preclude the trace also *acting* — a living repository is both. Record the coexistence with `edit-record actant --manifests-as <inscription-iri>` (C9, ADR-0007). Optional, never forced.

## Critical rules

- **Never bypass the dry-run.** The review document is the seam where the ethnographer validates content (C7).
- **Never auto-extract from prose.** If the notes lack the `ant:` block, help write it; do not NER-extract actants from free text.
- **Uploads are perspective-agnostic.** Do not ask which perspective a PDF belongs to; *characterizations of it* have perspectives.
- **Keep provenance.** Never strip the sha256 `dcterms:source` from an upload.
- **TTL is never hand-edited.**

## Handoffs

- Characterize what was ingested → [ant-mgmt](../ant-mgmt/SKILL.md) step 7.
- Regenerate briefs → [ant-refresh](../ant-refresh/SKILL.md).
- Mixing paths (upload the paper, ingest the notes, then characterize in conversation) is normal — announce each switch so the ethnographer knows what is happening.
