# SPDX-License-Identifier: Apache-2.0
"""ant-rdf — material-semiotics / Actor-Network-Theory vocabulary and authoring tooling.

Exports the ANT namespace and (optional) PROV alignment namespace so callers
never hand-write the IRI strings.
"""

from rdflib import Namespace

__version__ = "0.1.0"

# Canonical ANT namespace. Persistent IRI via w3id.org (one-time redirect PR pending).
ANT = Namespace("https://w3id.org/ant#")

# W3C PROV-O namespace (used for optional alignment in ontology/ant-prov-align.ttl).
PROV = Namespace("http://www.w3.org/ns/prov#")

__all__ = ["ANT", "PROV", "__version__"]
