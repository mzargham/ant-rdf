<!-- SPDX-License-Identifier: CC-BY-4.0 -->

---
name: ant-gvrn
description: |
  Ontology governance for ant-rdf. Use when a contributor wants to add,
  modify, or remove terms in the ontology (material-semiotics-core.ttl,
  alignment modules, SHACL shapes), or when reconciling SHACL warnings
  via constraint waivers. Enforces atomicity: every OWL change has a
  matching Pydantic model and serialize-dispatch update.
---

# ant-gvrn — ontology governance skill

You are helping a contributor change the ontology, the alignment modules, or the SHACL shapes — or recording a constraint waiver. **Ontology changes are high-stakes** because they change the contract every existing record was authored against. Before touching `ontology/*.ttl`, confirm the change is necessary and walk the atomicity checklist.

## Pre-action checklist (every ontology change)

1. **State the change in one sentence** for the contributor to confirm before any file edit.

   Example: "Adding `ant:Controversy` as a class subclassing `ant:Network`, with `ant:contestedTranslation` linking it to the translation that broke."

2. **Run `git diff ontology/`** so the contributor (and you) sees the actual proposed change, not a summary.

3. **Run `uv run ant ontology validate`** to confirm the ontology + alignment + shapes parse together.

4. **Run `uv run ant verify` against existing instances** to confirm the change doesn't break existing records. If it does (e.g., new Tier-1 shape that existing data fails), discuss with the contributor whether the existing data is at fault or the shape is too strict.

5. **Atomicity rule (per RIME inheritance).** Every OWL class change implies a matching Pydantic model change AND a `serialize.py` dispatch update. All three live in the same commit:
   - Add the OWL class in `ontology/material-semiotics-core.ttl`
   - Add the Pydantic model in `src/ant_rdf/models.py`
   - Add the `_add_*` helper and dispatch entry in `src/ant_rdf/serialize.py`
   - Add a `new_record.create_*` function and CLI subcommand if user-authored

6. **Add `dcterms:source`** to every new term (per R9). If the term is synthesized rather than from a founding text, source it as "Synthesized per plan §X.Y" or to the specific ADR.

7. **Update `ONTOLOGICAL_COMMITMENTS.md` and/or `adr/0000-foundational-decisions.md`** if the change touches an existing commitment or resolved decision.

## SHACL shape changes

Adding or modifying SHACL shapes is governance — these change what the CLI considers a violation or warning.

- **New Tier-1 (sh:Violation) shape:** very high bar. The shape must encode something that breaks downstream tooling. Discuss with the contributor whether the constraint is *structural* (Tier-1) or *analytical hygiene* (Tier-2).
- **New Tier-2 (sh:Warning) shape:** medium bar. The shape encodes "should-conform" intuition. Be sure to put `sh:severity sh:Warning` on each property shape (pyshacl doesn't propagate from NodeShape — see verify.py implementation note).
- **New Tier-3 (sh:Info) shape:** low bar. Lint-style; only surfaces with `--lint`. Should self-target ontology terms or use restrictive patterns to avoid firing on instance data.
- After any shape change, run `uv run ant verify` and check that existing instances either still conform or that any new violations represent real data issues to fix.

## Constraint waivers (Tier-2 only)

If `ant verify` surfaces a Tier-2 warning a contributor wants to acknowledge:

1. Confirm with the contributor: **what is the justification, in their own words?** Do not invent.
2. Run:
   ```bash
   uv run ant waive add <shape-iri> <target-iri> \
       --by <prov-agent-iri> \
       --justification "<verbatim from contributor>"
   ```
3. The waiver is written to `instances/waivers/<date>-<slug>.ttl` (append-only, per §4.6).
4. Tier-1 (sh:Violation) waivers are **rejected by `ant verify`**. If the contributor tries to waive a structural violation, explain that structural integrity is not waivable — fix the data instead. If the data is correct and the shape is wrong, that's an ontology change (back to the checklist above).

## Cross-graph reference resolution

The custom `_check_crossrefs` in `verify.py` flags dangling IRIs in `ant:` cross-reference properties (e.g., `ant:participatesIn` pointing at a Network that doesn't exist anywhere in the loaded graph). This is **always a Tier-1 violation** (cannot be waived). To fix:

- Either: add the missing record (most common — typo or genuinely missing data)
- Or: edit the source TTL to remove the dangling reference

## What to refuse

- **Bypass `--no-verify` on git commit.** Ontology changes go through CI; don't suggest workarounds.
- **Disjointness assertions on the role classes.** `ant:Mediator` and `ant:Intermediary` are NOT `owl:disjointWith` — they are simultaneously assignable via different Characterizations under different practices (R3). The same applies to `ant:ProvAgent` / `ant:ProvInfluencer`.
- **Subclass `ant:Actant` under `prov:Agent`.** Never. Per R2, that typing is observer-relative and assigned via Characterization, not globally.
- **Subclasses splitting Actant by human/non-human.** Refuse. C2 generalized symmetry forbids exactly that asymmetry.
- **AIME modes-of-existence in v1.** Per R7, deferred to v2 extension module `ant-aime.ttl`.

## Reviewing a contributor's proposed ontology PR

When asked to review changes to `ontology/`:

1. Walk the checklist above.
2. Spot-check: does every new term have `dcterms:source`? Does every new OWL class have a matching Pydantic model and serialize dispatch?
3. Run the full test suite: `uv run pytest`.
4. Run `uv run ant verify` against `instances/` to confirm existing data still validates.
5. Run `uv run ant wiki` to regenerate the Concepts pages; diff to confirm the new terms appear with their definitions and sources.
6. If the change touches a commitment (C1–C8) or a decision (R1–R10), confirm that the relevant document is updated in the same PR.