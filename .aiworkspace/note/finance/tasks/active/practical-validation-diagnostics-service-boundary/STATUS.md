# Practical Validation Diagnostics Service Boundary Status

Status: Complete
Created: 2026-05-20

## Progress

- Task opened to move the large Practical Validation diagnostic builder out of `app/web`.
- Current helper is Streamlit-free but service imports it from a UI package.
- Moved the helper module to `app/services/backtest_practical_validation_diagnostics.py`.
- Updated Practical Validation service, Compare, and Candidate Review imports.
- Added a diagnostics service contract test for Streamlit-free import, profile building, and compact curve snapshots.

## Result

- Practical Validation diagnostics ownership now sits under `app/services`.
- UI files still render controls / session state, while service modules own source/profile/diagnostic data construction.

## Verification

- `py_compile` passed for Practical Validation service, diagnostics service, replay service, UI callers, and service contract tests.
- `.venv/bin/python -m unittest tests/test_service_contracts.py` passed 15 tests.
- `check_ui_engine_boundary.py` passed with only transitional `app.services -> app.web` advisories.
- `git diff --check` and `git diff --cached --check` passed.
