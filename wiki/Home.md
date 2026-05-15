# ant-rdf wiki

## Abstract — a material-semiotic reading of this repository

`ant-rdf` is a docs-as-code semantic-web vocabulary and authoring toolkit for actor-network / material-semiotic analysis, synthesising Callon's sociology of translation, Latour's classical ANT, and post-ANT material semiotics (Law, Mol). The canonical form of every record is RDF (Turtle in the [`https://w3id.org/ant#`](https://w3id.org/ant) namespace); compilers render the canonical RDF into reviewable Markdown briefs and a hyperlinked wiki; a Python CLI authors the records, callable directly or through an LLM-mediated conversational catechism.

This much is technical. The methodological move worth naming up front is reflexive: **`ant-rdf` is itself an assemblage of the kind that material-semiotic analysis is built to interrogate**. Ethnographers, ANT/STS scholars, a Python toolchain, an LLM mediator, deterministic Turtle, SHACL constraints, GitHub Actions, a hyperlinked wiki, and the cases being studied are not external supports to an otherwise neutral instrument. They are the actants whose webs of relations *produce* the analytical work that gets attributed to "the ethnographer's reading" downstream.

Taking that observation seriously has three operational consequences:

1. **The toolkit is a prosthesis**, in the literal Latourian sense. It changes what it amplifies. Treating it as a neutral instrument would itself be a category mistake — the exact mistake material-semiotics refuses. Every analysis produced through `ant-rdf` is an analysis produced *via* a particular apparatus with specific affordances: catechism prompts that nudge toward particular framings, SHACL shapes that surface certain absences, a CC0 vocabulary that pre-defines the analyst's terms, a deterministic-Turtle invariant that mistrusts blank-node identity. These cannot be assumed neutral; they have to be accounted for in the same documents that report findings.

2. **Validation proceeds in three tiers**, not one. Reproducing the canonical cases the source texts already analysed (the *training set* — the St Brieuc scallops, Latour's hotel-keys, the Portuguese maritime network, *The Body Multiple*'s atherosclerosis enactments) is the lowest bar. Cases not used to develop these theories or this repo (the *testing set* — Akrich's de-scription, the Zimbabwe bush pump, contemporary STS fieldwork) test generalisation. Only after a documented assessment of model adequacy with strengths and weaknesses spelled out is the toolkit permitted to produce *novel* ethnographic claims; those claims must reason about machine mediation within the analysis itself.

3. **Comparison studies are the key future research thread.** Paired analyses of the same field site — one with and one without the `ant-rdf` prosthesis, by collaborating teams that exchange materials but maintain methodological independence until comparison — will surface what is *gained*, *lost*, and (most consequentially) *transformed* by machine mediation. The methodological commitment is that comparison-study reports are co-authored across both methods; neither is permitted to grade itself.

4. **Git and RDF/SHACL are canonically complementary, and the commit history of this repository is itself a research artifact.** Git records *change as time-ordered authored events* — who altered which file, when, and (via the message) why. RDF + SHACL records *state as structured validated relations* — what holds, between which entities, conforming to which shapes. Each answers questions the other can't: git tells you the history of an analysis without telling you what the analysis says; RDF tells you what the analysis says without telling you how it came to say that. Held together, they let a reader reconstruct both *the structure of the field as currently read* and *the trajectory by which that reading was reached*. This complementarity was tested empirically in [flexo-conflict-resolution-policy-research/experiments/](https://github.com/Open-MBEE/flexo-conflict-resolution-policy-research/tree/main/experiments) (Zargham et al., 2026 — see arc 14–20 specifically), and `ant-rdf` inherits the finding rather than re-deriving it. Practically: as the prosthesis evolves under use, its commit history becomes data for the comparison-study programme — the toolkit transforming-as-it-is-applied is observable in the repo itself, alongside the cases it mediates.

The repository is therefore both an instrument and an object of study — a self-instrumented experiment in machine-mediated material-semiotic analysis. It ships v1 as a minimalist seedbed: enough mechanics in place to author cases end-to-end, validate them, and render them as navigable briefs and wiki pages. What gets built next is what *use surfaces as necessary*, including the comparison-study programme that will tell us whether, when, and how the prosthesis is worth keeping.

## Lineage — a small pattern language

The docs-as-code paradigm this repo follows — versioned RDF as canonical source, deterministic compilers producing reviewable Markdown, an LLM-callable CLI as authoring surface, three-tier SHACL severity with waivers as recorded analytical decisions — is a pattern that has been developed across several repositories before landing here. Direct ancestors include [Open-MBEE/flexo-conflict-resolution-policy-research](https://github.com/Open-MBEE/flexo-conflict-resolution-policy-research) (Zargham et al., 2026 — the empirical foundation for the git/RDF complementarity claim above) and the [`RIME-product-docs`](https://github.com/dynamicalsystems-group/RIME-product-docs) pattern exemplar from which `ant-rdf` borrows its MVC structure and the verify/compile/wiki discipline.

The pattern is *replicating* across these repos because its ergonomics suit the kind of accountability that contemporary LLM-mediated work — being adopted widely and frequently mindlessly — has so far avoided. By forcing every claim through a versioned, validatable, reviewable artifact, the pattern adds rigour, reproducibility, and explainability without requiring the analyst to be sceptical of the LLM at every moment. We name this a small *pattern language* (in the Christopher Alexander sense) deliberately: the pattern is not specific to any one domain, and each new repository it instantiates contributes back to the language's shared affordances. `ant-rdf` is the latest iteration; the comparison-study programme is, in part, a stress-test of whether the pattern itself holds up under sustained ethnographic use.

---

The eight ontological commitments that ground the vocabulary are in [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md); the ten resolved foundational decisions are in [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md); the scope-out items, the three-tier validation regime, and the comparison-study programme are in [FUTURE_WORK.md](FUTURE_WORK.md). The two worked cases that exist today — Callon's scallops and Latour's hotel-keys — are in [instances/cases/](instances/cases/), compiled to briefs in [briefs/](briefs/), and navigable through the [wiki](wiki/).

_Source: [`abstract.md`](https://github.com/mzargham/ant-rdf/blob/main/abstract.md) in the main repo. Regenerated into this Home page by `ant wiki`._

---

## Navigation

Hyperlinked traversal of the canonical RDF in `instances/`. Every actant, translation, characterization, and perspective is a click away — and every concept on the right is a glossary entry with a citation to its founding text.

## Cases

- **[hotel-keys](Cases/hotel-keys.md)** — The hotel-keys assemblage
  > The network of hotel manager, guests, front-desk staff, key, weighted fob, and request sign analyzed by Latour (1991) in 'Technology is society made durable'. The fob translates the moral injunction 'please return your key' into a physical …
- **[scallops](Cases/scallops.md)** — St Brieuc Bay scallop-farming network
  > The heterogeneous network Michel Callon analyzed in 'Some Elements of a Sociology of Translation' (1986). Three researchers from the Brest Oceanographic Centre attempt to enrol scallops, fishermen of St Brieuc Bay, and scientific colleagues…

## Actants by case

### hotel-keys

- [Weighted brass fob](Actants/hotel-keys--fob.md)
- [Front-desk staff](Actants/hotel-keys--front-desk.md)
- [Hotel guest](Actants/hotel-keys--guest.md)
- [The hotel building](Actants/hotel-keys--hotel.md)
- [Room key](Actants/hotel-keys--key.md)
- [Hotel manager](Actants/hotel-keys--manager.md)
- [Polite request sign](Actants/hotel-keys--sign.md)

### scallops

- [Scientific colleagues](Actants/scallops--colleagues.md)
- [Fishermen of St Brieuc Bay](Actants/scallops--fishermen.md)
- [Larvae collectors (towlines)](Actants/scallops--larvae-collectors.md)
- [Three researchers from Brest](Actants/scallops--researchers.md)
- [Scallops (Pecten maximus)](Actants/scallops--scallops.md)

## Translations

- [The hotel-keys translation chain](Translations/hotel-keys--main.md) _(case: [hotel-keys](Cases/hotel-keys.md))_
- [The Callon-1986 translation chain](Translations/scallops--main.md) _(case: [scallops](Cases/scallops.md))_

## Perspectives

- [hotel-keys::_default](Perspectives/hotel-keys--_default.md)
- [scallops::_default](Perspectives/scallops--_default.md)

## Concepts (the ontology as a glossary)

Every term below renders as a page with `rdfs:comment` and `dcterms:source` to a founding text.

**Classes**

- [Actant](Concepts/Actant.md)
- [Analysis](Concepts/Analysis.md)
- [AnalysisReport](Concepts/AnalysisReport.md)
- [AntiProgram](Concepts/AntiProgram.md)
- [BlackBox](Concepts/BlackBox.md)
- [Characterization](Concepts/Characterization.md)
- [ConstraintWaiver](Concepts/ConstraintWaiver.md)
- [DiscursiveStability](Concepts/DiscursiveStability.md)
- [Durability](Concepts/Durability.md)
- [Enrolment](Concepts/Enrolment.md)
- [ImmutableMobile](Concepts/ImmutableMobile.md)
- [Inscription](Concepts/Inscription.md)
- [Interessement](Concepts/Interessement.md)
- [Intermediary](Concepts/Intermediary.md)
- [MaterialDurability](Concepts/MaterialDurability.md)
- [Mediator](Concepts/Mediator.md)
- [Mobilization](Concepts/Mobilization.md)
- [ModeOfOrdering](Concepts/ModeOfOrdering.md)
- [Network](Concepts/Network.md)
- [ObligatoryPassagePoint](Concepts/ObligatoryPassagePoint.md)
- [Perspective](Concepts/Perspective.md)
- [Practice](Concepts/Practice.md)
- [Problematization](Concepts/Problematization.md)
- [ProgramOfAction](Concepts/ProgramOfAction.md)
- [ProvAgent](Concepts/ProvAgent.md)
- [ProvInfluencer](Concepts/ProvInfluencer.md)
- [Scope](Concepts/Scope.md)
- [Spokesperson](Concepts/Spokesperson.md)
- [StrategicDurability](Concepts/StrategicDurability.md)
- [Translation](Concepts/Translation.md)

**Properties**

- [assignsRole](Concepts/assignsRole.md)
- [characterizes](Concepts/characterizes.md)
- [enrols](Concepts/enrols.md)
- [hasMoment](Concepts/hasMoment.md)
- [hasProgram](Concepts/hasProgram.md)
- [inscribes](Concepts/inscribes.md)
- [invarianceCriterion](Concepts/invarianceCriterion.md)
- [isPunctualizationOf](Concepts/isPunctualizationOf.md)
- [opposes](Concepts/opposes.md)
- [participatesIn](Concepts/participatesIn.md)
- [passesThrough](Concepts/passesThrough.md)
- [perPractice](Concepts/perPractice.md)
- [perspectiveGroundedIn](Concepts/perspectiveGroundedIn.md)
- [perspectiveHeldBy](Concepts/perspectiveHeldBy.md)
- [perspectiveTracksInvariance](Concepts/perspectiveTracksInvariance.md)
- [speaksFor](Concepts/speaksFor.md)
- [translates](Concepts/translates.md)
- [waivedBy](Concepts/waivedBy.md)
- [waiverExpires](Concepts/waiverExpires.md)
- [waiverJustification](Concepts/waiverJustification.md)
- [waivesForTarget](Concepts/waivesForTarget.md)
- [waivesShape](Concepts/waivesShape.md)
- [withinNetwork](Concepts/withinNetwork.md)

