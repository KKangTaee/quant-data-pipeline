# Phase 9 Cost / Slippage / Liquidity Realism Risks

Status: Active
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Cost bps exists but was not applied to returns | False practical readiness | distinguish assumption-only from net-curve-applied proof |
| Turnover missing | cost impact cannot be estimated | require turnover or rebalance cadence review evidence |
| Liquidity evidence stale / partial | portfolio may be hard to trade | use provider freshness / DB price liquidity context |
| Capacity assumption absent | virtual capital may exceed realistic liquidity | add capacity evidence before selected-route pass |
| Sensitivity NOT_RUN is hidden | over-trusts point estimate | expose NOT_RUN / missing sensitivity in Backtest Realism Audit |
| New storage sprawl | user concern regression | no new JSONL registry; keep raw evidence in DB and compact evidence in existing workflow |

## Open Questions

- Which strategies currently apply `transaction_cost_bps` to the actual result curve?
- Can turnover be computed from existing portfolio weights without adding a new persistence path?
- Which liquidity threshold should differ by profile or strategy type?
- Should capacity be based on portfolio notional, target weight, ADV, AUM, or a conservative blend?
