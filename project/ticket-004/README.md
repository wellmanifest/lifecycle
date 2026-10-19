# Ticket 004: Lifecycle DSL compaction constructs and audit

- **ID**: ticket-004
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-19

## Goal and scope

Extend Lifecycle DSL v1 (`wellmanifest/lifecycle`) with deterministic compile-time desugaring constructs (`STATES [...]`, `EVENTS [...]`, `EVIDENCES [...]`, `TRANSITION [...] -> TARGET ON EVENT [REQUIRES EVIDENCE]`, `REJECT [...] ON EVENT WITH ERROR`) that expand into canonical single-item declarations and transitions, add a static compaction analyzer (`audit_compaction` / CLI `lifecycle audit PATH [--format text|json]`), and compact `profiles/reference.lifecycle` and `profiles/wellmanifest-ecosystem.lifecycle`.

## Acceptance criteria

- [x] AC-01: Implement `STATES [...]`, `EVENTS [...]`, `EVIDENCES [...]`, state-set `TRANSITION [...]`, state-set `REJECT [...]`, and `lifecycle audit` in `src/lifecycle.py` and `spec/LIFECYCLE_DSL.md` while preserving 100% `lifecycle.validation/v1` report equivalence.
- [x] AC-02: Compact `profiles/reference.lifecycle` and `profiles/wellmanifest-ecosystem.lifecycle` to `0` compaction findings and pass `pytest -q`, `./project/governance-check.sh`, and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
