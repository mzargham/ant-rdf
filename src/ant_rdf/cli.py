# SPDX-License-Identifier: Apache-2.0
"""``ant`` CLI — Typer app exposing record authoring, validation, compilation, and wiki.

Subcommands:

* ``ant new-record <kind> ...``    — create a record (flag-driven)
* ``ant new-record interactive``    — walk-me-through (conversational)
* ``ant edit-record <kind> ...``    — set-replace fields on a record, in place
* ``ant remove-record``             — delete one record (cross-ref pre-check)
* ``ant ingest notes|upload``       — non-conversational paths
* ``ant verify``                    — SHACL + cross-reference (tri-severity)
* ``ant waive``                     — record a Tier-2 constraint waiver
* ``ant compile <file> <DocumentKind>`` — render a brief via the compiler REGISTRY
* ``ant refresh <case>``            — regenerate a case's whole brief set
* ``ant list``                      — census of records (scopeable by case/perspective)
* ``ant query <subcommand>``        — read-only navigation (roles, flips, show, …)
* ``ant ontology validate``         — governance helper
* ``ant scope new``                 — declare a scope (act 1 of the four acts, ADR-0000 R5; stub)
* ``ant analyze list-methods``      — analytical methods (act 3 stub, v2)
* ``ant wiki``                      — generate wiki pages

This file is the user-facing surface and intentionally thin — heavy lifting
lives in serialize.py, verify.py, new_record.py, edit_record.py, query.py,
ingest.py, compilers/, wiki.py.
"""

from __future__ import annotations

import typer
from rich.console import Console

from ant_rdf import __version__
from ant_rdf.compilers import REGISTRY as _KINDS

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
ingest_app = typer.Typer(help="Non-conversational ingestion: YAML-frontmatter notes and raw-material uploads.")
ontology_app = typer.Typer(help="Ontology governance helpers.")
waive_app = typer.Typer(help="Record or audit Tier-2 SHACL waivers.")
scope_app = typer.Typer(help="Scope selection (act 1 of the four acts, ADR-0000 R5). Stub — not implemented.")
analyze_app = typer.Typer(help="Analysis (act 3 of the four acts, ADR-0000 R5). Stub — no methods yet.")
query_app = typer.Typer(
    help="Read-only graph queries for navigating the field (see the ant-query skill)."
)

app.add_typer(new_record_app, name="new-record")
app.add_typer(edit_record_app, name="edit-record")
app.add_typer(query_app, name="query")
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
    """SHACL + cross-reference validation with tri-severity output (C7 / R9b)."""
    from ant_rdf.verify import run_verify

    code = run_verify(graph=graph, strict=strict, lint=lint, no_waivers=no_waivers)
    raise typer.Exit(code=code)


@app.command()
def compile(
    file: str = typer.Argument(..., help="Source TTL file (or case slug)."),
    document_kind: str = typer.Argument(..., help="DocumentKind — one of: " + ", ".join(sorted(_KINDS)) + "."),
    output: str | None = typer.Option(None, "-o", "--output", help="Output Markdown path (omit to print to stdout). CaseCatalog always writes to briefs/case-catalog.md."),
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
    perspective: str | None = typer.Option(None, "--perspective", help="Scope to one perspective/frame."),
    case: str | None = typer.Option(None, "--case", help="Scope to one case slug."),
) -> None:
    """List records in the loaded graph (scopeable by --case / --perspective)."""
    from ant_rdf.verify import run_list

    run_list(kind=kind, iri=iri, perspective=perspective, case=case)


@app.command()
def wiki(
    output_dir: str | None = typer.Option(None, "-o", "--output-dir"),
) -> None:
    """Generate wiki pages to wiki/ (ethnographer-navigable)."""
    from ant_rdf.wiki import run_wiki

    run_wiki(output_dir=output_dir)


