# Glossary: koi

Two vocabularies a reader may want to check, kept apart. First the **material-semiotics (Actor-Network Theory) terms** the reading is built from (actant, mediator, translation, and so on). Then any **load-bearing terms from other fields** the reading leans on. Every definition is taken faithfully from a cited source, never the ethnographer's own.

# Material semiotics (Actor-Network Theory) vocabulary

The method's own terms, as this case uses them. Definitions are the ontology's; sources are the founding texts of the tradition.

## Roles a characterization can assign

**Intermediary (role)**: A role characterizing an interaction as TRANSMITTING WITHOUT TRANSFORMATION: it PRESERVES the invariant named by ant:invarianceCriterion directly, by pass-through, without having to vary other dimensions to hold it. (A Mediator preserves its invariant the hard way, by regulating; an Intermediary preserves its invariant the easy way, by relaying.) Observer-relative — assigned via ant:Characterization. NOT a kind of actant. The same actant can be an Intermediary on the dimensions it passes through and a Mediator on the ones it regulates simultaneously; the perspective selects which dimensions matter for the coding. (Compare ant:ImmutableMobile: a mobile that is unaltered when drawn on.) NB: Callon 1991 uses 'intermediary' differently (a thing passed between actors); this ontology follows Latour 2005's sense.
Source: Latour, B. (2005). Reassembling the Social.

**Mediator (role)**: A role characterizing an interaction as TRANSFORMING what it transmits (its outputs cannot be predicted from its inputs). Cybernetically it REGULATES: it varies some dimensions IN ORDER TO PRESERVE the invariant named by ant:invarianceCriterion (requisite variety — the regulator must command variety to hold the essential variable constant). Observer-relative — assigned via ant:Characterization with explicit ant:perPractice and ant:invarianceCriterion. NOT a kind of actant. The SAME actant can be a Mediator on the dimensions it regulates and an Intermediary on the ones it passes through, at the same time; the perspective selects which dimensions are coded. (Compare ant:FluidObject: a mobile that is varied when drawn on.) R3 and
Source: Latour, B. (2005). Reassembling the Social.

**Obligatory passage point (emergent attribute)**: An emergent attribute, NOT a kind of thing. An actant comes to play this role within a network when every other actant must pass through it to realize its interests. v1 supports manual assertion via ant:Characterization; v2 will support rule-based tagging from network topology ( R6). Design does not preclude either path.
Source: Callon, M. (1986). Some Elements of a Sociology of Translation.

**Spokesperson (role)**: A role: an actant that speaks for / represents others. Emerges through the mobilization moment of translation.
Source: Callon, M. (1986); Latour, B. (1987). Science in Action.

## Core concepts

**Actant**: Any human or non-human entity participating in a web of relations. Methodological category for the analyst; NOT an ontological commitment about the world. The deliberately pre-categorical term refuses the human/non-human split that material semiotics dissolves.
Source: Greimas (semiotics, via Latour); foundational across Callon, Latour, Law.

**Characterization**: A reified n-ary relation that assigns a role to a target actant or interaction *within a context*: a network, an authoring practice, and (where relevant) the invariance criterion being tracked. The mechanism that lets the same actant be simultaneously characterized as Mediator under one practice and Intermediary under another without OWL inconsistency. Also used for the dual PROV-Agent / PROV-Influencer alignment ( R2) and for ethnographer-asserted OPP assignment ( R6).
Source: post-Law 2008; R3 (observer-relative roles via Characterization).

**Enrolment (moment)**: Moment 3 of translation: definition and coordination of the roles actants will play. Disambiguated from the v1.1 reified ant:EnrolmentRelation (a qualified edge carrying strength/time/contestation) — this class is the Callon process-moment, not the relational state.
Source: Callon, M. (1986). Some Elements of a Sociology of Translation.

**Inscription**: A material trace (text, graph, instrument reading, photograph, file) that allows action at a distance and accumulation in centres of calculation. Inscriptions are perspective-agnostic by convention — they are raw materials any perspective may characterize. Candidate alignment: crm:E34_Inscription (see ant-cidoc-align.ttl).
Source: Latour, B. (1990). Drawing Things Together; Latour, B. (1987). Science in Action.

**Interessement**: Moment 2 of translation: locking other actants into the proposed roles, cutting alternative associations.
Source: Callon, M. (1986). Some Elements of a Sociology of Translation.

**Mobilization**: Moment 4 of translation: spokespersons become representative; the network speaks with one voice.
Source: Callon, M. (1986). Some Elements of a Sociology of Translation.

**Network**: An analyst's named summary of a heterogeneous, traceable set of associations. NOT a container — networks ARE their traces. A Network record is an act-4 (documentation) artifact: the analyst's commitment to a particular reading of a region of the graph. Distinct from ant:Scope (act-1, what is in view) and ant:Analysis (act-3, computation). R5 (the four acts).
Source: Shared across Callon, Latour, Law.

**Perspective**: A named analysis scope on a fieldsite. A perspective is the relation between a perspective-haver (an analyst or team) and what is being seen — so perspectives belong inside cases. In v1 a first-class RDF subject; in v2 the same IRI becomes the URI of a named graph (no migration). See C6.
Source: post-Mol & Law.

**Practice**: A patterned, situated doing that enacts a reality (Mol; Law). Practices ground perspectives — a perspective is grounded in one or more practices. Used as the value of ant:perPractice on Characterizations to make the observer-frame explicit.
Source: Mol, A. (2002). The Body Multiple; Law, J. (2008). Actor Network Theory and Material Semiotics.

**Problematization**: Moment 1 of translation: an actant defines a problem and positions itself as indispensable to the network's resolution of it.
Source: Callon, M. (1986). Some Elements of a Sociology of Translation.

**Translation**: The process by which one actant enrols others into a program of action — transformation of interests, alignment of associations. Abstract superclass of the four Callon moments (Problematization, Interessement, Enrolment, Mobilization). Translation is always insecure (Callon 1986; Law 2008) — a process susceptible to failure.
Source: Callon, M. (1986). Some Elements of a Sociology of Translation; Serres, M. (1974) La Traduction.

# Load-bearing terms from other fields

_No external terms recorded. Author one with `ant new-record glossary-term` when the reading leans on a word from another field._

---

**See also:** [Reading guide](koi-guide.md) · [Synopsis](koi-synopsis.md) · [Positionality](koi-positionality.md)
