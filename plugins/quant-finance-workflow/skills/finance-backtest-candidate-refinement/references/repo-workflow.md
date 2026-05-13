# Repo Workflow Reference

## Read first

- `.note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
- `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/docs/INDEX.md`
- `.note/finance/docs/ROADMAP.md`
- `.note/finance/docs/PROJECT_MAP.md`
- active task or phase docs under `.note/finance/tasks/active/` or `.note/finance/phases/active/`
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

For current-candidate persistence, run:

```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
```

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

1. candidate consolidation
   - current candidate를 compare / weighted / saved workflow와 더 잘 연결
2. current candidate persistence
   - registry와 summary를 같이 유지
3. automation baseline
   - phase bundle / hygiene / registry helper를 다음 세션에서도 다시 쓰기 쉽게 유지
