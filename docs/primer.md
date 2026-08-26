<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Material semiotics in ten minutes — and one worked case

This is the primer for someone new to Actor-Network Theory (ANT) and its material-semiotic successors. It defines every term the toolkit uses, in the order you will meet them, and then reads one case — Callon's 1986 scallops of St Brieuc Bay — record by record. Where a term is contested or deliberately constrained here, the pointer goes to the commitment (C-number, in [ONTOLOGICAL_COMMITMENTS.md](../ONTOLOGICAL_COMMITMENTS.md)) or the decision (R-number in [ADR-0000](../adr/0000-foundational-decisions.md), or a later ADR in [adr/](../adr/README.md)) that records why.

One framing first: ANT is not a theory that explains why things happen. It is a *toolkit of sensibilities* for describing **how** heterogeneous things — people, animals, instruments, texts, organisations — get assembled into something that holds together for a while (Law 2008; **C1**). Everything below is vocabulary for telling that kind of story precisely.

## The vocabulary

### Actant

Anything that makes a difference in a network: a person, a scallop, a towline, a paper, a committee. The word is chosen over "actor" to refuse a split between humans who act and things that are acted upon — **generalized symmetry** (Callon 1986; **C2**). The toolkit never asks "is this a person or a thing?"; an `ant:Actant` is a row in the analyst's notebook, a methodological convenience, not a claim about what the thing *is* (**C3**, **R1**).

### Translation, and the four moments

A translation is the process by which one actant defines the identities and interests of others so that they come to act together (Callon 1986). It has four moments, which the toolkit records as four subclasses of `ant:Translation` linked from the translation by `ant:hasMoment`:

| Moment | The move |
|---|---|
| **Problematization** | someone defines the problem and positions themselves as indispensable to its solution |
| **Interessement** | the alternatives are cut off — other associations the actants might have made are blocked |
| **Enrolment** | each actant accepts (or resists) the role scripted for it |
| **Mobilization** | spokespersons emerge who speak for the assembled network in public |

Translations can fail, and networks unravel; durability is achieved, never given (**C5**). So a translation is "done" not when it is permanent but when a new behavioral regularity has stabilized. The toolkit records that standing as a **status** — stabilized, precarious, unravelled — and treats the *absence* of a status as a fourth, deliberate state: *forming / not yet assessed* ([ADR-0002](../adr/0002-cross-frame-links-and-status.md)).

### Mediator vs intermediary — and the invariance that decides it

Latour (2005): an **intermediary** transmits without transformation — what comes out can be predicted from what goes in; a **mediator** transforms what it carries — outputs cannot be predicted from inputs. The toolkit adds one clarifying question, because both roles serve something held constant: *which invariance are you tracking?* An intermediary preserves the invariant by passing it through unchanged; a mediator preserves it by *regulating* — varying other dimensions in order to keep this one constant. The same actant can be both, on different dimensions, at the same time; it is the observer's practice that selects which dimensions are coded ([ADR-0006](../adr/0006-invariance-variance-coding-axis.md)). That is why the briefs render the criterion through the role: "passes through: X" vs "regulates to preserve: X".

### Characterization, perspective, practice — observer-relativity

The load-bearing record of the toolkit. A **Characterization** is a reified statement: *this actant* is read as *this role* — Mediator, Intermediary, Spokesperson, Obligatory Passage Point, or a PROV agent/influencer — *within this network*, *from this practice*, *tracking this invariance*. Roles are values inside a Characterization, never types on the actant (**R3**, **R6**): the toolkit will never let you write "X is a Mediator", only "under practice P, X is characterized as a Mediator".

A **Practice** is the enacting frame the reading comes from — experimental oceanography, seasonal fishing labor, hotel administration (**C4**: practices enact realities). A **Perspective** is provenance: who holds the reading (`perspectiveHeldBy`), from which practice (`perspectiveGroundedIn`), tracking which invariance (`perspectiveTracksInvariance`). Several perspectives can read the same field site, and may disagree; the toolkit keeps them apart (**C6**, [ADR-0001](../adr/0001-perspective-isolation-named-graphs.md)) and links each translation to the perspective it was authored under ([ADR-0004](../adr/0004-graph-derivable-translation-frame.md)). Agreement across perspectives is a finding, not objectivity.

### Inscription, immutable mobile, fluid object

