---
name: ant-query
description: |
  Read-only graph queries via `ant query` and scoped censuses via `ant list`.
  Use when a reader needs a specific fact the briefs don't surface directly —
  an actant's roles across frames, what clears a passage, what is precarious
  or still forming, where frames flip, same-program clusters, anti-programs,
  which inscriptions are also actants, a text search, or one record narrated
  faithfully. Curated queries bake in fidelity (a role is always shown inside
  its Characterization with practice / network / invariance); SPARQL is the
  escape hatch.
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-query — read-only graph queries

You are helping a reader **pull specific facts from the graph** with the read-only `ant query` command — the reader's counterpart to `new-record` / `edit-record`. For routing a question to a whole brief, use [ant-read](../ant-read/SKILL.md); the always-on map is [AGENTS.md](../../../AGENTS.md).

All commands take a **bare slug or a full IRI** (`larvae-collectors`, `fishermen`, `https://w3id.org/ant/cases/scallops/actant/scallops`) and accept `--json`. A slug is matched on the IRI's local name; if the same slug exists in two cases, pass the full IRI.

## When to use

- A reader asks a factual question about the graph ("how is X read?", "what's precarious?").
- Checking that a brief agrees with the graph before quoting it.

## Procedure — the subcommands, by reader question

| Question | Command | Notes |
|---|---|---|
| How is this actant read, and by whom? | `ant query roles <actant>` | one row per Characterization: frame · role · network · invariance · which characterization |
| Where do the frames disagree about what something is? | `ant query flips` | actants characterized with different roles in two or more grounded frames |
| What must clear this passage? | `ant query traffic <opp-actant>` | translations that `tracesToPassage` / `passesThrough` it, with their frame |
| What's precarious / stabilized / unravelled / still forming? | `ant query status precarious` | `forming` = no `hasStatus` — a deliberate state, not missing data |
| One program read across frames? | `ant query same-program [--of <translation>]` | `readsSameProgramAs` clusters |
| What runs against what? | `ant query anti-programs` | the `ant:opposes` edges |
| Which inscriptions are also actants? | `ant query manifests` | the `ant:manifestsAs` edges (C9 / ADR-0007) |
| Where is a word mentioned? | `ant query search <text>` | labels + descriptions, case-insensitive |
| What exactly does one record say? | `ant query show <slug>` | labels resolved; a Characterization is narrated |
| Anything else | `ant query sparql "<SELECT …>"` | escape hatch over the instance graph |

Scoped censuses: `ant list --kind Actant --case <case> [--perspective <p>]` (file-path scoping; sibling perspectives excluded). `ant list --iri <IRI>` is a raw predicate dump and always sees the full graph.

Worked examples on the public cases: `ant query roles larvae-collectors` (the scallops flip: Intermediary under experimental-oceanography, Mediator under seasonal-fishing-labor); `ant query flips` (the koi case); `ant query show collectors-as-mediator`.

## Critical rules

- **Read-only, always.** `ant query` and `ant list` never write. To change a fact, switch to [ant-mgmt](../ant-mgmt/SKILL.md); **never hand-edit TTL.**
- **A role is perspective-relative** (R3 / R6 / C2 / C3). Report it with its frame: "under seasonal-fishing-labor practice the collectors are characterized as a Mediator", never "the collectors are a Mediator".
- **`forming` ≠ missing.** Say "forming / not yet assessed".
- **Counts across frames are triples, not entities** — a shared actant recurs per frame in a census.
- A characterization with **no practice** shows `(no practice)`; that is a Tier-2 warning, not a fact about the field.
- **Prefer a curated query over raw SPARQL** when one fits — it encodes the fidelity a bare `SELECT` does not.
- **Verify against the brief.** A curated query and its brief must agree (`flips` vs the comparison brief; `status precarious` vs the durability dashboard); if they diverge the briefs are stale → [ant-refresh](../ant-refresh/SKILL.md).

## Handoffs

- Interpretation and which brief to read → [ant-read](../ant-read/SKILL.md).
- Stale briefs → [ant-refresh](../ant-refresh/SKILL.md).
