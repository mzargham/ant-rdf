# About ant-rdf — a material-semiotic reading of this repository

[← Home](Home.md)

`ant-rdf` is a docs-as-code semantic-web vocabulary and authoring toolkit for actor-network / material-semiotic analysis, synthesising Callon's sociology of translation, Latour's classical ANT, and post-ANT material semiotics (Law, Mol). The canonical form of every record is RDF (Turtle in the [`https://w3id.org/ant#`](https://w3id.org/ant) namespace); compilers render the canonical RDF into reviewable Markdown briefs and a hyperlinked wiki; a Python CLI authors the records, callable directly or through an LLM-mediated conversational catechism.

This much is technical. The methodological move worth naming up front is reflexive: **`ant-rdf` is itself an assemblage of the kind that material-semiotic analysis is built to interrogate**. Ethnographers, ANT/STS scholars, a Python toolchain, an LLM mediator, deterministic Turtle, SHACL constraints, GitHub Actions, a hyperlinked wiki, and the cases being studied are not external supports to an otherwise neutral instrument. They are the actants whose webs of relations *produce* the analytical work that gets attributed to "the ethnographer's reading" downstream.

Taking that observation seriously has three operational consequences:

1. **The toolkit is a prosthesis**, in the literal Latourian sense. It changes what it amplifies. Treating it as a neutral instrument would itself be a category mistake — the exact mistake material-semiotics refuses. Every analysis produced through `ant-rdf` is an analysis produced *via* a particular apparatus with specific affordances: catechism prompts that nudge toward particular framings, SHACL shapes that surface certain absences, a CC0 vocabulary that pre-defines the analyst's terms, a deterministic-Turtle invariant that mistrusts blank-node identity. These cannot be assumed neutral; they have to be accounted for in the same documents that report findings.

2. **Validation proceeds in three tiers**, not one. Reproducing the canonical cases the source texts already analysed (the *training set* — the St Brieuc scallops, Latour's hotel-keys, the Portuguese maritime network, *The Body Multiple*'s atherosclerosis enactments) is the lowest bar. Cases not used to develop these theories or this repo (the *testing set* — Akrich's de-scription, the Zimbabwe bush pump, contemporary STS fieldwork) test generalisation. Only after a documented assessment of model adequacy with strengths and weaknesses spelled out is the toolkit permitted to produce *novel* ethnographic claims; those claims must reason about machine mediation within the analysis itself.

3. **Comparison studies are the key future research thread.** Paired analyses of the same field site — one with and one without the `ant-rdf` prosthesis, by collaborating teams that exchange materials but maintain methodological independence until comparison — will surface what is *gained*, *lost*, and (most consequentially) *transformed* by machine mediation. The methodological commitment is that comparison-study reports are co-authored across both methods; neither is permitted to grade itself.

4. **Git and RDF/SHACL are canonically complementary, and the commit history of this repository is itself a research artifact.** Git records *change as time-ordered authored events* — who altered which file, when, and (via the message) why. RDF + SHACL records *state as structured validated relations* — what holds, between which entities, conforming to which shapes. Each answers questions the other can't: git tells you the history of an analysis without telling you what the analysis says; RDF tells you what the analysis says without telling you how it came to say that. Held together, they let a reader reconstruct both *the structure of the field as currently read* and *the trajectory by which that reading was reached*. This complementarity was tested empirically in [flexo-conflict-resolution-policy-research/experiments/](https://github.com/Open-MBEE/flexo-conflict-resolution-policy-research/tree/main/experiments) (Zargham et al., 2026 — see arc 14–20 specifically), and `ant-rdf` inherits the finding rather than re-deriving it. Practically: as the prosthesis evolves under use, its commit history becomes data for the comparison-study programme — the toolkit transforming-as-it-is-applied is observable in the repo itself, alongside the cases it mediates.

The repository is therefore both an instrument and an object of study — a self-instrumented experiment in machine-mediated material-semiotic analysis. It ships v1 as a minimalist seedbed: enough mechanics in place to author cases end-to-end, validate them, and render them as navigable briefs and wiki pages. What gets built next is what *use surfaces as necessary*, including the comparison-study programme that will tell us whether, when, and how the prosthesis is worth keeping.

---

## Where this continues

- [Theoretical Frame](Theoretical-Frame.md) — AOI / building-the-loop framing and DSG's self-infrastructuring
- [Lineage](Lineage.md) — the small pattern language `ant-rdf` extends

## Further reading

The eight ontological commitments that ground the vocabulary are in [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md); the ten resolved foundational decisions are in [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md); the scope-out items, the three-tier validation regime, and the comparison-study programme are in [FUTURE_WORK.md](FUTURE_WORK.md); the AOI / "building the loop" theoretical frame is developed at length in Rennie et al. (2026), [DOI:10.1111/epic.70009](https://doi.org/10.1111/epic.70009). The two worked cases that exist today — Callon's scallops and Latour's hotel-keys — are in [instances/cases/](instances/cases/), compiled to briefs in [briefs/](briefs/), and navigable through the [wiki](wiki/).
