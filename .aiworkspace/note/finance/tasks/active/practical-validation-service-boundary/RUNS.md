# Practical Validation Service Boundary Runs

Commands and verification for this task.

## 2026-05-20

- Inspected project maps and Practical Validation V2 design docs.
- Inspected `app/web/backtest_practical_validation.py`, `app/web/backtest_practical_validation_helpers.py`, and replay helpers to identify the first service extraction slice.
- Added `app/services/backtest_practical_validation.py`.
- Updated Practical Validation, Compare, and Candidate Review handoff call sites to apply service-returned session contracts.
- Ran `py_compile` for the new service and affected UI/helper files: pass.
- Ran service import smoke and confirmed `streamlit_loaded False`.
- Ran no-Streamlit boundary check against the new service and Practical Validation helper: pass.
- Ran `git diff --check`: pass.
