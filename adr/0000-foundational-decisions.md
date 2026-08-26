<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0000 — Foundational decisions (R1–R10, with R8a, R9a, R9b)

**Status:** accepted (v0.1.0-draft) — pending expert-call confirmation per remaining open items.
**Date:** 2026-05-14
**Deciders:** repo maintainers + Ellie Rennie + project ethnographers
**Supersedes:** none (initial set)
**Amended by:** [ADR-0001](0001-perspective-isolation-named-graphs.md) (R8 / C6: single-graph discipline now, named graphs later), [ADR-0002](0002-cross-frame-links-and-status.md) (R9: cross-frame terms), [ADR-0003](0003-shared-actant-home-and-identity-guard.md) (R9b: `ActantShape` joins Tier-1), [ADR-0004](0004-graph-derivable-translation-frame.md) (R3: translations attributed to a perspective), [ADR-0005](0005-fluid-objects-and-material-carry-forward.md), [ADR-0006](0006-invariance-variance-coding-axis.md) (R3: the invariance axis), [ADR-0007](0007-inscriptions-can-be-actants-manifests-as.md) (R1: C9). Index: [README.md](README.md).

This document records the foundational design decisions made before v0.1.0. Each decision (R1–R10, plus the sub-decisions R8a, R9a, R9b) was raised as an open question during planning and resolved by the user with expert input. The decisions are folded into the body of the codebase at the locations noted in the "Where it lives" column; this ADR is the durable record of the *decisions themselves* and the reasoning, so future contributors can understand why the system is shaped the way it is.

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

**Where it lives.** [ontology/ant-prov-align.ttl](../ontology/ant-prov-align.ttl); `ant:ProvAgent` / `ant:ProvInfluencer` classes in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl).

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

**Where it lives.** `ant:Network`, `ant:Scope`, `ant:Analysis`, `ant:AnalysisReport` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl). Acts 1 and 3 have data shapes but no engine (`ant scope new`, `ant analyze list-methods` are stubs); act 2 is `ant query`; act 4 is `ant new-record network` and the compiled briefs.

---

## R6 — OPP as emergent attribute (manual in v1; rule-based tagging in v2 — design must not preclude)

**Decision.** `ant:ObligatoryPassagePoint` is **not** a class of thing; it is an emergent attribute assigned to an actant within a `(network, perspective)` context. v1 supports manual ethnographer assertion via `ant:Characterization` with `ant:assignsRole ant:ObligatoryPassagePoint`. v2 will support rule-based tagging from network topology (e.g., "any actant with maximum betweenness centrality on the enrolment subgraph gets OPP role within this perspective").

**The design must not preclude path 2.** Computed Characterizations have the same shape as ethnographer-asserted ones; the provenance (`ant:perPractice` referencing the analytical practice, plus v2 PROV-O attribution) distinguishes their origin.

**Generalization.** This pattern (`ant:TaggingRule` in v2) supports the analyst's move "any actant that satisfies `<rule>` should get `<attribute>`" for any role — OPP, Spokesperson, Mediator/Intermediary (where invariance can be computed), ImmutableMobile, etc.

**Where it lives.** `ant:ObligatoryPassagePoint` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl); traffic through a passage is recorded with `ant:tracesToPassage` ([ADR-0002](0002-cross-frame-links-and-status.md)) and rendered by `OPPMap`.

---

## R7 — AIME modes-of-existence: out of v1 scope

**Decision.** Latour's *An Inquiry into Modes of Existence* (AIME) is post-classical-ANT and represents a *correction* to ANT (where the "network" is one of 15 modes). Including AIME's mode vocabulary in v1 would muddle the Callon+Latour+Law/Mol synthesis. Reserved for a v2 extension module `ant-aime.ttl`.

**Where it lives.** Nowhere yet — no class is defined in v1.

---

## R8 — Mol's multiplicity deferred to v2; v1 must not foreclose

**Decision.** Annemarie Mol's multiplicity (different practices enacting different realities of the same object) is technically deep — in RDF it requires either named graphs per enactment or per-practice reification. v2 lifts to named graphs over a quadstore. v1 must not paint into a corner that forces a breaking change.

**Operational guarantee.** Quad-readiness (R8a, below).

