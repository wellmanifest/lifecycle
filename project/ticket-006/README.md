# Ticket 006: Register lifecycle_audit and lifecycle_catalog in pyproject.toml py-modules

- **ID**: ticket-006
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Register the newly extracted `lifecycle_audit` and `lifecycle_catalog` Python
modules under `[tool.setuptools].py-modules` in `pyproject.toml` so installed
wheel and editable distributions bundle all three `src/lifecycle*.py` modules
alongside the `lifecycle` console script, and close merged `ticket-005`.

## Acceptance criteria

- [x] AC-01: Update `pyproject.toml` `[tool.setuptools].py-modules` to include
      `lifecycle`, `lifecycle_audit`, and `lifecycle_catalog`.
- [x] AC-02: Mark merged `project/ticket-005/README.md` `DONE` / `PUBLICATION`.
- [x] AC-03: Pass `pytest -q`, `./project/governance-check.sh --base origin/main`,
      and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
