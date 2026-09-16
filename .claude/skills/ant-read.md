<!-- SPDX-License-Identifier: CC-BY-4.0 -->

---
name: ant-read
description: |
  Reader navigation + interpretation for an existing reading. Use when someone
  wants to understand, traverse, or answer a question about what the graph
  already says (not author new records). Routes a question to the right brief,
  teaches the perspective / shared-actant model, and guards the interpretive
  pitfalls (roles are perspective-relative, never rdf:types).
---

# ant-read — reader navigation & interpretation

You are helping a reader (or yourself, on their behalf) **navigate and interpret an existing reading** — not author new records. The reading is a compiled, deterministic view of an RDF graph; your job is to route them to the right artifact and keep them from misreading it. For pulling specific graph facts, hand off to [ant-query](ant-query.md); to change the graph, hand off to [ant-mgmt](ant-mgmt.md) and [CLAUDE.md](../../CLAUDE.md). The always-on map is [AGENTS.md](../../AGENTS.md); this skill is the procedure.

## 1. Start here

For a case with a grounded perspective the entry point is **`briefs/<case>-guide.md`** ("Start here"). For the interpretive key first, read `briefs/<case>-positionality.md`; for the gist, `briefs/<case>-synopsis.md`. Four hub briefs — guide, synopsis, positionality, glossary — are linked from every analysis brief's footer, so no page is an island. A case whose only perspective is the ungrounded `_default` stub (the canonical scallops case) has just its network brief and the catalog; start at `briefs/<case>-network.md` or `wiki/Case-<case>.md`.

## 2. Route the question to a brief

Match the reader's question, then confirm the facts with `ant query` if they want the underlying records.

| The reader asks… | Send them to | Confirm with |
|---|---|---|
| "In what order do I read this?" | `briefs/<case>-guide.md` | — |
| "Who is speaking, from which practice?" | `briefs/<case>-positionality.md` | — |
| "What's the whole case at a glance?" | `briefs/<case>-synopsis.md` | — |
| "What is one frame's full reading?" | `briefs/<case>-<frame>-network.md` (or `<case>-network.md`) | — |
| "How is actant X read across frames?" | `briefs/<case>-actants-across-frames.md` | `ant query roles <X>` |
| "Where do the frames agree vs flip?" | `briefs/<case>-comparison.md` | `ant query flips` |
| "Which actants are OPPs / what clears one?" | `briefs/<case>-opp-map.md` | `ant query traffic <passage>` |
| "What carries forward / who produces & draws on what?" | `briefs/<case>-inscriptions.md` | — |
| "Which inscriptions are also actants?" | `briefs/<case>-inscriptions.md` | `ant query manifests` |
| "Which actants are read vs left bare?" | `briefs/<case>-coverage.md` | `ant query roles <X>` |
| "What's precarious / still forming?" | `briefs/<case>-durability.md` | `ant query status precarious` |
| "What's contested / under strain?" | `briefs/<case>-tensions.md` | `ant query anti-programs` |
| "One program across all frames?" | `briefs/<case>-same-program-trace.md` | `ant query same-program` |
| "What does term T mean?" | `briefs/<case>-glossary.md` or `wiki/Concept-<T>.md` | `ant query show <T>` |

The cross-frame briefs (comparison, actants-across-frames, same-program-trace) exist only for cases with two or more grounded perspectives; `ant refresh <case>` compiles exactly the set the case supports (`refresh_plan(case)` lists it).

## 3. The mental model (say this before interpreting)

- **Perspectives are provenance.** Each is held by someone, grounded in a practice, tracking an invariance. Agreement across frames is a finding, not objectivity — especially when one person holds several frames.
- **Actant identity is shared; readings diverge.** An actant's IRI is the same across frames (its identity may live once in `instances/cases/<case>/shared/`, ADR-0003). What differs, per frame, is its `ant:Characterization`.
- **A `Characterization` is the load-bearing record** — a reified n-ary binding *(target actant → role)* within *(network, practice, invariance)*. Read it, and you read the frame.

## 4. The six interpretive pitfalls (do not let a reader fall in)

1. **Roles are not types.** `Mediator` / `Intermediary` / `ObligatoryPassagePoint` / `Spokesperson` are values assigned *inside* a `Characterization`, **never `rdf:type` on an actant** (R3, R6, C2, C3). The same actant is Mediator in one frame and Intermediary in another with no contradiction (the scallops towlines). Reading a role as a typing inverts the whole method.
2. **A reading is provenance, not fact** (C6, C7). Every claim is authored from one frame.
3. **`ant:Network` is a summary, not a container** (R5). Actants relate via `participatesIn`, not membership.
4. **Shared IRIs inflate counts.** `ant list --kind Actant` counts triples across frames, not distinct entities.
5. **No status is deliberate.** A translation with no `hasStatus` / `hasDurability` is **"forming / not yet assessed"** (neither stabilized nor precarious), not missing data (ADR-0002).
6. **Actant and Inscription are parallel registers, not disjoint types** (C9). The same entity can be both — a living repository is an inscription (a trace that circulates) *and* an actant (a node that acts). Coexistence is recorded with `ant:manifestsAs` (ADR-0007), never inferred; surfaced as "Also an actant" in the inscriptions brief and via `ant query manifests`.

## Critical rules

- **Read, don't write.** This skill and `ant query` are read-only. If the reader wants to *change* a claim, that is authoring — switch to [ant-mgmt](ant-mgmt.md) / [ant-ingest](ant-ingest.md); **never hand-edit TTL or a brief.**
- **Never restate a role as a typing** in your prose without its frame and practice — say "under seasonal-fishing-labor practice, the collectors are characterized as a Mediator," not "the collectors are a Mediator."
- **Cite the brief.** When you answer from a brief, name it (`briefs/<case>-….md`) so the reader can verify.
- **Theory lives in the repo docs.** For the C1–C9 commitments, R1–R10 decisions, and the ANT vocabulary, point to `ONTOLOGICAL_COMMITMENTS.md`, `adr/*`, and `wiki/Concept-*.md`.

## When the briefs look stale

If a brief disagrees with the graph, the briefs are out of date, not wrong-by-hand (they are derived). Switch to [ant-refresh](ant-refresh.md) to regenerate, then re-read.
