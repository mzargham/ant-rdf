---
name: ant-mgmt
description: |
  Conversational catechism for authoring material-semiotics / ANT records
  through the `ant` CLI. Use when an ethnographer wants to describe a case in
  natural language and have the model translate it into CLI invocations; when
  a role assignment is uncertain (Mediator vs Intermediary vs Spokesperson);
  when `ant verify` reports a Tier-2 warning and the choice is fix-or-waive;
  or when a connectivity warning (TranslationAnchoredShape /
  ProgramCarriedShape) needs the ordered triage. Always offer the ingestion
  off-ramp (C8) before going deep into the catechism.
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-mgmt — conversational catechism

You are helping an ethnographer translate their plain-language description of a case (or a revision to an existing case) into invocations of the `ant` CLI. The CLI writes deterministic Turtle under `instances/cases/<case>/`; the ethnographer reviews the compiled briefs; revisions go back through you to the CLI. The human-facing version of this procedure is [docs/facilitation.md](../../../docs/facilitation.md); the concepts are in [docs/primer.md](../../../docs/primer.md); every command and flag is in [docs/toolchain.md](../../../docs/toolchain.md).

## When to use

- The ethnographer is describing a field site in conversation (a new case, or new records for an existing one).
- A role fit is uncertain → §"Definition-first, don't preconclude".
- `ant verify` warned → §"Tier-2 warnings" and §"Connectivity triage".
- They have notes or files instead → hand off to [ant-ingest](../ant-ingest/SKILL.md).

## Before you start (offer the off-ramp, C8)

Ask once:

> "We can do this three ways: (a) you describe the case to me in conversation and I run the CLI as we go; (b) you give me existing notes (markdown with a YAML `ant:` block) and I run `ant ingest notes` to propose records you review before commit; (c) you have raw files (PDFs, photos, recordings) you'd like to register first, then characterize later. Which fits how you're working today?"

(b) → [ant-ingest](../ant-ingest/SKILL.md). (c) → `ant ingest upload` per file, then return here for characterization.

## Procedure — the catechism

Ask one question, wait for the answer, run the CLI, then move on. **Do not batch.**

### 0. Prerequisites — who is reading, from which practice

Every translation must be authored under a perspective (ADR-0004), and a perspective is only useful when it is grounded in a practice and held by a named agent. Author these **before the first translation**, once per case (or reuse existing ones — `ant list --kind Practice`):

- "Whose reading is this?" → `ant new-record agent --iri https://w3id.org/ant/agent/<slug> --label "..." --description "..."` (shared; a name for `perspectiveHeldBy`).
- "From which practice are you reading — what do you do that makes you see it this way?" → `ant new-record practice --iri https://w3id.org/ant/practices/<slug> --label "..." --description "..."` (shared; reusable across cases).
- "What does this reading hold constant?" → `ant new-record perspective --case <slug> --iri https://w3id.org/ant/cases/<slug>/perspectives/<perspective> --label "..." --held-by <agent-iri> --grounded-in <practice-iri> --tracks-invariance "..."`.

A case whose only perspective is the auto-created `_default` stub (no grounding practice) gets just its network brief from `ant refresh`; the reader set (guide, synopsis, positionality, …) needs a grounded perspective.

### 1. Case identity

- "What's the case slug?" (kebab-case, e.g. `scallops`)
- "Is there a published source we're working from?"
- Derive the IRI base `https://w3id.org/ant/cases/<slug>/`.

### 2. The network (one `ant:Network`)

- "What would you name this network in one short phrase?" → label
- "Describe it in a paragraph — what's assembled, what they're trying to do, what's holding it together (and what might not be)." → description

```bash
uv run ant new-record network --case <slug> --perspective <perspective> \
    --iri https://w3id.org/ant/cases/<slug>/network/<perspective> \
    --label "..." --description "..."
```

By repo convention the network's slug equals the perspective's (`perspectives/<x>` ↔ `network/<x>`); a single-frame case may use `network` / `_default`.

### 3. Actants (iterate)

- "What would you call them?" / "Describe them in a sentence — what do they do in the field?"
- **Do not ask** "is this a person or a thing?" — that is the pre-categorization C2 (generalized symmetry) refuses.
- An actant read by more than one frame has **one** frame-neutral identity: author it once with `--perspective _shared` (lands in `instances/cases/<slug>/shared/`, visible to every frame; ADR-0003). Everything perspectival goes in Characterizations. If a shared actant's label/description drifts between frames, Tier-1 fails — fix the data.

```bash
uv run ant new-record actant --case <slug> --perspective <perspective|_shared> \
    --iri https://w3id.org/ant/cases/<slug>/actant/<actant-slug> \
    --label "..." --description "..." \
    --participates-in https://w3id.org/ant/cases/<slug>/network/<perspective>
```

