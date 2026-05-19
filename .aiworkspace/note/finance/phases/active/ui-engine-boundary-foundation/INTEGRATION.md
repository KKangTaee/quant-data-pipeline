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
5. Extract Practical Validation save / handoff contract after Compare is stable.
6. Defer provider gap job orchestration and evidence read models until their contracts are clear.

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

Run after Practical Validation service slice:

```bash
.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/web/backtest_practical_validation.py app/web/backtest_practical_validation_helpers.py app/web/backtest_compare.py app/web/backtest_candidate_review_helpers.py
.venv/bin/python - <<'PY'
import sys
import app.services.backtest_practical_validation
print("streamlit_loaded", "streamlit" in sys.modules)
PY
rg '(^|[^[:alnum:]_])st\\.|import streamlit|from streamlit' app/services/backtest_practical_validation.py app/web/backtest_practical_validation_helpers.py
git diff --check
```

Run after Evidence Read Model service slice:

```bash
.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review.py app/web/final_selected_portfolio_dashboard_helpers.py app/web/final_selected_portfolio_dashboard.py
.venv/bin/python - <<'PY'
import sys
import app.services.backtest_evidence_read_model
print("streamlit_loaded", "streamlit" in sys.modules)
PY
rg '(^|[^[:alnum:]_])st\\.|import streamlit|from streamlit' app/services/backtest_evidence_read_model.py
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
