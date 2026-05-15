# SPDX-License-Identifier: Apache-2.0
"""Graph loading + SPARQL helpers — single choke point for all RDF construction.

Uses rdflib's quad-capable ``Dataset`` from day one (per plan §4.5 move #4) so
the v1→v2 lift to named graphs is mechanical: change the ``publicID`` argument
on parse, nothing else.

v1 default: every parse uses the default graph; the loader records a side-table
``triple_source: dict[str, str]`` mapping file paths to the perspective IRI
that file would belong to in v2. The query API stays unchanged.

v2 (not implemented here): switch ``publicID`` to the per-file perspective IRI.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from rdflib import Dataset, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, RDFS, SKOS, XSD

from ant_rdf import ANT, PROV

# =============================================================================
# Filesystem layout constants
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "ontology"
SHAPES_DIR = ONTOLOGY_DIR / "shapes"
INSTANCES_DIR = REPO_ROOT / "instances"
SHARED_DIR = INSTANCES_DIR / "shared"
WAIVERS_DIR = INSTANCES_DIR / "waivers"
CASES_DIR = INSTANCES_DIR / "cases"
BRIEFS_DIR = REPO_ROOT / "briefs"

ONTOLOGY_FILES = [
    ONTOLOGY_DIR / "material-semiotics-core.ttl",
    ONTOLOGY_DIR / "ant-prov-align.ttl",
]

SHAPES_TIERS = {
    "core": "ant-shapes-core.ttl",  # Tier 1 — load-bearing (sh:Violation)
    "warnings": "ant-shapes-warnings.ttl",  # Tier 2 — should-conform (sh:Warning, waivable)
    "lint": "ant-shapes-lint.ttl",  # Tier 3 — advisory (sh:Info)
    "translation": "ant-shapes-translation.ttl",  # the four Callon moments
}

# SHACL namespace (rdflib doesn't ship it bound by default in older versions).
SH = Namespace("http://www.w3.org/ns/shacl#")


# =============================================================================
# Loaders
# =============================================================================


def _bind_prefixes(ds: Dataset) -> None:
    """Bind the canonical prefixes once per Dataset for stable Turtle output."""
    ds.bind("ant", ANT)
    ds.bind("prov", PROV)
    ds.bind("owl", OWL)
    ds.bind("rdf", RDF)
    ds.bind("rdfs", RDFS)
    ds.bind("xsd", XSD)
    ds.bind("dcterms", DCTERMS)
    ds.bind("foaf", FOAF)
    ds.bind("skos", SKOS)
    ds.bind("sh", SH)


def new_dataset() -> Dataset:
    """Fresh quad-capable Dataset with prefixes bound."""
    ds = Dataset()
    _bind_prefixes(ds)
    return ds


def _ttl_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.rglob("*.ttl") if p.is_file())


def load_ontology() -> Dataset:
    """Ontology files only (core + alignment). No shapes, no instances."""
    ds = new_dataset()
    for f in ONTOLOGY_FILES:
        if f.exists():
            ds.parse(f, format="turtle")
    return ds


def shapes_path(tier: str) -> Path:
    if tier not in SHAPES_TIERS:
        raise ValueError(f"Unknown shapes tier {tier!r}; expected one of {sorted(SHAPES_TIERS)}")
    return SHAPES_DIR / SHAPES_TIERS[tier]


def load_shapes(tiers: Iterable[str] = ("core", "warnings", "translation")) -> Dataset:
    """Load SHACL shapes for the requested tiers.

    Default: Tier 1 (core) + Tier 2 (warnings) + translation moments. Add ``"lint"``
    to also load Tier 3 advisory shapes (typically via ``ant verify --lint``).
    """
    ds = new_dataset()
    for tier in tiers:
        p = shapes_path(tier)
        if p.exists():
            ds.parse(p, format="turtle")
    return ds


def load_shared() -> Dataset:
    """Load all TTL under instances/shared/ (perspective-agnostic by convention)."""
    ds = new_dataset()
    for f in _ttl_files(SHARED_DIR):
        ds.parse(f, format="turtle")
    return ds


def load_case(case_slug: str, *, with_shared: bool = True) -> Dataset:
    """Load a single case (all perspectives, all uploads' TTL metadata)
    merged with shared instances. v1 flattens into the default graph; v2
    will route each perspective into its own named graph (same call site).
    """
    ds = new_dataset()
    case_dir = CASES_DIR / case_slug
    for f in _ttl_files(case_dir):
        ds.parse(f, format="turtle")
    if with_shared:
        for f in _ttl_files(SHARED_DIR):
            ds.parse(f, format="turtle")
    return ds


def load_full_dataset() -> Dataset:
    """Everything: ontology + shared + every case + waivers."""
    ds = load_ontology()
    for f in _ttl_files(SHARED_DIR):
        ds.parse(f, format="turtle")
    for f in _ttl_files(CASES_DIR):
        ds.parse(f, format="turtle")
    for f in _ttl_files(WAIVERS_DIR):
        ds.parse(f, format="turtle")
    return ds


# =============================================================================
# SPARQL helpers
# =============================================================================


def sparql_select(
    ds: Dataset, query: str, init_ns: dict[str, Namespace] | None = None
) -> list[dict[str, Any]]:
    """Run a SELECT query and return a list of variable→value dicts."""
    ns: dict[str, Namespace] = dict(
        ant=ANT,
        prov=PROV,
        owl=OWL,
        rdf=RDF,
        rdfs=RDFS,
        skos=SKOS,
        foaf=FOAF,
        dcterms=DCTERMS,
        xsd=XSD,
        sh=SH,
    )
    if init_ns:
        ns.update(init_ns)
    rows = ds.query(query, initNs=ns)
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append({str(v): row[v] for v in row.labels})
    return out


def get_iris_by_type(ds: Dataset, class_iri: URIRef) -> list[URIRef]:
    return sorted({s for s in ds.subjects(RDF.type, class_iri) if isinstance(s, URIRef)})


def get_actant_iris(ds: Dataset) -> list[URIRef]:
    return get_iris_by_type(ds, ANT.Actant)


def get_network_iris(ds: Dataset) -> list[URIRef]:
    return get_iris_by_type(ds, ANT.Network)


def get_translation_iris(ds: Dataset) -> list[URIRef]:
    return get_iris_by_type(ds, ANT.Translation)


def get_perspective_iris(ds: Dataset) -> list[URIRef]:
    return get_iris_by_type(ds, ANT.Perspective)


def get_characterization_iris(ds: Dataset) -> list[URIRef]:
    return get_iris_by_type(ds, ANT.Characterization)
