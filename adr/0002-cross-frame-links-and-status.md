<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0002 — Cross-frame linking predicates + translation status/durability

- **Status:** accepted
- **Date:** 2026-08-02 (authored downstream; mirrored upstream 2026-08-25)
- **Context builds on:** ADR-0000 (R9 provenance per term), [ADR-0001](0001-perspective-isolation-named-graphs.md) (single-graph discipline; cross-frame checks run over the union)

## Context

A multi-perspective case reads one field site through several perspective frames that share actant IRIs. As such a reading matures, three kinds of structure that are *real* in the model tend to exist **only as prose** and cannot be queried or compiled:

1. **Cross-frame correspondences** — one frame's text refers to another frame's OPP, program, or concept ("the passage point from the other frame"; the personas that internalize each frame; the same program read several ways).
2. **A translation's behavioral standing** — stabilized vs precarious vs unravelled — lives in Mobilization prose, unqueryable. (Per the project's reading of Callon: a translation is done when a new behavioral regularity stabilizes; success is that regularity's durability, failure its unravelling.)
3. **Durability** — Law's material / strategic / discursive tree (`ant:Durability`) existed in the ontology but was wired to nothing.

ADR-0001 anticipated this: cross-frame joins were "by string convention … fragile."

## Decision

Add a small, load-bearing set of terms to `ontology/material-semiotics-core.ttl` (each with `dcterms:source` per R9), wired through `models.py` / `serialize.py` / `new-record` / `edit-record`:

- **Cross-frame linking predicates**
  - `ant:readsSameProgramAs` — `owl:SymmetricProperty`, `Translation → Translation`. The same program read from different frames.
  - `ant:correspondsTo` — `owl:SymmetricProperty`, `Actant → Actant`. Cross-frame correspondence of referents read differently by frame (weaker than identity; cf. `skos:closeMatch`).
  - `ant:internalizes` — `Actant → Perspective`. A persona actant internalizes the frame it stands for (for reflexive readings where one observer holds several frames).
  - `ant:tracesToPassage` — `Translation → Actant`. A commitment / program traces to an OPP it must clear (complements `ant:passesThrough`, whose subject is an Actant).
- **Status + durability on `Translation`**
  - `ant:TranslationStatus` class + individuals `ant:Stabilized` / `ant:Precarious` / `ant:Unravelled`, and `ant:hasStatus`. **Absence of a status is a deliberate state** ("forming / not yet assessed"), not missing data.
  - `ant:hasDurability` (`Translation → ant:Durability`) — wires the existing Law-2008 tree.

**Consumption (ADR-0001 §Decision 2):** these are cross-frame links, so compilers read them **over the union graph**, never per frame. Symmetric predicates are authored once; consumers query both directions, since no reasoner runs at verify time.

## Consequences

- Cross-perspective compilers become possible (actant-across-frames, OPP map, same-program trace, durability dashboard) — see the Wave-3 port.
- No Tier-1 SHACL change. A Tier-2 warning for a `Translation` lacking `ant:hasStatus` is deliberately **not** added (status is descriptive, not structural). The connectivity warning `ant:TranslationAnchoredShape` (a translation should `tracesToPassage` or `readsSameProgramAs` something) *is* added, waivable, so islands are surfaced rather than silently accumulated.
- The `DurabilityKind` type alias in `models.py` (previously dead) is reachable via `ant:hasDurability`.
- CLI: `new-record translation` / `edit-record translation` gain `--reads-same-program-as`, `--traces-to-passage`, `--durability {material|strategic|discursive}`, `--status {stabilized|precarious|unravelled}` and `--clear-status` / `--clear-durability`; `new-record actant` / `edit-record actant` gain `--corresponds-to`, `--internalizes`.
