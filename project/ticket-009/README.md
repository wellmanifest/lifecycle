# Ticket 009: Harden lifecycle UTF-8 surrogates, catalog integer bounds, and regular-file ancestor checks

- **ID**: ticket-009
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-11

## Goal and scope

Harden `src/lifecycle.py` and `src/lifecycle_catalog.py` against lone UTF-16
surrogates, ASCII C0/DEL control bytes, `10**400` catalog integer overflow,
symlink ancestor traversal, and `max_bytes` type/range violations while keeping
`src/lifecycle.py` standalone-copyable and strictly below 500 lines, expand
`tests/test_lifecycle_hardening.py`, and mark merged `ticket-008` `DONE`.

## Acceptance criteria

- [x] AC-01: Anchor all regexes with `\A...\Z`, reject lone UTF-16 surrogates
      and C0/DEL control bytes in `parse_bundle` and `load_catalog_impl`, reject
      `10**400` integer overflow in `_check_json_depth`, and enforce positive
      integer `max_bytes`, bounded `os.read`, and symlink ancestor checks in
      `read_regular_bytes` while keeping `src/lifecycle.py` < 500 lines.
- [x] AC-02: Pass `ruff check --no-cache src tests`, `PYTHONPATH=src pytest -q -p no:cacheprovider`,
      `./project/governance-check.sh --base origin/main`, and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
