# Ticket 001: Standardize Lifecycle DSL v1

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-11

## Goal and scope

Define Lifecycle DSL v1 as a domain-neutral, line-oriented state-machine
contract. Deliver a dependency-free Python validator, stable diagnostics, and
one multi-document reference bundle proving both Git branch and governed-ticket
lifecycles. The validator observes definitions only; it never authorizes or
executes lifecycle transitions.

## Acceptance criteria

- [ ] AC-01: The public specification defines declarations, transitions,
  evidence requirements, reject rules, errors, document boundaries, and exit
  behavior without domain-specific assumptions.
- [ ] AC-02: The validator rejects syntax errors, duplicate declarations,
  unresolved references, nondeterministic state/event pairs, unreachable
  states, invalid terminal transitions, and incorrect error bindings with
  stable `LFC-*` diagnostics.
- [ ] AC-03: Text and JSON output are deterministic and invalid input exits 1;
  unexpected internal failure remains distinct at exit 2.
- [ ] AC-04: The reference bundle validates independent Git-branch and governed
  ticket lifecycles, including evidence-gated destructive or terminal actions.
- [ ] AC-05: Positive and negative tests pass on the host and in the pinned,
  networkless Docker image.
- [ ] AC-06: Adopted `new-project` governance passes with zero errors and the
  implementation changes exactly the five files budgeted by this ticket.

## Risks

- Ambiguous free-form conditions could make profiles non-portable. V1 therefore
  uses declared identifiers and explicit graph edges rather than expressions.
- A lifecycle description could be mistaken for execution authority. The spec
  and validator explicitly produce validated data only, never permission.
- Extending V1 for orchestration could destabilize the core. Runtime adapters,
  bindings, and additional profiles remain separate tickets.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