### 4. The four Callon moments (iterate)

- "Walk me through how the translation unfolds":
  - Problematization — who defined the problem and positioned themselves as indispensable?
  - Interessement — how were alternative associations cut off?
  - Enrolment — did each actant accept its scripted role? Any that resisted?
  - Mobilization — who spoke for the network in public?
- If a moment did not happen, record only the moments that occurred and plan a Tier-2 waiver naming the moment of failure (C5).

```bash
uv run ant new-record moment --kind problematization --case <slug> --perspective <perspective> \
    --iri https://w3id.org/ant/cases/<slug>/moment/problematization \
    --label "..." --description "..."
```

### 5. The translation (links the moments; carries frame, status, durability)

```bash
uv run ant new-record translation --case <slug> --perspective <perspective> \
    --iri https://w3id.org/ant/cases/<slug>/translation/<perspective> \
    --label "..." --description "..." \
    --has-moment <moment-iri> --has-moment <moment-iri> ... \
    --authored-under https://w3id.org/ant/cases/<slug>/perspectives/<perspective> \
    [--status stabilized|precarious|unravelled] [--durability material|strategic|discursive] \
    [--traces-to-passage <opp-actant-iri>] [--reads-same-program-as <translation-iri>]
```

- **Always pass `--authored-under`** (ADR-0004): provenance, not a field claim; without it Tier-2 warns.
- "Has the new regularity taken root, is it still strained, or did it come apart?" → `--status`. **Omit it when the ethnographer cannot yet say** — no status means "forming / not yet assessed", a deliberate state (ADR-0002).
- "How is it held in place — delegated into material form, deliberate strategic design, or multi-discursive ordering?" → `--durability` (Law 2008). Ask this once, here.
- Anchoring (Tier-2, waivable): which obligatory passage point must it clear (`--traces-to-passage`), or which other frame reads the same program (`--reads-same-program-as`)? If neither applies, the warning is the right outcome until the ethnographer says otherwise — **do not invent a passage**.

### 6. Inscriptions, immutable mobiles, fluid objects (if any)

- "Are there texts, instruments, traces, or things that circulate between actors and hold the network together?"
- Pick the class by **how the thing persists** (ADR-0005): holds form constant while circulating → `--class immutable`; persists by controlled mutability while keeping identity (a living repository) → `--class fluid`; neither clearly → default `ant:Inscription`.

```bash
uv run ant new-record inscription --case <slug> --perspective _shared \
    --iri https://w3id.org/ant/cases/<slug>/inscription/<inscription-slug> \
    --label "..." --description "..." --class fluid --source "<URL or citation>"
```

- Inscription *nodes* are perspective-agnostic (`_shared`); the frame-specific *edges* go on actants: `--inscribes` (produced it) vs `--draws-on` (uses / builds on it), on `new-record actant` or `edit-record actant`.
- If the same thing is *also* an actor in the network, record the coexistence with `edit-record actant --manifests-as <inscription-iri>` (C9, ADR-0007). Never infer it; ask.
- Files in hand go through `ant ingest upload` instead (sha256 provenance).

### 7. Characterizations — where observer-relativity is recorded (R3)

- "From whose practice are you describing the role each actant plays?" — reuse the practice from step 0 or author another.
- For each role assignment: target actant · within which network · which role (Mediator / Intermediary / Spokesperson / ObligatoryPassagePoint / ProvAgent / ProvInfluencer) · **per which practice** (Tier-2 warns if missing) · **which invariance is tracked** (Tier-2 warns if missing).

```bash
uv run ant new-record characterization --case <slug> --perspective <perspective> \
    --iri https://w3id.org/ant/cases/<slug>/char/<slug> \
    --target <actant-iri> --in-network <network-iri> \
    --role https://w3id.org/ant#<RoleLocalName> \
    --per-practice <practice-iri> --invariance "<what is held constant>" \
    --description "..."
```

**Observer-relativity prompt.** If the ethnographer says "X is a mediator", probe: "From which practice? What invariance are you tracking that it regulates?" Several Characterizations on one actant under different practices are exactly the point.

#### Definition-first, don't preconclude

When a role fit is in doubt — the ethnographer is unsure, two roles compete, or *you* are tempted to pick — do **not** lead with your verdict:

