# Backtest Real-Money Stage Boundary V1 Runs

## 2026-05-30

- `.venv/bin/python -m py_compile app/web/backtest_result_display.py app/web/backtest_compare.py app/web/backtest_history.py`
  - Result: pass.
- `git diff --check`
  - Result: pass.
- `rg` targeted legacy visible label check against Backtest result / Compare / History modules.
  - Result: no user-facing `Probation / Monitoring`, `Deployment Readiness`, `Deployment checklist`, `Checklist 상세 보기`, `paper tracking`, `routine monthly`, `소액 trial`, or `비중 확대` labels found.
- Browser smoke on `http://127.0.0.1:8502/backtest`
  - Ran Equal Weight / Dividend ETFs backtest.
  - Opened Real-Money tab.
  - Confirmed required labels: `Suggested Route`, `Next Validation Focus`, `Execution Preview`, `Preview 상세 보기`.
  - Confirmed absent in Real-Money tab text: `Probation / Monitoring`, `Deployment Readiness`, `Deployment`, `Checklist 상세 보기`, `paper tracking`, `routine monthly`, `소액 trial`, `비중 확대`.
