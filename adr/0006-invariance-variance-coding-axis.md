<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0006 — Invariance / variance as the Mediator–Intermediary coding axis (surface + document)

- **Status:** accepted (documentation + rendering; no schema change)
- **Date:** 2026-08-02 (authored downstream; mirrored upstream 2026-08-25)
- **Context builds on:** R3 (Mediator / Intermediary are observer-relative roles assigned via `ant:Characterization`), the existing `ant:invarianceCriterion` datatype property, [ADR-0005](0005-fluid-objects-and-material-carry-forward.md) (`ant:FluidObject` / `ant:drawsOn`).

## Context

Both roles serve an **invariant** — the thing held constant — and `ant:invarianceCriterion` names it. The difference is the *mechanism* (a cybernetic reading): an **Intermediary** preserves the invariant by transmitting without transformation (pass-through), whereas a **Mediator** preserves it by **regulating** — varying *other* dimensions in order to keep that invariant (requisite variety: a regulator must command variety to hold the essential variable constant). So the criterion is **what is preserved in both cases**; "regulate" never names the invariant, it names the *means*.

Crucially the two roles are not exclusive per actant: the *same* actant can be a Mediator on the dimensions it **regulates** *and* an Intermediary on the dimensions it **passes through** at the same time, and it is the analyst's **perspective** that selects which dimensions are load-bearing for the coding. This is why role divergence across frames is honest signal, not contradiction — the scallops towlines are an Intermediary under experimental-oceanography practice (anchoring substrate as designed) and a Mediator under seasonal-fishing-labor practice (rhythms of bay work).

The ontology already carried the hook, but `ant:invarianceCriterion` was under-utilised: authored thinly, its preserved-vs-varied reading left implicit, and never surfaced in the rendered artifacts. It is the *same axis* as `ant:FluidObject` vs `ant:ImmutableMobile` under `ant:drawsOn` (fluid = varied when drawn on; immutable = invariant) — invariance / variance is one idea running through both the role coding and the material trace.

## Decision

**Surface it and document it; do not change the schema.**

1. **Render role-aware, everywhere a characterization appears** — the network brief and wiki characterization tables read `ant:invarianceCriterion` through `ant:assignsRole`: Intermediary → **"passes through: {criterion}"**, Mediator → **"regulates to preserve: {criterion}"**; other roles show the criterion as is (`compilers._common.invariance_display`).
2. **Document the axis** — enriched `rdfs:comment`s on `ant:Mediator`, `ant:Intermediary`, and `ant:invarianceCriterion` spell out the preserved-vs-varied dimension sets, the simultaneous dual coding, and perspective selection, and tie the axis to `ant:FluidObject` / `ant:ImmutableMobile` under `ant:drawsOn`. Concept pages regenerate from these comments.
3. **Keep the free-text field** — a single `ant:invarianceCriterion` per characterization is sufficient because the dual coding lives across *two* characterizations (one per role), each naming its own dimension. No new predicate is minted.

## Consequences

- The preserved-vs-varied reading is legible in briefs and wiki without touching the data model. Committed briefs and wiki pages that render characterizations changed accordingly in the same commit.
- **Ethnographer content, not tooling:** crisper per-characterization `invarianceCriterion` wording that names the dimensions precisely is the ethnographer's to author; the tool only renders it faithfully.
- **Deferred:** the v1.1 reification to a first-class `ant:Invariance` (structured dimension objects with explicit preserved / varied flags) remains open, to be taken up only if surface-and-document proves insufficient.
