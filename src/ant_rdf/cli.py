# SPDX-License-Identifier: Apache-2.0
"""``ant`` CLI — Typer app exposing record authoring, validation, compilation, and wiki.

Subcommands (per plan §5):

* ``ant new-record <kind> ...``    — create a record (flag-driven)
* ``ant new-record interactive``    — walk-me-through (conversational)
* ``ant edit-record <kind> ...``    — mutate a record
* ``ant ingest notes|transcript|observation|upload`` — non-conversational paths
* ``ant verify``                    — SHACL + cross-reference (tri-severity)
* ``ant waive``                     — record a Tier-2 constraint waiver
* ``ant compile <file> <DocumentKind>`` — render a brief via the compiler REGISTRY
* ``ant list``                      — query records in the loaded graph
* ``ant ontology validate|diff``    — governance helpers
* ``ant scope new|list|show``       — declare a scope (act 1, §4.7)
* ``ant query <scope>``             — SPARQL against a scope (act 2)
* ``ant analyze list-methods``      — analytical methods (act 3 stub, v2)
* ``ant wiki``                      — generate wiki pages

This file is the user-facing surface and intentionally thin — heavy lifting
lives in serialize.py, verify.py, new_record.py, ingest.py, compilers/, wiki.py.
"""

from __future__ import annotations

import typer
from rich.console import Console

from ant_rdf import __version__

app = typer.Typer(
    name="ant",
    help="ant-rdf: material-semiotics / ANT authoring & compilation CLI.",
    no_args_is_help=True,
)
console = Console()


# ---------------------------------------------------------------------------
# Sub-apps (populated by their own modules; stubs here keep imports cheap)
# ---------------------------------------------------------------------------

new_record_app = typer.Typer(help="Create a record (flag-driven or interactive).")
edit_record_app = typer.Typer(help="Mutate an existing record.")
ingest_app = typer.Typer(help="Non-conversational ingestion: notes, transcripts, uploads.")
ontology_app = typer.Typer(help="Ontology governance helpers.")
waive_app = typer.Typer(help="Record or audit Tier-2 SHACL waivers.")
scope_app = typer.Typer(help="Scope-selection (act 1 of the four acts; §4.7).")
analyze_app = typer.Typer(help="Analysis (act 3 of the four acts; v1 stub).")

app.add_typer(new_record_app, name="new-record")
app.add_typer(edit_record_app, name="edit-record")
app.add_typer(ingest_app, name="ingest")
app.add_typer(ontology_app, name="ontology")
app.add_typer(waive_app, name="waive")
app.add_typer(scope_app, name="scope")
app.add_typer(analyze_app, name="analyze")


# ---------------------------------------------------------------------------
# Top-level commands (stubs — real logic lives in dedicated modules)
# ---------------------------------------------------------------------------


@app.command()
def version() -> None:
    """Print the ant-rdf version."""
    console.print(f"ant-rdf {__version__}")


@app.command()
def verify(
    graph: str | None = typer.Option(None, "--graph", help="Optional single TTL file to validate."),
    strict: bool = typer.Option(False, "--strict", help="Make Tier-2 warnings break (non-zero exit)."),
    lint: bool = typer.Option(False, "--lint", help="Also report Tier-3 advisory shapes."),
    no_waivers: bool = typer.Option(False, "--no-waivers", help="Ignore waivers; raw warnings."),
) -> None:
    """SHACL + cross-reference validation with tri-severity output (§4.6)."""
    from ant_rdf.verify import run_verify

    code = run_verify(graph=graph, strict=strict, lint=lint, no_waivers=no_waivers)
    raise typer.Exit(code=code)


@app.command()
def compile(
    file: str = typer.Argument(..., help="Source TTL file (or case slug)."),
    document_kind: str = typer.Argument(..., help="DocumentKind (e.g., NetworkBrief)."),
    output: str | None = typer.Option(None, "-o", "--output", help="Output Markdown path."),
    perspective: str | None = typer.Option(
        None, "--perspective", help="Render from a specific perspective (default: merge-all)."
    ),
) -> None:
    """Render a brief via the compiler REGISTRY."""
    from ant_rdf.compilers import compile_document

    compile_document(file=file, document_kind=document_kind, output=output, perspective=perspective)


