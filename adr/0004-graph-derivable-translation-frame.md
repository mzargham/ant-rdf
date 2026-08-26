<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0004 — Graph-derivable translation frame (`ant:authoredUnder`)

- **Status:** accepted
- **Date:** 2026-08-02 (authored downstream; mirrored upstream 2026-08-25)
- **Context builds on:** [ADR-0001](0001-perspective-isolation-named-graphs.md) ("a record's perspective is a file-routing field, not a triple"), [ADR-0002](0002-cross-frame-links-and-status.md), R9, R3 (the observer frame is explicit, not implicit).

## Context

A compiler audit found that cross-perspective compilers were deriving a translation's **frame** from a **filesystem scan** (which `perspectives/<slug>/` folder the record's file sat in), not from the graph. A `Characterization` carries its frame in the graph (`ant:withinNetwork` + `ant:perPractice`), but a **`Translation` carried no such triple**, so its frame was only recoverable from where its file lived.

Consequence: those briefs **could not be rebuilt from the union graph alone** — the rendered view depended on the on-disk directory layout. That is a faithfulness gap for a project whose premise is that compiled briefs are a deterministic view *of the RDF*. It also left `NetworkBrief`'s translations section unscoped in a whole-case compile (every frame's translation listed under one network) and made frame attribution untestable on in-memory fixtures.

## Decision

1. **New predicate `ant:authoredUnder`** (`owl:ObjectProperty`, domain `ant:Translation`, range `ant:Perspective`, `dcterms:source` per R9). It records the perspective a translation is authored under / enacted within — the **translation analogue** of a Characterization's `withinNetwork` / `perPractice`. `ant:withinNetwork` is domain-locked to `Characterization`, so a new predicate is used rather than overloading it.
2. **Threaded through the tool:** `Translation.authored_under` in `models.py`; emitted by `serialize._add_translation`; `new-record` / `edit-record translation --authored-under`; `edit_record._EDIT_SPEC`; `verify._CROSSREF_PROPERTIES` (the target perspective must exist).
3. **Compilers read the graph.** `NetworkBrief` uses `authoredUnder` to exclude translations explicitly authored under a *different* frame (a no-op under `--perspective`; un-attributed translations are kept for backward compatibility). Cross-frame compilers (Wave 3) take the frame from `local_name(ant:authoredUnder)` — the perspective IRI's local name *is* the frame slug.
4. **A Tier-2 guard.** `ant:TranslationFrameShape` (warnings) requires exactly one `ant:authoredUnder` per translation, keeping frame provenance graph-derivable going forward. Waivable, so it does not hard-block cases that have not adopted the predicate.

## Relationship to ADR-0001

This does **not** pre-empt named graphs: it gives translations the *same* graph-level frame attributability that characterizations already have, so every first-class record can be frame-attributed from the union graph today. When named graphs land, a translation's authoring graph and its `authoredUnder` agree.

## Consequences

- Briefs are reproducible from the union graph alone.
- The public cases' translations were given their `authoredUnder` via `ant edit-record translation --authored-under <perspective IRI>` in the same change that introduced the predicate. This records only what the file layout already asserted (the perspective directory each translation lives in); it is provenance, not a field claim.
- New translations should set `--authored-under`; the `ant-mgmt` catechism asks for it.

## Where it lives

`ant:authoredUnder` in [ontology/material-semiotics-core.ttl](../ontology/material-semiotics-core.ttl); `Translation.authored_under` across `models.py` / `serialize.py` / `new_record.py` / `edit_record.py` / `cli.py`; the `NetworkBrief` frame filter in [networkbrief.py](../src/ant_rdf/compilers/networkbrief.py); the guard in [ontology/shapes/ant-shapes-warnings.ttl](../ontology/shapes/ant-shapes-warnings.ttl); tests in [tests/test_networkbrief_frame.py](../tests/test_networkbrief_frame.py) and [tests/test_connectivity_shapes.py](../tests/test_connectivity_shapes.py).
