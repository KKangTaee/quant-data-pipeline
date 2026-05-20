# Runtime Package Boundary Status

Status: Complete
Created: 2026-05-20

## Progress

- Task 5 opened.
- 5-01 scope set: move `app/web/runtime` to `app/runtime` and update imports.
- 5-01 completed: runtime package moved to `app/runtime`, repo imports now use `app.runtime`.
- 5-02 completed: Candidate Library replay helper moved to `app/runtime/candidate_library.py`.
- Boundary lint now scans both `app/services` and `app/runtime`.

## Result

- Task 5 complete.
- `app/web` no longer owns runtime package files.
- `app/runtime` owns DB-backed backtest wrappers, JSONL repository helpers, selected portfolio runtime model, and Candidate Library replay helper.

## Verification

- `py_compile` passed for `app/runtime`, `app/services`, affected `app/web` callers, service contract tests, and boundary lint helper.
- `.venv/bin/python -m unittest tests/test_service_contracts.py` passed 16 tests.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` passed.
