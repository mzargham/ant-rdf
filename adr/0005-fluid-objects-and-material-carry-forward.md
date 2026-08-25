<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0005 — `ant:FluidObject`, and the produce / consume split on inscriptions

- **Status:** accepted
- **Date:** 2026-08-02 (authored downstream; mirrored upstream 2026-08-25)
- **Context builds on:** R9 (every `ant:` term carries `dcterms:source`); the Latourian inscription cluster (`ant:Inscription`, `ant:ImmutableMobile`, `ant:inscribes`); the standing rule that the ontology stays load-bearing only.

## Context

A reading that models an assemblage being reconfigured — worksites wound down, repurposed, or carried forward — captures the *behavioral* side well (a translation with a durability and a status). The *material* side is easy to leave in prose: when a worksite winds down its output is harvested forward into a successor, but with no inscription instances and no `ant:inscribes` edges anywhere in the case, that carry-forward is unqueryable.

The harvested material is typically a **git repository, not an immutable mobile**. An immutable mobile (Law 1986) holds *form constant* while circulating; that is exactly what a living repository does *not* do. A repository persists *by mutation* — it can be absorbed, repurposed, and pulled in a new direction — and that capacity to keep changing is precisely what lets it be harvested and re-pointed. `ant:ImmutableMobile`'s own comment already flagged the missing sibling ("Compare ant:FluidObject (v2; de Laet & Mol 2000) which works by mutability instead"). The term was scoped but never declared.

## Decision

1. **Declare `ant:FluidObject`** — `rdfs:subClassOf ant:Inscription`, a **sibling** of `ant:ImmutableMobile` (NOT a subclass of it; a fluid object is precisely *not* immutable). `dcterms:source` = de Laet, M. & Mol, A. (2000), *The Zimbabwe Bush Pump: Mechanics of a Fluid Technology*. Typing rule: **holds form constant → `ImmutableMobile`; persists by controlled mutability → `FluidObject`.** A git repository is the paradigm fluid object; a pinned commit hash is an immutable-mobile *snapshot* of it.
2. **Model material carry-forward as a shared inscription** — the origin produces it and a receiving stream re-uses the *same* object; the shared object **is** the carry-forward. The **translation unravels** (behavior ends) while the **fluid/immutable object persists** (material re-circulates). No directed `harvestsInto` / `absorbs` lineage predicate: the shared object carries that, and the harvesting *act* stays narrated in the translation.
3. **Split produce from consume.** `ant:inscribes` means "produces / generates", so "a stream inscribes the paper it draws on" wrongly asserts the stream produced it. Keep `ant:inscribes` for the origin (who made it) and add **`ant:drawsOn`** for the consumer (who uses / builds on it). This is load-bearing material semiotics, not org-model plumbing: **drawing on an `ant:FluidObject` may alter it (the consumer keeps developing the living object), while an `ant:ImmutableMobile` is unaltered.** That is the invariance / variance distinction (Intermediary preserves / Mediator varies), now on the inscription itself — see [ADR-0006](0006-invariance-variance-coding-axis.md).
4. **Inscriptions get a first-class authoring path**: `ant new-record inscription --class {inscription|immutable|fluid} [--source …]` for material referenced by URL / citation rather than uploaded as a file (`ant ingest upload` remains the file-hash path); `--inscribes` / `--draws-on` on `new-record actant` / `edit-record actant`. Inscription *nodes* are perspective-agnostic and can live in the frame-neutral shared home (`--perspective _shared`, ADR-0003); the frame-specific `inscribes` / `drawsOn` *edges* live on the reading's actants.

## Consequences

- Carry-forward is **queryable**: `origin --inscribes--> FluidObject <--drawsOn-- consumer` is a real path, not prose.
- Carry-forward is **not exclusive to unraveling**: an origin may be a wound-down worksite, a repurposed one, an external collaboration, or an older object picked back up. The mechanism is the shared object, not the origin's fate.
- The Tier-2 `ant:InscriptionSourceShape` now targets `ant:Inscription`, `ant:ImmutableMobile` **and** `ant:FluidObject` explicitly (direct typing at verify time does not inherit the target), closing a coverage gap where subclass instances were never warned for a missing `dcterms:source`.
- A modeling *paradigm* is **not** an inscription — only its implementations / instances (a codebase, a model built with it) are.
