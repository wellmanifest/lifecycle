# Lifecycle DSL v1

Lifecycle DSL is a deterministic, line-oriented language for finite state
lifecycles. It describes what a domain accepts, rejects, and requires as
evidence. It does not execute transitions or grant authority to execute them.

## Document model

A UTF-8 file contains one or more documents. Every document starts with
`LIFECYCLE` and ends with `END`. Blank lines and comments beginning with `#`
are ignored. String values use POSIX tokenization and examples use double
quotes; quoting is required when a value contains whitespace. Interpolation
and command execution do not exist.

```text
LIFECYCLE <name> VERSION <positive-integer>
DESCRIPTION "<human-readable text>"
STATE <STATE_ID> [INITIAL] [TERMINAL]
EVENT <EVENT_ID>
EVIDENCE <EVIDENCE_ID>
TRANSITION <STATE_ID> -> <STATE_ID> ON <EVENT_ID> [REQUIRES <EVIDENCE_ID>]
REJECT <STATE_ID> ON <EVENT_ID> WITH <ERROR_CODE>
ERROR <ERROR_CODE> SEVERITY <INFO|WARNING|ERROR|CRITICAL> MESSAGE "<message>"
END
```

`<name>` matches `[a-z][a-z0-9]*(?:-[a-z0-9]+)*`. State, event, and evidence
identifiers match `[A-Z][A-Z0-9_]*`. Profile error codes match
`[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}` and must not use the reserved `LFC-`
prefix.

## Normative semantics

1. A document declares exactly one `INITIAL` state.
   A bundle contains at least one document.
   This validator implements version `1` and rejects every other document
   version rather than guessing future semantics.
2. State, event, evidence, and error identifiers are unique in their own
   namespaces. Lifecycle names and profile error codes are unique across a
   multi-document bundle.
3. Every transition references declared source/target states and an event.
   Optional evidence must also be declared.
4. Every reject rule references a declared state, event, and profile error.
   Every declared profile error is used by at least one reject rule.
5. A `(state, event)` pair has at most one decision: one transition or one
   reject. Duplicate or mixed decisions are nondeterministic and invalid.
6. Every declared state is reachable from the initial state through transition
   edges. Reject rules do not create reachability.
7. A `TERMINAL` state has no outgoing transition. It may declare reject rules
   that explain why further events are invalid.
8. An unmentioned `(state, event)` pair is not authorized. A consumer must fail
   closed or apply a separately versioned policy; it must not invent a
   transition.
9. Evidence identifiers describe required proof, not boolean claims. A runtime
   adapter is responsible for authenticating evidence before using a validated
   model. The validator checks only declaration and binding integrity.
10. Validation never implies permission, approval, or successful execution.

## Multiple lifecycles

Documents are independent even when stored in one bundle:

```text
LIFECYCLE first VERSION 1
STATE START INITIAL
STATE DONE TERMINAL
EVENT COMPLETE
TRANSITION START -> DONE ON COMPLETE
END

LIFECYCLE second VERSION 1
STATE OFF INITIAL
STATE ON
EVENT ENABLE
TRANSITION OFF -> ON ON ENABLE
END
```

A bundle is valid only when every document and all bundle-wide uniqueness rules
are valid.

## Diagnostics

Core validator diagnostics are defined by `errors/catalog.json` using schema
`lifecycle.diagnostics/v1`. The catalog is closed: emitting an unknown core
code is an internal error. Profile `ERROR` declarations are domain data and do
not replace core `LFC-*` validation diagnostics.

| Code | Meaning |
|---|---|
| `LFC-IO-001` | Input cannot be read. |
| `LFC-SYNTAX-001` | Input is not UTF-8. |
| `LFC-SYNTAX-002` | A statement is malformed, unknown, or out of context. |
| `LFC-DOC-001` | Document boundaries are invalid. |
| `LFC-DOC-002` | A lifecycle name is duplicated in the bundle. |
| `LFC-MODEL-001` | An identifier or scalar is invalid. |
| `LFC-MODEL-002` | A declaration is duplicated. |
| `LFC-MODEL-003` | Initial-state cardinality is not exactly one. |
| `LFC-MODEL-004` | A statement references an undeclared symbol. |
| `LFC-MODEL-005` | A state/event pair has more than one decision. |
| `LFC-MODEL-006` | A state is unreachable from the initial state. |
| `LFC-MODEL-007` | A terminal state has an outgoing transition. |
| `LFC-ERROR-001` | A profile error declaration is invalid. |
| `LFC-ERROR-002` | A profile error is unresolved or unused. |
| `LFC-ERROR-003` | A profile error code is duplicated across documents. |
| `LFC-CATALOG-001` | The core catalog itself is invalid. |

Diagnostics contain `code`, `severity`, stable `message`, source `path`, source
`line`, optional lifecycle `document`, and contextual `detail`. Details may
vary with input; code and message semantics remain stable within v1.

## CLI contract

```text
python -m lifecycle validate PATH [--format text|json] [--catalog PATH]
```

- Exit `0`: every lifecycle is valid.
- Exit `1`: input or model validation diagnostics were produced, including
  when the requested input could not be read.
- Exit `2`: usage, catalog, or unexpected internal failure prevented a trusted
  validation result.

JSON output uses schema `lifecycle.validation/v1`, deterministic key ordering,
and a stable diagnostic order of source line, code, document, and detail.

## Compatibility

Adding a statement, changing identifier grammar, changing validation semantics,
or changing a core diagnostic meaning requires a new Lifecycle DSL version.
Adding a profile document or a new profile error does not change the language
version when all v1 rules remain unchanged.
