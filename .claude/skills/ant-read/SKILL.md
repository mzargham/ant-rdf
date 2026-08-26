---
name: ant-read
description: |
  Reader navigation and interpretation for an existing reading. Use when
  someone wants to understand, traverse, or answer a question about what the
  graph already says (not author new records): routes a question to the brief
  that answers it, states the mental model, and guards the interpretive
  pitfalls (roles are perspective-relative values, never types).
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-read — reader navigation & interpretation

You are helping a reader (or yourself, on their behalf) **navigate and interpret an existing reading** — not author new records. The reading is a compiled, deterministic view of an RDF graph; your job is to route them to the right artifact and keep them from misreading it. The canonical router table, mental model and pitfalls live in [AGENTS.md](../../../AGENTS.md) — read it first and do not restate it from memory; the concepts are in [docs/primer.md](../../../docs/primer.md).

## When to use

- "Where do I start?", "what does this case say?", "how is X read?", "what does term T mean?"
- Narrating results from a brief to a person.

## Procedure

1. **Find the entry point.** A case with a grounded perspective has a reading guide: `briefs/<case>-guide.md` ("start here"); the positionality ledger is the interpretive key, the synopsis the gist. A case whose only perspective is the ungrounded `_default` stub (the canonical scallops case) has just `briefs/<case>-network.md`. `wiki/Home.md` spans the whole graph.
2. **Route the question** with the table in [AGENTS.md](../../../AGENTS.md) §"Question → brief"; name the brief you answer from so the reader can verify.
3. **Confirm with a query** when the reader wants the underlying records ([ant-query](../ant-query/SKILL.md)): the table gives the confirming command per row.
4. **State the mental model before interpreting** (AGENTS.md §"The mental model"): perspectives are provenance; actant identity is shared and readings diverge; the Characterization is the load-bearing record.
5. **Check the pitfalls** (AGENTS.md §"Six interpretive pitfalls") before you narrate: roles are not types; a reading is provenance, not fact; a network is a summary, not a container; shared IRIs inflate counts; no status is deliberate; actant and inscription are non-disjoint registers.
6. **If a brief disagrees with the graph**, the brief is stale, not wrong-by-hand → [ant-refresh](../ant-refresh/SKILL.md), then re-read.

## Critical rules

- **Read, don't write.** To change a claim, switch to [ant-mgmt](../ant-mgmt/SKILL.md) / [ant-ingest](../ant-ingest/SKILL.md); **never hand-edit TTL or a brief.**
- **Never restate a role as a typing** without its frame and practice — "under seasonal-fishing-labor practice, the collectors are characterized as a Mediator", not "the collectors are a Mediator".
- **Cite the brief** (`briefs/<case>-….md`) or the wiki page you answered from.
- **Agreement across frames is a finding, not objectivity** — especially when one person holds several frames.

## Handoffs

- A fact, not a brief → [ant-query](../ant-query/SKILL.md).
- Stale briefs → [ant-refresh](../ant-refresh/SKILL.md).
- Theory → [docs/primer.md](../../../docs/primer.md), [ONTOLOGICAL_COMMITMENTS.md](../../../ONTOLOGICAL_COMMITMENTS.md), [adr/README.md](../../../adr/README.md).
