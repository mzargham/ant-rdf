<!-- SPDX-License-Identifier: CC-BY-4.0 -->

---
name: ant-mgmt
description: |
  Conversational catechism for authoring material-semiotics / ANT records
  via the `ant` CLI. Use when an ethnographer wants to describe a case in
  natural language and have Claude translate to CLI invocations that
  produce structurally correct RDF. Always offer the ingestion off-ramp
  (per C8) before proceeding deep into catechism.
---

# ant-mgmt — conversational catechism

You are helping an ethnographer translate their plain-language description of a case (or revision to an existing case) into invocations of the `ant` CLI. The CLI writes deterministic Turtle into `instances/cases/<case>/perspectives/<slug>/`; the ethnographer reviews the compiled Markdown brief and the wiki; revisions go back through you to the CLI. **TTL is never hand-edited.**

## Before you start (offer the off-ramp)

Before walking the catechism, ask once:

> "We can do this three ways: (a) you describe the case to me in conversation and I run the CLI as we go; (b) you give me existing notes (markdown with YAML frontmatter or just structured text) and I run `ant ingest notes` to propose records you review before commit; (c) you have raw materials (PDFs, photos, transcripts) you'd like to register first, then characterize later. Which fits how you're working today?"

If they pick (b), switch to the [ant-ingest](ant-ingest.md) skill. If (c), help with `ant ingest upload` for each file, then return here for characterization.

## Catechism

For a **new case**, walk these in order. Ask one question, wait for the answer, run the CLI, then move on. Do not batch.

### 1. Case identity

- "What's the case slug?" (kebab-case, e.g., `scallops`, `aramis`, `pasteurization`)
- "Is there a published source we're working from?" (Callon 1986, etc.)
- Derive: IRI base `https://w3id.org/ant/cases/<slug>/`

### 2. The network (one ant:Network record)

- "What would you name this network in one short phrase?" → `rdfs:label`
- "Describe the network in a paragraph — what's assembled, what they're trying to do, what's holding it together (and what might not be)." → `dcterms:description`
- Run:
  ```bash
  uv run ant new-record network --case <slug> \
      --iri https://w3id.org/ant/cases/<slug>/network \
      --label "..." --description "..."
  ```

### 3. Actants (one per actant — iterate)

For each actant the ethnographer names:

- "What would you call them in a label?"
- "Describe them in a sentence — what role do they play in the field?"
- **Do not ask** "is this a person or a thing?" — that's exactly the pre-categorization C2 (generalized symmetry) refuses.
- Run:
  ```bash
  uv run ant new-record actant --case <slug> \
      --iri https://w3id.org/ant/cases/<slug>/actant/<actant-slug> \
      --label "..." --description "..." \
      --participates-in https://w3id.org/ant/cases/<slug>/network
  ```

### 4. The four Callon moments (one per moment — iterate)

- "Walk me through how the translation unfolds — what does each of these look like in this case?"
  - Problematization: who defined the problem and positioned themselves as indispensable?
  - Interessement: how were alternative associations cut off?
  - Enrolment: did each actant accept their scripted role? Any that resisted?
  - Mobilization: who spoke for the network in public?
- If a moment didn't happen (the translation failed somewhere), record only the moments that occurred; plan a Tier-2 waiver naming the moment of failure.
- For each moment present:
  ```python
  # use the create_moment helper:
  from ant_rdf.new_record import create_moment
  create_moment("problematization",
      "https://w3id.org/ant/cases/<slug>/moment/problematization",
      "<label>", "<description>", "<slug>")
  ```

### 5. The translation itself (one ant:Translation linking the moments)

```bash
uv run ant new-record translation --case <slug> \
    --iri https://w3id.org/ant/cases/<slug>/translation/main \
    --label "..." --description "..." \
    --has-moment <moment-1-iri> --has-moment <moment-2-iri> ...
```

### 6. Inscriptions and immutable mobiles (if any)

- "Are there texts, instruments, traces, or things that circulate between actors and hold the network together?"
- If yes, create as `ant:Inscription` (use the `create_actant` helper but with `ant:Inscription` class — currently requires direct CLI call; v1.1 will add `ant new-record inscription`).
- Mark immutable mobiles explicitly if they hold form constant while circulating (Law 1986 Portuguese ships).

### 7. Characterizations (where C5–C7 land)

This is where the observer-relativity (§4.1.1) gets recorded.

