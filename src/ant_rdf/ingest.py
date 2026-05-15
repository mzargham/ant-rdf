# SPDX-License-Identifier: Apache-2.0
"""Non-conversational ingestion paths: notes, transcripts, observations, uploads.

Each command produces a dry-run review document; only after human confirmation
do triples land in the graph. Implementation arrives at plan §10 step 10a.
"""

from __future__ import annotations


def ingest_notes(**kwargs: object) -> None:  # pragma: no cover — step 10a
    raise NotImplementedError("ingest_notes — step 10a of plan §10.")


def ingest_transcript(**kwargs: object) -> None:  # pragma: no cover — step 10a
    raise NotImplementedError("ingest_transcript — step 10a of plan §10.")


def ingest_observation(**kwargs: object) -> None:  # pragma: no cover — step 10a
    raise NotImplementedError("ingest_observation — step 10a of plan §10.")


def ingest_upload(**kwargs: object) -> None:  # pragma: no cover — step 10a
    raise NotImplementedError("ingest_upload — step 10a of plan §10.")
