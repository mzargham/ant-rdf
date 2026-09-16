<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0007 — Inscriptions can be actants: the `ant:manifestsAs` coexistence link

- **Status:** accepted
- **Date:** 2026-08-03 (authored downstream; mirrored upstream 2026-08-25)
- **Context builds on:** [ADR-0002](0002-cross-frame-links-and-status.md) (optional cross-entity predicates authored once, read by convention), [ADR-0005](0005-fluid-objects-and-material-carry-forward.md), [ADR-0006](0006-invariance-variance-coding-axis.md), R1 / R3 (Actant is methodological; readings are observer-relative), R9, and commitment **C9**.

## Context

An inscription (a material trace) and an actant (a thing that acts) are not disjoint categories: the same worldly entity can be both, in parallel registers. Ethnographers surface this in two directions — capture an actant and later code it as an inscription, or capture an inscription and later recognize it as an actant (possibly under a different frame). The two registers should be **non-disjoint** but **not forced** into a relation; they exist in parallel, and it is worthy of note when they coexist.

The grounding case is docs-as-code: git repositories supplant frozen documents as the knowledge-carrying artifact. The shift is **immutable → fluid**: a frozen document is an `ant:ImmutableMobile` that merely circulates, holding its form, whereas a living repository is an `ant:FluidObject` that *acts*, because it keeps changing under governed control. Its livingness is why it is preferred — conditioned on the verification machinery (C7) that makes a living artifact trustworthy. So a repository is at once an inscription (a named material trace) and an actant (a live node that acts): the immutable→fluid shift confers agency. This generalizes the C2 / C3 symmetry (objects are actors) to the trace-versus-actor axis. An open-source project is the textbook case — at once a community that governs and acts, and a codebase tightly coupled to it (CISA's C4 framework assesses exactly that pairing).

## Decision

**Add a directional object property `ant:manifestsAs` (`ant:Actant` → `ant:Inscription`).** "This actant is manifested as these inscriptions." It records coexistence without dual-typing any node.

1. **Directional, not symmetric.** It mirrors `ant:inscribes` / `ant:drawsOn` (an actant → an inscription) — *not* the symmetric `ant:correspondsTo`. `inscribes` (produces a separate trace) and `drawsOn` (consumes one) relate an actant to a *different* thing; `manifestsAs` relates an actant to the *same* thing read in the other register.
2. **Optional and never inferred.** No SHACL shape requires or forbids it; the two classes carry no `owl:disjointWith` (and the `ant-gvrn` skill refuses to add one). The link is asserted by the ethnographer, recovered on demand, never forced.
3. **Recoverable both ways.** Authored actant → inscription; the reverse reading ("this inscription is also an actant") is recovered by querying the subjects of `ant:manifestsAs` (Wave 3: `ant query manifests`, and the inscriptions / actants-across-frames briefs).
4. **Typically a fluid object, not enforced.** The range is `ant:Inscription`; the affinity with `ant:FluidObject` is intuitive (a thing that both acts and is its own circulating trace tends to persist by mutation) but an actant may in principle manifest as an immutable mobile too.

## Consequences

- **No Tier-1 SHACL change.** `ant verify` and the identity guard are unaffected. Per R9 the term carries `dcterms:source`.
- The chain is authored end to end: OWL term, `Actant.manifests_as`, `serialize._add_actant`, `new-record actant --manifests-as` / `edit-record actant --manifests-as` / `--clear-manifests-as`, `verify._CROSSREF_PROPERTIES`.
- **Ethnographer content, not tooling:** which actants coexist with which inscriptions is the ethnographer's to assert. The tooling only makes the assertion expressible and recoverable.
- **Deferred:** a symmetric same-entity predicate (a `coincidesWith`-style 1:1 coextension), to be taken up only if `manifestsAs` proves insufficient.
