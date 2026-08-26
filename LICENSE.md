<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Licensing

This repository contains three classes of artifact, each licensed
appropriately. The split is deliberate — every *source* file carries an
SPDX-License-Identifier header naming which clause applies; generated
artifacts and case data inherit the license of their directory per the
table below. When in doubt, check the header on the specific file, then
this table.

| Artifact class | License | File |
|---|---|---|
| **Code** (Python in `src/` and `tests/`, GitHub Actions workflows, scripts) | **Apache License 2.0** | [LICENSE-CODE](LICENSE-CODE) |
| **Ontology** (`ontology/*.ttl`, SHACL shapes, alignment modules) | **Creative Commons Zero v1.0 Universal (CC0-1.0)** | [LICENSE-ONTOLOGY](LICENSE-ONTOLOGY) |
| **Documentation, briefs, wiki and case data** (`README.md`, `CLAUDE.md`, `AGENTS.md`, `ONTOLOGICAL_COMMITMENTS.md`, `FUTURE_WORK.md`, `abstract.md`, `docs/`, `adr/`, `.claude/skills/`, the generated `briefs/` and `wiki/`, and the ethnographic case records under `instances/`) | **Creative Commons Attribution 4.0 International (CC-BY-4.0)** | [LICENSE-DOCS](LICENSE-DOCS) |

## Why three licenses?

- **Apache-2.0 for code** — standard permissive license for Python tooling
  with an explicit patent grant; broadly compatible with downstream use.
- **CC0 for the ontology** — the linked-data norm for shared vocabularies
  (see [LOV](https://lov.linkeddata.es/)). No attribution burden on
  consumers who import the IRIs; vocabulary terms work like punctuation.
- **CC-BY-4.0 for documentation** — narrative and case-study material
  carries authorship; ethnographers and contributors get credit. Reuse is
  permitted with attribution.

## SPDX headers

Every source file carries an SPDX-License-Identifier comment so
license-scanning tools and humans can quickly see which terms apply
without consulting this file:

```
# SPDX-License-Identifier: Apache-2.0          # Python files, workflows, tools
# SPDX-License-Identifier: CC0-1.0             # ontology/*.ttl and ontology/shapes/*.ttl
<!-- SPDX-License-Identifier: CC-BY-4.0 -->    # hand-written Markdown
```

Generated Markdown (`briefs/`, `wiki/`) and the instance Turtle under
`instances/` (written only by the `ant` CLI) carry no per-file header; they
are CC-BY-4.0 by the table above. The `pyproject.toml` license field names
Apache-2.0 alone because the distributed wheel contains only `src/ant_rdf`.
If you find a *source* file without a header, please flag it.

## Contributions

By contributing to this repository you agree that your contributions are
licensed under the same terms as the artifact class they belong to (per
the table above). No CLA is required.
