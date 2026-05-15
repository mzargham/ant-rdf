# SPDX-License-Identifier: Apache-2.0
"""Non-conversational ingestion: notes, transcripts, observations, uploads.

All paths produce structurally correct RDF (per C7) and route through a
dry-run + review-document workflow before committing triples — the
ethnographer always sees what *would* be asserted before it lands. Per C8,
this is one ingestion path among several; the same backing ``serialize.py``
and ``new_record`` functions are used.

v1 supports two ingestion formats:

1. **YAML-frontmatter Markdown notes** — a markdown file whose YAML
   frontmatter contains an ``ant:`` block declaring records to create.
2. **Raw-material uploads** — register a file (PDF, image, audio) as an
   ``ant:Inscription`` with content-addressed provenance.

Transcript and observation ingestion stubs are exposed in the CLI but
defer their real parsers to v1.1 — the v1 commitment is the workflow
shape, not heroic NLP.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date as _date
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from ant_rdf.graph import CASES_DIR
from ant_rdf.new_record import (
    create_actant,
    create_characterization,
    create_moment,
    create_network,
    create_perspective,
    create_translation,
)

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _file_hash(path: Path) -> str:
    """sha256 of the file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter (between leading ``---`` lines) and body."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    header = text[3:end].lstrip("\n")
    body = text[end + 4:].lstrip("\n")
    parsed = yaml.safe_load(header) or {}
    if not isinstance(parsed, dict):
        raise ValueError("YAML frontmatter must be a mapping at the top level.")
    return parsed, body


# ---------------------------------------------------------------------------
# notes ingestion
# ---------------------------------------------------------------------------


def ingest_notes(
    file: str,
    case: str,
    perspective: str = "_default",
    dry_run: bool = True,
    review_out: str | None = None,
) -> None:
    """Parse a YAML-frontmatter markdown note into candidate records.

    Frontmatter shape (see ``docs/ingest-notes-format.md`` once written):

        ---
        ant:
          actants:
            - iri: https://w3id.org/ant/cases/x/actant/y
              label: Y
              description: One sentence about Y.
              participates_in:
                - https://w3id.org/ant/cases/x/network
          translations:
            - iri: ...
              has_moment: [...]
        ---
        # Field notes from session 1

        Free-form prose follows here...
    """
    src = Path(file)
    if not src.exists():
        raise SystemExit(f"file not found: {src}")

    text = src.read_text(encoding="utf-8")
    front, body = _parse_frontmatter(text)
    ant_block = front.get("ant", {}) if isinstance(front, dict) else {}

    candidates = _extract_candidates(ant_block, case, perspective, src)

    if not candidates:
        console.print(
            "[yellow]No `ant:` block found in frontmatter (or no records inside it). "
            "Nothing to ingest.[/yellow]"
        )
        return

    # Always write the review document
    review_path = Path(review_out) if review_out else Path(f"/tmp/ant-review-{src.stem}.md")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(_render_review(candidates, src, dry_run), encoding="utf-8")
    console.print(f"[blue]Review document written to {review_path}[/blue]")

    if dry_run:
        console.print(
            f"[yellow]Dry-run.[/yellow] Found {len(candidates)} candidate record(s). "
            "Inspect the review document and re-run with `--commit` to land the triples."
        )
        return

    # Commit: dispatch each candidate
    written = 0
    for cand in candidates:
        kind = cand.pop("_kind")
        fn = _COMMITTERS.get(kind)
        if fn is None:
            console.print(f"[red]No committer for kind {kind!r}; skipping.[/red]")
            continue
        try:
            fn(**cand)
            written += 1
        except Exception as e:  # pragma: no cover — surface to user
            console.print(f"[red]Failed to commit {kind} record: {e}[/red]")
    console.print(f"[green]✓ committed {written} record(s)[/green]")


_COMMITTERS = {
    "network": create_network,
    "actant": create_actant,
    "translation": create_translation,
    "perspective": create_perspective,
    "characterization": create_characterization,
    "moment": create_moment,
}


