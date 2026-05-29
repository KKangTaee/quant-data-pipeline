# Walk-forward / OOS Source Map V1 Notes

Status: Complete
Created: 2026-05-29

## Findings

- Practical Validation already has a strong curve normalization path. It prefers runtime replay curve, then embedded source curve, then component curves, then DB price proxy fallback.
- Runtime backtest already computes rolling and OOS metadata against benchmark, including recent excess, drawdown gap, in-sample excess, out-sample excess, and split deterioration.
- Robustness Lab already exposes rolling evidence, but current rolling evidence uses portfolio curve only and does not compute rolling benchmark excess.
- Validation Efficacy Audit currently checks replay, period coverage, benchmark parity, provider freshness, robustness, PIT, survivorship, and execution boundary. It does not yet have explicit walk-forward / OOS / regime rows.
- Final Review gate can consume new evidence through Validation Efficacy Audit and gate policy rows without a new persistence path.

## Decision

Proceed to `walkforward-split-contract-v1` first.
Do not combine walk-forward, OOS holdout, and regime split into one implementation slice.

## Storage Note

This task added no runtime persistence.
Future Phase 10 implementation should keep raw split details out of workflow JSONL and store only compact audit evidence through existing validation result payloads.
