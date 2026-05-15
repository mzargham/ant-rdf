<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0000 — Foundational decisions (R1–R10)

**Status:** accepted (v0.1.0-draft) — pending expert-call confirmation per remaining open items.
**Date:** 2026-05-14
**Deciders:** repo maintainers + Ellie Rennie + project ethnographers
**Supersedes:** none (initial set)

This document records the foundational design decisions made before v0.1.0. Each decision (R1–R10) was raised as an open question during planning and resolved by the user with expert input. The decisions are folded into the body of the codebase at the locations noted in the "Where it lives" column; this ADR is the durable record of the *decisions themselves* and the reasoning, so future contributors can understand why the system is shaped the way it is.

A decision listed here is **accepted**, not frozen. To revise: open an issue tagged `adr-revision`, name the R-number, and propose the change. Revisions require updating this ADR and the body locations together.

---

## R1 — `ant:Actant` as methodological category, not ontological commitment

**Decision.** `ant:Actant` is a class for the analyst's convenience (it lets the CLI, compilers, and SHACL operate on a target type). It is **not** an ontological claim about the world. Documentation everywhere this class appears makes the methodological status explicit.

**Tension acknowledged.** Reifying actants as a class violates the spirit of Latour's flat ontology. We accept the cost — without a class, the tooling cannot operate. The mitigation is honest documentation.

**Where it lives.** [ONTOLOGICAL_COMMITMENTS.md](../ONTOLOGICAL_COMMITMENTS.md) C2/C3; `rdfs:comment` on `ant:Actant` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl).

---

## R2 — `prov:Agent` and `prov:Influencer` are **both** available, never globally asserted

**Decision.** Whether an actant is treated as a responsibility-bearing `prov:Agent` or a lighter `prov:Influencer` is itself observer-relative. The ontology provides `ant:ProvAgent` and `ant:ProvInfluencer` as role values assignable via `ant:Characterization`. There is **no** global `ant:Actant rdfs:subClassOf prov:Agent` declaration.

**Why.** Latour's generalized symmetry refuses pre-network agency attribution; some perspectives carry responsibility-attribution framing (policy analysts), others reject it (Latourian fieldworkers). Forcing one global typing would smuggle one observer-frame into the ontology.

**Where it lives.** [ontology/ant-prov-align.ttl](../ontology/ant-prov-align.ttl); `ant:ProvAgent` / `ant:ProvInfluencer` classes in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl); §4.3 of the plan in `.claude/plans/`.

---

## R3 — Mediator/Intermediary as observer-relative roles via Characterization

**Decision.** Latour 2005's distinction (mediator *transforms*; intermediary *transmits without transformation*) is encoded as **roles** (`rdfs:subClassOf prov:Role`), not as subclasses of `ant:Actant`. The same actant can simultaneously be characterized as Mediator under one practice and Intermediary under another via two separate `ant:Characterization` instances carrying explicit `(within_network, per_practice, invariance_criterion)` context. No OWL inconsistency.

**Why.** The mediator/intermediary distinction is observer-relative — the same interaction can be perceived as invariance-preserving by one analyst (tracking invariance α) and as transformation-introducing by another (tracking invariance β). The reified Characterization lets both characterizations coexist with explicit grounds.

**Where it lives.** `ant:Mediator`, `ant:Intermediary`, `ant:Characterization` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl); demonstrated in [instances/cases/scallops/perspectives/_default/characterizations.ttl](../instances/cases/scallops/perspectives/_default/characterizations.ttl).

**Worked example.** The scallops case includes both `:char/collectors-as-intermediary` and `:char/collectors-as-mediator` on the same larvae-collectors actant — see [briefs/scallops-network.md](../briefs/scallops-network.md).

---

## R4 — `ant:Enrolment` names the moment; `ant:EnrolmentRelation` reserved for v1.1

**Decision.** `ant:Enrolment` (the OWL class) refers to the **third moment of translation** (Callon canon). The v1.1 reified qualified-relation class will be named `ant:EnrolmentRelation` to avoid the overload of using one term for both a process-moment and a relational state.

**Why.** "Enrolment" is overloaded in the ANT literature — both a moment in the four-step translation sequence and a relational state of having-been-enrolled. Both deserve a class; using two names is awkward but honest.

