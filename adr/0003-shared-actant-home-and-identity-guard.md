<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0003 — Frame-neutral shared home for actant identity + a cross-frame identity guard

- **Status:** accepted
- **Date:** 2026-08-02 (authored downstream; mirrored upstream 2026-08-25)
- **Context builds on:** [ADR-0001](0001-perspective-isolation-named-graphs.md) §Decision 5 (a shared actant's identity triples MUST be frame-neutral and byte-identical) and §Decision 2 (cross-frame checks run over the union); R3 (the actant is frame-invariant; the observer-relative reading is the Characterization's job).

## Context

In a multi-perspective case, a **shared actant** (one `cases/<case>/actant/<slug>` read by more than one frame) was **re-declared once per perspective** — the same `a ant:Actant`, `rdfs:label`, and `dcterms:description` copied into every frame's `actants.ttl`, each copy carrying that frame's `ant:participatesIn`. ADR-0001 requires those identity triples to be **byte-identical** everywhere (rdflib dedupes identical triples into one in the union).

That byte-identity was held **by convention only**, and it silently breaks: a readability pass over one frame's file leaves the same actant with two slightly different descriptions, `ant verify` does not catch it, and `description_of` returns an arbitrary one. The duplication buys nothing except a drift surface.

Per ADR-0001 / R3, actant identity is **frame-neutral by design** — there is nothing at the identity level to hold apart across frames. Every meaningful frame difference already lives in `ant:Characterization` (`withinNetwork`-scoped). So the clean rule is: **identity → one triple; the perspectival reading → Characterizations (already separate).**

## Decision

1. **A frame-neutral shared home.** A shared actant's whole declaration — identity (`label`, `description`), its full multi-valued `ant:participatesIn` (the union of the networks it is in), and any frame-neutral cross-frame links (`ant:correspondsTo`, `ant:internalizes`) — lives **once**, in `instances/cases/<case>/shared/actants.ttl`. This path sits **outside** `perspectives/`, so `_in_perspective_scope` includes it in **every** perspective-scoped compile, and `load_case` / `load_full_dataset` / `ant verify` / `ant list --case` include it in the whole-case union. It declares **no** `ant:Perspective` node — it is a storage home, not an observer frame.
2. **Authored through the tool via a reserved `_shared` token.** `new-record` / `edit-record` / `remove-record --perspective _shared` route to the shared home (one special case in `new_record._perspective_dir`, inherited by `edit_record`); `_ensure_perspective_record` is a no-op for `_shared`. **TTL is still never hand-edited.**
3. **Frames keep only what is theirs.** A perspective folder holds its `networks`, `translations`, `moments`, `characterizations`. **Single-frame actants** (declared in exactly one frame) stay in that frame's `actants.ttl`. An actant appears in the shared home **iff** it is shared.
4. **A Tier-1 identity guard.** `ant:ActantShape` (core shapes) sets `sh:maxCount 1` on `rdfs:label` and `dcterms:description` for `ant:Actant`. Over the union graph, byte-identical identity dedupes to one value (passes); the moment any declaration drifts, the actant carries two values and it **fails** as a Tier-1 violation — non-waivable, defending the invariant even for per-frame re-declarations that have not migrated to the shared home.

## Relationship to ADR-0001

This **realizes** ADR-0001 §Decision 5 *structurally*, without waiting for the deferred named-graph lift. When one named graph per perspective lands, the shared home maps cleanly onto a frame-neutral graph.

## Consequences

- **The union graph is unchanged** by migrating a case to the shared home — the collapse only relocates triples that already deduped, so every compiled brief is byte-identical before and after. Pure physical relayout, zero semantic change. The public `koi` case is **not** migrated by this ADR (its per-frame copies agree, so the guard passes); migration is optional and can be done case by case with `remove-record` + `new-record actant --perspective _shared`.
- **Drift becomes impossible where it mattered** (shared identity single-sourced) and **caught everywhere else** (the guard).
- **One obvious authoring target** for a shared actant.

## Where it lives

The `_shared` routing in [new_record.py](../src/ant_rdf/new_record.py) (`SHARED_PERSPECTIVE`, `_perspective_dir`, `_ensure_perspective_record`), inherited by [edit_record.py](../src/ant_rdf/edit_record.py); the guard in [ontology/shapes/ant-shapes-core.ttl](../ontology/shapes/ant-shapes-core.ttl) (`ant:ActantShape`); tests in [tests/test_shared_home_and_guard.py](../tests/test_shared_home_and_guard.py).
