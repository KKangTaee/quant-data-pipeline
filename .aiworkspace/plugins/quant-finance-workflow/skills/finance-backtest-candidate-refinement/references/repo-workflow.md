# Repo Workflow Reference

## Read first

- `.aiworkspace/note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
- `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.aiworkspace/note/finance/docs/INDEX.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- active task docs under `.aiworkspace/note/finance/tasks/active/` when this refinement belongs to a current workstream
- active phase docs under `.aiworkspace/note/finance/phases/active/` only when the user explicitly framed the work as phase-owned
- relevant strategy hub:
  - `VALUE_STRICT_ANNUAL.md`
  - `QUALITY_STRICT_ANNUAL.md`
  - `QUALITY_VALUE_STRICT_ANNUAL.md`
  - `GTAA.md`
- relevant strategy `*_BACKTEST_LOG.md`

## Runtime code path

- `app/web/streamlit_app.py`
- `app/web/pages/backtest.py`
- `app/web/runtime/backtest.py`
- `finance/engine.py`
- `finance/strategy.py`
- `finance/performance.py`

## Required doc sync after meaningful search

1. Append the result to the relevant strategy `*_BACKTEST_LOG.md` when it is worth revisiting.
2. Update the strategy hub when the candidate changes how that strategy family should be understood.
3. Update the current-candidate summary if the strongest point, near-miss set, or deployment interpretation changed.
4. Update a candidate one-pager only when a specific candidate remains a stable human-readable reference.
5. Put one-off source reports from a separate analysis session under `.aiworkspace/note/finance/reports/backtests/runs/YYYY/`.
6. Touch `WORK_PROGRESS.md` or `QUESTION_AND_ANALYSIS_LOG.md` only with concise milestone / decision summaries.
7. Update registry JSONL only when the user explicitly asks or the product workflow needs machine-readable persistence.

## Quick hygiene command

After a refinement pass, run:

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

This script checks the current git diff and highlights:

- changed strategy hubs / candidate one-pagers / backtest logs
- changed active phase docs, if any
- whether root concise logs were touched
- whether generated artifacts are still present

For current-candidate persistence, run:

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
```

## Candidate language rules

- Distinguish:
  - current best practical point
  - same-gate exact hit
  - lower-MDD but weaker-gate near-miss
  - same-MDD but higher-CAGR improvement
  - rejected defensive variant
- always record:
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`
- Record period, universe, benchmark, rebalance cadence, and material settings when they affect interpretation.

## Boundaries

- Do not treat a candidate one-pager as source-of-truth. The registry and product workflow own machine-readable candidate state.
- Do not commit run history, temp CSV, notebook scratch, or local generated artifacts unless the user explicitly asks.
- Do not reopen a broad search after a bounded follow-up unless the user changed the scope.
- Do not turn a candidate refinement note into a UI, ingestion, or strategy implementation task. Route those to the matching finance skill.

## Current priority

1. Keep current-candidate interpretation aligned across registry, summary, and strategy logs.
2. Keep bounded follow-ups small enough that results are comparable.
3. Keep human-readable evidence in `reports/backtests/` and machine-readable state in `registries/`.
