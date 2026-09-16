<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Architecture decision records

Each ADR records one decision that shapes the vocabulary, the tooling contract, or the file layout — with the reasoning, so a contributor can tell why the system is shaped as it is. ADR-0000 holds the founding resolutions **R1–R10** (plus **R8a**, **R9a**, **R9b**); the later ADRs refine them. The philosophical premises they serve are **C1–C9** in [ONTOLOGICAL_COMMITMENTS.md](../ONTOLOGICAL_COMMITMENTS.md).

**Provenance.** ADR-0001 through ADR-0007 were first authored in a downstream case repository that consumes this toolkit, and were mirrored upstream (rewritten case-agnostic) on 2026-08-25. The dates below are the decision dates.

| # | Title | Status | Date | What it changes | Relates to |
|---|---|---|---|---|---|
| [0000](0000-foundational-decisions.md) | Foundational decisions | accepted | 2026-05-14 | R1–R10 (+R8a, R9a, R9b): actant as method, dual PROV alignment, roles via Characterization, the four acts, OPP as emergent, provenance per term, tri-severity verification, tri-licensing | C1–C9 |
| [0001](0001-perspective-isolation-named-graphs.md) | Perspective isolation: named graphs (target) vs single-graph discipline (now) | accepted in principle; implementation deferred | 2026-08-01 | the standing rule that a shared actant's identity is frame-neutral and byte-identical; named graphs as the v2 target | R3, R8, C6 |
| [0002](0002-cross-frame-links-and-status.md) | Cross-frame linking predicates + translation status/durability | accepted | 2026-08-02 | `readsSameProgramAs`, `correspondsTo`, `internalizes`, `tracesToPassage`; `TranslationStatus`, `hasStatus`, `hasDurability`; the connectivity warnings | R9, C5 |
| [0003](0003-shared-actant-home-and-identity-guard.md) | Frame-neutral shared home for actant identity + identity guard | accepted | 2026-08-02 | the `_shared` perspective token → `instances/cases/<case>/shared/`; Tier-1 `ActantShape` | ADR-0001 Decision 5, R3 |
| [0004](0004-graph-derivable-translation-frame.md) | Graph-derivable translation frame (`authoredUnder`) | accepted | 2026-08-02 | `ant:authoredUnder`; Tier-2 `TranslationFrameShape`; NetworkBrief scopes translations by frame | R3, R9, C6 |
| [0005](0005-fluid-objects-and-material-carry-forward.md) | `FluidObject`, and the produce / consume split on inscriptions | accepted | 2026-08-02 | `ant:FluidObject`; `ant:drawsOn` vs `ant:inscribes`; `new-record inscription` | R9, C5 |
| [0006](0006-invariance-variance-coding-axis.md) | Invariance / variance as the Mediator–Intermediary coding axis | accepted (rendering + documentation) | 2026-08-02 | how `invarianceCriterion` is read and rendered ("passes through" vs "regulates to preserve") | R3 |
| [0007](0007-inscriptions-can-be-actants-manifests-as.md) | Inscriptions can be actants: `manifestsAs` | accepted | 2026-08-03 | `ant:manifestsAs`; Actant / Inscription non-disjoint | C9, R1, R3, R9 |

## Adding an ADR

1. Take the next number; title the file `NNNN-kebab-title.md` with the CC-BY-4.0 SPDX header.
2. Give it a **Status**, **Date**, and **Context builds on** header naming the R-numbers, C-numbers and earlier ADRs it depends on.
3. If it changes a commitment, update ONTOLOGICAL_COMMITMENTS.md in the same commit; if it adds a term, the `ant-gvrn` atomicity rule applies (term + model + serializer + CLI + test).
4. Add a row to the table above.
