# SPDX-License-Identifier: Apache-2.0
"""SHACL validation + cross-reference resolution + tri-severity output (§4.6).

Three constraint tiers (per plan §4.6):

* **Tier 1 — Violations** (load-bearing). Break by default; never waivable.
* **Tier 2 — Warnings** (should-conform). Surface, but waivable via
  ``ant:ConstraintWaiver`` with required justification. ``--strict`` makes
  them break.
* **Tier 3 — Info** (advisory). Surface only with ``--lint``; never break.

CI default per R9b: warnings surface in the log but do not break the build.
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path

from pyshacl import validate as _pyshacl_validate
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF
from rich.console import Console

from ant_rdf import ANT
from ant_rdf.graph import (
    CASES_DIR,
    SHARED_DIR,
    SH,
    WAIVERS_DIR,
    load_ontology,
    load_shapes,
    new_dataset,
    shapes_path,
)

console = Console()

# Cross-reference properties whose object IRIs must resolve in the loaded graph.
# Excludes ant:waivesShape (points into the SHAPES graph, not data) and
# ant:assignsRole (points to role classes in the ontology — also expected to
# resolve there but we don't load it as data).
_CROSSREF_PROPERTIES: tuple[URIRef, ...] = (
    ANT.participatesIn,
    ANT.hasMoment,
    ANT.characterizes,
    ANT.withinNetwork,
    ANT.perPractice,
    ANT.isPunctualizationOf,
    ANT.speaksFor,
    ANT.enrols,
    ANT.translates,
    ANT.inscribes,
    ANT.hasProgram,
    ANT.opposes,
    ANT.waivesForTarget,
    ANT.waivedBy,
)


# =============================================================================
# Entry points
# =============================================================================


def run_verify(
    graph: str | None = None,
    strict: bool = False,
    lint: bool = False,
    no_waivers: bool = False,
) -> int:
    """Run validation; return exit code (0 ok, non-zero on violations or
    (with ``--strict``) on warnings)."""
    # 1. Build the data graph
    data_ds = _build_data_dataset(graph)

    # 2. Load Tier-1 + Tier-2 shapes (lint is run separately below).
    #    IMPORTANT: load once and pass the *same* Graph instance to both
    #    pyshacl and the walkback helper, so blank-node IDs match.
    shapes = load_shapes(("core", "warnings", "translation"))

    # 3. Load ontology for OWL hints
    ont = load_ontology()

    # 4. Run pyshacl with the shapes graph we'll re-use for walkback
    conforms, report_g, _report_text = _pyshacl_validate(
        data_graph=data_ds.default_graph,
        shacl_graph=shapes,
        ont_graph=ont,
        inference="none",
        debug=False,
        meta_shacl=False,
        advanced=True,
    )

    violations, warnings = _classify_results(report_g, shapes)

    # 5. Cross-reference resolution (custom — not SHACL)
    crossref_violations = _check_crossrefs(data_ds)
    violations.extend(crossref_violations)

    # 6. Waiver suppression for warnings
    waivers = _load_waivers(data_ds) if not no_waivers else {}

    # 7. Print + decide exit code
    exit_code = _print_report(
        violations=violations,
        warnings=warnings,
        waivers=waivers,
        strict=strict,
    )

    # 8. Tier-3 lint (separate run against ontology only)
    if lint:
        _run_lint()

    return exit_code


def run_list(
    kind: str | None = None,
    iri: str | None = None,
    perspective: str | None = None,
) -> None:
    """List records in the loaded graph."""
    ds = _build_data_dataset(None)
    g = ds.default_graph

    if iri:
        console.print(f"[bold]Details for[/bold] {iri}")
        for p, o in g.predicate_objects(URIRef(iri)):
            console.print(f"  {p} → {o}")
        return

    classes_to_list: list[URIRef]
    if kind:
        classes_to_list = [_resolve_kind(kind)]
    else:
        classes_to_list = [
            ANT.Network, ANT.Actant, ANT.Translation, ANT.Perspective,
            ANT.Characterization, ANT.Inscription,
        ]

    for cls in classes_to_list:
        subjects = sorted(s for s in g.subjects(RDF.type, cls) if isinstance(s, URIRef))
        if not subjects:
            continue
        console.print(f"\n[bold]{cls}[/bold] ({len(subjects)} records)")
        for s in subjects:
            labels = list(g.objects(s, _ant_label_predicate()))
            label_str = labels[0] if labels else "(no label)"
            console.print(f"  {s} — {label_str}")


def create_waiver(
    shape: str,
    target: str,
    by: str,
    justification: str,
    expires: str | None = None,
) -> None:
    """Record an ant:ConstraintWaiver TTL file (Tier-2 only)."""
    if _is_tier1_shape(shape):
        console.print(
            f"[red]Refused:[/red] {shape} is a Tier-1 (sh:Violation) shape and is "
            "not waivable. Tier-1 represents structural integrity; fix the data instead."
        )
        raise SystemExit(2)

    from rdflib import XSD as _XSD

    from ant_rdf.models import ConstraintWaiver
    from ant_rdf.serialize import add, write_turtle

    today = _date.today().isoformat()
    slug = _slug_from(target)
    waiver_iri = f"https://w3id.org/ant/waivers/{today}/{slug}"

    waiver = ConstraintWaiver(
        iri=waiver_iri,
        waives_shape=shape,
        waives_for_target=target,
        waived_by=by,
        date=today,
        justification=justification,
        expires=expires,
    )

    ds = new_dataset()
    add(ds, waiver)

    WAIVERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = WAIVERS_DIR / f"{today}-{slug}.ttl"
    write_turtle(ds, out_path)
    console.print(f"[green]✓ waiver written[/green] {out_path}")


def list_waivers(active: bool = False, expired: bool = False, all_: bool = True) -> None:
    """List waivers; flags filter by active/expired status."""
    if not WAIVERS_DIR.exists():
        console.print("(no waivers recorded)")
        return
    g = Graph()
    for f in sorted(WAIVERS_DIR.glob("*.ttl")):
        g.parse(f, format="turtle")
    today = _date.today().isoformat()
    rows: list[tuple[str, str, str, str]] = []
    for w in sorted(g.subjects(RDF.type, ANT.ConstraintWaiver)):
        if not isinstance(w, URIRef):
            continue
        shape = next(iter(g.objects(w, ANT.waivesShape)), "?")
        target = next(iter(g.objects(w, ANT.waivesForTarget)), "?")
        just = next(iter(g.objects(w, ANT.waiverJustification)), "?")
        exp = next(iter(g.objects(w, ANT.waiverExpires)), None)
        is_expired = bool(exp and str(exp) < today)
        if active and is_expired:
            continue
        if expired and not is_expired:
            continue
        suffix = " [EXPIRED]" if is_expired else ""
        rows.append((str(w), str(shape), str(target), f"{just}{suffix}"))
    for w, shape, target, just in rows:
        console.print(f"[bold]{w}[/bold]")
        console.print(f"  shape  : {shape}")
        console.print(f"  target : {target}")
        console.print(f"  why    : {just}")


# =============================================================================
# Internals
# =============================================================================


def _build_data_dataset(graph: str | None) -> Dataset:
    ds = new_dataset()
    if graph:
        ds.parse(graph, format="turtle")
    else:
        for f in _all_ttl_files(SHARED_DIR):
            ds.parse(f, format="turtle")
        for f in _all_ttl_files(CASES_DIR):
            ds.parse(f, format="turtle")
        for f in _all_ttl_files(WAIVERS_DIR):
            ds.parse(f, format="turtle")
    return ds


def _all_ttl_files(d: Path) -> list[Path]:
    if not d.exists():
        return []
    return sorted(p for p in d.rglob("*.ttl") if p.is_file())


def _ant_label_predicate() -> URIRef:
    from rdflib.namespace import RDFS
    return RDFS.label


def _classify_results(
    report_g: Graph, shapes: Graph
) -> tuple[list[dict], list[dict]]:
    """Split SHACL report into (violations, warnings) lists of dicts.

    Walks blank-node property shapes back to their named parent NodeShape so
    the reported ``source_shape`` is a stable IRI an analyst can pass to
    ``ant waive add``. ``shapes`` MUST be the same Graph instance that was
    handed to pyshacl, so blank-node IDs line up.
    """
    violations: list[dict] = []
    warnings: list[dict] = []
    for result in report_g.subjects(RDF.type, SH.ValidationResult):
        severity = next(iter(report_g.objects(result, SH.resultSeverity)), SH.Violation)
        focus = next(iter(report_g.objects(result, SH.focusNode)), None)
        msg_nodes = list(report_g.objects(result, SH.resultMessage))
        msg = str(msg_nodes[0]) if msg_nodes else "(no message)"
        source_shape = next(iter(report_g.objects(result, SH.sourceShape)), None)
        # If the source shape is a blank node, look up its named parent.
        named_shape = _named_parent_shape(shapes, source_shape) if source_shape else None
        bucket = {
            "severity": str(severity),
            "focus": str(focus) if focus else "?",
            "message": msg,
            "source_shape": str(named_shape) if named_shape else (
                str(source_shape) if source_shape else "?"
            ),
        }
        if severity == SH.Violation:
            violations.append(bucket)
        elif severity == SH.Warning:
            warnings.append(bucket)
        else:
            # sh:Info — only when lint shapes are loaded; we skip here
            continue
    return violations, warnings


def _named_parent_shape(shapes: Graph, child: URIRef) -> URIRef | None:
    """Given a (possibly blank) property-shape, find its named NodeShape parent."""
    if isinstance(child, URIRef):
        return child
    for parent in shapes.subjects(SH.property, child):
        if isinstance(parent, URIRef):
            return parent
    return None


def _check_crossrefs(ds: Dataset) -> list[dict]:
    """Verify every IRI used in object position of a cross-ref property
    actually resolves to a subject somewhere in the graph (i.e., has at
    least one outgoing triple)."""
    g = ds.default_graph
    subjects_with_triples: set[URIRef] = {
        s for s in g.subjects() if isinstance(s, URIRef)
    }
    violations: list[dict] = []
    for prop in _CROSSREF_PROPERTIES:
        for s, o in g.subject_objects(prop):
            if not isinstance(o, URIRef):
                continue
            if o in subjects_with_triples:
                continue
            # Don't flag references into external namespaces (prov:, etc.) —
            # only flag dangling refs within the ant: namespace.
            o_str = str(o)
            if not o_str.startswith("https://w3id.org/ant"):
                continue
            violations.append({
                "severity": str(SH.Violation),
                "focus": str(s),
                "message": (
                    f"Dangling cross-reference: {prop} → {o} does not resolve "
                    f"to any subject in the loaded graph."
                ),
                "source_shape": "(cross-graph reference resolution)",
            })
    return violations


def _load_waivers(ds: Dataset) -> dict[tuple[str, str], dict]:
    """Index waivers by (shape, target) for warning suppression."""
    g = ds.default_graph
    today = _date.today().isoformat()
    waivers: dict[tuple[str, str], dict] = {}
    for w in g.subjects(RDF.type, ANT.ConstraintWaiver):
        if not isinstance(w, URIRef):
            continue
        shape = next(iter(g.objects(w, ANT.waivesShape)), None)
        target = next(iter(g.objects(w, ANT.waivesForTarget)), None)
        if not shape or not target:
            continue
        exp = next(iter(g.objects(w, ANT.waiverExpires)), None)
        if exp and str(exp) < today:
            continue  # expired — no suppression
        just = next(iter(g.objects(w, ANT.waiverJustification)), Literal(""))
        waivers[(str(shape), str(target))] = {
            "iri": str(w),
            "justification": str(just),
        }
    return waivers


def _print_report(
    violations: list[dict],
    warnings: list[dict],
    waivers: dict[tuple[str, str], dict],
    strict: bool,
) -> int:
    if violations:
        console.print(f"\n[red bold]{len(violations)} Violation(s) — these break the build[/red bold]")
        for v in violations:
            console.print(f"  [red]✗[/red] {v['focus']}")
            console.print(f"     shape : {v['source_shape']}")
            console.print(f"     msg   : {v['message']}")

    waived_count = 0
    surfaced_warnings: list[dict] = []
    for w in warnings:
        key = (w["source_shape"], w["focus"])
        waiver = waivers.get(key)
        if waiver:
            waived_count += 1
            console.print(
                f"  [yellow]⚠[/yellow] {w['focus']} "
                f"[dim][WAIVED: {waiver['justification'][:80]}][/dim]"
            )
        else:
            surfaced_warnings.append(w)

    if surfaced_warnings:
        verb = "break" if strict else "do not break"
        console.print(
            f"\n[yellow]{len(surfaced_warnings)} Warning(s) — surfaced; "
            f"these {verb} the build[/yellow]"
        )
        for w in surfaced_warnings:
            console.print(f"  [yellow]⚠[/yellow] {w['focus']}")
            console.print(f"     shape : {w['source_shape']}")
            console.print(f"     msg   : {w['message']}")
            console.print(f"     fix   : run `ant waive add <shape> <target> ...` to record a justification.")

    if waived_count:
        console.print(f"\n[dim]({waived_count} warning(s) suppressed by waivers)[/dim]")

    if not violations and not surfaced_warnings:
        console.print("[green]✓ all conforms (Tier 1 + Tier 2)[/green]")

    if violations:
        return 1
    if strict and surfaced_warnings:
        return 2
    return 0


def _run_lint() -> None:
    """Tier-3 lint — run against the ONTOLOGY graph specifically (per the
    note in ant-shapes-lint.ttl; lint shapes self-target every owl:Class /
    owl:Property which would explode against merged instance graphs)."""
    console.print("\n[bold]Tier-3 lint (ontology governance):[/bold]")
    ont = load_ontology()
    lint = Graph()
    lint.parse(shapes_path("lint"), format="turtle")
    conforms, report_g, _ = _pyshacl_validate(
        data_graph=ont, shacl_graph=lint, inference="none",
    )
    infos: list[str] = []
    for result in report_g.subjects(RDF.type, SH.ValidationResult):
        focus = next(iter(report_g.objects(result, SH.focusNode)), None)
        msg_nodes = list(report_g.objects(result, SH.resultMessage))
        msg = str(msg_nodes[0]) if msg_nodes else "(no message)"
        infos.append(f"  [blue]i[/blue] {focus} — {msg}")
    if infos:
        console.print(f"  ({len(infos)} info)")
        for line in infos[:20]:
            console.print(line)
        if len(infos) > 20:
            console.print(f"  …and {len(infos) - 20} more")
    else:
        console.print("  [green]✓ no lint findings[/green]")


def _resolve_kind(kind: str) -> URIRef:
    """Map a shorthand or qualified class name to a URIRef."""
    if ":" in kind and not kind.startswith("http"):
        prefix, local = kind.split(":", 1)
        if prefix == "ant":
            return getattr(ANT, local)
    if kind.startswith("http"):
        return URIRef(kind)
    return getattr(ANT, kind)  # bare local name → ant:<kind>


def _slug_from(iri: str) -> str:
    """Derive a filesystem slug from an IRI's tail segment."""
    tail = iri.rstrip("/").rsplit("/", 1)[-1]
    if "#" in tail:
        tail = tail.rsplit("#", 1)[-1]
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in tail).strip("-") or "untitled"


def _is_tier1_shape(shape_iri: str) -> bool:
    """Check the shapes graph to see if the shape's severity is sh:Violation."""
    shapes = load_shapes(("core", "warnings", "translation"))
    severity = next(iter(shapes.objects(URIRef(shape_iri), SH.severity)), None)
    return severity == SH.Violation
