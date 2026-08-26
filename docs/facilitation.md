<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Facilitating a session — mapping a field site with an ethnographer

This guide is for the person sitting with an ethnographer and running the toolchain on their behalf — a colleague at the keyboard, or an operator driving an LLM that has the `ant-*` skills. The procedures below are the same ones the skills encode ([`.claude/skills/`](../.claude/skills/)), written for a human. The concepts are in [primer.md](primer.md); every command is in [toolchain.md](toolchain.md).

## The division of labour (C7)

| The ethnographer owns | The tool owns | You, the facilitator |
|---|---|---|
| every claim about the field: who the actants are, what role each plays, from which practice, which invariance, whether a translation held | structural correctness: the record shapes, cross-references, deterministic files, the tri-severity check | translate their words into commands; ask the next question; read warnings back verbatim; never fill a gap with your own guess |

You are the scribe. When you do not have an answer from the ethnographer, the record stays silent (a translation with no status is *forming*; a characterization with no practice draws a warning) — that silence is correct, and inventing something to quiet a warning is the one real failure mode.

## The session shape

A first session runs 60–90 minutes and moves through: framing → the reading's provenance → the network → the actants → the four moments → the translation → inscriptions → characterizations → what is contested → verify → review the brief together. One question at a time; run the command; move on. Do not batch questions — the records build on each other and the ethnographer needs to see each one land.

## Before you start: the off-ramp (C8)

Ask once how they want to work, and mean it:

> "We can do this three ways: (a) you describe the case and I enter it as we go; (b) you already have notes — I'll turn them into a review document you approve before anything is committed; (c) you have materials (papers, photos, recordings) to register first and characterize later. Which fits how you're working today?"

(b) is the [notes format](notes-format.md) and `ant ingest notes --dry-run`; (c) is `ant ingest upload`. Mixing paths is normal — say out loud when you switch ("I'm switching to the conversation to characterize the paper we just registered").

## Prerequisites: who is reading, from which practice

Before the first translation, a reading needs its provenance, or the tool cannot attribute anything to a frame (ADR-0004) and the case gets no reader briefs:

1. **The reader** — "Whose reading is this?" → `ant new-record agent` (a name for the holder).
2. **The practice** — "What do you do that makes you see it this way — from which practice are you reading?" → `ant new-record practice`. Practices are shared across cases; check `ant list --kind Practice` first.
3. **The perspective** — "What does this reading hold constant?" → `ant new-record perspective --held-by … --grounded-in … --tracks-invariance "…"`.

Multi-perspective case (two ethnographers, or one person reading from two roles): repeat for each frame. An actant that several frames will read gets **one** identity, authored with `--perspective _shared`; everything perspectival goes in characterizations. If the two frames would describe the actant differently, that difference *is* a characterization, not two descriptions.

## The questions to ask, in order

**1. The case.** "What shall we call it?" (a kebab-case slug) — "Is there a published source we're working from?"

**2. The network.** "What would you name this network in one short phrase?" — "Describe it in a paragraph: what's assembled, what they're trying to do, what's holding it together, and what might not be." → `ant new-record network`.

**3. The actants.** For each: "What would you call them?" — "In a sentence, what do they do in the field?" → `ant new-record actant`. **Never ask whether it is a person or a thing** — that is the pre-categorization generalized symmetry refuses (C2); scallops and researchers enter on the same terms.

**4. The four moments.** "Walk me through how the translation unfolds":
- *Problematization* — who defined the problem and positioned themselves as indispensable?
- *Interessement* — how were the alternatives cut off?
- *Enrolment* — did each actant accept its scripted role? Who resisted?
- *Mobilization* — who spoke for the network in public?

→ `ant new-record moment --kind …` for each moment that happened. If one did not, record only those that did; the missing one becomes a Tier-2 warning the ethnographer can waive with their reason (that *is* the finding, C5).

**5. The translation.** Link the moments; attribute the frame (`--authored-under`, always). Then three questions, each of which may go unanswered:
- "Has the new regularity taken root, is it strained, or did it come apart?" → `--status stabilized | precarious | unravelled`. If they cannot say, leave it out: *forming*.
- "How is it held in place — delegated into material form, deliberate design, or the way people keep talking about it?" → `--durability material | strategic | discursive`.
- "What must it get past — is there an actant everything has to go through?" → `--traces-to-passage`. Do not supply one.