An **inscription** is a material trace that circulates between actors — a chart, a paper, a register (Latour 1987, 1990). An **immutable mobile** holds its form constant while it travels and so enables action at a distance (Law 1986: Portuguese ships, charts, almanacs). A **fluid object** persists the other way — by controlled mutability, keeping identity and lineage while its content changes, so it can be absorbed and redirected (de Laet & Mol 2000: the Zimbabwe bush pump; a living git repository). The toolkit records who **produces** an inscription (`ant:inscribes`) separately from who **draws on** it (`ant:drawsOn`), because drawing on a fluid object may alter it while an immutable mobile is left unchanged — the same invariance/variance axis as mediator/intermediary, on the trace itself ([ADR-0005](../adr/0005-fluid-objects-and-material-carry-forward.md)).

### Obligatory passage point (OPP)

An actant every other actant must pass through to realise its interests (Callon 1986). It is an *emergent attribute*, not a kind of thing: assigned by a Characterization, within a network and a practice, never as a type (**R6**). The toolkit can then trace which translations must clear a given passage (`ant:tracesToPassage`).

### Durability and status

Two different questions about a holding configuration. **Durability** is *how* it holds — delegated into material form, held by deliberate strategic design, or by multi-discursive ordering (Law 1994, 2008: `MaterialDurability`, `StrategicDurability`, `DiscursiveStability`). **Status** is *whether* it holds — stabilized, precarious, unravelled, or not yet assessed. Both are recorded on the translation.

### A trace can act (C9)

An inscription and an actant are not disjoint categories: the same worldly thing can be both, read in two registers. A frozen document merely circulates; a living repository *acts*, because it keeps changing under governed control — the immutable→fluid shift is what confers agency. The toolkit records the coexistence explicitly with `ant:manifestsAs`, never infers it (**C9**, [ADR-0007](../adr/0007-inscriptions-can-be-actants-manifests-as.md)).

## The worked case: scallops, read record by record

Everything below is in `instances/cases/scallops/perspectives/_default/` and can be checked with the commands shown. The compiled brief is [briefs/scallops-network.md](../briefs/scallops-network.md); the wiki page is [wiki/Case-scallops.md](../wiki/Case-scallops.md).

**The network** (`network`, in `networks.ttl`) — "St Brieuc Bay scallop-farming network": three researchers from the Brest Oceanographic Centre attempt to enrol scallops, fishermen and scientific colleagues into a programme to domesticate *Pecten maximus* with a harvesting technique borrowed from Japan; the translation succeeds for several seasons before fishermen trawl the protected larvae grounds and the web unravels. A Network record is the analyst's named summary of an assemblage — not a container the actants sit in (**R5**).

**The actants** (`actants.ttl`) — five, entered on the same terms (C2): `researchers` (the three oceanographers who problematize the decline and propose the experiment), `scallops` (whose larvae must anchor for the network to succeed), `fishermen` (whose forbearance from trawling is what the translation requires), `larvae-collectors` (the towlines with anchoring substrate borrowed from Japanese practice), and `colleagues` (the wider scientific community whose acceptance is the final mobilization condition). Each `participatesIn` the network.

**The translation** (`translation/main`, in `translations.ttl`) — "The Callon-1986 translation chain", authored under the case's one perspective, with all four moments (`moments.ttl`):

- `moment/problematization` — the researchers define the problem (declining, unstudied populations) and position themselves as indispensable by making fishermen and scallops pass through their apparatus;
- `moment/interessement` — competing alternatives are cut: fishermen are negotiated out of trawling the protected zones, and the collectors are designed so larvae cannot anchor anywhere else;
- `moment/enrolment` — scallops anchor in significant numbers (some seasons), fishermen accept the no-trawl zones, colleagues accept the results;
- `moment/mobilization` — the researchers speak for the scallops (anchoring counts), the fishermen (community acceptance) and the bay itself — "the network speaks with one voice — until it doesn't."

The translation's own description records the ending: ultimately precarious, "a single winter's trawling unravels the web." Note that the record carries no `hasStatus`: it is *forming / not yet assessed* in the toolkit's terms, because the ethnographer has not yet coded it — and the toolkit does not code it for them. (Doing so is one `ant edit-record translation --status unravelled` away, and is the ethnographer's call.)

**The flip** (`characterizations.ttl`) — the case's central lesson, and the toolkit's central move (R3). The larvae collectors carry two Characterizations on one actant:

- `char/collectors-as-intermediary` — under `practices/experimental-oceanography`, tracking `anchoring-substrate-as-designed`: the collectors transmit the Japanese anchoring technique without transformation;
- `char/collectors-as-mediator` — under `practices/seasonal-fishing-labor`, tracking `rhythms-of-bay-work`: the same collectors reframe stretches of bay as off-limits and restructure the rhythm of fishing work.

Same actant, two roles, no contradiction — because each is read from a named practice against a named invariant. Check it: `uv run ant query roles larvae-collectors`.

**The passage and the voice** — `char/researchers-as-opp` characterizes the researchers as the obligatory passage point under `practices/network-funding` (invariant `resource-allocation-routing`: every actant passes through those who control the experimental design and publication rights); `char/researchers-as-spokesperson` characterizes the same researchers as Spokesperson under `practices/scientific-publication` (invariant `citational-credit`), the role that emerges in the mobilization moment.

**Why scallops gets only one brief.** The case's perspective is the auto-created `_default` stub (`_perspective.ttl`): it has a holder placeholder but is grounded in no practice. `ant refresh scallops` therefore writes just the network brief and the cross-case catalog; the reader set (guide, synopsis, positionality, …) needs a grounded perspective, and the cross-frame views need two. The **koi** case is the multi-perspective example — two grounded perspectives reading one field site, with flips between them: start at [briefs/koi-guide.md](../briefs/koi-guide.md).

## Where each concept lives

| Concept | Term(s) | Founding text | Commitment / decision |
|---|---|---|---|
| Actant, generalized symmetry | [`Actant`](../wiki/Concept-Actant.md) | Callon 1986; Latour 2005; Law 2008 | C2, C3, R1 |
| Translation, four moments | [`Translation`](../wiki/Concept-Translation.md), `Problematization`, `Interessement`, `Enrolment`, `Mobilization` | Callon 1986 | C5, R4 |
| Status, forming | [`TranslationStatus`](../wiki/Concept-TranslationStatus.md), `hasStatus` | Callon 1986; Law 2008 | ADR-0002 |
| Mediator, intermediary, invariance | [`Mediator`](../wiki/Concept-Mediator.md), [`Intermediary`](../wiki/Concept-Intermediary.md), [`invarianceCriterion`](../wiki/Concept-invarianceCriterion.md) | Latour 2005 | R3, ADR-0006 |
| Characterization | [`Characterization`](../wiki/Concept-Characterization.md) | synthesized, post-Law 2008 | R3, C4 |
| Perspective, practice | [`Perspective`](../wiki/Concept-Perspective.md), [`Practice`](../wiki/Concept-Practice.md), `authoredUnder` | Mol 2002; Law 2008 | C4, C6, R9a, ADR-0001, ADR-0004 |
| Inscription, immutable mobile, fluid object | [`Inscription`](../wiki/Concept-Inscription.md), [`ImmutableMobile`](../wiki/Concept-ImmutableMobile.md), [`FluidObject`](../wiki/Concept-FluidObject.md), `inscribes`, `drawsOn` | Latour 1990; Law 1986; de Laet & Mol 2000 | ADR-0005 |
| Obligatory passage point | [`ObligatoryPassagePoint`](../wiki/Concept-ObligatoryPassagePoint.md), `tracesToPassage` | Callon 1986 | R6, ADR-0002 |
| Durability | [`Durability`](../wiki/Concept-Durability.md) and its three forms, `hasDurability` | Law 1994, 2008 | C5, ADR-0002 |
| Programs and anti-programs | [`ProgramOfAction`](../wiki/Concept-ProgramOfAction.md), `opposes`, `hasProgram` | Latour 1991 | — |
| A trace can act | [`manifestsAs`](../wiki/Concept-manifestsAs.md) | de Laet & Mol 2000; Latour 1987 | C9, ADR-0007 |
| Spokesperson | [`Spokesperson`](../wiki/Concept-Spokesperson.md) | Callon 1986 | — |

Every concept page in the wiki carries the ontology's definition and the founding-text citation (**R9**). The full list is on [wiki/Home.md](../wiki/Home.md).

Next: [docs/toolchain.md](toolchain.md) to install and author; [docs/facilitation.md](facilitation.md) to run a session with an ethnographer.
