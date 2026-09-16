<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Ontological commitments (C1–C9)

The vocabulary in this repo is built on nine explicit commitments — synthesized from Callon's sociology of translation, Latour's classical ANT, and Law/Mol post-ANT material semiotics. These are the philosophical premises a contributor is opting into when they author records, write SHACL shapes, or extend the ontology. They are also what `ant verify` and the wiki render are *implicitly* documenting in every artifact they produce.

Every contentious commitment names the founding-text move it inherits. Pushback from the expert call should be on whether the *commitment* lands correctly, not whether we got Latour/Callon/Law/Mol "right" — those debates are settled here by citation, not arbitration.

---

## C1 — Material semiotics is a toolkit, not a theory

ANT/material-semiotics is *descriptive*, not foundational. The vocabulary is for **telling stories about how** relations assemble; it does not **explain why**.

*Source:* Law (2008): "Actor network theory is not a theory. Theories usually try to explain why something happens, but actor network theory is descriptive rather than foundational in explanatory terms."

*What this means in practice:*

- The compilers produce **briefs and traces**, not explanatory accounts.
- SHACL shapes encode *analytical hygiene*, not *truth tests*.
- A `dcterms:source` field on every term acknowledges that we inherit from specific texts, not from a foundational metaphysics.

---

## C2 — Generalized symmetry

Humans, non-humans, objects, texts, animals, ideas, organizations enter the analysis in the same terms. The vocabulary refuses pre-categorical splits.

*Source:* Callon's "generalized symmetry" (1986), extended by Latour (1991, 2005) and Law (2008).

*What this means in practice:*

- `ant:Actant` has **no** `ant:HumanActant` / `ant:NonHumanActant` subclasses (those would be exactly the asymmetry ANT rejects).
- The CLI catechism does not ask "is this a person or an object?" — that question is post-network, not pre-network.
- `prov:Agent`'s "bears responsibility" framing is **deliberately not** imported as a global typing claim on `ant:Actant` — see C7 and R2 in [ADR-0000](adr/0000-foundational-decisions.md).

---

## C3 — Relationality is primary

Actants are *effects* of webs of relations, not pre-existing entities with intrinsic properties. The class `ant:Actant` is a **methodological convenience** for the analyst — a label on a row in the analyst's notebook — not an ontological declaration about the world.

*Source:* Law (2008): "Webs of materially heterogeneous relations that produce and reshuffle all kinds of actors including objects, subjects, human beings, machines, animals, 'nature,' ideas, organizations, inequalities, scale and sizes, and geographical arrangements."

*Tension this creates:*

Writing `:x a ant:Actant` is *technically* a pre-categorization — exactly what Latour's flat ontology resists. We accept the cost: the vocabulary needs a class for the CLI and compilers to operate on. The mitigation is to document the methodological status of `ant:Actant` everywhere it appears (which is what `rdfs:comment` on the class does).

*Expected pushback from the expert call:* "You've reified what should be flat." Acknowledged. The cost is purchased by the analytical leverage that comes with first-class records.

---

## C4 — Performativity / enactment over construction

Practices **enact** realities; we model enactments, not constructions. There is no `ant:socially_constructs` property. There are practices that produce more-or-less precarious realities.

*Source:* Mol (2002), *The Body Multiple*; Law (2008): "Something seismic is happening here. We are no longer dealing with construction… Rather we are dealing with enactment or performance."

*What this means in practice:*

- `ant:Practice` is a first-class class, not a property modifier.
- `ant:Characterization` (the reified role-assignment mechanism, R3) carries `ant:perPractice` to make the *enacting practice* explicit on every observer-relative claim.
- The CLI does not ask "what social context produced this?" — it asks "from within which practice are you describing this?"

---

## C5 — Precariousness and process

Translations can fail. Networks unravel. Durability is achieved, never given. The vocabulary makes this visible — every association is in principle contestable.

*Source:* Callon (1986) on the St Brieuc scallops: "All it takes is for one translation to fail and the whole web of reality unravels." Law (2008): "Translation is always insecure, a process susceptible to failure."

*What this means in practice:*

- `ant:Translation` is `rdfs:subClassOf prov:Activity` (under optional PROV alignment) — a process, not a static relation.
- The Tier-2 SHACL warning that translations *should* have all four moments lets analysts ship translations that **failed** (with a waiver naming the moment of failure) — modeling unraveling, not just successful enrolment.
- `ant:Durability` and its subclasses (`MaterialDurability`, `StrategicDurability`, `DiscursiveStability`) per Law 2008 make *how* networks hold first-class.

---

## C6 — Multiplicity and partial connection (v2-ready via quad-ready v1)

Different perspectives / analysis scopes on the same field site may be **simultaneously valid even when otherwise contradictory** — Mol's multiplicity and Law's modes of ordering. The v2 ontology lifts this into named graphs over a quadstore.

**v1 is quad-ready** — every assertion already carries the perspective it was authored under, and the file-system + IRI conventions name the graphs v2 will instantiate. The v1→v2 transition is mechanical, not a rewrite. Until then the single-graph discipline of [ADR-0001](adr/0001-perspective-isolation-named-graphs.md) is in force: a shared actant's identity is frame-neutral and byte-identical (guarded at Tier-1, [ADR-0003](adr/0003-shared-actant-home-and-identity-guard.md)), and every translation is attributed to its perspective in the graph ([ADR-0004](adr/0004-graph-derivable-translation-frame.md)).

*Source:* Mol (2002), *The Body Multiple*; Strathern (1991), *Partial Connections*; Law (2008).

*What this means in practice:*

