# Ticket 010: Harden lifecycle deep absolute symlink ancestors, in-memory byte bounds, and strict JSON output

- **ID**: ticket-010
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: On 2026-11-11 user authorized auditing, fixing bugs, and hardening across `wellmanifest/*` standard repositories.

Reject deep absolute-path symlink ancestors (`sym_dir/nested/model.lifecycle`) in `read_regular_bytes`, enforce `MAX_INPUT_BYTES` on in-memory `parse_bundle` / `validate_text` / `audit_compaction` inputs, pass `allow_nan=False` to CLI `json.dumps` in `src/lifecycle.py` while keeping `src/lifecycle.py` standalone-copyable and strictly `< 500` lines, expand `tests/test_lifecycle_hardening.py`, and reconcile merged `project/ticket-009/README.md` to `DONE`.

## Acceptance criteria

- [x] AC-01: `read_regular_bytes` rejects nested absolute-path symlink ancestors, `parse_bundle` emits `LFC-IO-001` when in-memory UTF-8 text exceeds `MAX_INPUT_BYTES` or `text` is not `str`, and CLI JSON output enforces `allow_nan=False` while `src/lifecycle.py` stays strictly `< 500` lines.
- [x] AC-02: Pass `ruff check --no-cache src tests`, `PYTHONPATH=src pytest -q -p no:cacheprovider`, `./project/governance-check.sh --base origin/main`, and `wellman check`, and mark merged `project/ticket-009/README.md` `DONE`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
