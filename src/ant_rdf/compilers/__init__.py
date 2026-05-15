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
    # "ActantProfile": "ant_rdf.compilers.actantprofile",        # step 12
    # "TranslationTrace": "ant_rdf.compilers.translationtrace",  # step 12
    # "CaseCatalog": "ant_rdf.compilers.casecatalog",            # step 12
}


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

    # Build the dataset: the explicit file plus everything it cross-references.
    # v1 simplest path: load the file plus all sibling files in its case directory.
    src = Path(file)
    ds = new_dataset()
    if src.exists() and src.is_file():
        # Load the named file and (for crossref resolution) all TTL in the
        # surrounding case directory.
        ds.parse(src, format="turtle")
        case_root = _case_root_for(src)
        if case_root:
            for p in sorted(case_root.rglob("*.ttl")):
                if p.resolve() == src.resolve():
                    continue
                ds.parse(p, format="turtle")
    else:
        # Treat ``file`` as a case slug
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
