# Repo Workflow Reference

## Read first

- `.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
- `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md`
- relevant strategy hub:
  - `VALUE_STRICT_ANNUAL.md`
  - `QUALITY_STRICT_ANNUAL.md`
  - `QUALITY_VALUE_STRICT_ANNUAL.md`

## Runtime code path

- `app/web/streamlit_app.py`
- `app/web/pages/backtest.py`
- `app/web/runtime/backtest.py`
- `finance/engine.py`
- `finance/strategy.py`
- `finance/performance.py`

## Required doc sync after meaningful search

1. active phase raw report
2. strategy hub
3. one-pager if strongest/current candidate changed
4. strategy backtest log
5. current candidate summary
6. `WORK_PROGRESS.md`
7. `QUESTION_AND_ANALYSIS_LOG.md`

## Quick hygiene command

After a refinement pass, run:

```bash
python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

This script checks the current git diff and highlights:

- changed phase docs
- changed strategy hubs / one-pagers / backtest logs
- whether root concise logs were touched
- whether generated artifacts are still present

## Candidate language rules

- distinguish:
  - same-gate exact hit
  - lower-MDD but weaker-gate near-miss
  - same-MDD but higher-CAGR improvement
- always record:
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`

## Current priority

1. `Value`
   - rescue lower-MDD near-miss if possible
2. `Quality + Value`
   - preserve strongest practical point and search for lower-MDD same-gate follow-up
3. `Quality`
   - maintain as reference/supporting track