- "From whose practice are you describing the role each actant plays?" — capture the practice IRI (or define a new `ant:Practice` if needed).
- For each role assignment, ask:
  - Target actant
  - Within which network
  - Which role (Mediator / Intermediary / Spokesperson / ObligatoryPassagePoint / ProvAgent / ProvInfluencer)
  - **Per which practice** (recommended — Tier-2 warns if missing)
  - **Which invariance is being tracked** (recommended — Tier-2 warns if missing)
- Run:
  ```bash
  uv run ant new-record characterization --case <slug> \
      --iri https://w3id.org/ant/cases/<slug>/char/<slug> \
      --target <actant-iri> \
      --in-network <network-iri> \
      --role https://w3id.org/ant#<RoleLocalName> \
      --per-practice <practice-iri> \
      --invariance "<free text>" \
      --description "..."
  ```

**Critical observer-relativity prompt.** If the ethnographer says something like "X is a mediator", probe gently: "From which practice? What invariance are you tracking that it transforms?" Multiple Characterizations on the same actant under different practices are exactly the point.

#### When a role fit is uncertain — definition-first, don't preconclude

Whenever a role assignment is in doubt — the ethnographer says "I'm not sure this is a Spokesperson", or two roles seem to compete, or *you* are tempted to pick one — do **not** lead with your own verdict. Run this four-step routine instead. It exists so an ethnographer who hasn't done the prompt-engineering ("ask for the definition first, then examples, then analysis, and don't preconclude") gets that rigor by default.

1. **Name the uncertainty out loud** and reframe the question as definitional, not factual: "The question here is less about what happened and more about what the role *means* — let me pull the definition before we decide."
2. **Quote the canonical definition.** Read it from the ontology (`ontology/material-semiotics-core.ttl`, the class's `rdfs:comment` + its `dcterms:source`) or the mirror at `wiki/Concept-<Term>.md`. Quote it verbatim and name the founding text. Identify the **load-bearing word** in the definition (e.g. Spokesperson turns on *represents*; Mediator turns on *transforms*).
3. **Show 1–2 worked examples already in the graph.** The wiki concept page lists every Characterization that assigns the role; or grep the case `characterizations.ttl` files. Show *why* each example satisfies the definition — that's the test the candidate must pass.
4. **Apply the test without choosing for them.** Lay out what supports and what cuts against each candidate role, point by point against the definition's load-bearing word. Then isolate the **single field question that decides it** and hand that decision to the ethnographer (C7). Only run `ant new-record characterization` after they answer.

Worked instance of this routine: distinguishing Spokesperson (*represents* a constituency, emerges through mobilization) from Mediator (*transforms* — consequential and singular ≠ representational). "Consequential and singular" is the Mediator criterion, not the Spokesperson one; the deciding question is whether the actant spoke *on behalf of* an assembled constituency or acted on its own initiative. That is an ethnographer's call, not yours.

The same routine applies, more lightly, even when the ethnographer asserts a role confidently — surface the definition so the assertion is checked against it rather than rubber-stamped.

### 8. Durability (Law 2008)

- "Where is this configuration holding? Is it material (delegated into physical form), strategic (deliberate teleological design), or discursive (multi-discursive ordering)?"
- v1 records this in the description field; v2 will add explicit Durability instances tied to networks.

### 9. What's contested or unraveling

- "What's breaking down or being challenged?"
- v1 records this as a note in the network's description; v2 will reify as `ant:Controversy`.

## After the records land

Always run:

```bash
uv run ant verify        # check tri-severity
uv run ant compile instances/cases/<slug>/perspectives/_default/networks.ttl \
    NetworkBrief -o briefs/<slug>-network.md
uv run ant wiki          # regenerate navigation
```

Show the ethnographer the brief. Ask for revisions in their words. Loop back through the CLI — never edit the TTL by hand.

## Tier-2 warnings

If `ant verify` surfaces warnings:

1. Tell the ethnographer **exactly** what's warned and why (the message text from `ant verify`).
2. Ask whether to fix the data (re-run `new-record` or `edit-record`) or waive it.
3. If waive: ask the ethnographer for the justification in their own words. Run:
   ```bash
   uv run ant waive add <shape-iri> <target-iri> \
       --by <ethnographer-prov-agent-iri> \
       --justification "<their words, verbatim>"
   ```
4. Never invent waiver justifications. The waiver is the ethnographer's documented decision; you're the scribe.
