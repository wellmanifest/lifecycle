# Ticket 008: Harden lifecycle regex anchors, int/float bounds, and regular-file inode checks

- **ID**: ticket-008
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Harden `wellmanifest/lifecycle` (`src/lifecycle.py` and `src/lifecycle_catalog.py`):
anchor all identifier/code/integer regexes with `\Z`, bound `LIFECYCLE ... VERSION`
digit conversion before `int(raw_ver)` so >4300-digit inputs emit `LFC-MODEL-001`
rather than raising Python's integer conversion `ValueError`, verify `os.lstat` regular
file mode and `(st_dev, st_ino)` inode stability in `read_regular_bytes`, reject
overflow IEEE-754 floats (`1e999` / `-1e999`) in `src/lifecycle_catalog.py`, keep all
modules strictly `< 500` lines while preserving standalone copy execution, and mark
merged `ticket-007` `DONE`.

## Acceptance criteria

- [x] AC-01: `src/lifecycle.py` and `src/lifecycle_catalog.py` enforce `\Z` regex anchors,
      bounded `VERSION` digit parsing, `lstat`+`fstat` regular-file inode checks, and
      finite float parsing (`1e999` rejected) while keeping every file `< 500` lines.
- [x] AC-02: `PYTHONPATH=src python3 -m unittest discover -s tests -v` and
      `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q` pass, including standalone copy validation.
- [x] AC-03: Close merged `ticket-007`, and pass `./project/governance-check.sh --base origin/main`
      and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