@app.command()
def refresh(
    case: str = typer.Argument(..., help="Case slug whose brief set to regenerate (e.g. 'koi')."),
    wiki: bool = typer.Option(False, "--wiki", help="Also regenerate the wiki/."),
    verify: bool = typer.Option(False, "--verify", help="Also run `ant verify` at the end."),
    plan: bool = typer.Option(False, "--plan", help="Print what would be written and exit (no files touched)."),
) -> None:
    """Regenerate a case's whole canonical brief set (one command instead of
    one `ant compile` per brief). Briefs are derived — never hand-edit them."""
    from ant_rdf.compilers import refresh_case, refresh_plan

    if plan:
        for kind, output, persp in refresh_plan(case):
            console.print(f"  {kind:<26} → {output}" + (f"  (--perspective {persp})" if persp else ""))
        return
    refresh_case(case, do_wiki=wiki, do_verify=verify)


# ---------------------------------------------------------------------------
# query subcommands — read-only graph navigation (see the ant-query skill)
# ---------------------------------------------------------------------------

_JSON = typer.Option(False, "--json", help="Emit JSON instead of Rich text.")


def _run_query(fn, *args) -> None:  # type: ignore[no-untyped-def]
    from ant_rdf.query import QueryError
    try:
        fn(*args)
    except QueryError as e:
        raise typer.BadParameter(str(e)) from e


@query_app.command("roles")
def query_roles_cmd(
    actant: str = typer.Argument(..., help="Actant slug or IRI (e.g. 'larvae-collectors')."),
    as_json: bool = _JSON,
) -> None:
    """Every role an actant is given, frame by frame (via ant:Characterization)."""
    from ant_rdf.query import run_roles
    _run_query(run_roles, actant, as_json)


@query_app.command("flips")
def query_flips_cmd(as_json: bool = _JSON) -> None:
    """Actants read as different roles by different frames."""
    from ant_rdf.query import run_flips
    _run_query(run_flips, as_json)


@query_app.command("traffic")
def query_traffic_cmd(
    passage: str = typer.Argument(..., help="OPP actant slug or IRI."),
    as_json: bool = _JSON,
) -> None:
    """Translations that trace to / pass through an obligatory passage point."""
    from ant_rdf.query import run_traffic
    _run_query(run_traffic, passage, as_json)


@query_app.command("status")
def query_status_cmd(
    status: str = typer.Argument(..., help="stabilized | precarious | unravelled | forming"),
    as_json: bool = _JSON,
) -> None:
    """Translations by behavioral status (forming = no ant:hasStatus)."""
    from ant_rdf.query import run_status
    _run_query(run_status, status, as_json)


@query_app.command("same-program")
def query_same_program_cmd(
    of: str | None = typer.Option(None, "--of", help="Only the cluster containing this translation."),
    as_json: bool = _JSON,
) -> None:
    """Clusters of translations linked by ant:readsSameProgramAs."""
    from ant_rdf.query import run_same_program
    _run_query(run_same_program, of, as_json)


@query_app.command("anti-programs")
def query_anti_programs_cmd(as_json: bool = _JSON) -> None:
    """The ant:opposes edges (program of action -> what it runs against)."""
    from ant_rdf.query import run_anti_programs
    _run_query(run_anti_programs, as_json)


@query_app.command("manifests")
def query_manifests_cmd(as_json: bool = _JSON) -> None:
    """The ant:manifestsAs edges (an actant that is also an inscription; C9)."""
    from ant_rdf.query import run_manifests
    _run_query(run_manifests, as_json)


@query_app.command("search")
def query_search_cmd(
    text: str = typer.Argument(..., help="Case-insensitive substring."),
    as_json: bool = _JSON,
) -> None:
    """Search labels and descriptions across the whole graph."""
    from ant_rdf.query import run_search
    _run_query(run_search, text, as_json)


@query_app.command("show")
def query_show_cmd(
    record: str = typer.Argument(..., help="Record slug or IRI."),
    as_json: bool = _JSON,
) -> None:
    """A fidelity-aware record view (labels resolved; Characterizations narrated)."""
    from ant_rdf.query import run_show
    _run_query(run_show, record, as_json)