**6. Inscriptions.** "Are there texts, instruments, traces, or things that circulate between the actors and hold this together?" For each: "Does it hold its form as it travels, or does it keep changing while staying itself?" → `--class immutable` / `--class fluid`. "Who made it? Who uses it?" → `--inscribes` / `--draws-on` on the actants. "Is it also *doing* something in the network?" → `--manifests-as` (ask; never infer).

**7. Characterizations.** For each actant the ethnographer wants to read: "From whose practice are you describing this?" — "Within which network?" — "Which role — does it pass something on unchanged, transform what it carries, speak for others, or is it what everyone must pass through?" — "What is it holding constant?" → `ant new-record characterization`. If they say "X is a mediator", probe: "From which practice? What is it regulating to keep what constant?" Several characterizations of one actant from different practices are the point, not a contradiction.

**8. What is contested.** "What's breaking down or being challenged?" A competing script is a program of action that opposes the translation, carried by some actant → `ant new-record program --opposes …`, `edit-record actant --has-program …`. Strain in the translation itself is its status (step 5).

## Definition-first, don't preconclude

When a role fit is uncertain — the ethnographer hesitates, two roles compete, or *you* are tempted to pick — do not lead with a verdict:

1. **Name the uncertainty** and turn it into a definitional question: "This is less about what happened than about what the role means — let me read the definition."
2. **Read the definition aloud** from the concept page (`wiki/Concept-Spokesperson.md`, `wiki/Concept-Mediator.md`: the ontology's definition and its founding text). Find the load-bearing word: Spokesperson turns on *represents*; Mediator on *transforms / regulates*.
3. **Show one or two worked examples** already in the graph (`ant query sparql` on the role, or the concept page's list) and say why each satisfies the definition.
4. **Apply the test without choosing**: what supports and what cuts against each candidate; then isolate the *single field question* that decides it — "did it speak on behalf of an assembled constituency, or act on its own initiative?" — and hand that question to the ethnographer. Record only after they answer.

Do this lightly even when they are confident: the definition checks the assertion instead of rubber-stamping it.

## When `ant verify` warns: fix or waive

1. Read the warning **verbatim** — the record, the shape, the message. Do not paraphrase a validator at the person.
2. Ask: fix the data, or waive? Fixing means another command (`edit-record …`); waiving means their reason, in their words: `ant waive add <shape> <record> --by <agent> --justification "…"`.
3. Never write a justification for them.

## The connectivity triage

Two warnings — a translation anchored to nothing (`TranslationAnchoredShape`) and a program no actant carries (`ProgramCarriedShape`) — mean a record would sit as an island: the prose names a connection the graph does not draw. Walk these **in order**, the ethnographer deciding at each step:

1. **Intent mismatch** — read the record back. Does it mean something other than any candidate connection would claim? Then the record needs revising, not the graph around it.
2. **Missing data** — the description usually names the connection (a passage, a sibling translation, a carrier). Ask for the claim and author it. If the counterpart has no record yet, that is the finding: author the missing actant first.
3. **Ill-formed** — if the record does not survive scrutiny as a translation or program *of this network*, remove it and say why in the commit.
4. **Waive** — only if none of the above apply, with their justification.

## The review loop

1. `ant refresh <case> --verify --wiki`.
2. Open the reading guide (`briefs/<case>-guide.md`) or, for a single-frame case, the network brief, and read it with the ethnographer. The positionality ledger is where they see themselves named as the frame.
3. Take revisions in their words and put them back through `edit-record`; never edit a brief.
4. Commit the regenerated briefs and wiki together with the records that moved them — the ethnographer accepts the rendered artifact, not the raw triples.

## Narrating results: the guardrails

- Say the frame: "under seasonal-fishing-labor practice, the collectors are characterized as a Mediator" — never "the collectors are a Mediator" (roles are not types).
- A reading is provenance, not fact; agreement between two frames is a finding, not objectivity — especially when one person holds both frames.
- "Forming" is a state, not missing data. A missing practice on a characterization is a warning to raise with the ethnographer, not a gap to paper over.
- An inscription can also be an actant (C9); the coexistence is recorded, never assumed.

The full router — which brief answers which question, and the query that confirms it — is [AGENTS.md](../AGENTS.md).
