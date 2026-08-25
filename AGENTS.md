<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# AGENTS.md — navigating & interpreting this repo

This file is the **reader's / navigator's** contract: how to find and correctly interpret what the graph already says. It is the companion to [CLAUDE.md](CLAUDE.md), which owns **authoring** (writing to the graph). When in doubt: **reading is this file + the `ant-query` / `ant-refresh` skills; authoring is CLAUDE.md + `ant-mgmt` / `ant-ingest` / `ant-gvrn`.**

## What this repo is

A docs-as-code toolkit for Actor-Network-Theory / material-semiotic readings of a field site: an OWL vocabulary with SHACL shapes, an `ant` CLI that authors validated RDF, and deterministic compilers that render the RDF as Markdown briefs and a wiki. The **deliverable for any case is its compiled briefs in `briefs/`**, rendered from `instances/cases/<case>/`. The canonical worked example is the Callon 1986 scallops case; the koi case shows one field site read through two perspectives. See [README.md](README.md) for the fuller framing.

## Read this first

Start at [`wiki/Home.md`](wiki/Home.md) for the whole graph, or at a case's network brief (`briefs/scallops-network.md`) for one reading. For a multi-perspective case, the comparison brief (`briefs/koi-comparison.md`) is the interpretive key.

## Question → brief (and the query that confirms it)

| The question | Brief | Confirming query |
|---|---|---|
| Which cases exist, how big is each? | `briefs/case-catalog.md` | `ant list --case <case>` |
| One perspective's full reading of a case? | `briefs/<case>-network.md` or `briefs/<case>-<perspective>-network.md` | `ant list --kind Actant --case <case> --perspective <p>` |
| How is actant X read, and by whom? | the network brief's "Characterizations" table | `ant query roles X` |
| Where do two frames agree vs flip? | `briefs/<case>-comparison.md` | `ant query flips` |
| Which actant is the obligatory passage point? | the network brief's "Characterizations" table | `ant query sparql` on `ant:assignsRole ant:ObligatoryPassagePoint` |
| What does an ontology term mean, and where does it come from? | `wiki/Concept-<Term>.md` | — |
| Where is a word mentioned? | — | `ant query search <text>` |
| What exactly does one record say? | `wiki/Actant-<case>--<slug>.md` | `ant query show <slug>` |

## The mental model

- **A Characterization is the load-bearing record.** It is a reified binding *(target actant → role)* within *(network, practice, invariance)*. Read it and you read the frame. The actant itself carries no role.
- **A Perspective is provenance.** It names who is reading (`perspectiveHeldBy`), from which practice (`perspectiveGroundedIn`), tracking which invariance. Characterizations join to perspectives through their practice.
- **A Translation is the four Callon moments** — problematization, interessement, enrolment, mobilization — and is "done" when a behavioral regularity stabilizes, not forever.

## Five interpretive pitfalls (the fidelity risks)

1. **Roles are not types.** `Mediator` / `Intermediary` / `ObligatoryPassagePoint` / `Spokesperson` are values assigned *inside* a `Characterization` — **never `rdf:type` on an actant** (R3/R6/C2/C3). The same actant can be Mediator under one practice, Intermediary under another (the scallops towlines are the canonical example). Never write "X is a Mediator"; write "under <practice>, X is characterized as a Mediator."
2. **A reading is provenance, not fact** (C6/C7). Every claim is authored from one perspective; agreement across perspectives is a finding, not objectivity.
3. **`ant:Network` is a summary, not a container** (R5). Actants relate via `participatesIn`; the network is the analyst's act-4 name for the assemblage.
4. **Shared IRIs inflate counts.** A class census counts triples across perspectives, not distinct entities; an actant present in two frames appears twice.
5. **A missing practice on a Characterization is a warning, not a shrug.** `ant verify` reports it at Tier-2; `ant query roles` shows the frame as `(no practice)`. Do not paper over it in prose.

## Read-only CLI cheatsheet

Everything here is read-only (never writes triples). See the [`ant-query`](.claude/skills/ant-query.md) skill for the recipe book.

```bash
uv run ant query roles larvae-collectors   # an actant's roles, frame by frame (via Characterization)
uv run ant query flips                     # actants read as different roles across frames
uv run ant query search scallop            # text search over labels + descriptions
uv run ant query show fishermen            # fidelity-aware record view
uv run ant query sparql "SELECT ..."       # escape hatch
uv run ant list --kind Actant --case koi --perspective architectural   # scoped census
uv run ant compile koi PerspectiveComparison   # preview one brief on stdout
uv run ant verify                          # SHACL Tier-1/2 + cross-refs
```

## The skills

- **Reading (this file's companions):** [`ant-query`](.claude/skills/ant-query.md) (graph-fact recipes), [`ant-refresh`](.claude/skills/ant-refresh.md) (regenerate briefs/wiki).
- **Authoring (see CLAUDE.md):** [`ant-mgmt`](.claude/skills/ant-mgmt.md) (catechism), [`ant-ingest`](.claude/skills/ant-ingest.md) (notes/uploads), [`ant-gvrn`](.claude/skills/ant-gvrn.md) (ontology governance).

## Handoffs

- **To change the graph** → [CLAUDE.md](CLAUDE.md) and the authoring skills. **TTL is never hand-edited; briefs are never hand-edited** — both change only through the CLI, then `ant refresh <case>`.
- **Theory & constraints** → [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md) (C1–C8), [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md) (R1–R10).
