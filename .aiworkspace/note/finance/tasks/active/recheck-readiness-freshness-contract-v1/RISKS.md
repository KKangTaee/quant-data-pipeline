# Recheck Readiness / Freshness Contract V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

- Embedded replay contracts may be incomplete for older selected rows.
- Current Candidate Registry fallback keeps older rows usable, but source drift remains visible through metrics.
- Symbol freshness is still DB metadata; it does not collect missing OHLCV data.

## Mitigation

- Missing or invalid replay contracts route to blocked.
- Missing price data routes to needs data.
- Stale price data routes to review.
- Execution boundary explicitly disables DB write, registry write, monitoring log auto write, approval, order, and auto rebalance.
