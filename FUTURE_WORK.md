<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Future work and validation regime

`ant-rdf` v0.1.0-draft ships a deliberately **minimalist** v1 — the pattern in place, the round-trip working end-to-end, two training cases authored entirely through the CLI. Enough for a working ethnographer (specifically: Ellie) to use, find the seams, and tell us what's actually needed. This document records what was held out of v1, how features arrive, and the three-tier validation regime that should govern when machine-mediated analyses are permitted to make novel ethnographic claims.

**A note on framing.** Future work here is not a binary v1-vs-v2 ladder. It's a **what / why / when** question driven by use:

- **What** — what feature is being added or extended
- **Why** — what real workload (a case study, a comparison, an authoring friction) makes it necessary
- **When** — when it ships, which is *after* the workload is concrete, not in anticipation of it

So the sections below describe scope-outs as candidates the toolkit is structurally ready for; whether and when they arrive depends on what the people using `ant-rdf` find missing. Two priorities are already named: a **test suite** (correctness floor for the existing v1) and **operational temporality** (the user has agreed temporality is critical for academic use in practice, and it's the most likely first request once real fieldwork starts landing).

**The framing premise.** This toolkit is a **prosthesis**. Like every prosthesis it changes what it amplifies. Treating it as a neutral instrument would itself be an analytical mistake — exactly the kind of mistake material-semiotics insists we should refuse. So future work is not only about adding features; it is about understanding what the prosthesis does to the analyses it mediates.

## 1. What v1 deliberately held out of scope

Each of the following was a *resolved* decision during planning to defer the feature, not an oversight. The decisions are recorded in [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md) and revisited here with the implementation paths we expect to follow.

### 1.1 Operational temporality — top priority for the first real-fieldwork increment

**Structural placeholder is already in place.** In `ontology/ant-prov-align.ttl`, `ant:Translation`, the four moments (`Problematization`, `Interessement`, `Enrolment`, `Mobilization`), `ant:Practice`, and `ant:Analysis` all subclass `prov:Activity`. PROV-O Activities carry `prov:startedAtTime` and `prov:endedAtTime` as optional, well-known properties. Any consumer that imports the alignment file can attach temporal triples to existing records and they store and round-trip without complaint — `rdflib.Dataset` accepts them, SHACL doesn't object, and existing data validates unchanged. **This is the lift that v1 paid for in advance.**

**Operational temporality is not built.** Concretely, v1 has none of:
- A `started_at` / `ended_at` field on any Pydantic model
- A `--started-at` / `--ended-at` flag on any CLI subcommand
- A catechism prompt in the conversational skill that asks for dates
- A SHACL warning (Tier-2) that translations "should" carry an interval
- A compiler that renders timelines, intervals, or temporal ordering

So if an ethnographer says "the larvae anchored in winter 1985 but the fishermen invaded the protected grounds the following winter," that's currently captured in `dcterms:description` prose, not as separable temporal data. The model knows *that* the mobilization happened; it doesn't know *when*.

**Why operational temporality is the top-priority increment.** Academic use in practice requires:
- Citing the year a fieldwork episode happened
- Tracing how a translation's durability changes over seasons or years
- Reasoning about *precariousness* (C5) — Law 2008's "translation is always insecure" — which is only legible when the analysis can name *when* the unravelling occurred
- Comparing two perspectives' temporal accounts of the same network (does the policy-analyst's clock match the fieldworker's clock?)

The user has explicitly named this as critical for academic use. It is the most likely first request once Ellie's fieldwork starts landing in the toolkit.

**Implementation path (what / why / when).**

What:
- Add optional `started_at: date | None` and `ended_at: date | None` to the `Translation`, `Problematization`, `Interessement`, `Enrolment`, `Mobilization`, `Practice`, and `Analysis` Pydantic models.
- Extend the serializer adders to emit `prov:startedAtTime` / `prov:endedAtTime` when fields are set.
- Add `--started-at` / `--ended-at` flags to the corresponding CLI subcommands.
- Add the conversational catechism prompt: "Roughly when did this moment unfold? (year, season, or interval is fine — leave blank if you'd rather narrate it.)"
- Add a Tier-2 SHACL warning: translations *should* have at least a `prov:startedAtTime` if any of their moments do.
- Add a `TranslationTimeline` compiler — render a translation's moments on a horizontal axis when temporal data is present; fall back to ordered-narrative when absent.
- Update the existing scallops and hotel-keys cases to attach the dates that are recoverable from the source texts (Callon 1986 uses seasons; Latour 1991 is generic). Leave dates absent where the source is silent — that's data, not a defect.

Why: real-fieldwork legibility. Listed above.

When: as the first non-trivial v1 increment, almost certainly *before* Ellie's first contemporary case lands — because the contemporary case will likely have specific dates and the toolkit should not be the bottleneck on capturing them.

### 1.2 Multiplicity proper — named graphs over a quadstore

**Out of v1 scope.** v1 stores all assertions in a single default graph; different perspectives merge on load. The reified `ant:Characterization` mechanism gives us a partial down-payment: the same actant can simultaneously be characterized as Mediator under one practice and Intermediary under another *without OWL inconsistency*, but the canonical-graph identity of an actant is still single.

**Why deferred.** Mol's multiplicity (different practices enacting different *realities* of the same object — *The Body Multiple*, 2002) is technically deep. A clean implementation requires (a) a quad-capable store with per-graph SHACL, (b) compilers that can render contrastively across graphs, and (c) a UX for the ethnographer to declare which-graph-am-I-writing-into without that becoming a paperwork burden. v1 commits to the *data shape* that admits this lift but does not build the rendering or UX.

**Implementation path (what / why / when).**

What:
- Flip `graph.py`'s loader to use per-perspective `publicID` arguments; each `ant:Perspective` IRI becomes a named graph URI. No data migration required (per R8) — the file-system layout already names the graphs.
- Add `ant verify --per-perspective` to apply SHACL within each named graph (so contradictions across graphs are *not* errors).
- Add `ant compile <kind> --perspectives a,b --mode contrast` to render comparative briefs.
- Decide what "the same actant in two graphs" means at compile time — partial connection rendering (Strathern 1991) rather than aggregate union.

Why: a case actually requires multiplicity — a clinical/medical case (Mol's territory), a controversy with genuinely incommensurable readings, or a comparison study where two ethnographer-teams analyse the same field site under different theoretical practices.

When: when such a case is on the workload. The lift cost is small (one `publicID` argument plus per-graph SHACL); we don't need to pay it speculatively.

### 1.3 Rule-based tagging engine for analytical enrichment

**Out of v1 scope.** OPP, Spokesperson, BlackBox status, and related role assignments are recorded manually via `ant:Characterization` in v1. The ontology and CLI shape does not preclude rule-based assignment from network topology — for example, "any actant with maximum betweenness centrality on the enrolment subgraph in this scope should be tagged OPP under the network-funding practice" — but the engine that runs such rules is not built yet.

**Why deferred.** The data shape and the philosophical positioning (per R6 in ADR-0000) needed to land before the computation engine. v1 demonstrates that manually-asserted Characterizations work end-to-end; the rule-based path is additive. Both produce identical RDF; provenance distinguishes their origin.

**Implementation path (what / why / when).**

What:
- Add `ant:TaggingRule` class with a SPARQL ASK pattern + a target role.
- Add `ant analyze run <rule-iri> --in-scope <scope-iri>` that materializes computed Characterizations whose `ant:perPractice` references the analytical practice and whose PROV-O attribution traces the rule and execution.
- Library of rules to consider: maximum-betweenness OPP detection; immutable-mobile detection (an actant whose properties stay constant across translations); spokesperson detection (an actant that's the source of `ant:speaksFor` to many others within a translation's mobilization moment).
- **Critical UX commitment:** tagged Characterizations always render distinctly in compiled briefs ("⚙ computed from rule X" vs "✍ asserted by ethnographer Y"), so a reader can never confuse machine and human attributions.

Why: scaling — when a case has hundreds of actants, manual OPP assignment becomes impractical, and a rule that flags candidates for ethnographer confirmation is a useful prosthesis.

When: after a real case generates enough actants that manual characterization is the bottleneck, and after the comparison-study programme (§2.4) has begun so we have evidence about how machine-mediated tagging affects ethnographic readings.

### 1.4 AIME modes-of-existence

**Out of v1 scope.** Latour's *An Inquiry into Modes of Existence* (AIME, 2013) introduces 15 modes of existence — Reference [REF], Reproduction [REP], Fiction [FIC], Law [LAW], Religion [REL], Politics [POL], Organisation [ORG], etc. — of which "Network" is just one. Including these in v1 would muddle the Callon+Latour+Law/Mol synthesis we committed to.

**Why view as distinct project.** AIME is post-classical-ANT and Latour explicitly framed it as a *correction* to the network-everything tendency. Including it as a parallel vocabulary requires careful curation by AIME-fluent scholars, and the AIME platform itself is HTML-only (no published RDF). Premature inclusion would smuggle AIME's commitments into the analytical baseline. 

**Implementation path (extension module).**
- A separate `ontology/ant-aime.ttl` that consumers import alongside core when they want AIME's modes available.
- `ant:Mode` as a SKOS concept scheme (rather than OWL class), with the 15 modes as `skos:Concept` instances.
- Each Mode entry carries citations to the AIME platform and the 2013 book.
- Compilers gain optional `--include-modes` flag.

### 1.5 Reified qualified relations (`EnrolmentRelation` and kin)

**Out of v1 scope.** v1's `ant:enrols`, `ant:translates`, `ant:passesThrough`, `ant:speaksFor` are binary properties. The PROV qualified-influence pattern (where a relation gets reified as a node carrying strength, time, contestation status, justification, etc.) is the natural next extension once a case needs them.

**Why deferred.** Binary properties cover the common case; qualified relations are a heavier authoring burden. v1 should be cheap to use.

**Implementation path.**
- Add `ant:EnrolmentRelation`, `ant:TranslationRelation`, `ant:RolePlaying` as reified n-ary nodes with `ant:strength`, `ant:isContested`, `ant:contestedBy`, plus the temporal properties from §1.1.
- CLI: `ant new-record enrolment-relation --strength 0.7 --contested-by <iri>` etc.
- Compilers gain a "strength heatmap" view across a network's translations.

### 1.6 Better ingest parsers (transcripts, observations, NER-from-prose)

**Out of v1 scope.** `ant ingest transcript` and `ant ingest observation` are stubs that point users to `ant ingest notes` with YAML frontmatter. We deliberately did NOT implement NER-style auto-extraction of actants from free prose.

**Why deferred.** Auto-extraction from prose is exactly the place where machine mediation can start making claims the ethnographer didn't make. The v1 commitment is the **review-document dry-run pattern**: every ingestion path lands as *candidates* requiring explicit human confirmation. Building better parsers without first establishing the candidate-review-confirm discipline would invite drift.

**Implementation path (when transcript/observation workload arrives).**
- Transcript parser: detect speaker turns, attributions ("X said that…"), and named entities. Always emit candidates into the review document — never assert.
- Observation parser: detect declarative sentences with subjects matching candidate actant patterns. Same dry-run rule.
- Lift to LLM-mediated extraction *only after* the three-tier validation regime (below) has been exercised on simpler input formats — so we know what failure modes to look for.

### 1.7 Comparative compilers + scope-aware briefs

**Out of v1 scope.** Compilers v1 render one record or one case at a time. Cross-perspective contrastive views, scope-aware filtering, and side-by-side comparative analysis are deferred.

**Implementation path (paired with §1.2 multiplicity work).**
- `--perspectives a,b --mode contrast` flag on NetworkBrief renders the same network from two perspectives side-by-side, highlighting where Characterizations diverge (this is the §4.1.1 mechanism made visually legible).
- `ant scope new` becomes operational (act 1 of the four acts per §4.7); `ant compile … --scope <iri>` filters compilation to that scope.

### 1.8 Test suite

**Out of v1 scope.** v0.1.0-draft has no `pytest` tests beyond the CI scaffold. Working v1.0 requires a test suite.

**Implementation path (immediate next correctness pass; should land before any contemporary case-study fieldwork lands).**
- Determinism tests: same model → byte-identical Turtle (D15 invariant).
- Round-trip tests: `new-record → verify → compile → wiki` produces stable artifacts.
- SHACL tier tests: Tier-1 violations break; Tier-2 warnings surface; waivers suppress.
- Ingest tests: dry-run produces expected review documents; commit produces matching triples.

---

## 2. Validation regime: training, testing, novel

How do we know whether `ant-rdf` is producing good analyses? We treat the toolkit like any model that produces claims and subject it to a structured validation regime with three tiers.

This regime is methodologically load-bearing: we do not believe a research method is justified just because its outputs *look* like good ethnography. Every claim produced through machine mediation should be traceable to which validation tier the toolkit had cleared at the time the claim was made.

### Tier 1 — Training cases (canonical cases from the source texts)

The first validation is **review against the training set** — getting back what you put in.

The toolkit is built on Callon (1986), Latour (1991, 2005), Law (1986, 1994, 2008), Mol (2002), and a small set of allied texts. Each canonical example in those works — the scallops of St Brieuc Bay, the hotel-key fob, the Portuguese maritime network, Pasteur's anthrax vaccine, *The Body Multiple*'s atherosclerosis enactments, the laboratory's modes of ordering — is a *training case*. Producing them through the toolkit and getting back analyses that the original authors would recognise is the lowest bar. **If we can't reproduce these, we have nothing.**

**v1 status.** Two training cases shipped: [scallops](instances/cases/scallops/) (Callon 1986) and [hotel-keys](instances/cases/hotel-keys/) (Latour 1991, Goodwin/Kuehn 2021 parity). Both are end-to-end demonstrations that the v1 mechanics work.

**Expected v1.0 set.**
- Scallops (Callon 1986) ✓
- Hotel keys (Latour 1991, Goodwin/Kuehn 2021 parity) ✓
- Portuguese maritime network (Law 1986) — immutable mobiles canon
- Pasteur and anthrax (Latour 1988) — "great man as network effect"
- *The Body Multiple* atherosclerosis (Mol 2002) — multiplicity, demands the §1.2 named-graph lift before it can be honoured
- Aramis (Latour 1996) — failed translation, modes-of-existence pre-AIME
- Laboratory modes-of-ordering (Law 1994) — discursive durability

**What success looks like.** Each case compiles to a brief and wiki entry; the original author (or a scholar deeply familiar with the work) reviews the brief and confirms it preserves the analytical substance. Where the brief loses something, that loss is documented as a known limitation, not silently absorbed.

### Tier 2 — Testing cases (canonical cases NOT used to build the theory or this repo)

The second validation is **generalisation testing**. Cases that:

- are from the wider ANT / material-semiotics tradition,
- have published, scholarly analyses we can compare against,
- but were **not** used to develop the founding works the vocabulary inherits from,
- and were **not** consulted during this repo's design.

Examples we expect to explore:
- Akrich's *De-scription of technical objects* (1992) — predates Latour 2005's mediator/intermediary refinement, lets us probe whether v1's encoding survives the terminology shift.
- de Laet & Mol's Zimbabwe bush pump (2000) — fluid technology that should *break* `ant:ImmutableMobile` in interesting ways and force an `ant:FluidObject` extension.
- Singleton's UK cervical screening programme (1998) — ambivalent enrolment, partial translation.
- Hennion's music amateurs / drug addicts attachment studies (1999, 2001) — affective material semiotics.
- A contemporary STS case the project ethnographers select, ideally one with a recent peer-reviewed analysis we can compare against.

**What success looks like.** The toolkit produces analyses that a scholar familiar with the source case — but not involved in this project — judges to capture the analytical move the original work made. *And* the toolkit's analyses surface points where its categories are incommensurable with the case (these are not failures; they are calibration data).

**What success does not require.** Getting the case "right" by some neutral standard. ANT/material-semiotics is not aiming at a neutral standard. We are aiming for analyses that participate well in the conversation the source case is part of.

### Tier 3 — Novel results, with explicit machine-mediation accounting

Only after a documented assessment of model adequacy — **with strengths and weaknesses spelled out** from Tiers 1 and 2 — do we authorise the toolkit's use to produce *novel* ethnographic claims about field sites that have no prior canonical analysis.

The discipline here is twofold:

1. **Don't claim more than the calibration supports.** If Tier 2 testing showed the toolkit reliably under-reads multiplicity in clinical settings, novel-results analyses of clinical fieldwork must flag that known underread.
2. **Reason about machine mediation within the analysis itself.** Material semiotics is precisely the school of thought that requires us to treat instruments and apparatus as part of the network being analysed. An ANT analysis produced via `ant-rdf` is an analysis produced via a particular technical prosthesis, with specific affordances (catechism prompts that nudge toward certain framings, SHACL shapes that surface certain absences, deterministic Turtle that mistrusts blank-node identity, a CC0-licensed vocabulary that pre-defines the analyst's terms). These cannot be assumed neutral. They must be accounted for in the same paper that reports the findings.

### 2.4 Machine-mediation comparison studies (the key future research thread)

What we are most interested in producing — beyond any single field analysis — is **paired analyses of the same field site, one with and one without the `ant-rdf` prosthesis**, written by collaborating teams who exchange materials but maintain methodological independence until comparison.

The questions this is designed to answer:

- **What is gained by machine mediation?** Categories surfaced that the unaided ethnographer might miss. Symmetric treatment of human/non-human that prose drift might compromise. Cross-case comparison that a single ethnographer's notebooks can't easily produce. Reviewability of inscriptions and provenance that paper notes mislay.
- **What is lost?** The texture of fieldwork prose. The interpretive moves that don't fit the catechism's question structure. The cases where forcing a Characterization into the Mediator/Intermediary mould obscures something the analyst would have written narratively. The slippage between "the ethnographer's understanding" and "what the CLI made it possible to record."
- **What is transformed?** Material semiotics teaches that translations don't just transmit, they **transform**. The most important comparison-study findings will likely be the categories that simply look *different* in machine-mediated vs. unaided analyses — neither better nor worse, but other.

The methodological commitment: comparison-study reports are **co-authored** by the ethnographic team and the toolkit team, with both methods rendered legible enough for outside readers to assess. Neither method is permitted to grade itself.

---

## 3. How features arrive

Features land in this repo when use surfaces them as needed — not before. The plan in `.claude/plans/` records what we *expected* to need; the issue tracker and the comparison-study findings will record what we *actually* need.

Practical norms:

- **No speculative features.** If no current case-study workload requires a feature, we don't build it. Half-built features collect cost without producing analytical leverage.
- **Each new feature ships with a training case that uses it.** If the Akrich case requires reified `EnrolmentRelation`, the PR that adds the class also adds the case-study record that motivates the class.
- **Tier-2 testing is the gate for Tier-3 novel-results use.** No claim "the toolkit can produce reliable analyses of X" without testing-case evidence that it does.
- **Comparison-study findings change the ontology.** If a paired-analysis study shows the toolkit's Mediator/Intermediary characterization systematically obscures something the unaided analyst captures, that's data the next ontology revision must respond to — not a deficiency of the unaided analyst.

---

## 4. Open follow-ups for the expert call

Carrying forward from [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md):

- Email Goodwin & Kuehn (2021) for any TTL draft of the hotel-keys ontology they may have — citable prior art and (if available) reference content for the existing hotel-keys case.
- Walk the eight ontological commitments (C1–C8) and ten resolved decisions (R1–R10) with the ethnographers and ANT-fluent reviewers before the first contemporary case study is committed.
- Confirm the priorities of §1 above (which §1 features land first) against ethnographer-team workload.
- Sign off on the validation regime in §2: do we accept Tier 1/2/3 as the gating structure for permitting novel-results use?
- Sign off on the comparison-study design in §2.4: which collaborating ethnographer-team pair will run the first paired analysis, and on which field site?
