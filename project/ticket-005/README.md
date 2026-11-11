# Ticket 005: Harden Lifecycle DSL validator, catalog loader, and audit CLI under 500 lines

- **ID**: ticket-005
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Modularize and harden `wellmanifest/lifecycle` so every Python module stays
under 500 lines (`src/lifecycle.py`, `src/lifecycle_audit.py`,
`src/lifecycle_catalog.py`, `tests/test_lifecycle.py`) while keeping
`src/lifecycle.py` 100% standalone-runnable as a byte-pinned validator per
`spec/LIFECYCLE_DSL.md`, fix fail-open/crash defects in `load_catalog`,
`audit_path`, and `parse_bundle`, and close merged `ticket-003` / `ticket-004`.

## Acceptance criteria

- [x] AC-01: Split external catalog loading (`src/lifecycle_catalog.py`) and
      compaction auditing (`src/lifecycle_audit.py`) from `src/lifecycle.py`
      so every `.py` file is `< 500` lines and standalone `lifecycle.py validate`
      remains self-contained.
- [x] AC-02: Reject duplicate JSON keys and boolean `"version": true` in
      `load_catalog`, handle missing/non-UTF-8 files cleanly in `audit_path`
      with `LFC-IO-001` / `LFC-SYNTAX-001` (exit `1`), split bundle lines
      strictly on `\r\n`/`\r`/`\n`, and reject non-canonical `VERSION` tokens
      (`+1`, `01`, `1_0`) with `LFC-MODEL-001`.
- [x] AC-03: Pass `ruff check`, `pytest -q`, networkless Docker container tests,
      `./project/governance-check.sh --base origin/main`, and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
