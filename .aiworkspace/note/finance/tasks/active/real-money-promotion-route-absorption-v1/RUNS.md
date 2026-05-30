# Real-Money Promotion Route Absorption V1 Runs

## 2026-05-30

- `.venv/bin/python -m py_compile app/web/backtest_result_display.py`
  - Result: pass.
- `git diff --check`
  - Result: pass.
- `rg -n "Candidate Shortlist|Shortlist Status|Shortlist Next Step|후보 전략 숏리스트|shortlist_hold|resolve_contract_gaps_before_shortlist|title\\\": \\\"Shortlist\\\"" app/web/backtest_result_display.py .aiworkspace/note/finance/docs/GLOSSARY.md .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
  - Result: pass; no user-facing legacy labels matched.
- Browser smoke on `http://127.0.0.1:8502/backtest`
  - Result: pass.
  - Ran Equal Weight, opened `Real-Money`, and confirmed the main screen shows `Promotion`, `Suggested Route`, and `Route Next Step`.
  - Confirmed `Shortlist`, `후보 전략 숏리스트`, and `resolve_contract_gaps_before_shortlist` are not present in visible page text.
  - Note: direct `/backtest` navigation still logs Streamlit `_stcore/health` and `_stcore/host-config` 404s; the page rendered and interaction completed.
