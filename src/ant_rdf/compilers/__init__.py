# SPDX-License-Identifier: Apache-2.0
"""Compiler registry: DocumentKind → compile function (per plan §6).

Each compiler module exposes a ``compile_(dataset, subject=None) -> str``
that produces deterministic Markdown.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from rdflib import URIRef
from rich.console import Console

from ant_rdf.graph import CASES_DIR, new_dataset

console = Console()

# DocumentKind → import path of the compiler module.
REGISTRY: dict[str, str] = {
    "NetworkBrief": "ant_rdf.compilers.networkbrief",
    "ActantProfile": "ant_rdf.compilers.actantprofile",
    "TranslationTrace": "ant_rdf.compilers.translationtrace",
    "CaseCatalog": "ant_rdf.compilers.casecatalog",
}

# Compilers in this set load the FULL dataset rather than just one case —
# they're cross-case indexes / catalogs.
_CROSS_CASE_KINDS: set[str] = {"CaseCatalog"}


def compile_document(
    file: str,
    document_kind: str,
    output: str | None = None,
    perspective: str | None = None,
) -> None:
    if document_kind not in REGISTRY:
        raise SystemExit(
            f"DocumentKind {document_kind!r} not registered. "
            f"Available: {sorted(REGISTRY)}"
        )

    # Build the dataset. Cross-case kinds load the full dataset; per-case
    # kinds load the named file plus sibling TTL in the same case for
    # crossref resolution.
    src = Path(file)
    if document_kind in _CROSS_CASE_KINDS:
        from ant_rdf.graph import load_full_dataset
        ds = load_full_dataset()
    else:
        ds = new_dataset()
        if src.exists() and src.is_file():
            ds.parse(src, format="turtle")
            case_root = _case_root_for(src)
            if case_root:
                for p in sorted(case_root.rglob("*.ttl")):
                    if p.resolve() == src.resolve():
                        continue
                    ds.parse(p, format="turtle")
        else:
            case_dir = CASES_DIR / file
            if not case_dir.exists():
                raise SystemExit(f"No such file or case directory: {file}")
            for p in sorted(case_dir.rglob("*.ttl")):
                ds.parse(p, format="turtle")

    module = import_module(REGISTRY[document_kind])
    md = module.compile_(ds, subject=None)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        console.print(f"[green]✓ wrote[/green] {out_path}")
    else:
        # Echo to stdout — useful for shell pipelines and quick previews.
        print(md)


def _case_root_for(path: Path) -> Path | None:
    """Walk up from a file to find the nearest ``instances/cases/<slug>/`` root."""
    p = path.resolve().parent
    while p != p.parent:
        if p.parent.name == "cases" and p.parent.parent.name == "instances":
            return p
        p = p.parent
    return None