- `ant:Perspective` is a first-class v1 class. Its IRI string *is* the named-graph URI v2 will use (no migration step changes IRIs).
- Records live under `instances/cases/<case>/perspectives/<slug>/` — the directory layout is the v2 graph shape; v1 flattens on load.
- `graph.py` uses `rdflib.Dataset` (quad-capable) from day one. The v1→v2 switch is one `publicID` argument.
- **v1 partial down-payment on multiplicity:** reified `ant:Characterization` (R3) lets the same actant carry incompatible role-assignments (e.g., Mediator under one practice, Intermediary under another) without OWL inconsistency — *before* quad activation. See [the scallops case](instances/cases/scallops/) for a worked example.

---

## C7 — Verification is machine; validation is human; severity is tiered

The CLI guarantees **structural correctness** of RDF (SHACL Tier-1 Violations, cross-reference resolution, deterministic Turtle) regardless of which ingestion mode produced the triples. The ethnographer / domain expert is responsible for **content correctness**.

Between these sit **Tier-2 Warnings** — analytical hygiene that should not be violated silently but may be waived with a justification when the analyst has good reason.

*Source:* RIME's V&V terminology (verification/validation distinction), extended with the tri-severity SHACL audit (R9b in [ADR-0000](adr/0000-foundational-decisions.md)).

*What this means in practice:*

- `ant verify` exits non-zero on Tier-1 Violations; surfaces but does not break on Tier-2 Warnings.
- `ant:ConstraintWaiver` is append-only, with required `ant:waiverJustification`. Tier-1 waivers are rejected by `ant verify`. No co-sign required; no default expiry.
- The CLI does not auto-assert ethnographic claims. Auto-extraction always lands as **candidate** triples requiring human confirmation (per `ant ingest notes` dry-run pattern).
- CI default per R9b: warnings surface in the log but do not break the build. Teams that want stricter gating use `ant verify --strict`.

---

## C8 — Plural ingestion paths

Ethnographers ingest material through multiple channels: live conversational catechism with an LLM; structured-note import from existing markdown/text fieldnotes; bulk upload of raw materials (PDFs, transcripts, audio, image references) as inscription-instances pending later characterization; direct CLI flag-driven authoring by experts who prefer it.

**All paths land in the same RDF graph and pass the same SHACL bar.** The conversational catechism is *one* path, not *the* path.

*Source:* Synthesized for this toolkit (ADR-0000) and user-confirmed.

*What this means in practice:*

- The CLI has one mechanism (`new_record.create_*`) and multiple front-ends (catechism prompts, flags, ingest-from-notes, ingest-from-upload).
- The conversational skill (`ant-mgmt`) explicitly offers an off-ramp to other ingestion paths at every step.
- LLM-callable surfaces are the same surfaces a human can call directly — no "human mode" vs "LLM mode" split.
- Uploaded raw materials are first-class `ant:Inscription` instances with file-hash provenance; characterization (role assignments within specific perspectives) is a separate later step. This decouples "I have a PDF / photo / audio" from "I have analyzed it."

---

## C9 — Inscriptions can be actants (the trace register and the actor register are non-disjoint)

An inscription (a material trace) and an actant (a thing that acts) are not disjoint categories: the same worldly entity can be both, read in two parallel registers. This generalizes the C2 symmetry move (humans and non-humans enter on the same terms) and C3 relationality (objects, subjects, machines are all actors) to a second axis — the trace-versus-actor axis.

The shift that lets an inscription act is **immutable → fluid**. A frozen document (an `ant:ImmutableMobile`) merely circulates, holding its form; a living git repository (an `ant:FluidObject`) acts, because it keeps changing under governed control. In a docs-as-code paradigm repositories supplant frozen documents as the knowledge-carrying artifact precisely because their livingness confers agency — conditioned on the verification machinery (C7) that makes a living artifact trustworthy. So a repository is at once an inscription (a named material trace that circulates) and an actant (a live node that acts).

*Source:* Law, J. (2008), generalized symmetry (objects, subjects, machines are actors); Latour, B. (1987, *Science in Action*; 2005, *Reassembling the Social*), inscriptions act at a distance; de Laet, M. & Mol, A. (2000), the living fluid object has agency.

*What this means in practice:*

- The two classes carry no `owl:disjointWith`; a node may be typed both, and the same entity may be named in both registers. The `ant-gvrn` skill refuses to add the disjointness.
- The coexistence is never inferred or forced; it is asserted, optionally, with `ant:manifestsAs` (an actant is manifested as an inscription) — see [ADR-0007](adr/0007-inscriptions-can-be-actants-manifests-as.md).
- The relation is directional in authoring (actant → inscription) but recoverable both ways by querying the subjects of `ant:manifestsAs`.
- It is the immutable→fluid shift, not the fact of being code, that makes a trace an actor: prefer `ant:FluidObject` ([ADR-0005](adr/0005-fluid-objects-and-material-carry-forward.md)) for the inscription side when the thing persists by mutation; the same invariance/variance axis governs the Mediator–Intermediary reading ([ADR-0006](adr/0006-invariance-variance-coding-axis.md)).

---

## How to push back on these commitments

Each commitment is held with humility (per C1). If you disagree with one:

1. Open an issue tagged `commitment`. Name the commitment (C1–C9).
2. Cite the founding text passage you think we've misread, or the analytical move you think is foreclosed.
3. Propose how the vocabulary, CLI, or compilers should change.

The commitments are revisable. [ADR-0000](adr/0000-foundational-decisions.md) records the resolutions that led to the current ones (`R1–R10`, with `R8a`, `R9a`, `R9b`), and [adr/README.md](adr/README.md) indexes the later decisions. If a commitment is revised, both files must be updated in the same commit.
