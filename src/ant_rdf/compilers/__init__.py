# SPDX-License-Identifier: Apache-2.0
"""Compiler registry: DocumentKind → compile function (per plan §6).

Each compiler module exposes a ``compile_(dataset, subject=None) -> str``
that produces deterministic Markdown.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from rdflib import RDF, URIRef
from rich.console import Console

from ant_rdf import ANT
from ant_rdf.graph import CASES_DIR, new_dataset

console = Console()

# DocumentKind → import path of the compiler module.
REGISTRY: dict[str, str] = {
    "NetworkBrief": "ant_rdf.compilers.networkbrief",
    "ActantProfile": "ant_rdf.compilers.actantprofile",
    "TranslationTrace": "ant_rdf.compilers.translationtrace",
    "CaseCatalog": "ant_rdf.compilers.casecatalog",
    "PerspectiveComparison": "ant_rdf.compilers.perspectivecomparison",
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
                    if not _in_perspective_scope(p, perspective):
                        continue
                    ds.parse(p, format="turtle")
        else:
            case_dir = CASES_DIR / file
            if not case_dir.exists():
                raise SystemExit(f"No such file or case directory: {file}")
            for p in sorted(case_dir.rglob("*.ttl")):
                if not _in_perspective_scope(p, perspective):
                    continue
                ds.parse(p, format="turtle")

    subject = _resolve_perspective_subject(file, src, perspective)

    module = import_module(REGISTRY[document_kind])
    md = module.compile_(ds, subject=subject)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        console.print(f"[green]✓ wrote[/green] {out_path}")
    else:
        # Echo to stdout — useful for shell pipelines and quick previews.
        print(md)


def _in_perspective_scope(p: Path, perspective: str | None) -> bool:
    """Whether a TTL file belongs in a perspective-scoped compile.

    A perspective-scoped brief should see only its own observer-frame plus
    shared content: files under ``perspectives/<perspective>/``, the
    ``_default`` perspective, and any case-level file not under
    ``perspectives/`` at all. Files under a *sibling* perspective are excluded
    — without this, every perspective's translations and characterizations
    leak into the graph and the brief renders them all.
    """
    if perspective is None:
        return True
    parts = p.parts
    if "perspectives" not in parts:
        return True
    i = parts.index("perspectives")
    if i + 1 >= len(parts):
        return True
    seg = parts[i + 1]
    return seg in (perspective, "_default")


def _resolve_perspective_subject(
    file: str, src: Path, perspective: str | None
) -> URIRef | None:
    """Pin the Network subject to the requested perspective.

    Without this, a compiler that renders "one Network" falls back to the
    first network found alphabetically — silently ignoring ``--perspective``
    when a case holds several perspective-scoped networks.
    """
    if not perspective:
        return None

    if src.exists() and src.is_file():
        case_root = _case_root_for(src)
    else:
        case_root = CASES_DIR / file
    if case_root is None:
        return None

    networks_ttl = case_root / "perspectives" / perspective / "networks.ttl"
    if not networks_ttl.is_file():
        return None

    g = new_dataset().default_graph
    g.parse(networks_ttl, format="turtle")
    nets = sorted(
        s for s in g.subjects(RDF.type, ANT.Network) if isinstance(s, URIRef)
    )
    return nets[0] if nets else None


def _case_root_for(path: Path) -> Path | None:
    """Walk up from a file to find the nearest ``instances/cases/<slug>/`` root."""
    p = path.resolve().parent
    while p != p.parent:
        if p.parent.name == "cases" and p.parent.parent.name == "instances":
            return p
        p = p.parent
    return None
