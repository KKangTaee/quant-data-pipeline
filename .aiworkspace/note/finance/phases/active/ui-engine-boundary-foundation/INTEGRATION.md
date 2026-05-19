# UI Engine Boundary Foundation Integration

Status: Active
Created: 2026-05-19

## Integration Strategy

This phase should integrate one boundary slice at a time.

Order:

1. Audit and document current coupling.
2. Extract Single Strategy execution service.
3. Verify Streamlit behavior remains compatible.
4. Use the same pattern for Compare only after the first slice is stable.
5. Defer Practical Validation and evidence read models until their contracts are clear.

## Verification Baseline

Run after phase doc updates:

```bash
git status --short
git diff --check
find .aiworkspace/note/finance/phases/active/ui-engine-boundary-foundation -maxdepth 1 -type f | sort
find .aiworkspace/note/finance/tasks/active/ui-engine-boundary-audit -maxdepth 1 -type f | sort
```

Run after first implementation slice:

```bash
.venv/bin/python -m py_compile app/services/backtest_execution.py app/web/backtest_single_runner.py
.venv/bin/python - <<'PY'
import app.services.backtest_execution
print("ok")
PY
rg "import streamlit|st\\." app/services/backtest_execution.py
git diff --check
```

## Commit Strategy

- Commit phase/task documentation as one coherent planning unit.
- Commit each service extraction task separately.
- Do not stage `.DS_Store`, `__pycache__`, run history, registry JSONL, or generated artifacts.

## Handoff Rule

Before starting each implementation task, record:

- target files
- behavior to preserve
- validation command
- rollback concern