**Where it lives.** `ant:Enrolment` class in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl) with `rdfs:comment` noting the disambiguation.

---

## R5 — Networks are act-4 documentation artifacts; the four acts stay separable

**Decision.** `ant:Network` records are **analyst-named summaries** — act-4 artifacts (documentation), not containers and not scopes. The four acts around networks remain separable:

| Act | Artifact | What it represents |
|---|---|---|
| 1 — Scope selection | `ant:Scope` | What is in analytical view (cases, perspectives, filters) |
| 2 — Query | (ad-hoc, no record) | SPARQL retrieval against a scope |
| 3 — Analysis | `ant:Analysis` | Computation/derivation against a scope (v2 engine) |
| 4 — Documentation | `ant:Network`, `ant:AnalysisReport` | Analyst-named summary; reading committed to |

**Why.** Conflating these acts (e.g., letting `ant networks list` silently mix "what scope am I in", "what query did I run", "what computation did I do", "what did I commit to as my reading") is exactly the analytical opacity material-semiotic commitments reject (C1, C4, C7). Each act produces a distinct, citable artifact.

**SPARQL CONSTRUCT** can derive a candidate Network from associations, but materializing it into the graph is an explicit human commitment via `ant new-record network --from-construct <q.sparql>` — never silent auto-derivation.

**Where it lives.** `ant:Network`, `ant:Scope`, `ant:Analysis`, `ant:AnalysisReport` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl); §4.7 of the plan.

---

## R6 — OPP as emergent attribute (manual in v1; rule-based tagging in v2 — design must not preclude)

**Decision.** `ant:ObligatoryPassagePoint` is **not** a class of thing; it is an emergent attribute assigned to an actant within a `(network, perspective)` context. v1 supports manual ethnographer assertion via `ant:Characterization` with `ant:assignsRole ant:ObligatoryPassagePoint`. v2 will support rule-based tagging from network topology (e.g., "any actant with maximum betweenness centrality on the enrolment subgraph gets OPP role within this perspective").

**The design must not preclude path 2.** Computed Characterizations have the same shape as ethnographer-asserted ones; the provenance (`ant:perPractice` referencing the analytical practice, plus v2 PROV-O attribution) distinguishes their origin.

**Generalization.** This pattern (`ant:TaggingRule` in v2) supports the analyst's move "any actant that satisfies `<rule>` should get `<attribute>`" for any role — OPP, Spokesperson, Mediator/Intermediary (where invariance can be computed), ImmutableMobile, etc.

**Where it lives.** `ant:ObligatoryPassagePoint` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl); §4.1.2 of the plan.

---

## R7 — AIME modes-of-existence: out of v1 scope

**Decision.** Latour's *An Inquiry into Modes of Existence* (AIME) is post-classical-ANT and represents a *correction* to ANT (where the "network" is one of 15 modes). Including AIME's mode vocabulary in v1 would muddle the Callon+Latour+Law/Mol synthesis. Reserved for a v2 extension module `ant-aime.ttl`.

**Where it lives.** `ant:Mode` listed under "Deferred to v2" in the plan inventory; no class defined in v1.

---

## R8 — Mol's multiplicity deferred to v2; v1 must not foreclose

**Decision.** Annemarie Mol's multiplicity (different practices enacting different realities of the same object) is technically deep — in RDF it requires either named graphs per enactment or per-practice reification. v2 lifts to named graphs over a quadstore. v1 must not paint into a corner that forces a breaking change.

**Operational guarantee.** Quad-readiness (R8a, below) — every assertion already carries the perspective it was authored under; the file-system + IRI conventions name the graphs v2 will instantiate; `graph.py` uses `rdflib.Dataset` (quad-capable) from day one.

**Where it lives.** §4.5 of the plan; [ONTOLOGICAL_COMMITMENTS.md](../ONTOLOGICAL_COMMITMENTS.md) C6.

---

## R9 — Every `ant:*` term carries `dcterms:source` to a founding text

**Decision.** Every class, object property, and datatype property in the ontology carries a `dcterms:source` literal naming the founding text (Callon 1986, Latour 1991/2005, Law 1986/1994/2008, Mol 2002) or `"Synthesized per plan §X"` for terms we coined.

