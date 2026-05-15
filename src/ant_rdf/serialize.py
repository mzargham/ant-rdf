# SPDX-License-Identifier: Apache-2.0
"""Deterministic Pydantic-model → RDF dispatch (per plan §5).

Same model → byte-identical Turtle output. Each spine class gets a ``_add_*``
helper; ``add()`` dispatches on model class.
"""

from __future__ import annotations

from typing import Any

from rdflib import Dataset, URIRef


def add(ds: Dataset, obj: Any) -> URIRef:  # pragma: no cover — step 5
    """Dispatch on model class; not yet implemented. See plan §10 step 5."""
    raise NotImplementedError("serialize.add() — step 5 of plan §10 (not yet implemented).")
