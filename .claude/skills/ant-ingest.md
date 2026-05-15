<!-- SPDX-License-Identifier: CC-BY-4.0 -->

---
name: ant-ingest
description: |
  Note-and-upload ingestion for ant-rdf. Use when the ethnographer has
  existing material (markdown notes, transcripts, PDFs, photos) rather
  than starting from a blank conversation. Walks the dry-run + review-doc
  round-trip; never auto-commits triples.
---

# ant-ingest — note-and-upload skill

You are helping an ethnographer ingest **existing material** into the ant-rdf graph: structured notes (markdown), interview transcripts, raw uploads. The workflow is always: parse → propose candidates → write review document → human confirms → commit. **Never bypass the review document.**

## Two paths

### A. Structured notes (markdown with YAML frontmatter)

For each notes file:

1. Ask the ethnographer: "Which case does this belong to? Which perspective (default `_default`)?"
2. Check the file has a YAML frontmatter `ant:` block. The expected shape is:

   ```yaml
   ---
   ant:
     actants:
       - iri: https://w3id.org/ant/cases/<slug>/actant/<actant-slug>
         label: ...
         description: ...
         participates_in:
           - https://w3id.org/ant/cases/<slug>/network
     translations:
       - iri: ...
         label: ...
         description: ...
         has_moment:
           - ...
     characterizations:
       - iri: ...
         target: ...
         within_network: ...
         assigns_role: https://w3id.org/ant#<Role>
         per_practice: ...
         invariance: ...
         description: ...
   ---
   # Free-form prose follows — the YAML above is what gets ingested
   ```

3. If the file doesn't have the frontmatter yet, help the ethnographer add it. Use the same catechism instincts as [ant-mgmt](ant-mgmt.md) but translate the answers into YAML rather than running the CLI directly.

4. Run dry-run:
   ```bash
   uv run ant ingest notes <path/to/notes.md> --case <slug> --dry-run
   ```

5. Read the review document at `/tmp/ant-review-<stem>.md`. Walk through each candidate with the ethnographer. If they want changes, edit the notes file and re-run dry-run.

6. Only when the ethnographer **explicitly confirms** ("yes, commit these"), run:
   ```bash
   uv run ant ingest notes <path/to/notes.md> --case <slug> --commit
   ```

7. After commit, run `ant verify`, `ant compile`, `ant wiki` as in [ant-mgmt](ant-mgmt.md).

### B. Raw materials (PDFs, photos, audio)

For each raw material file:

1. Ask: "What case does this belong to?"
2. Run:
   ```bash
   uv run ant ingest upload <path/to/file> --case <slug>
   ```
3. The file is registered as an `ant:Inscription` with sha256-based provenance. The file itself stays at its original location; only the metadata TTL is written.
4. **Crucially:** characterization (assigning roles within a specific perspective) is a separate step. After registration, ask: "Would you like to characterize this inscription within a specific network and perspective now, or later?" If now, switch to the Characterization step in [ant-mgmt](ant-mgmt.md).

## Critical rules

- **Never bypass dry-run.** Always show the review document before committing. The dry-run is the seam where the ethnographer validates content per C7.
- **Never auto-extract from prose.** If the ethnographer's notes don't have the frontmatter, help them add it — don't try to NER-extract actants from free text in v1.
- **Uploads are perspective-agnostic.** Don't ask "what perspective does this PDF belong to?" — the PDF itself doesn't have a perspective; *characterizations of it* do.
- **Provenance per upload.** Every `ant:Inscription` from `ant ingest upload` carries its sha256 hash in `dcterms:source`. Don't strip that.

## When the ethnographer wants to mix paths

This is normal. A common pattern:

1. Upload the source paper as an Inscription
2. Ingest field notes that describe the network
3. Switch to ant-mgmt to characterize the Inscription within the network from a specific perspective

Just announce the path-switch ("Switching to the catechism for characterization") so the ethnographer knows what's happening.