**Where it lives.** [ONTOLOGICAL_COMMITMENTS.md](../ONTOLOGICAL_COMMITMENTS.md) C6; the in-force single-graph discipline and the named-graph target are [ADR-0001](0001-perspective-isolation-named-graphs.md).

---

## R8a — Quad-readiness: v1 stores the graphs v2 will instantiate

**Decision.** Every assertion already carries the perspective it was authored under: records live under `instances/cases/<case>/perspectives/<slug>/`, an `ant:Perspective` IRI is the name of the graph v2 will route that directory into, `graph.py` uses `rdflib.Dataset` (quad-capable) from day one, and a translation names its perspective in the graph itself (`ant:authoredUnder`, [ADR-0004](0004-graph-derivable-translation-frame.md)). The v1→v2 lift is a `publicID` argument on parse, not a data migration.

**Where it lives.** [src/ant_rdf/graph.py](../src/ant_rdf/graph.py); the file layout in [docs/toolchain.md](../docs/toolchain.md).

---

## R9 — Every `ant:*` term carries `dcterms:source` to a founding text

**Decision.** Every class, object property, and datatype property in the ontology carries a `dcterms:source` literal naming the founding text (Callon 1986, Latour 1991/2005, Law 1986/1994/2008, Mol 2002) or `"Synthesized for this vocabulary; ADR-#### R# (…)"` for terms we coined.

**Why.** Lets disagreements on the expert call become "you cited the wrong source" (resolvable by reading the text) rather than "you got Latour wrong" (unresolvable). Also makes the wiki's `Concept-<Term>.md` pages function as a navigable glossary with citations.

**Where it lives.** [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl) — every term carries a `dcterms:source` line. Tier-3 lint shape `ant:OntologyClassSourceShape` enforces this at governance time.

---

## R9a — Perspectives live inside cases; current metadata fields good enough; no per-perspective SHACL in v1; cross-perspective contradictions deferred to v2

**Decision.** (a) Perspectives belong inside cases (perspective = relation between holder and seen-thing). (b) Current perspective metadata fields (`perspectiveHeldBy`, `perspectiveGroundedIn`, `perspectiveTracksInvariance`) are sufficient for v1. (c) No `--per-perspective` SHACL machinery in v1 — keep `ant verify` running across the merged graph. (d) Handling of overlapping/contradictory perspectives deferred to v2 with named-graph support.

**Where it lives.** [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl) `ant:Perspective`.

---

## R9b — Tier-1 list as drafted; waivers carry no expiry default and no co-sign; CI default is non-strict

**Decision.** The Tier-1 SHACL list (`NetworkShape`, `ActantShape` — exactly one label and description, [ADR-0003](0003-shared-actant-home-and-identity-guard.md) —, `PerspectiveShape`, `TranslationShape` ≥ 1 moment, `CharacterizationShape`, `ConstraintWaiverShape`, plus cross-reference resolution in `verify.py`) is the load-bearing set. Waivers:

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

The planning-phase open items, with their current status:

1. **Email Goodwin & Kuehn (2021)** for any TTL draft they may have — citable prior art and a potential parity reference for the hotel-keys case. *Open.*
2. **Walk C1–C9 with the ethnographers and ANT experts.** Confirm that the methodological framing of `ant:Actant` (R1) lands without scholarly objection, and that the four-acts separation (R5) maps to fieldwork conceptualization. *Open* — contemporary cases have since been committed, so this is a review rather than a gate.
3. **First-case selection beyond scallops.** *Resolved:* both paths were taken — hotel-keys (Goodwin/Kuehn parity) and two contemporary cases (koi, pi-learning).
4. **Wiki structure feedback after the first case lands.** *Resolved:* the wiki moved to a flat `Concept-*` / `Case-*` / `Actant-*` layout, and the reader-oriented briefs (guide, synopsis, positionality, …) were added on ethnographer feedback ([docs/toolchain.md](../docs/toolchain.md)).
5. **v2 roadmap signoff.** Confirm the v2 priorities — named graphs for multiplicity (R8, [ADR-0001](0001-perspective-isolation-named-graphs.md)), rule-based tagging engine for analytical enrichment (R6), temporality via PROV-O properties on existing moment-classes ([FUTURE_WORK.md](../FUTURE_WORK.md)) — are the right next-priorities. *Open.*
