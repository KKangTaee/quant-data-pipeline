# GTAA SPY Low-MDD Style Top-2 ADV20

Status: Candidate review result
Date: 2026-06-29

## Goal

Find a GTAA portfolio that improves on SPY by CAGR and MDD, keeps MDD magnitude within 15%, reaches at least 11% CAGR, and passes the current first-pass candidate judgment.

## Candidate

| Field | Value |
|---|---|
| Preset | `GTAA SPY Low-MDD Style Top-2 ADV20` |
| Universe | `QQQ, SOXX, MTUM, QUAL, USMV, IAU, IEF, TLT` |
| Requested period | `2016-01-01` to `2026-05-01` |
| Effective result window | `2016-01-29` to `2026-02-27` |
| Top assets | `2` |
| Signal interval | `4` months |
| Score horizons | `1M / 6M` |
| Trend filter | `MA200` |
| Risk-off mode | `cash_only` |
| Minimum price | `$5` |
| Minimum ADV20D | `$20M` |
| Transaction cost | `10 bps` |
| Benchmark | `SPY` |

## Result

| Metric | GTAA | SPY |
|---|---:|---:|
| CAGR | `24.078108%` | `13.363791%` |
| MDD | `-9.990100%` | `-20.610791%` |
| Sharpe | `3.373899` | `2.214603` |
| End balance | `87963.37` | `35411.42` |

## Gate

| Signal | Status |
|---|---|
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Deployment readiness | `small_capital_ready` |
| Validation | `normal` |
| Benchmark policy | `normal` |
| Liquidity policy | `normal` |
| Guardrail policy | `normal` |
| ETF operability | `normal` |
| Liquidity clean coverage | `90.625%` |

## Interpretation

This candidate satisfies the user constraints under the current local DB/runtime:

- CAGR is above 11%.
- MDD magnitude is below 15%.
- CAGR is higher than SPY over the same effective result window.
- MDD is materially better than SPY over the same effective result window.
- Current first-pass promotion reaches `real_money_candidate`.

This is not a Final Review selected portfolio or live-trading approval. Practical Validation / Final Review remains the next workflow if the user wants to promote it beyond first-pass candidate status.
