<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# AGENTS.md — navigating & interpreting this repo

This file is the **reader's / navigator's** contract: how to find and correctly interpret what the graph already says. It is the companion to [CLAUDE.md](CLAUDE.md), which owns **authoring** (writing to the graph). When in doubt: **reading is this file + the `ant-query` / `ant-refresh` skills; authoring is CLAUDE.md + `ant-mgmt` / `ant-ingest` / `ant-gvrn`.**

## What this repo is

A docs-as-code toolkit for Actor-Network-Theory / material-semiotic readings of a field site: an OWL vocabulary with SHACL shapes, an `ant` CLI that authors validated RDF, and deterministic compilers that render the RDF as Markdown briefs and a wiki. The **deliverable for any case is its compiled briefs in `briefs/`**, rendered from `instances/cases/<case>/`. The canonical worked example is the Callon 1986 scallops case; the koi case shows one field site read through two perspectives. See [README.md](README.md) for the fuller framing.

## Read this first

For a case with a grounded perspective, start at its reading guide (`briefs/koi-guide.md`, `briefs/pi-learning-guide.md`) — it links every other brief in reading order; the positionality ledger is the interpretive key and the synopsis the gist. For the canonical scallops case (one ungrounded `_default` perspective) start at `briefs/scallops-network.md`. [`wiki/Home.md`](wiki/Home.md) spans the whole graph.

## Question → brief (and the query that confirms it)

| The question | Brief | Confirming query |
|---|---|---|
| Which cases exist, how big is each? | `briefs/case-catalog.md` | `ant list --case <case>` |
| In what order do I read a case? | `briefs/<case>-guide.md` | — |
| Who is speaking, from which practice? | `briefs/<case>-positionality.md` | — |
| The whole case at a glance? | `briefs/<case>-synopsis.md` | — |
| One perspective's full reading of a case? | `briefs/<case>-network.md` or `briefs/<case>-<perspective>-network.md` | `ant list --kind Actant --case <case> --perspective <p>` |
| How is actant X read, and by whom? | `briefs/<case>-actants-across-frames.md` (or the network brief's "Characterizations" table) | `ant query roles X` |
| Where do two frames agree vs flip? | `briefs/<case>-comparison.md` | `ant query flips` |
| Which actants are OPPs / what clears one? | `briefs/<case>-opp-map.md` | `ant query traffic <passage>` |
| What carries forward / who produces & draws on what? | `briefs/<case>-inscriptions.md` | `ant query manifests` |
| Which actants are read vs left bare? | `briefs/<case>-coverage.md` | `ant query roles X` |
| What's precarious / still forming? | `briefs/<case>-durability.md` | `ant query status precarious` |
| What's contested / under strain? | `briefs/<case>-tensions.md` | `ant query anti-programs` |
| One program across all frames? | `briefs/<case>-same-program-trace.md` | `ant query same-program` |
| What does an ontology term mean, and where does it come from? | `briefs/<case>-glossary.md` or `wiki/Concept-<Term>.md` | — |
| Where is a word mentioned? | — | `ant query search <text>` |
| What exactly does one record say? | `wiki/Actant-<case>--<slug>.md` | `ant query show <slug>` |

The cross-frame briefs exist only for cases with two or more grounded perspectives; `ant refresh <case>` compiles exactly the set the case supports.

## The mental model

- **A Characterization is the load-bearing record.** It is a reified binding *(target actant → role)* within *(network, practice, invariance)*. Read it and you read the frame. The actant itself carries no role.
- **A Perspective is provenance.** It names who is reading (`perspectiveHeldBy`), from which practice (`perspectiveGroundedIn`), tracking which invariance. Characterizations join to perspectives through their practice.
- **A Translation is the four Callon moments** — problematization, interessement, enrolment, mobilization — and is "done" when a behavioral regularity stabilizes, not forever.

## Six interpretive pitfalls (the fidelity risks)

1. **Roles are not types.** `Mediator` / `Intermediary` / `ObligatoryPassagePoint` / `Spokesperson` are values assigned *inside* a `Characterization` — **never `rdf:type` on an actant** (R3/R6/C2/C3). The same actant can be Mediator under one practice, Intermediary under another (the scallops towlines are the canonical example). Never write "X is a Mediator"; write "under <practice>, X is characterized as a Mediator."
2. **A reading is provenance, not fact** (C6/C7). Every claim is authored from one perspective; agreement across perspectives is a finding, not objectivity.
3. **`ant:Network` is a summary, not a container** (R5). Actants relate via `participatesIn`; the network is the analyst's act-4 name for the assemblage.
4. **Shared IRIs inflate counts.** A class census counts triples across perspectives, not distinct entities; an actant present in two frames appears twice.
5. **A missing practice on a Characterization is a warning, not a shrug.** `ant verify` reports it at Tier-2; `ant query roles` shows the frame as `(no practice)`. Do not paper over it in prose.
6. **Actant and Inscription are parallel registers, not disjoint types** (C9). The same entity can be both — a living repository is an inscription (a trace that circulates) *and* an actant (a node that acts). Coexistence is recorded with `ant:manifestsAs` ([ADR-0007](adr/0007-inscriptions-can-be-actants-manifests-as.md)), never inferred. Likewise **no status on a translation is deliberate** — "forming / not yet assessed", not missing data ([ADR-0002](adr/0002-cross-frame-links-and-status.md)).

## Read-only CLI cheatsheet

Everything here is read-only (never writes triples). See the [`ant-query`](.claude/skills/ant-query.md) skill for the recipe book.

```bash
uv run ant query roles larvae-collectors   # an actant's roles, frame by frame (via Characterization)
uv run ant query flips                     # actants read as different roles across frames
uv run ant query traffic <passage>         # translations that must clear an OPP
uv run ant query status precarious         # or: stabilized | unravelled | forming
uv run ant query same-program              # one program read across frames
uv run ant query anti-programs             # the ant:opposes edges
uv run ant query manifests                 # actant/inscription coexistence (C9)
uv run ant query search scallop            # text search over labels + descriptions
uv run ant query show fishermen            # fidelity-aware record view
uv run ant query sparql "SELECT ..."       # escape hatch
uv run ant list --kind Actant --case koi --perspective architectural   # scoped census
uv run ant compile koi PerspectiveComparison   # preview one brief on stdout
uv run ant verify                          # SHACL Tier-1/2 + cross-refs
```

## The skills

- **Reading (this file's companions):** [`ant-read`](.claude/skills/ant-read.md) (route a question + interpret), [`ant-query`](.claude/skills/ant-query.md) (graph-fact recipes), [`ant-refresh`](.claude/skills/ant-refresh.md) (regenerate briefs/wiki).
- **Authoring (see CLAUDE.md):** [`ant-mgmt`](.claude/skills/ant-mgmt.md) (catechism), [`ant-ingest`](.claude/skills/ant-ingest.md) (notes/uploads), [`ant-gvrn`](.claude/skills/ant-gvrn.md) (ontology governance).

## Handoffs

- **To change the graph** → [CLAUDE.md](CLAUDE.md) and the authoring skills. **TTL is never hand-edited; briefs are never hand-edited** — both change only through the CLI, then `ant refresh <case>`.
- **Theory & constraints** → [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md) (C1–C9), [adr/0000-foundational-decisions.md](adr/0000-foundational-decisions.md) (R1–R10).