@query_app.command("sparql")
def query_sparql_cmd(
    query: str = typer.Argument(..., help="A SPARQL SELECT/ASK over the instance graph."),
    as_json: bool = _JSON,
) -> None:
    """Escape hatch: run arbitrary SPARQL over the full instance graph."""
    from ant_rdf.query import run_sparql
    _run_query(run_sparql, query, as_json)


# ---------------------------------------------------------------------------
# new-record subcommands (stubs — real impl in new_record.py)
# ---------------------------------------------------------------------------

# Short tokens accepted by --class / --durability / --status (or pass a full IRI).
_INSCRIPTION_CLASS_TOKENS = {
    "inscription": "https://w3id.org/ant#Inscription",
    "immutable": "https://w3id.org/ant#ImmutableMobile",
    "immutable-mobile": "https://w3id.org/ant#ImmutableMobile",
    "fluid": "https://w3id.org/ant#FluidObject",
    "fluid-object": "https://w3id.org/ant#FluidObject",
    "ant:Inscription": "https://w3id.org/ant#Inscription",
    "ant:ImmutableMobile": "https://w3id.org/ant#ImmutableMobile",
    "ant:FluidObject": "https://w3id.org/ant#FluidObject",
}
_DURABILITY_TOKENS = {
    "material": "https://w3id.org/ant#MaterialDurability",
    "strategic": "https://w3id.org/ant#StrategicDurability",
    "discursive": "https://w3id.org/ant#DiscursiveStability",
}
_STATUS_TOKENS = {
    "stabilized": "https://w3id.org/ant#Stabilized",
    "precarious": "https://w3id.org/ant#Precarious",
    "unravelled": "https://w3id.org/ant#Unravelled",
    "unraveled": "https://w3id.org/ant#Unravelled",  # accept US spelling
}


