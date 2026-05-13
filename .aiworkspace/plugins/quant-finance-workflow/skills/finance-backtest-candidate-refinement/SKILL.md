---
name: finance-backtest-candidate-refinement
description: Use when iterating on existing `finance` backtest candidates in quant-data-pipeline, especially bounded Value, Quality, Quality + Value, or GTAA refinements, current-candidate comparison, and synchronized update of registry-backed candidate evidence, strategy hubs, backtest logs, backtest reports, and root handoff logs.
---

# Finance Backtest Candidate Refinement

Use this skill for bounded candidate refinement around an existing practical backtest anchor.
This is not a net-new strategy design skill and not a DB / UI implementation skill.

Pair it with:
- `finance-task-management` when active task docs or handoff status need updates.
- `finance-doc-sync` when durable reports, indexes, roadmap, or root logs must be aligned.

## When To Use

Use this skill when the task is one of:

- bounded `Top N` follow-up
- one-factor addition or replacement around a current anchor
- downside-focused candidate refinement
- structural downside-improvement kickoff or follow-up
- same-gate vs weaker-gate near-miss comparison
- updating strategy hubs, strategy backtest logs, candidate one-pagers, or current-candidate summary
- reconciling human-readable candidate evidence with registry-backed source-of-truth

Do not use this skill for:

- net-new strategy implementation in `finance/strategy.py`
- ingestion or DB schema changes
- broad, unconstrained research with no current anchor
- purely UI wording tweaks with no backtest refinement component

## First Reads

Read only what is needed:
- `.aiworkspace/note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
- `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- the relevant strategy hub and `*_BACKTEST_LOG.md`
- the active task under `.aiworkspace/note/finance/tasks/active/` if this refinement is part of a current workstream

For detailed update targets and candidate language rules, read `references/repo-workflow.md`.

## Workflow

1. Identify the current anchor, benchmark, date range, universe, and exact refinement question.
2. Keep the search bounded: one factor, one `Top N` band, one benchmark sensitivity, one overlay sensitivity, or one near-miss rescue path at a time.
3. Record meaningful candidates with `CAGR`, `MDD`, promotion / shortlist / deployment judgment, and whether the point is an exact hit, near-miss, or rejected variant.
4. Keep machine-readable candidate state in registries only when the user explicitly asks or the product workflow requires it.
5. Put durable human-readable interpretation into the relevant strategy hub, strategy backtest log, current-candidate summary, one-pager, or `reports/backtests/runs/YYYY/`.
6. Keep root handoff logs concise; move detail to the active task or report.

## Practical Scripts

After a meaningful refinement or document sync, run:

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

For current-candidate registry inspection:

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
```
