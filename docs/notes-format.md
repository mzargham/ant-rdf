<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# The `ant ingest notes` format

`ant ingest notes` turns a markdown file with a YAML `ant:` block into candidate records, writes a review document, and — only on `--commit` — lands them through the same `create_*` functions the CLI uses. This page is the canonical specification; the skill [`ant-ingest`](../.claude/skills/ant-ingest/SKILL.md) and the module docstring in `src/ant_rdf/ingest.py` point here.

```bash
uv run ant ingest notes <file.md> --case <slug> [--perspective <p>] --dry-run [--review-out <path>]
uv run ant ingest notes <file.md> --case <slug> [--perspective <p>] --commit
```

The review document is written to `/tmp/ant-review-<stem>.md` unless `--review-out` is given. `--dry-run` is the default.

## Envelope

- YAML frontmatter delimited by `---` lines at the top of the file.
- A top-level `ant:` mapping. Each key is a **plural block name**; its value is a list of mappings, one per record.
- Everything after the frontmatter is free prose and is ignored — nothing is extracted from it (**C8**; the tool never infers records from text).

## Resolution rules

- A block name is turned into a kind by dropping one trailing `s`: `actants` → `actant`, `characterizations` → `characterization`, `moments` → `moment`.
- Every record receives `case` from `--case`. Every record except a `perspectives` entry receives `perspective` from `--perspective` (default `_default`), which a record may override with its own `perspective:` key (`_shared` is allowed).
- Key names are passed straight through to the matching `create_*` function. **Unknown keys fail at commit**, after the review — so check the tables below rather than guessing from CLI flag names.

## Kinds that can be committed

| Block | Kind | Creates |
|---|---|---|
| `networks` | network | `ant:Network` |
| `actants` | actant | `ant:Actant` |
| `translations` | translation | `ant:Translation` |
| `moments` | moment | one of the four Callon moment classes |
| `perspectives` | perspective | `ant:Perspective` |
| `characterizations` | characterization | `ant:Characterization` |
| `inscriptions` | inscription | `ant:Inscription` / `ImmutableMobile` / `FluidObject` |
| `programs` | program | `ant:ProgramOfAction` |

Not ingestable from notes (author with `ant new-record …` first): **practices**, **agents**, **glossary terms**.

## Keys per block

Required keys are marked **(req)**. Multi-valued keys take a YAML list.

**`networks`** — `iri` (req), `label` (req), `description` (req), `scope`, `from_construct`.

**`actants`** — `iri`, `label`, `description` (req); lists: `participates_in`, `corresponds_to`, `internalizes`, `inscribes`, `draws_on`, `manifests_as`, `has_program`, `enrols`.

**`translations`** — `iri`, `label`, `description` (req); lists: `has_moment`, `reads_same_program_as`, `traces_to_passage`; `authored_under` (a perspective IRI — set it, or Tier-2 warns); `has_status` (full IRI: `https://w3id.org/ant#Stabilized` | `Precarious` | `Unravelled`; omit = forming); `has_durability` (`https://w3id.org/ant#MaterialDurability` | `StrategicDurability` | `DiscursiveStability`).

**`moments`** — `moment_kind` (req: `problematization` | `interessement` | `enrolment` | `mobilization`), `iri`, `label`, `description` (req).

**`perspectives`** — `iri`, `label`, `held_by` (req: an agent IRI); lists: `grounded_in` (practice IRIs), `tracks_invariance` (strings); `description`.

**`characterizations`** — `iri`, `target` (actant IRI), `within_network`, `assigns_role` (req: full role IRI, e.g. `https://w3id.org/ant#Mediator`); `per_practice`, `invariance`, `description`.

**`inscriptions`** — `iri`, `label`, `description` (req); `klass` (`ant:Inscription` (default) | `ant:ImmutableMobile` | `ant:FluidObject`); `source` (URL, citation or hash).

**`programs`** — `iri`, `label`, `description` (req); list: `opposes`.

## Gotchas

- YAML keys are the **snake_case argument names**, not the CLI flags: `has_status` not `--status`, `has_durability` not `--durability`, `assigns_role` not `--role`, `within_network` not `--in-network`, `moment_kind` not `--kind`, `klass` not `--class`.
- Status and durability take **full IRIs** in notes (the CLI's short tokens `precarious` / `strategic` are a CLI convenience).
- Referenced IRIs (networks, moments, practices, perspectives, agents) must exist by the time the graph is verified — a dangling reference is a Tier-1 violation. Order the blocks so that networks and moments come before the translations and actants that point at them, or author the targets first.

## Worked example

```markdown
---
ant:
  networks:
    - iri: https://w3id.org/ant/cases/example/network
      label: The example assemblage
      description: One paragraph on what is assembled and what holds it together.
  actants:
    - iri: https://w3id.org/ant/cases/example/actant/instrument
      label: The instrument
      description: The device that circulates between the parties.
      participates_in: [https://w3id.org/ant/cases/example/network]
  moments:
    - moment_kind: problematization
      iri: https://w3id.org/ant/cases/example/moment/problematization
      label: Problematization
      description: Who defined the problem and made themselves indispensable.
  translations:
    - iri: https://w3id.org/ant/cases/example/translation/main
      label: The main translation
      description: How the parties came to act together, and for how long.
      has_moment: [https://w3id.org/ant/cases/example/moment/problematization]
      authored_under: https://w3id.org/ant/cases/example/perspectives/_default
      has_status: https://w3id.org/ant#Precarious
  characterizations:
    - iri: https://w3id.org/ant/cases/example/char/instrument-as-mediator
      target: https://w3id.org/ant/cases/example/actant/instrument
      within_network: https://w3id.org/ant/cases/example/network
      assigns_role: https://w3id.org/ant#Mediator
      per_practice: https://w3id.org/ant/practices/experimental-oceanography
      invariance: what-the-instrument-holds-constant
      description: Why, from this practice, the instrument transforms what it carries.
---
# Field notes, session 1

Free prose here is not ingested.
```

Run it with `--dry-run`, read the review document with the ethnographer, and commit only on their explicit confirmation. Then `uv run ant refresh example --verify`.
