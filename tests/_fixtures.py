# SPDX-License-Identifier: Apache-2.0
"""Test-fixture builders.

CLEARLY FAKE people (Alice / Bob / Carol Example) under a dedicated
``https://w3id.org/ant/test`` IRI space. These models are built in-memory and
serialized to tmp files inside tests only — they are NEVER written under
``instances/`` and never enter the actual graph.
"""

from __future__ import annotations

from ant_rdf.models import (
    Actant,
    Enrolment,
    Interessement,
    Mobilization,
    Network,
    Perspective,
    Practice,
    Problematization,
    Translation,
)

B = "https://w3id.org/ant/test"


def core_models() -> list:
    """A minimal valid core graph: network, actants, four moments, translation."""
    return [
        Perspective(
            iri=f"{B}/perspectives/_default", label="Fixture perspective",
            description="Isolated test perspective (fake).",
            held_by=f"{B}/person/alice-example", case="fixture",
            grounded_in=[f"{B}/practice/fieldwork"], tracks_invariance=["nothing real"],
        ),
        Practice(iri=f"{B}/practice/fieldwork", label="Fixture practice", description="Fake practice."),
        Network(iri=f"{B}/network", label="Fixture network", description="A fake network for tests.", case="fixture"),
        Actant(iri=f"{B}/person/alice-example", label="Alice Example", description="Fixture person (fake).", case="fixture", participates_in=[f"{B}/network"]),
        Actant(iri=f"{B}/thing/widget-example", label="Widget Example", description="Fixture non-human actant (fake).", case="fixture", participates_in=[f"{B}/network"]),
        Problematization(iri=f"{B}/moment/problematization", label="P", description="fake", case="fixture"),
        Interessement(iri=f"{B}/moment/interessement", label="I", description="fake", case="fixture"),
        Enrolment(iri=f"{B}/moment/enrolment", label="E", description="fake", case="fixture"),
        Mobilization(iri=f"{B}/moment/mobilization", label="M", description="fake", case="fixture"),
        Translation(
            iri=f"{B}/translation/main", label="Fixture translation", description="fake",
            case="fixture", has_moment=[
                f"{B}/moment/problematization", f"{B}/moment/interessement",
                f"{B}/moment/enrolment", f"{B}/moment/mobilization",
            ],
        ),
    ]
