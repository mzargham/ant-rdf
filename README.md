<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# ant-rdf

**A material-semiotics / Actor-Network-Theory vocabulary and authoring toolkit for ethnographers and STS analysts.**

`ant-rdf` is a docs-as-code repository for analyzing networks of heterogeneous associations — people, things, texts, organizations, animals, ideas — with the conceptual toolkit developed by Callon, Latour, Law, and Mol. The canonical source of truth is RDF (Turtle in the `https://w3id.org/ant#` namespace); compilers render it into reviewable Markdown briefs and a hyperlinked wiki; a Python CLI authors the records, callable directly or through an LLM-mediated conversation. The vocabulary is a synthesis of Callon's sociology of translation, Latour's classical ANT, and post-ANT material semiotics (Law 2008, Mol 2002), published as a reusable semantic-web vocabulary.

> **On naming.** Following Law 2008, "actor-network theory" is one strand of a broader **material semiotics** — a toolkit of sensibilities, not a theory. The repo keeps `ant-rdf` for recognition and frames the vocabulary as material-semiotic throughout. And reflexively: `ant-rdf` is itself an assemblage of the kind such analysis interrogates — the toolkit is a prosthesis, not a neutral instrument. That reading, and the validation and comparison-study programme it implies, is the [abstract](abstract.md).

## Start here, by who you are

| You are… | Read |
|---|---|
| **New to material semiotics / ANT** | [docs/primer.md](docs/primer.md) — every concept in ten minutes, then the scallops case read record by record |
| **Adopting the toolchain** (developer, analyst) | [docs/toolchain.md](docs/toolchain.md) — install, file layout, every command, the sixteen compilers, how to read a verification result, the C / R / ADR index |
| **Facilitating a session** with an ethnographer (a person at the keyboard, or driving an LLM) | [docs/facilitation.md](docs/facilitation.md) — the session shape, the questions to ask, what the ethnographer owns vs the tool, the review loop |
| **An LLM agent** working in this repo | [CLAUDE.md](CLAUDE.md) to author (write to the graph); [AGENTS.md](AGENTS.md) to read (route a question to a brief, interpret without misreading) |
| **Reviewing the theory or the design** | [ONTOLOGICAL_COMMITMENTS.md](ONTOLOGICAL_COMMITMENTS.md) (C1–C9) → [adr/README.md](adr/README.md) (R1–R10 and ADR-0001…0007) → [FUTURE_WORK.md](FUTURE_WORK.md) → [abstract.md](abstract.md) |

## Quickstart

```bash
git clone https://github.com/mzargham/ant-rdf && cd ant-rdf
uv sync
uv run ant version                          # ant-rdf 0.1.0
uv run ant verify                           # SHACL Tier-1/2 + cross-refs; a few Tier-2 warnings are expected on the public cases
uv run ant query roles larvae-collectors    # the scallops flip: Intermediary under one practice, Mediator under another
uv run ant refresh koi --plan               # what the multi-perspective case compiles to
```

Open [briefs/koi-guide.md](briefs/koi-guide.md) for a case with a reading guide, [briefs/scallops-network.md](briefs/scallops-network.md) for the canonical worked example, or [wiki/Home.md](wiki/Home.md) for the whole graph. Four public cases ship: **scallops** (Callon 1986, the canonical example), **hotel-keys** (Latour 1991), **koi** (a contemporary field site read from two perspectives) and **pi-learning** (a self-directed-learning network); see [briefs/case-catalog.md](briefs/case-catalog.md).

## How it works, in one paragraph

Records live under `instances/cases/<case>/perspectives/<perspective>/` as deterministic Turtle written only by the `ant` CLI. `ant verify` checks them against SHACL shapes in three tiers — structural violations break, analytical-hygiene warnings surface and can be waived with a justification, lint is advisory (**C7**: the tool guarantees structure, the ethnographer guarantees content). `ant refresh <case>` compiles the briefs a case supports; `ant wiki` regenerates the navigation; CI fails if committed artifacts differ from a fresh regeneration. The layout, the commands and the compilers are documented in [docs/toolchain.md](docs/toolchain.md).

```text
ontology/          the vocabulary + SHACL shapes (CC0)
instances/         shared practices/agents, and one directory per case
briefs/  wiki/     derived — never hand-edited
src/ant_rdf/       the `ant` CLI and the compilers          tests/  docs/  adr/
```

## Citation

If you use `ant-rdf` in published work, cite this repository and the founding texts the vocabulary inherits from (every term carries a `dcterms:source`; see the wiki's concept pages). The theoretical frame — Artificial Organisational Intelligence and "building the loop" — is developed in Rennie et al. (2026), [DOI:10.1111/epic.70009](https://doi.org/10.1111/epic.70009).

## Licensing

Tri-licensed by artifact class: **code** Apache-2.0, **ontology** CC0-1.0, **documentation, briefs, wiki and case data** CC-BY-4.0. See [LICENSE.md](LICENSE.md).
