# Licensing

This repository contains three classes of artifact, each licensed
appropriately. The split is deliberate — every file in the repo carries an
SPDX-License-Identifier header naming which clause applies. When in doubt,
check the header on the specific file.

| Artifact class | License | File |
|---|---|---|
| **Code** (Python in `src/` and `tests/`, GitHub Actions workflows, scripts) | **Apache License 2.0** | [LICENSE-CODE](LICENSE-CODE) |
| **Ontology** (`ontology/*.ttl`, SHACL shapes, alignment modules) | **Creative Commons Zero v1.0 Universal (CC0-1.0)** | [LICENSE-ONTOLOGY](LICENSE-ONTOLOGY) |
| **Documentation & briefs** (`README.md`, `CLAUDE.md`, `ONTOLOGICAL_COMMITMENTS.md`, `adr/`, `briefs/`, `wiki/`, narrative content) | **Creative Commons Attribution 4.0 International (CC-BY-4.0)** | [LICENSE-DOCS](LICENSE-DOCS) |

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

Every file in this repo carries an SPDX-License-Identifier comment so
license-scanning tools and humans can quickly see which terms apply
without consulting this file:

```
# SPDX-License-Identifier: Apache-2.0          # Python files
# SPDX-License-Identifier: CC0-1.0             # Turtle ontology / shapes
<!-- SPDX-License-Identifier: CC-BY-4.0 -->    # Markdown (where applicable)
```

If you find a file without a header, please flag it as an issue or PR.

## Contributions

By contributing to this repository you agree that your contributions are
licensed under the same terms as the artifact class they belong to (per
the table above). No CLA is required.