def _expand_token(token: str | None, mapping: dict[str, str], what: str) -> str | None:
    """Accept a short token (e.g. 'immutable', 'precarious') or a full IRI."""
    if token is None:
        return None
    if token in mapping:
        return mapping[token]
    if token.startswith("http"):
        return token
    raise typer.BadParameter(
        f"unknown {what} {token!r}; expected one of {sorted(set(mapping))} or a full IRI"
    )



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
    """Create an ant:Network record (an analyst-named summary; act 4 of the four acts, ADR-0000 R5)."""
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
    corresponds_to: list[str] = typer.Option([], "--corresponds-to", help="Actant IRIs this actant corresponds to across frames (ant:correspondsTo; symmetric)."),
    internalizes: list[str] = typer.Option([], "--internalizes", help="Perspective IRIs this (persona) actant internalizes (ant:internalizes)."),
    inscribes: list[str] = typer.Option([], "--inscribes", help="Inscription IRIs this actant produces (ant:inscribes)."),
    draws_on: list[str] = typer.Option([], "--draws-on", help="Inscription IRIs this actant consumes / builds on (ant:drawsOn)."),
    manifests_as: list[str] = typer.Option([], "--manifests-as", help="Inscription IRIs this actant is also present as (ant:manifestsAs; C9 / ADR-0007)."),
    has_program: list[str] = typer.Option([], "--has-program", help="ProgramOfAction IRIs this actant carries (ant:hasProgram — a program is never standalone)."),
    enrols: list[str] = typer.Option([], "--enrols", help="Actant IRIs this actant enrols (ant:enrols, binary v1 form; see FUTURE_WORK.md, reified relations)."),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Actant record. Use --perspective _shared for a shared actant's
    frame-neutral identity (ADR-0003)."""
    from ant_rdf.new_record import create_actant

    create_actant(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, participates_in=participates_in,
        corresponds_to=corresponds_to, internalizes=internalizes,
        inscribes=inscribes, draws_on=draws_on, manifests_as=manifests_as,
        has_program=has_program, enrols=enrols, out=out,
    )


@new_record_app.command("inscription")
def new_inscription(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    klass: str = typer.Option(
        "ant:Inscription", "--class",
        help="ant:Inscription | ant:ImmutableMobile | ant:FluidObject (or immutable / fluid).",
    ),
    source: str | None = typer.Option(
        None, "--source", help="dcterms:source — a URL, citation, or file hash for the material.",
    ),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Inscription (or ImmutableMobile / FluidObject) record.

    For material referenced by URL/citation (a repository, a paper) rather than
    an uploaded file — see `ant ingest upload` for file-hash provenance instead.
    Pick the class by how the thing persists: holds form constant → immutable;
    persists by controlled mutability (a living repository) → fluid.
    """
    from ant_rdf.new_record import create_inscription

    klass_iri = _expand_token(klass, _INSCRIPTION_CLASS_TOKENS, "inscription class") or ""
    klass_key = "ant:" + klass_iri.rsplit("#", 1)[-1]
    try:
        create_inscription(
            iri=iri, label=label, description=description, case=case,
            perspective=perspective, klass=klass_key, source=source, out=out,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@new_record_app.command("program")
def new_program(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    opposes: list[str] = typer.Option([], "--opposes"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:ProgramOfAction (use --opposes to pair a program with its anti-program).

    A program is never standalone: name its carrier with `--has-program` on the actant.
    """
    from ant_rdf.new_record import create_program_of_action

    create_program_of_action(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, opposes=opposes, out=out,
    )


@new_record_app.command("translation")
def new_translation(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    has_moment: list[str] = typer.Option([], "--has-moment"),
    reads_same_program_as: list[str] = typer.Option([], "--reads-same-program-as", help="Translation IRIs reading the same program from another frame (ant:readsSameProgramAs; symmetric)."),
    traces_to_passage: list[str] = typer.Option([], "--traces-to-passage", help="OPP actant IRIs this translation must clear (ant:tracesToPassage)."),
    durability: str | None = typer.Option(None, "--durability", help="material | strategic | discursive (ant:hasDurability, Law 2008)."),
    status: str | None = typer.Option(None, "--status", help="stabilized | precarious | unravelled (ant:hasStatus); omit = forming / not yet assessed."),
    authored_under: str | None = typer.Option(None, "--authored-under", help="Perspective IRI the translation is authored under (ant:authoredUnder; frame provenance, ADR-0004)."),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create an ant:Translation record (must have at least one moment — Tier 1)."""
    from ant_rdf.new_record import create_translation

    create_translation(
        iri=iri, label=label, description=description, case=case,
        perspective=perspective, has_moment=has_moment,
        reads_same_program_as=reads_same_program_as,
        traces_to_passage=traces_to_passage,
        has_durability=_expand_token(durability, _DURABILITY_TOKENS, "durability"),
        has_status=_expand_token(status, _STATUS_TOKENS, "status"),
        authored_under=authored_under,
        out=out,
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
    """Create an ant:Characterization (a reified, context-bound role assignment; ADR-0000 R3)."""
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


@new_record_app.command("agent")
def new_agent(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description"),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create a prov:Agent record (shared; a named holder for ant:perspectiveHeldBy)."""
    from ant_rdf.new_record import create_agent

    create_agent(iri=iri, label=label, description=description, out=out)


@new_record_app.command("glossary-term")
def new_glossary_term(
    iri: str = typer.Option(..., "--iri"),
    label: str = typer.Option(..., "--label"),
    description: str = typer.Option(..., "--description", help="Concise definition, faithful to a cited source."),
    acronym: str | None = typer.Option(None, "--acronym"),
    used_as: str | None = typer.Option(None, "--used-as", help="How this reading uses the word (the hook)."),
    category: str | None = typer.Option(None, "--category", help="Bucket for grouping in the glossary."),
    source: list[str] = typer.Option([], "--source", help="Citation (repeatable); may include a URL."),
    out: str | None = typer.Option(None, "--out"),
) -> None:
    """Create a skos:Concept glossary term (shared; a reader aid with a citable definition)."""
    from ant_rdf.new_record import create_glossary_term

    create_glossary_term(iri=iri, label=label, description=description,
                         acronym=acronym, used_as=used_as, category=category, sources=source, out=out)


@new_record_app.command("interactive")
def new_record_interactive(
    kind: str = typer.Argument(..., help="Record kind (network, actant, translation, perspective, characterization)."),
) -> None:
    """Walk-me-through prompts for a record kind (conversational catechism)."""
    from ant_rdf.new_record import interactive_create

    interactive_create(kind=kind)


# ---------------------------------------------------------------------------
# edit-record subcommands — in-place field upsert (set-replace provided fields)
# ---------------------------------------------------------------------------

def _run_edit(
    kind: str,
    iri: str,
    updates: dict[str, object],
    *,
    case: str | None = None,
    perspective: str | None = None,
) -> None:
    from ant_rdf.edit_record import EditError, edit_record

    if not updates:
        console.print("[yellow]No fields provided to edit; nothing changed.[/]")
        raise typer.Exit(code=1)
    try:
        path = edit_record(kind, iri, updates, case=case, perspective=perspective)
    except EditError as exc:
        console.print(f"[red]edit-record {kind}:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(
        f"[green]edited[/] {iri} in {path} (fields: {', '.join(sorted(updates))})"
    )


@edit_record_app.command("actant")
def edit_actant(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
    participates_in: list[str] = typer.Option([], "--participates-in"),
    clear_participates_in: bool = typer.Option(False, "--clear-participates-in", help="Remove all ant:participatesIn edges."),
    corresponds_to: list[str] = typer.Option([], "--corresponds-to"),
    clear_corresponds_to: bool = typer.Option(False, "--clear-corresponds-to"),
    internalizes: list[str] = typer.Option([], "--internalizes"),
    clear_internalizes: bool = typer.Option(False, "--clear-internalizes"),
    inscribes: list[str] = typer.Option([], "--inscribes", help="Inscription IRIs this actant produces."),
    clear_inscribes: bool = typer.Option(False, "--clear-inscribes"),
    draws_on: list[str] = typer.Option([], "--draws-on", help="Inscription IRIs this actant consumes / builds on."),
    clear_draws_on: bool = typer.Option(False, "--clear-draws-on"),
    manifests_as: list[str] = typer.Option([], "--manifests-as", help="Inscription IRIs this actant is also present as (C9 / ADR-0007)."),
    clear_manifests_as: bool = typer.Option(False, "--clear-manifests-as"),
    has_program: list[str] = typer.Option([], "--has-program", help="ProgramOfAction IRIs this actant carries."),
    clear_has_program: bool = typer.Option(False, "--clear-has-program"),
    enrols: list[str] = typer.Option([], "--enrols", help="Actant IRIs this actant enrols (binary v1 form)."),
    clear_enrols: bool = typer.Option(False, "--clear-enrols"),
) -> None:
    """Edit an ant:Actant in place (set-replace provided fields; --clear-* empties a multi-valued field)."""
    updates: dict[str, object] = {}
    if label is not None:
        updates["label"] = label
    if description is not None:
        updates["description"] = description
    for key, values, clear in (
        ("participates_in", participates_in, clear_participates_in),
        ("corresponds_to", corresponds_to, clear_corresponds_to),
        ("internalizes", internalizes, clear_internalizes),
        ("inscribes", inscribes, clear_inscribes),
        ("draws_on", draws_on, clear_draws_on),
        ("manifests_as", manifests_as, clear_manifests_as),
        ("has_program", has_program, clear_has_program),
        ("enrols", enrols, clear_enrols),
    ):
        if values:
            updates[key] = list(values)
        elif clear:
            updates[key] = []
    _run_edit("actant", iri, updates, case=case, perspective=perspective)


@edit_record_app.command("characterization")
def edit_characterization(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    target: str | None = typer.Option(None, "--target"),
    within_network: str | None = typer.Option(None, "--in-network"),
    assigns_role: str | None = typer.Option(None, "--role"),
    per_practice: str | None = typer.Option(None, "--per-practice"),
    invariance: str | None = typer.Option(None, "--invariance"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    """Edit an ant:Characterization in place (set-replace provided fields)."""
    updates: dict[str, object] = {}
    for key, val in (
        ("target", target),
        ("within_network", within_network),
        ("assigns_role", assigns_role),
        ("per_practice", per_practice),
        ("invariance", invariance),
        ("description", description),
    ):
        if val is not None:
            updates[key] = val
    _run_edit("characterization", iri, updates, case=case, perspective=perspective)


@edit_record_app.command("network")
def edit_network(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
    scope: str | None = typer.Option(None, "--scope"),
    from_construct: str | None = typer.Option(None, "--from-construct"),
) -> None:
    """Edit an ant:Network in place (set-replace provided fields)."""
    updates: dict[str, object] = {}
    for key, val in (
        ("label", label),
        ("description", description),
        ("scope", scope),
        ("from_construct", from_construct),
    ):
        if val is not None:
            updates[key] = val
    _run_edit("network", iri, updates, case=case, perspective=perspective)


@edit_record_app.command("translation")
def edit_translation(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
    has_moment: list[str] = typer.Option([], "--has-moment"),
    reads_same_program_as: list[str] = typer.Option([], "--reads-same-program-as"),
    clear_reads_same_program_as: bool = typer.Option(False, "--clear-reads-same-program-as"),
    traces_to_passage: list[str] = typer.Option([], "--traces-to-passage"),
    clear_traces_to_passage: bool = typer.Option(False, "--clear-traces-to-passage"),
    durability: str | None = typer.Option(None, "--durability", help="material | strategic | discursive"),
    clear_durability: bool = typer.Option(False, "--clear-durability", help="Remove ant:hasDurability (how the holding holds is not yet assessable)."),
    status: str | None = typer.Option(None, "--status", help="stabilized | precarious | unravelled"),
    clear_status: bool = typer.Option(False, "--clear-status", help="Remove ant:hasStatus — a 'forming / not yet assessed' translation."),
    authored_under: str | None = typer.Option(None, "--authored-under", help="Perspective IRI the translation is authored under (ADR-0004)."),
) -> None:
    """Edit an ant:Translation in place (set-replace provided fields)."""
    if clear_status and status is not None:
        raise typer.BadParameter("pass either --status or --clear-status, not both.")
    if clear_durability and durability is not None:
        raise typer.BadParameter("pass either --durability or --clear-durability, not both.")
    updates: dict[str, object] = {}
    if label is not None:
        updates["label"] = label
    if description is not None:
        updates["description"] = description
    if has_moment:
        updates["has_moment"] = list(has_moment)
    for key, values, clear in (
        ("reads_same_program_as", reads_same_program_as, clear_reads_same_program_as),
        ("traces_to_passage", traces_to_passage, clear_traces_to_passage),
    ):
        if values:
            updates[key] = list(values)
        elif clear:
            updates[key] = []
    if clear_durability:
        updates["has_durability"] = ""
    elif durability is not None:
        updates["has_durability"] = _expand_token(durability, _DURABILITY_TOKENS, "durability")
    if clear_status:
        updates["has_status"] = ""
    elif status is not None:
        updates["has_status"] = _expand_token(status, _STATUS_TOKENS, "status")
    if authored_under is not None:
        updates["authored_under"] = authored_under
    _run_edit("translation", iri, updates, case=case, perspective=perspective)


@edit_record_app.command("moment")
def edit_moment(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    """Edit a Callon moment's label/description in place (not its kind)."""
    updates: dict[str, object] = {}
    if label is not None:
        updates["label"] = label
    if description is not None:
        updates["description"] = description
    _run_edit("moment", iri, updates, case=case, perspective=perspective)


@edit_record_app.command("practice")
def edit_practice(
    iri: str = typer.Option(..., "--iri"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    """Edit a shared ant:Practice in place (set-replace provided fields)."""
    updates: dict[str, object] = {}
    if label is not None:
        updates["label"] = label
    if description is not None:
        updates["description"] = description
    _run_edit("practice", iri, updates)


@edit_record_app.command("program")
def edit_program(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
    opposes: list[str] = typer.Option([], "--opposes"),
    clear_opposes: bool = typer.Option(False, "--clear-opposes", help="Remove all ant:opposes edges."),
) -> None:
    """Edit an ant:ProgramOfAction in place (set-replace provided fields)."""
    updates: dict[str, object] = {}
    if label is not None:
        updates["label"] = label
    if description is not None:
        updates["description"] = description
    if opposes:
        updates["opposes"] = list(opposes)
    elif clear_opposes:
        updates["opposes"] = []
    _run_edit("program", iri, updates, case=case, perspective=perspective)


@edit_record_app.command("inscription")
def edit_inscription(
    iri: str = typer.Option(..., "--iri"),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    label: str | None = typer.Option(None, "--label"),
    description: str | None = typer.Option(None, "--description"),
    source: str | None = typer.Option(None, "--source", help="dcterms:source — a URL, citation, or file hash."),
    klass: str | None = typer.Option(None, "--class", help="ant:Inscription | ant:ImmutableMobile | ant:FluidObject (or immutable / fluid)."),
) -> None:
    """Edit an ant:Inscription (or ImmutableMobile / FluidObject) in place.

    Set-replace the provided fields, including the record's --class (rdf:type);
    the CLI path for changing an inscription without remove-and-recreate.
    """
    updates: dict[str, object] = {}
    if label is not None:
        updates["label"] = label
    if description is not None:
        updates["description"] = description
    if source is not None:
        updates["source"] = source
    if klass is not None:
        updates["class"] = _expand_token(klass, _INSCRIPTION_CLASS_TOKENS, "inscription class")
    _run_edit("inscription", iri, updates, case=case, perspective=perspective)


@app.command("remove-record")
def remove_record_cmd(
    iri: str = typer.Option(..., "--iri", help="IRI of the record to remove."),
    case: str = typer.Option(..., "--case"),
    perspective: str = typer.Option("_default", "--perspective"),
    force: bool = typer.Option(
        False, "--force", help="Remove even if other records reference it."
    ),
    target: str | None = typer.Option(
        None, "--target",
        help="Explicit kind-file to remove from (e.g. a shared file like "
        "instances/shared/practices.ttl that is not under a case perspective).",
    ),
) -> None:
    """Remove one record's triples from its kind-file (cross-ref pre-check)."""
    from pathlib import Path

    from ant_rdf.edit_record import EditError, remove_record

    try:
        path, refs = remove_record(
            iri, case=case, perspective=perspective, force=force,
            target=Path(target) if target else None,
        )
    except EditError as exc:
        console.print(f"[red]remove-record:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]removed[/] {iri} from {path}")
    if refs:
        console.print(
            f"[yellow]warning:[/] {len(refs)} record(s) still reference {iri} "
            "— now dangling; run `ant verify`:"
        )
        for r in refs:
            console.print(f"  - {r}")


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
# scope / analyze subcommands (the four acts, ADR-0000 R5) — stubs
# ---------------------------------------------------------------------------


@scope_app.command("new")
def scope_new(
    slug: str = typer.Argument(...),
    case: list[str] = typer.Option(..., "--case"),
    perspective: list[str] = typer.Option([], "--perspective"),
    filter_: list[str] = typer.Option([], "--filter"),
) -> None:
    """Declare an ant:Scope (act 1 of the four acts). STUB — not implemented yet."""
    console.print(
        "[yellow]ant scope new is a stub:[/yellow] scope selection (act 1, ADR-0000 R5) is not "
        "implemented yet. Compile per case with `ant compile <case> <DocumentKind>` or "
        "`ant refresh <case>`; see FUTURE_WORK.md."
    )
    raise typer.Exit(code=1)


@analyze_app.command("list-methods")
def analyze_list_methods() -> None:
    """List analytical methods (act 3). v1 stub — empty until v2 rule engine."""
    console.print("No analytical methods are registered in v1. Rule-based tagging arrives in v2.")


if __name__ == "__main__":
    app()
