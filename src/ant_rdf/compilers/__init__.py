# SPDX-License-Identifier: Apache-2.0
"""Compiler registry: DocumentKind → compile function (per plan §6).

Each compiler module exposes a ``compile(dataset, subject=None, perspective=None) -> str``
that produces deterministic Markdown.
"""

from __future__ import annotations

REGISTRY: dict[str, str] = {
    # "NetworkBrief": "ant_rdf.compilers.networkbrief",   # step 8
    # "ActantProfile": "ant_rdf.compilers.actantprofile",  # step 12
    # "TranslationTrace": "ant_rdf.compilers.translationtrace",  # step 12
    # "CaseCatalog": "ant_rdf.compilers.casecatalog",  # step 12
}


def compile_document(
    file: str,
    document_kind: str,
    output: str | None = None,
    perspective: str | None = None,
) -> None:  # pragma: no cover — step 8+
    if document_kind not in REGISTRY:
        raise NotImplementedError(
            f"DocumentKind {document_kind!r} not yet registered. "
            f"Available: {sorted(REGISTRY)}. (plan §10 step 8+)"
        )
    raise NotImplementedError("compile_document — step 8 of plan §10.")
