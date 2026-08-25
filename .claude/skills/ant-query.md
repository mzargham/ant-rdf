<!-- SPDX-License-Identifier: CC-BY-4.0 -->

---
name: ant-query
description: |
  Read-only graph queries via `ant query` and scoped censuses via `ant list`.
  Use when a reader needs a specific fact the briefs don't surface directly —
  an actant's roles across frames, where frames flip, a text search, one
  record narrated faithfully. Curated queries bake in fidelity (roles always
  shown inside their Characterization, with practice/network/invariance); a
  SPARQL escape hatch handles the rest.
---

# ant-query — read-only graph queries

You are helping a reader **pull specific facts from the graph** with the read-only `ant query` command — the reader's counterpart to `new-record` / `edit-record`. Every subcommand is read-only. For orientation (which brief answers which question) see [AGENTS.md](../../AGENTS.md).

All commands take a **bare slug or a full IRI** (`larvae-collectors`, `fishermen`, `https://w3id.org/ant/cases/scallops/actant/scallops`), and every command accepts `--json` for machine use. A slug is matched on the IRI's local name; if the same slug exists in two cases, pass the full IRI.

Curated queries **bake in fidelity**: a role is always reported as a `Characterization` value with its `perPractice` / `withinNetwork` / `invarianceCriterion` — never as a typing (R3/R6).

## The subcommands (each maps to a reader question)

- **Roles of an actant across frames** — "How is this actant read, and by whom?"
  ```bash
  uv run ant query roles larvae-collectors
  ```
  One row per `Characterization` (frame · role · network · invariance · which characterization), so two same-role readings in one frame stay distinguishable. In the scallops case this shows the canonical move: the same towlines are an Intermediary under one practice and a Mediator under another.

- **Role flips** — "Where do the frames disagree about what something is?"
  ```bash
  uv run ant query flips
  ```
  Actants that are characterized in two or more grounded perspectives with different roles. The koi case (two perspectives) is the worked example.

- **Traffic through a passage** — "What must clear this OPP?"
  ```bash
  uv run ant query traffic <opp-actant-slug>
  ```
  Translations that `tracesToPassage` / `passesThrough` an obligatory passage point, with the frame each is authored under.

- **By behavioral status** — "What's precarious? What's still forming?"
  ```bash
  uv run ant query status precarious      # or: stabilized | unravelled | forming
  ```
  `forming` = translations with **no** `hasStatus` (a deliberate 'not yet assessable' state, not missing data).

- **Same-program clusters** — "One program read across frames."
  ```bash
  uv run ant query same-program            # all clusters; --of <translation> for one
  ```

- **Anti-programs** — "What runs against what?"
  ```bash
  uv run ant query anti-programs           # the ant:opposes edges (X opposes Y)
  ```

- **Manifestations** — "Which inscriptions are also actants?"
  ```bash
  uv run ant query manifests               # the ant:manifestsAs edges (C9 / ADR-0007)
  ```

- **Text search** — "Where is X mentioned?"
  ```bash
  uv run ant query search scallop          # case-insensitive over labels + descriptions
  ```

- **Show one record (fidelity-aware)** — better than `list --iri`'s flat predicate dump.
  ```bash
  uv run ant query show collectors-as-mediator   # narrates a Characterization
  uv run ant query show fishermen                # any record: labels resolved
  ```

- **SPARQL escape hatch** — for anything the curated queries don't cover.
  ```bash
  uv run ant query sparql "PREFIX ant: <https://w3id.org/ant#> \
    SELECT ?c WHERE { ?c a ant:Characterization ; ant:assignsRole ant:ObligatoryPassagePoint }"
  ```

## Scoped censuses with `ant list`

For a plain inventory of a class, `ant list` scopes by case and/or perspective (a file-location fact — sibling perspectives' TTL is excluded):

```bash
uv run ant list --kind Actant --case scallops                     # one case
uv run ant list --kind Translation --case koi --perspective architectural
uv run ant list --iri <IRI>                                       # raw predicate dump (always full graph)
```

## Fidelity notes (state these when you report a result)

- A **role is perspective-relative** (R3/R6/C2/C3). Report it with its frame: "under seasonal-fishing-labor practice the collectors are characterized as a Mediator," never "the collectors are a Mediator."
- **Counts across frames are triples, not entities** — an actant shared by two perspectives recurs once per frame in a census.
- A characterization with **no practice** shows `(no practice)` as its frame; that is a Tier-2 warning in `ant verify`, not a fact about the field.

## Critical rules

- **Read-only, always.** `ant query` and `ant list` never write. If the reader wants to change a fact, that is authoring — switch to [ant-mgmt](ant-mgmt.md); **never hand-edit TTL.**
- **Prefer a curated query over raw SPARQL** when one fits — it encodes the fidelity a bare `SELECT` does not.
- **Verify against the brief.** A curated query and its brief must agree (e.g. `flips` and the "Where the frames diverge" section of the comparison brief; `status precarious` and the durability dashboard's Precarious count); if they diverge, the briefs are stale — see [ant-refresh](ant-refresh.md).
- **For orientation and interpretation** (which brief answers which question; the pitfalls), hand back to [ant-read](ant-read.md).
