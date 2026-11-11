# Ticket 007: Harden lifecycle file/JSON bounds, deduplicate SSOT constants, and slim lifecycle.py

- **ID**: ticket-007
- **Owner**: tom
- **Status**: DONE
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-11

## Goal and scope

Enforce `O_NOFOLLOW | O_NONBLOCK` regular-file checks and 4 MiB input caps across
`validate_path`, `audit_path`, and `load_catalog`, reject `NaN`/`Infinity` and
deeply nested JSON in external diagnostic catalogs, reject NUL bytes in bundle
lines, exclude duplicate/invalid declarations from compaction audit counts,
eliminate duplicated SSOT constants across `src/lifecycle*.py`, keep all Python
modules well below 500 lines while preserving standalone `lifecycle.py` copy
execution, and close merged `ticket-006`.

## Acceptance criteria

- [x] AC-01: Harden file reading (`read_regular_bytes` with `O_NOFOLLOW`, regular-file
      check, and 4 MiB limit), reject non-finite/deep catalog JSON and NUL bytes,
      and exclude duplicate/invalid declarations from compaction audit suggestions.
- [x] AC-02: Import `CATALOG_SCHEMA`, `SEVERITIES`, `CORE_CODE`, and `AUDIT_SCHEMA`
      from `lifecycle` in `lifecycle_catalog.py` and `lifecycle_audit.py`, keeping
      every `src/*.py` and `tests/*.py` module strictly below 500 lines while
      preserving standalone `lifecycle.py` execution.
- [x] AC-03: Mark merged `project/ticket-006/README.md` `DONE` / `PUBLICATION` and
      pass `./project/governance-check.sh --base origin/main`.
- [x] AC-04: Pass `ruff check src tests`, `PYTHONPATH=src python3 -m unittest discover -s tests -v`,
      `PYTHONPATH=src pytest -q`, and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