**Why.** Lets disagreements on the expert call become "you cited the wrong source" (resolvable by reading the text) rather than "you got Latour wrong" (unresolvable). Also makes the wiki's Concepts/ pages function as a navigable glossary with citations.

**Where it lives.** [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl) — every term carries a `dcterms:source` line. Tier-3 lint shape `ant:OntologyClassSourceShape` enforces this at governance time.

---

## R9a — Perspectives live inside cases; current metadata fields good enough; no per-perspective SHACL in v1; cross-perspective contradictions deferred to v2

**Decision.** (a) Perspectives belong inside cases (perspective = relation between holder and seen-thing). (b) Current perspective metadata fields (`perspectiveHeldBy`, `perspectiveGroundedIn`, `perspectiveTracksInvariance`) are sufficient for v1. (c) No `--per-perspective` SHACL machinery in v1 — keep `ant verify` running across the merged graph. (d) Handling of overlapping/contradictory perspectives deferred to v2 with named-graph support.

**Where it lives.** [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl) `ant:Perspective`; §4.5 of the plan.

---

## R9b — Tier-1 list as drafted; waivers carry no expiry default and no co-sign; CI default is non-strict

**Decision.** The Tier-1 SHACL list as drafted (NetworkShape, PerspectiveShape, TranslationShape ≥1 moment, CharacterizationShape, IRI shape, cross-graph resolution) is the load-bearing set. Waivers:

- **No expiry default.** Most waivers don't expire; `ant:waiverExpires` is schema-optional and unused by default.
- **No co-sign requirement.** A single accountable agent in `ant:waivedBy` is sufficient; sensitive cases handled by team policy, not ontology constraint.
- **CI default non-strict.** Warnings surface in the log but do not break the build. Teams that want stricter gating add `--strict` to their workflow.

**Where it lives.** [ontology/shapes/ant-shapes-core.ttl](../ontology/shapes/ant-shapes-core.ttl) (Tier 1), [ontology/shapes/ant-shapes-warnings.ttl](../ontology/shapes/ant-shapes-warnings.ttl) (Tier 2), [src/ant_rdf/verify.py](../src/ant_rdf/verify.py) (waiver handling and exit-code logic).

---

## R10 — Tri-licensing: Apache-2.0 (code), CC0-1.0 (ontology), CC-BY-4.0 (docs)

**Decision.** Three artifact classes, three licenses. SPDX-License-Identifier headers on every file declare which clause applies.

**Why.** Each artifact class has a different reuse profile. Python code wants Apache-2.0's patent clarity; shared vocabulary wants CC0's no-friction adoption (the LOV norm); ethnographic narrative wants attribution (CC-BY honors the ethnographer's authorship).

**Where it lives.** [LICENSE.md](../LICENSE.md), [LICENSE-CODE](../LICENSE-CODE), [LICENSE-ONTOLOGY](../LICENSE-ONTOLOGY), [LICENSE-DOCS](../LICENSE-DOCS).

---

## Remaining open items (for the expert call)

These are recorded in §9 of the plan in `.claude/plans/`. Summarized here as the ADR's "follow-ups":

1. **Email Goodwin & Kuehn (2021)** for any TTL draft they may have — citable prior art and a potential parity reference for the hotel-keys case (step 11 of the plan).
2. **Walk C1–C8 with the ethnographers and ANT experts** before the first ethnographer-authored case study is committed. Confirm that the methodological framing of `ant:Actant` (R1) lands without scholarly objection, and that the four-acts separation (R5) maps to fieldwork conceptualization.
3. **First-case selection** beyond scallops. Confirm whether to reproduce the Latour 1991 hotel-keys example (parity with Goodwin/Kuehn 2021) or to lead with a contemporary fieldwork case the ethnographers own — likely both, with the contemporary case driving wiki-template iteration per the user's note.
4. **Wiki structure feedback after first case lands** — the user has noted they expect the wiki layout to evolve to fit ethnographer use. The post-first-case review is a design checkpoint, not a polish pass.
5. **v2 roadmap signoff.** Confirm the v2 priorities — named graphs for multiplicity (R8), rule-based tagging engine for analytical enrichment (R6), temporality via PROV-O properties on existing moment-classes — are the right next-priorities.