def _extract_candidates(
    ant_block: dict, case: str, perspective: str, src: Path,
) -> list[dict[str, Any]]:
    """Walk an ant: frontmatter dict and produce one candidate per record."""
    out: list[dict[str, Any]] = []
    for kind_plural, records in ant_block.items():
        kind = kind_plural.rstrip("s") if kind_plural.endswith("s") else kind_plural
        if not isinstance(records, list):
            continue
        for rec in records:
            if not isinstance(rec, dict):
                continue
            cand: dict[str, Any] = {"_kind": kind, "case": case}
            if kind not in {"perspective"}:  # perspective derives its own perspective
                cand["perspective"] = rec.get("perspective", perspective)
            # Pass through all known fields, leaving unknowns to fail loudly at commit
            for k, v in rec.items():
                if k == "perspective":
                    continue
                cand[k] = v
            out.append(cand)
    return out


def _render_review(
    candidates: list[dict[str, Any]], src: Path, dry_run: bool,
) -> str:
    lines = [
        f"# Review document — ingest from `{src}`",
        "",
        f"Generated {_date.today().isoformat()}.",
        "",
        f"**Mode:** {'dry-run' if dry_run else 'commit'}",
        "",
        f"**Candidates: {len(candidates)}**",
        "",
        "Review each candidate below. To commit, re-run with `--commit`. "
        "To revise, edit the source notes file and re-run.",
        "",
        "---",
        "",
    ]
    for i, cand in enumerate(candidates, 1):
        kind = cand.get("_kind", "?")
        lines += [f"## Candidate {i}: `{kind}`", "", "```yaml"]
        for k, v in cand.items():
            if k.startswith("_"):
                continue
            lines.append(f"{k}: {v}")
        lines += ["```", ""]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# uploads
# ---------------------------------------------------------------------------


def ingest_upload(
    file: str,
    case: str,
    as_: str = "ant:Inscription",
) -> None:
    """Register a raw material file as an ant:Inscription with file-hash provenance.

    Per §5 ingestion-invariants: uploads are perspective-agnostic. The file
    itself is copied (via reference) into ``instances/cases/<case>/uploads/``;
    a corresponding TTL records the IRI, label, file hash, and original path.
    """
    src = Path(file)
    if not src.exists() or not src.is_file():
        raise SystemExit(f"file not found or not a file: {src}")

    if as_ not in {"ant:Inscription"}:
        raise SystemExit(
            f"Unsupported --as {as_!r}; only ant:Inscription supported in v1."
        )

    digest = _file_hash(src)
    short = digest[:12]
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "-", src.name)
    iri = f"https://w3id.org/ant/cases/{case}/uploads/{short}-{safe_name}"

    from ant_rdf.models import Inscription
    from ant_rdf.serialize import add, write_turtle
    from ant_rdf.graph import new_dataset

    obj = Inscription(
        iri=iri,
        label=src.name,
        description=(
            f"Raw upload registered via `ant ingest upload`. "
            f"Original path at ingestion time: {src.absolute()}. "
            f"Perspective-agnostic — characterize via `ant new-record characterization` "
            f"to attach a role within a specific (network, practice) frame."
        ),
        case=case,
        source=f"sha256:{digest}",
    )

    upload_dir = CASES_DIR / case / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    ttl_path = upload_dir / f"{short}-{safe_name}.ttl"

    ds = new_dataset()
    add(ds, obj)
    write_turtle(ds, ttl_path)
    console.print(
        f"[green]✓ registered upload[/green] {iri}\n"
        f"  sha256: {digest}\n"
        f"  metadata TTL: {ttl_path}\n"
        f"  (file itself not copied — kept at its original location)"
    )


# ---------------------------------------------------------------------------
# transcript / observation — v1.1 placeholders
# ---------------------------------------------------------------------------


def ingest_transcript(file: str, case: str, **_: Any) -> None:  # pragma: no cover
    raise SystemExit(
        "`ant ingest transcript` is reserved for v1.1. For now, structure your "
        "transcript as a YAML-frontmatter markdown note and use `ant ingest notes`."
    )


def ingest_observation(file: str, case: str, **_: Any) -> None:  # pragma: no cover
    raise SystemExit(
        "`ant ingest observation` is reserved for v1.1. For now, use "
        "`ant ingest notes` for structured observations or `ant ingest upload` "
        "for raw media files."
    )