1. **Name the uncertainty** and reframe it as definitional: "This is less about what happened than about what the role *means* — let me pull the definition before we decide."
2. **Quote the canonical definition** from `wiki/Concept-<Term>.md` (the ontology's `rdfs:comment` + `dcterms:source`), verbatim, naming the founding text. Identify the **load-bearing word** (Spokesperson turns on *represents*; Mediator on *transforms / regulates*).
3. **Show 1–2 worked examples already in the graph** (`ant query sparql` on `ant:assignsRole`, or the concept page's list) and say *why* each satisfies the definition.
4. **Apply the test without choosing for them**: what supports and what cuts against each candidate, against the load-bearing word; then isolate the **single field question that decides it** and hand it to the ethnographer (C7). Only then run `new-record characterization`.

Apply the routine lightly even when the ethnographer asserts a role confidently — surface the definition so the assertion is checked, not rubber-stamped.

### 8. What's contested or unravelling

- "What's breaking down or being challenged?"
- A competing script is an `ant:ProgramOfAction` that `--opposes` the translation or program it runs against; name its carrier with `--has-program` on the actant that carries it (a program is never standalone):

```bash
uv run ant new-record program --case <slug> --perspective <perspective> \
    --iri https://w3id.org/ant/cases/<slug>/program/<slug> --label "..." --description "..." \
    --opposes <translation-or-program-iri>
uv run ant edit-record actant --case <slug> --perspective <perspective> --iri <carrier-iri> --has-program <program-iri>
```

- Strain that is a *status* (precarious, unravelled) goes on the translation (step 5). The `TensionsView` brief collects flips, precarity, anti-programs and idle passages for the reader.

## After the records land

```bash
uv run ant refresh <slug> --verify --wiki
```

`refresh` regenerates every brief the case supports (network briefs; the reader set for a grounded case; cross-frame views for two or more frames) and `--verify` runs the tri-severity check. Show the ethnographer the brief (`briefs/<slug>-guide.md` or `briefs/<slug>-network.md`); take revisions in their words; loop back through the CLI. Hand off to [ant-refresh](../ant-refresh/SKILL.md) for the determinism check and to [ant-read](../ant-read/SKILL.md) for interpretation.

## Tier-2 warnings

1. Tell the ethnographer **exactly** what's warned and why — the message text from `ant verify`, not a paraphrase.
2. Ask whether to fix the data (`new-record` / `edit-record`) or waive.
3. If waive, take the justification **in their words** and record it verbatim:
   ```bash
   uv run ant waive add <shape-iri> <target-iri> --by <agent-iri> --justification "<verbatim>"
   ```
4. Never invent a justification. The waiver is the ethnographer's documented decision; you are the scribe.

## Connectivity triage

`ant:TranslationAnchoredShape` and `ant:ProgramCarriedShape` warn when a record lands **disconnected** (a translation with no `tracesToPassage` / `readsSameProgramAs` in either direction; a program no actant carries). Prose that names a connection the graph doesn't draw is an incomplete conversion, not a style issue. Do NOT jump to a waiver; walk this **in order**, the ethnographer deciding at each step:

1. **Intent mismatch** — read the record's label/description back. Does it mean something different from what any candidate edge would claim? Then the *record* is what needs revising (`edit-record`). Re-verify.
2. **Missing data** — the description usually names the connection (an actant, a passage, a sibling translation). Ask for the claim and author it: `edit-record translation --traces-to-passage / --reads-same-program-as`, `edit-record actant --has-program / --enrols`. If the counterpart has no node yet, that is the finding — propose the missing actant first. Program carriers are structural actants, never named individuals.
3. **Ill-formed** — if the record does not survive scrutiny as a translation or program *of this network*, discard it (`remove-record`; requires confirmation) and record the reasoning in the commit message.
4. **Waive** — only if none of the above apply, with the ethnographer's justification (rule above).

## Critical rules

- **TTL is never hand-edited; briefs are never hand-edited.** Every change goes through the CLI, then `ant refresh` (C7).
- **Assertions about the field come from the ethnographer.** Never invent a passage, a practice, an invariance, a status, or a waiver justification. Silence is recorded as absence (no `--status` = forming), not filled in.
- **Roles are Characterization values, never types** (R3, R6). Never write `:x a ant:Mediator`.
- **Never ask "person or thing?"** (C2).
- **Offer the off-ramp** (C8) at the start and whenever the ethnographer reaches for existing material.
- **Say the frame** when you report a role back: "under <practice>, X is characterized as a Mediator", never "X is a Mediator".

## Handoffs

- Existing notes or files → [ant-ingest](../ant-ingest/SKILL.md).
- Regenerate and review → [ant-refresh](../ant-refresh/SKILL.md); interpret and route questions → [ant-read](../ant-read/SKILL.md); pull a fact → [ant-query](../ant-query/SKILL.md).
- The change needs a new term or shape → [ant-gvrn](../ant-gvrn/SKILL.md).
