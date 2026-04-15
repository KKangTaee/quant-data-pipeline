---
name: finance-backtest-candidate-refinement
description: Use when iterating on `finance` backtest candidates in quant-data-pipeline, especially for bounded `Value`, `Quality`, or `Quality + Value` refinement, current-candidate comparison, and synchronized update of phase reports, strategy hubs, one-pagers, backtest logs, and root summary logs.
---

# Finance Backtest Candidate Refinement

## Overview

This skill is for repeated backtest-refinement work in `quant-data-pipeline`.
Use it when we are not building a brand-new strategy family, but improving or reassessing current practical candidates around an existing anchor.

## When To Use

Use this skill when the task is one of:

- bounded `Top N` follow-up
- one-factor addition or replacement around a current anchor
- downside-focused candidate refinement
- structural downside-improvement kickoff or follow-up
- same-gate vs weaker-gate near-miss comparison
- updating phase report + strategy hub + one-pager + backtest log together
- re-establishing repo context before the next refinement cycle

Do not use this skill for:

- net-new strategy implementation in `finance/strategy.py`
- ingestion or DB schema changes
- broad, unconstrained research with no current anchor
- purely UI wording tweaks with no backtest refinement component

## Workflow

### 1. Rebuild context quickly

- Read:
  - current candidate summary
  - active phase TODO
  - relevant strategy hub
- Only open one-pager or raw phase report after identifying the current anchor and the exact question.

See:
- `references/repo-workflow.md`

### 2. Keep the search bounded

Prefer narrow follow-ups such as:

- `Top N` narrow band
- one-factor add/replace
- benchmark sensitivity
- minimal overlay sensitivity
- rescue attempt for a lower-MDD weaker-gate near-miss

When bounded refinement has already closed out, switch to
`structural downside-improvement` framing:

- identify current architectural levers first
- separate immediate candidate work from operator-bridge work
- choose one implementation slice before reopening broad search

Do not jump to blanket gate relaxation or large family redesign unless the user explicitly asks.

### 3. Record the result in candidate language

For each meaningful candidate, record at minimum:

- `CAGR`
- `MDD`
- `Promotion`
- `Shortlist`
- `Deployment`

And classify it as one of:

- current best practical point
- same-gate exact hit
- lower-MDD but weaker-gate near-miss
- same-MDD but higher-CAGR improvement
- rejected defensive variant

### 4. Sync the right documents

When the result is durable enough to keep, update:

1. active phase raw report
2. strategy hub
3. one-pager if strongest/current candidate changed
4. strategy backtest log
5. current candidate summary
6. root concise logs if the decision changes future work

### 5. Keep root logs concise

If detailed history grows too much, archive older root logs and keep only:

- current workstream
- current strongest candidates
- active design decisions
- archive pointers

## Repo Reference

The repo-specific reading order and update targets live in:

- `references/repo-workflow.md`

## Practical Script

For a quick post-refinement hygiene pass, run:

```bash
python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

Use this after a bounded search or document-sync work unit to see:

- which finance docs changed
- whether backtest logs and root concise logs were touched
- whether index docs were updated
- whether generated artifacts are still sitting in git status

For machine-readable current-candidate persistence, run:

```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
```

For a new phase kickoff bundle, run:

```bash
python3 plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase 99 --title "Example Phase"
```
