# Strategy Promotion Contract Handoff Notes

Status: Active
Created: 2026-06-08

## Decisions

- Use an active task because this is a multi-file documentation/workflow contract task with verification and commit.
- Keep the main artifact in `reports/backtests/` because this is a human-readable handoff / report contract, not a registry source-of-truth.
- Do not create or approve a new strategy in `main-dev`.
- Treat `NOT_RUN` as missing evidence, not pass.
- Keep `Risk-On Momentum 5D` as an example of required evidence, not as an approved promotion.

## Required Handoff Fields

| Field Group | Required Items |
|---|---|
| Identity | strategy family, owner, target use case |
| Universe | universe definition, historical membership, survivorship assumption |
| Data | PIT data assumption, provider / macro / factor source boundary |
| Parameters | parameter set, optimization history, in-sample / out-of-sample split |
| Robustness | walk-forward, regime, stress, cost / slippage sensitivity |
| Realism | turnover, liquidity, benchmark / comparator parity |
| Replay | replay contract, generated artifact location, reproducibility notes |
| Evidence State | known failure cases, `NOT_RUN` / `REVIEW` / `BLOCKED` evidence |
| Product Handoff | Practical Validation source payload conditions, Final Review selected-route blockers, Portfolio Monitoring review triggers |

## Audit Findings

- `docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` explains how to implement strategy families but not how `backtest-dev` evidence becomes eligible for product promotion.
- `reports/backtests/TEMPLATE.md` covers report basics but does not require optimization, OOS, PIT, survivorship, cost / liquidity, or monitoring trigger fields.
- `PORTFOLIO_SELECTION_FLOW.md` already has strong selected-route gate language. Promotion contract should sit before Practical Validation source creation and feed those existing gates rather than create a parallel approval stage.
- `Monitoring Snapshot / Review Loop V2` is complete and gives the downstream monitoring loop a stable place to receive review triggers.

## Boundary Notes

- Contract docs should not rewrite registry / saved JSONL.
- Helper validation should check document completeness, not assert that a strategy is approved.
- Future implementation work may use `finance-strategy-implementation` and `finance-backtest-web-workflow`, but this task should stay contract-first.
