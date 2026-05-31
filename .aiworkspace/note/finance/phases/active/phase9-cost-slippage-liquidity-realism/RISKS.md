# Phase 9 Cost / Slippage / Liquidity Realism Risks

Status: Complete
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

## Resolved In Phase 9

- Runtime cost application is now exposed through compact cost / net curve proof contracts.
- Turnover evidence is holdings-derived when possible and cadence-only evidence remains review.
- Liquidity / capacity evidence reads compact provider context and keeps bridge / proxy / stale / partial evidence out of strong PASS.

## Carry Forward

- Profile-specific liquidity / capacity thresholds remain a future refinement.
- Full market impact / execution simulation is out of scope for Phase 9.
- Weighted / saved mix component-level aggregation may need deeper proof in later phases.
- Phase 10 should strengthen walk-forward / out-of-sample / regime split validation.