@app.command(name="list")
def list_records(
    kind: str | None = typer.Option(None, "--kind", help="Filter by class IRI / shorthand."),
    iri: str | None = typer.Option(None, "--iri", help="Show details for a single IRI."),
    perspective: str | None = typer.Option(None, "--perspective", help="Filter by perspective."),
) -> None:
    """Query records in the loaded graph."""
    from ant_rdf.verify import run_list  # placeholder; will move to dedicated module

    run_list(kind=kind, iri=iri, perspective=perspective)


@app.command()
def wiki(
    output_dir: str | None = typer.Option(None, "-o", "--output-dir"),
) -> None:
    """Generate wiki pages to wiki/ (ethnographer-navigable)."""
    from ant_rdf.wiki import run_wiki

    run_wiki(output_dir=output_dir)


# ---------------------------------------------------------------------------
# new-record subcommands (stubs — real impl in new_record.py)
# ---------------------------------------------------------------------------


@new_record_app.command("network")
def new_network(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    scope: str | None = typer.Option(None, "--scope"),
    from_construct: str | None = typer.Option(None, "--from-construct"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Network record (act-4: documentation of an analyst-named summary)."""
    from ant_rdf.new_record import create_network

    create_network(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, scope=scope, from_construct=from_construct, out=out,
    )


@new_record_app.command("actant")
def new_actant(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    participates_in: list[str] = typer.Option([], "--participates-in"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Actant record."""
    from ant_rdf.new_record import create_actant

    create_actant(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, participates_in=participates_in, out=out,
    )


@new_record_app.command("translation")
def new_translation(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    has_moment: list[str] = typer.Option([], "--has-moment"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Translation record (must have at least one moment — Tier 1)."""
    from ant_rdf.new_record import create_translation

    create_translation(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, has_moment=has_moment, out=out,
    )


@new_record_app.command("moment")
def new_moment(
    kind: str = typer.Option(
        ..., "--kind",
        help="One of: problematization, interessement, enrolment, mobilization.",
    ),
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create one of the four Callon moments (subclasses of ant:Translation).

    A moment is later linked from an ant:Translation via --has-moment.
    """
    from ant_rdf.new_record import create_moment

    try:
        create_moment(
            kind, iri, label, description, case,
            perspective=perspective, out=out,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@new_record_app.command("perspective")
def new_perspective(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    held_by: str = typer.Option(..., "--held-by"),
    case: str = typer.Option(..., "--case"),
    grounded_in: list[str] = typer.Option([], "--grounded-in"),
    tracks_invariance: list[str] = typer.Option([], "--tracks-invariance"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    """Create an ant:Perspective record (in v2 this IRI also becomes the named-graph URI)."""
    from ant_rdf.new_record import create_perspective

    create_perspective(
        iri=iri, label=label, held_by=held_by, case=case,
        grounded_in=grounded_in, tracks_invariance=tracks_invariance, description=description,
    )


@new_record_app.command("characterization")
def new_characterization(
    iri: str = typer.Option(..., "--iri"),
    target: str = typer.Option(..., "--target", help="IRI of the actant being characterized."),
    within_network: str = typer.Option(..., "--in-network"),
    per_practice: str | None = typer.Option(None, "--per-practice"),
    invariance: str | None = typer.Option(None, "--invariance"),
    assigns_role: str = typer.Option(..., "--role", help="Role IRI (ant:Mediator, ant:Intermediary, ant:ProvAgent, etc.)."),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    """Create an ant:Characterization (reified context-bound role assignment; §4.1.1)."""
    from ant_rdf.new_record import create_characterization

    create_characterization(
        iri=iri, target=target, within_network=within_network,
        per_practice=per_practice, invariance=invariance, assigns_role=assigns_role,
        case=case, perspective=perspective, description=description,
    )


@new_record_app.command("practice")
def new_practice(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Practice record (shared vocabulary; grounds perspectives and ant:perPractice)."""
    from ant_rdf.new_record import create_practice

    create_practice(iri=iri, label=label, description=description, out=out)


@new_record_app.command("interactive")
def new_record_interactive(
    kind: str = typer.Argument(..., help="Record kind (network, actant, translation, perspective, characterization)."),
) -> None:
    """Walk-me-through prompts for a record kind (conversational catechism)."""
    from ant_rdf.new_record import interactive_create

    interactive_create(kind=kind)


# ---------------------------------------------------------------------------
# ingest subcommands (stubs — real impl in ingest.py)
# ---------------------------------------------------------------------------


@ingest_app.command("notes")
def ingest_notes(
    file: str = typer.Argument(..., help="Markdown / structured-text notes file."),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    dry_run: bool = typer.Option(True, "--dry-run/--commit"),
    review_out: str | None = typer.Option(None, "--review-out"),
) -> None:
    """Parse notes and propose RDF additions; human reviews before commit."""
    from ant_rdf.ingest import ingest_notes as _ingest

    _ingest(file=file, case=case, perspective=perspective, dry_run=dry_run, review_out=review_out)


@ingest_app.command("upload")
def ingest_upload(
    file: str = typer.Argument(..., help="Path or glob for raw materials to register."),
    case: str = typer.Option(..., "--case"),
    as_: str = typer.Option("ant:Inscription", "--as", help="RDF class for the upload (default ant:Inscription)."),
) -> None:
    """Register raw materials (PDFs, images, etc.) as ant:Inscription instances."""
    from ant_rdf.ingest import ingest_upload as _ingest

    _ingest(file=file, case=case, as_=as_)


# ---------------------------------------------------------------------------
# waive subcommands
# ---------------------------------------------------------------------------


@waive_app.command("add")
def waive_add(
    shape: str = typer.Argument(..., help="SHACL shape IRI being waived."),
    target: str = typer.Argument(..., help="Target IRI the waiver applies to."),
    by: str = typer.Option(..., "--by"),
    justification: str = typer.Option(..., "--justification"),
    expires: str | None = typer.Option(None, "--expires"),
) -> None:
    """Record an ant:ConstraintWaiver (Tier-2 only; Tier-1 attempts rejected)."""
    from ant_rdf.verify import create_waiver

    create_waiver(shape=shape, target=target, by=by, justification=justification, expires=expires)


@waive_app.command("list")
def waive_list(
    active: bool = typer.Option(False, "--active"),
    expired: bool = typer.Option(False, "--expired"),
    all_: bool = typer.Option(True, "--all"),
) -> None:
    """List waivers."""
    from ant_rdf.verify import list_waivers

    list_waivers(active=active, expired=expired, all_=all_)


# ---------------------------------------------------------------------------
# ontology subcommands
# ---------------------------------------------------------------------------


@ontology_app.command("validate")
def ontology_validate() -> None:
    """Confirm the ontology + alignment + shapes all parse."""
    from ant_rdf.graph import load_ontology, load_shapes

    load_ontology()
    load_shapes()
    console.print("[green]ontology validates[/green]")


# ---------------------------------------------------------------------------
# scope / analyze subcommands (the four acts, §4.7)
# ---------------------------------------------------------------------------


@scope_app.command("new")
def scope_new(
    slug: str = typer.Argument(...),
    case: list[str] = typer.Option(..., "--case"),
    perspective: list[str] = typer.Option([], "--perspective"),
    filter_: list[str] = typer.Option([], "--filter"),
) -> None:
    """Declare an ant:Scope (act 1)."""
    raise NotImplementedError("ant scope new — to be implemented in src/ant_rdf/scope.py (v1.1)")


@analyze_app.command("list-methods")
def analyze_list_methods() -> None:
    """List analytical methods (act 3). v1 stub — empty until v2 rule engine."""
    console.print("No analytical methods are registered in v1. Rule-based tagging arrives in v2.")


if __name__ == "__main__":
    app()
