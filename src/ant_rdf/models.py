# SPDX-License-Identifier: Apache-2.0
"""Pydantic mirrors of the OWL classes in material-semiotics-core.ttl.

Atomicity rule (RIME convention): every OWL class in the ontology mirrors here;
every controlled-vocab individual mirrors as a ``Literal[...]`` type alias.
Both must be updated in the same commit.

v1 inventory mirrors plan §4.1 spine + the v1 Law/Latour additions and the
non-spine essentials (Perspective, Characterization, ConstraintWaiver).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Controlled-vocab type aliases (role values for ant:Characterization)
# ---------------------------------------------------------------------------

# Roles assignable via Characterization (Latour 2005 mediator/intermediary
# plus the dual PROV alignment per §4.3).
RoleIri = Literal[
    "https://w3id.org/ant#Mediator",
    "https://w3id.org/ant#Intermediary",
    "https://w3id.org/ant#Spokesperson",
    "https://w3id.org/ant#ObligatoryPassagePoint",
    "https://w3id.org/ant#ProvAgent",
    "https://w3id.org/ant#ProvInfluencer",
]

DurabilityKind = Literal[
    "https://w3id.org/ant#MaterialDurability",
    "https://w3id.org/ant#StrategicDurability",
    "https://w3id.org/ant#DiscursiveStability",
]


# ---------------------------------------------------------------------------
# Base — all model types share these conventions
# ---------------------------------------------------------------------------


class AntModel(BaseModel):
    """Base for every record. Each record carries its IRI and a human label."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    iri: str = Field(..., description="HTTP(S) IRI for this record.")
    label: str = Field(..., description="rdfs:label — short human-readable name.")
    description: str = Field(..., description="dcterms:description — narrative paragraph.")


# ---------------------------------------------------------------------------
# Spine (v1 minimum, per user choice)
# ---------------------------------------------------------------------------


class Network(AntModel):
    """An analyst's named summary of associations (act-4 documentation; §4.7).

    A Network is NOT a container; it is the analyst's *commitment to a reading*.
    Multiple Networks may live in the same scope under different perspectives.
    """

    case: str
    perspective: str = "_default"
    scope: str | None = None
    from_construct: str | None = None  # provenance: SPARQL CONSTRUCT query path


class Actant(AntModel):
    """A human or non-human entity participating in a web of relations.

    Methodological category for the analyst, not an ontological commitment
    about the world (per plan C3).
    """

    case: str
    perspective: str = "_default"
    participates_in: list[str] = Field(default_factory=list)


class Translation(AntModel):
    """The process by which actants are enrolled into programs of action.

    Abstract superclass of the four Callon moments. Tier-1 SHACL requires
    at least one moment; Tier-2 warns if not all four are present.
    """

    case: str
    perspective: str = "_default"
    has_moment: list[str] = Field(default_factory=list)


class Problematization(AntModel):
    """Moment 1 of translation (Callon 1986). Subclass of ant:Translation."""

    case: str
    perspective: str = "_default"


class Interessement(AntModel):
    """Moment 2 of translation (Callon 1986)."""

    case: str
    perspective: str = "_default"


class Enrolment(AntModel):
    """Moment 3 of translation (Callon 1986).

    Disambiguated from v1.1's reified ``EnrolmentRelation`` (per R4).
    """

    case: str
    perspective: str = "_default"


class Mobilization(AntModel):
    """Moment 4 of translation (Callon 1986)."""

    case: str
    perspective: str = "_default"


# ---------------------------------------------------------------------------
# Perspective + Characterization (§4.1.1, §4.5)
# ---------------------------------------------------------------------------


class Perspective(AntModel):
    """A named analysis scope. In v2 the IRI becomes a named-graph URI."""

    held_by: str  # prov:Agent IRI of the analyst/team
    case: str
    grounded_in: list[str] = Field(default_factory=list)  # ant:Practice IRIs
    tracks_invariance: list[str] = Field(default_factory=list)


class Characterization(BaseModel):
    """Reified n-ary role assignment with (network, practice, invariance) context.

    Lets the same actant be simultaneously characterized as Mediator under
    one practice and Intermediary under another (§4.1.1).
    """

    model_config = ConfigDict(extra="forbid")

    iri: str
    characterizes: str  # IRI of the target actant
    within_network: str
    assigns_role: RoleIri
    per_practice: str | None = None
    invariance: str | None = None
    case: str
    perspective: str = "_default"
    description: str | None = None


# ---------------------------------------------------------------------------
# Latourian additions (Inscription, ImmutableMobile, Spokesperson, OPP, programs)
# ---------------------------------------------------------------------------


class Inscription(AntModel):
    """A material trace enabling action at a distance (Latour)."""

    case: str
    perspective: str = "_default"
    source: str | None = None  # dcterms:source (URL or file hash for uploads)


class ImmutableMobile(Inscription):
    """An inscription that holds form constant while circulating (Law 1986)."""


class ProgramOfAction(AntModel):
    """A scripted course of action (Latour 1991)."""

    case: str
    perspective: str = "_default"
    opposes: list[str] = Field(default_factory=list)  # IRIs of anti-programs


# ---------------------------------------------------------------------------
# Four-acts artifacts (§4.7)
# ---------------------------------------------------------------------------


class Scope(AntModel):
    """Declarative selection of what is in analytical view (act 1)."""

    cases: list[str]
    perspectives: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)


class Analysis(AntModel):
    """A reified record of a computation against a scope (act 3, v1 data-shape only)."""

    scope_iri: str
    method: str
    query: str | None = None  # SPARQL or rule reference
    results: str | None = None  # path to results artifact


class AnalysisReport(AntModel):
    """Documented reading of analysis output (act 4)."""

    scope_iri: str
    analysis_iri: str | None = None
    network_iri: str | None = None


# ---------------------------------------------------------------------------
# Governance — waivers
# ---------------------------------------------------------------------------


class ConstraintWaiver(BaseModel):
    """Append-only acknowledgement of a Tier-2 SHACL warning (§4.6).

    Tier-1 violations are NOT waivable; ``ant waive add`` rejects attempts
    to waive a Violation-severity shape.
    """

    model_config = ConfigDict(extra="forbid")

    iri: str
    waives_shape: str
    waives_for_target: str
    waived_by: str
    date: str  # ISO yyyy-mm-dd
    justification: str
    expires: str | None = None  # optional ISO yyyy-mm-dd
