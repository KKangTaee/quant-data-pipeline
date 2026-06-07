# Runs

Status: Completed
Last Verified: 2026-06-07

## Code / Document Inspection

```bash
wc -l app/web/backtest_compare.py app/web/backtest_compare_components.py app/web/ingestion_console.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/runtime/backtest.py app/runtime/backtest_risk_on_momentum.py app/runtime/backtest_real_money.py app/runtime/backtest_strict.py
```

Result: recorded a targeted line-count snapshot. `app/web/backtest_compare.py` remains 5,890 lines after 9차.

```bash
find app/web app/runtime app/services finance -name '*.py' -type f -print0 | xargs -0 wc -l | sort -nr | sed -n '1,35p'
```

Result: largest remaining files are `backtest_compare.py`, `overview_dashboard.py`, `final_selected_portfolios.py`, `overview_market_intelligence.py`, and `ingestion_console.py`.

```bash
.venv/bin/python - <<'PY'
import ast
from pathlib import Path
path = Path('app/web/backtest_compare.py')
source = path.read_text(encoding='utf-8')
tree = ast.parse(source)
rows = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        end = getattr(node, 'end_lineno', node.lineno)
        rows.append((end - node.lineno + 1, node.lineno, end, node.name))
for size, start, end, name in sorted(rows, reverse=True)[:25]:
    print(f'{size:5d} {start:5d}-{end:<5d} {name}')
PY
```

Result: `_render_strategy_compare_workspace` is the largest remaining `backtest_compare.py` function at about 1,581 lines.

```bash
rg -n "\\.note/finance|\\.note" app finance tests .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md .aiworkspace/note/finance/tasks/active/README.md
```

Result: no production code recreates `.note/finance`; one historical `quant-research/.note/research` metadata string remains in `app/runtime/backtest.py`.

## Closeout Verification

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 287 tests.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result: passed. Hard violations: none. Advisories: none.

```bash
git diff --check
curl -fsS http://localhost:8501/_stcore/health
```

Result: passed. Streamlit health returned `ok`.

```bash
if rg -n "import streamlit|from streamlit|app\\.web" app/services app/runtime finance; then exit 1; else echo "no streamlit/reverse-web boundary hits"; fi
```

Result: passed. No Streamlit imports or reverse `app.web` imports were found in `app/services`, `app/runtime`, or `finance`.

## Browser QA

Not run for 10차 because this closeout changed documentation and state manifests only.
The latest UI screenshot artifact from 9차 remains untracked and should stay unstaged unless explicitly requested.
