# Recommendation

Status: Approved for Implementation Planning
Last Updated: 2026-07-16

## One-Line Recommendation

Build a vintage-aware, interpretable four-phase U.S. cycle model with calibrated `현재 / +1개월 / +2개월` probabilities, then surface it in Market Context with a cycle clock and calendar regime ribbon; keep gold, dollar, rates, and credit as market-implied context rather than the phase definition.

## Why This Direction

The user's study note captures a useful investor intuition: policy, inflation, credit, rates, gold, and dollar moves reveal what markets are anticipating. Its main weakness is treating those market reactions as if they directly define the real economy. NBER, CFNAI, ADS, and dynamic-factor research instead emphasize broad co-movement across employment, income, production, and sales.

A pure rule table would be easy to explain but brittle. A pure four-state hidden model would be statistically elegant but difficult to audit and prone to state-label instability. The recommended hybrid keeps a transparent activity/leading-factor structure, uses a constrained transition prior, and calibrates direct one- and two-month probability forecasts. This gives the UI meaningful uncertainty while preserving source-level explanations.

## Recommended Build Roadmap

### 1차. Semantics, Series Catalog, And Vintage Contract

Purpose:

- Define what each phase means and make historical evaluation point-in-time correct.

Likely files:

- `finance/data/db/schema.py`
- `finance/data/macro.py` or a focused vintage collector module
- `finance/loaders/macro.py` or a focused cycle loader
- `app/jobs/ingestion_jobs.py`
- focused tests and task docs

Completion conditions:

- Core series catalog and transformations are approved.
- Forecast-origin reads cannot see later releases or revisions.
- Existing macro consumers remain compatible.

Connection:

- Supplies valid training and replay data to 2차.

### 2차. Current Four-Phase Engine And Historical Classification

Purpose:

- Build coincident/leading factors and estimate current phase probabilities.

Likely files:

- new focused finance/service model modules
- tests for transformations, missing data, phase semantics, and historical turning points

Completion conditions:

- Historical classifications can be replayed by forecast date.
- Current probability includes evidence contributions and data cutoff.
- Naive and official-index benchmarks are recorded.

Connection:

- Establishes the current state and labels used by 3차.

### 3차. One- And Two-Month Probability Forecast

Purpose:

- Add horizon-specific transition distributions and honest uncertainty.

Completion conditions:

- Rolling-origin Brier/log-loss/calibration results beat or contextualize naive baselines.
- Forecast degrades visibly when coverage is insufficient.
- No unvalidated numeric probability is published.

Connection:

- Produces the read-model contract consumed by 4차.

### 4차. Market Context Economic-Cycle UI

Purpose:

- Let the user complete the real task: understand past, current, and possible next phases in one place.

Likely files:

- `app/web/overview/market_context.py`
- `app/web/overview/market_context_helpers.py`
- new isolated economic-cycle React component
- focused UI/service tests

Completion conditions:

- Market Context exposes `경제 사이클 | S&P 500 | 미국 개별주식` at one hierarchy level.
- Cycle clock, regime ribbon, horizon probabilities, and evidence pillars are responsive.
- Existing valuation flows have no regression.

Connection:

- Makes the validated engine usable without exposing ops diagnostics.

### 5차. Browser QA, Documentation Alignment, And Operational Handoff

Purpose:

- Verify the end-to-end workflow and leave durable data/method/runbook knowledge.

Completion conditions:

- Desktop and 420px Browser QA with one retained screenshot.
- Focused Python/TypeScript tests, build, `git diff --check`, and boundary checks pass.
- Data, architecture, flow, and runbook docs match the shipped behavior.

Current research-stage status: the user approved the hybrid model, clock+ribbon hierarchy, data/model validation contract, and five-step roadmap. 1차 implementation has not started; the approved design is recorded in `docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md`.

## What Not To Do Yet

- Do not ship a chart-only placeholder or manually authored current-cycle label.
- Do not use gold, dollar, 2Y, or 10Y direction as a deterministic four-phase lookup table.
- Do not backtest on today's revised history and call the result point-in-time.
- Do not imply NBER has declared a recession or recovery from the model output.
- Do not add allocation, buy/sell, or risk-on/risk-off instructions.
- Do not fetch sources from the Streamlit/React render path.
- Do not fold the full cycle domain into the existing valuation component.

## Decision Rules

Approved decisions:

- Use the hybrid model direction and clock+ribbon visual hierarchy.
- Implement the vintage-aware data/schema slice before the visible tab.
- Keep exact probabilities unavailable until rolling-origin calibration passes.
- Preserve unrelated local research work and do not stage it with this feature.

## Final Recommendation

Approve the recommended hybrid architecture and the five-step roadmap. The first code work should be the vintage-aware evidence contract, not UI scaffolding. This is the smallest route that can honestly support the requested historical view and one-/two-month probability forecast.
