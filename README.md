# lifecycle

`lifecycle` standardizes a small, deterministic DSL for describing state
lifecycles, accepted transitions, evidence requirements, rejected operations,
and stable diagnostic codes. The first reference profiles cover Git ticket
branches and governed work tickets; the core is intentionally independent of
either domain.

## Planned interface

```text
python -m lifecycle validate profiles/reference.lifecycle
python -m lifecycle validate profiles/reference.lifecycle --format json
```

The validator is dependency-free at runtime and fails closed on malformed,
ambiguous, unreachable, or internally inconsistent lifecycle definitions.
LLM-assisted authoring may be added as an advisory layer, but deterministic
parsing and validation remain the source of truth.

## Repository state

Ticket [`ticket-001`](project/ticket-001/README.md) owns the initial DSL,
validator, error catalog, and reference profiles. Architecture and execution
flow are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
[`docs/LOGIC_FLOW.md`](docs/LOGIC_FLOW.md).

## Governance

This repository adopts `wellmanifest/new-project` `0.14.1` at an immutable
commit recorded in `.governance/manifest.lock.json`. Implementation changes
must belong to exactly one active ticket and pass the local, container, and
protected GitHub checks before merge.
