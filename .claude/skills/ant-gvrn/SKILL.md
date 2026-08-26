---
name: ant-gvrn
description: |
  Ontology governance for ant-rdf. Use when a contributor wants to add, modify,
  or remove terms in the ontology (material-semiotics-core.ttl, the PROV
  alignment, SHACL shapes), when a shape change is proposed, or when reviewing
  an ontology PR. Enforces the atomicity rule (OWL term + Pydantic model +
  serializer + CLI + edit spec in one change) and provenance per term (R9).
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-gvrn — ontology governance

You are helping a contributor change the ontology, the alignment module, or the SHACL shapes. **Ontology changes are high-stakes**: they change the contract every existing record was authored against, and `ontology/` edits require the maintainer's explicit confirmation (CLAUDE.md). The decisions that shape the vocabulary are indexed in [adr/README.md](../../../adr/README.md); the commitments in [ONTOLOGICAL_COMMITMENTS.md](../../../ONTOLOGICAL_COMMITMENTS.md).

## When to use

- A new class, property, or role is requested.
- A SHACL shape is added, tightened, or loosened.
- Reviewing a PR that touches `ontology/`.
- (Waivers are *not* governance — see ant-mgmt §"Tier-2 warnings".)

## Procedure — every ontology change

1. **State the change in one sentence** for the contributor to confirm before any edit.
2. **`git diff ontology/`** so the actual change is visible, not a summary.
3. **`uv run ant ontology validate`** — ontology + alignment + shapes parse together.
4. **`uv run ant verify --lint`** against the existing instances — nothing existing breaks, and Tier-3 confirms every term has `dcterms:source`. If a new Tier-1 shape fails existing data, decide with the contributor whether the data or the shape is wrong.
5. **Atomicity rule** — one change, all layers, one commit:
   - the OWL term in `ontology/material-semiotics-core.ttl`
   - the Pydantic model / field in `src/ant_rdf/models.py`
   - the `_add_*` helper and dispatch entry in `src/ant_rdf/serialize.py`
   - `new_record.create_*` + the `new-record` / `edit-record` CLI flags and `edit_record._EDIT_SPEC`
   - `verify._CROSSREF_PROPERTIES` if the property points at another record
   - a test (a negative control for any shape: it must fire on the bad case)
6. **`dcterms:source` on every new term** (R9). A founding text where one exists; otherwise `"Synthesized for this vocabulary; ADR-#### R# (…)"` naming the decision record.
7. **Update the record**: a new ADR in `adr/` (next number; add it to `adr/README.md`), and `ONTOLOGICAL_COMMITMENTS.md` if a commitment changes. Regenerate the wiki (`ant wiki`) so the concept page appears.

## SHACL shape changes

- **Tier-1 (`sh:Violation`)** — very high bar: only what breaks downstream tooling or structural integrity (e.g. the cross-frame identity guard, ADR-0003). Never waivable.
- **Tier-2 (`sh:Warning`)** — analytical hygiene; waivable with justification. Put `sh:severity sh:Warning` on each *property* shape (pyshacl does not propagate it from the node shape). Give the message an actionable fix naming the CLI flag.
- **Tier-3 (`sh:Info`)** — lint, `--lint` only; self-target ontology terms so it never fires on instance data.
- Direct typing only at verify time (`advanced=False`): a shape targeting `ant:Translation` does not fire on the four moment subclasses, and a shape targeting `ant:Inscription` must list `ImmutableMobile` / `FluidObject` explicitly.

## Cross-reference resolution

`verify._check_crossrefs` flags a dangling IRI in any `ant:` cross-reference property as a **Tier-1** violation (never waivable). Fix by adding the missing record or removing the reference — through the CLI.

## Critical rules (what to refuse)

- **No `--no-verify` commits**; ontology changes go through CI.
- **No `owl:disjointWith` between the role classes** (`Mediator` / `Intermediary`; `ProvAgent` / `ProvInfluencer`) — they are simultaneously assignable under different practices (R3).
- **No `owl:disjointWith` between `ant:Actant` and `ant:Inscription`** — C9 / ADR-0007: coexistence is asserted with `ant:manifestsAs`, never forced or forbidden.
- **Never subclass `ant:Actant` under `prov:Agent`** — that typing is observer-relative (R2).
- **No human / non-human subclasses of Actant** — C2.
- **No AIME modes in v1** — R7.
- **No bare `:x a ant:Mediator` patterns** in shapes or data — roles are Characterization values (R3, R6).

## Reviewing an ontology PR

Walk the procedure above; spot-check `dcterms:source` and the atomicity layers; `uv run pytest`; `uv run ant verify --lint`; `uv run ant wiki` and diff the new concept pages; confirm the ADR and, if a commitment changed, ONTOLOGICAL_COMMITMENTS.md are in the same PR.

## Handoffs

- Authoring records against the vocabulary → [ant-mgmt](../ant-mgmt/SKILL.md).
- Waiving a Tier-2 warning → ant-mgmt §"Tier-2 warnings" (a waiver is the ethnographer's decision, not governance).
