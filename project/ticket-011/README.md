# Ticket 011: Harden lifecycle relative symlink traversal, bracket syntax, and catalog integer bounds

- **ID**: ticket-011
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-11

## Goal and scope

Harden `read_regular_bytes` in `src/lifecycle.py` against relative `symdir/..`,
`../symdir`, symlinked working directory (`cwd`), and un-normalized absolute
symlink-parent traversal while keeping `src/lifecycle.py` standalone-copyable
and strictly `< 500` lines. Reject malformed double-bracket tokens (`[[A, B]`,
`[A, B]]`) as `LFC-SYNTAX-002` in `_extract_bracketed_list`, bound JSON integer
digit length (`<= 309`) before `int()` conversion in `src/lifecycle_catalog.py`,
expand `tests/test_lifecycle_hardening.py`, and reconcile merged
`project/ticket-010/README.md` to `DONE`.

## Acceptance criteria

- [x] AC-01: Reject relative `symdir/..`, `../symdir`, symlinked-`cwd`, and
      un-normalized absolute symlink-parent traversal in `read_regular_bytes`,
      reject malformed double-bracket batch syntax as `LFC-SYNTAX-002`, and
      bound catalog JSON integer digits before `int()` conversion while keeping
      all modules strictly `< 500` lines and `src/lifecycle.py`
      standalone-copyable.
- [x] AC-02: Pass `ruff check --no-cache src tests`,
      `PYTHONPATH=src pytest -q -p no:cacheprovider`,
      `./project/governance-check.sh --base origin/main`, and `wellman check`,
      and mark merged `project/ticket-010/README.md` `DONE`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
