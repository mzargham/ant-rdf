<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ADR-0001 — Perspective isolation: named graphs (target) vs single-graph discipline (current)

- **Status:** accepted in principle; **implementation deferred**. The single-graph discipline (§Decision 5) is in force now.
- **Date:** 2026-08-01 (authored downstream; mirrored upstream 2026-08-25)
- **Relates to:** R3 (Mediator/Intermediary via Characterization), R8 (multiplicity deferred to v2), C6 (multiplicity, quad-ready v1); the v2 stubs in [graph.py](../src/ant_rdf/graph.py) and [models.py](../src/ant_rdf/models.py).

## Context

Multi-perspective cases (the public `koi` case is the worked example) **share actant IRIs across frames**: the same `cases/<case>/actant/<slug>` is re-declared in each perspective's `actants.ttl`, once per frame, each declaration carrying that frame's `ant:participatesIn` and authored alongside the frame's own `networks / translations / moments / characterizations.ttl`.

**v1 loads every perspective's TTL into one default graph.** `load_case` / `load_full_dataset` flatten all files into rdflib's default graph; the quad-capable `Dataset` and the `publicID` plumbing for per-perspective **named graphs** are present but unused.

**The "bleeding" this produces.** In a union load a shared actant carries the *union* of its per-frame triples. Two of the three kinds are single-graph-native and correct:

- `ant:participatesIn` — legitimately multi-valued (the actant *is* in several networks).
- `ant:Characterization` — already network-scoped via `ant:withinNetwork`, so the per-frame role reading never collides.

The one genuine bleed is a **divergent `dcterms:description` (or `rdfs:label`) on a shared actant** — if a frame re-declares the actant with different identity prose, the union graph holds two descriptions and a naïve `description_of` returns an arbitrary one.

**Per-frame views work today by convention, not structure:** compile is file-scoped (`--perspective <p>` parses only that perspective's files), and `PerspectiveComparison` joins by string convention (network slug == perspective slug; `characterization.perPractice` ∈ `perspective.perspectiveGroundedIn`). A drifted slug mis-associates silently instead of erroring.

## Decision

1. **Target architecture: one named graph per perspective** (perspective IRI = graph IRI). Perspective isolation becomes *structural*; the file-scoping and slug-matching conventions retire; a shared actant can carry per-frame triples without collision; the union view remains available when explicitly wanted.
2. **Verify policy under named graphs:** SHACL shapes validate **per graph** (structural correctness within a frame); **cross-reference / cross-frame** checks run over the **union**.
3. **Rejected — RDF collections.** `rdf:List` / `Bag` / `Seq` group *values inside* a graph; they do not partition assertions-about-a-resource by context, so they do not address bleeding.
4. **Implementation deferred.** The change is tool-level (loader graph assignment, every compiler's scope, the verify target of §2) and changes the CLI's structural contract, so it lands as a coordinated migration, not piecemeal. Until then we **proceed single-graph**.
5. **Single-graph discipline (in force now).** While the store is one flat graph, do not author patterns that only make sense under named graphs:
   - A shared actant's **identity triples (`rdfs:label`, `dcterms:description`) MUST be frame-neutral and byte-identical in every frame that declares it** (rdflib dedupes identical triples → one triple in the union). [ADR-0003](0003-shared-actant-home-and-identity-guard.md) makes this structural.
   - **All perspectival content** — the role reading, the tracked invariance, the frame-specific interpretation — lives in `ant:Characterization` (already `withinNetwork`-scoped) or the network narrative, **never on the actant**. This is R3 applied to storage.

## Consequences

- The single-graph model stays honest; no latent description bleed; the later lift to named graphs is non-destructive.
- Keep network slug == perspective slug until named graphs land; the conventional joins depend on it. (Multiple grounding practices per perspective are supported — `perspective_index()` maps every practice.)
- The `queries/` and compiler code that match the default graph will need a `GRAPH ?frame` clause once perspectives move to named graphs; treat every such query as carrying this forward-compat note.

## Where it lives

This ADR; the v2 stubs in `graph.py` / `models.py`; the shared-actant convention demonstrated in [instances/cases/koi/](../instances/cases/koi/). To revise: open an issue tagged `adr-revision`, name this ADR, and update it together with the tool change.
