# SPDX-License-Identifier: Apache-2.0
"""SHACL validation + cross-reference resolution + tri-severity output (§4.6).

Stub — real implementation lands at plan §10 step 7.
"""

from __future__ import annotations


def run_verify(
    graph: str | None = None,
    strict: bool = False,
    lint: bool = False,
    no_waivers: bool = False,
) -> int:  # pragma: no cover — step 7
    raise NotImplementedError("run_verify — step 7 of plan §10.")


def run_list(
    kind: str | None = None,
    iri: str | None = None,
    perspective: str | None = None,
) -> None:  # pragma: no cover — step 7
    raise NotImplementedError("run_list — step 7 of plan §10.")


def create_waiver(**kwargs: object) -> None:  # pragma: no cover — step 7
    raise NotImplementedError("create_waiver — step 7 of plan §10.")


def list_waivers(**kwargs: object) -> None:  # pragma: no cover — step 7
    raise NotImplementedError("list_waivers — step 7 of plan §10.")
