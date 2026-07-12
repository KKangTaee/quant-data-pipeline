# Overview Market Context S&P 500 Valuation V1 Risks

Status: Active
Last Updated: 2026-07-12

## Open Risks

### S&P Workbook Access

Official Index Earnings workbook automation may be blocked or subject to usage terms. V1 must support deterministic local/uploaded source ingestion and preserve source identity.

Mitigation implemented: deterministic local `.xlsx` import remains optional with mandatory source release date and explicit status columns. Daily automation imports it when `SP500_INDEX_EARNINGS_PATH` and `SP500_INDEX_EARNINGS_RELEASE_DATE` are configured; otherwise graph 2 uses the latest Shiller TTM EPS as a visibly labeled `interpolated_ttm_proxy` rather than blocking or pretending it is official actual.

### Monthly Earnings PIT

Shiller monthly earnings are interpolated research data. They support current descriptive valuation bands but not strict historical signal timing claims.

V1.2 mitigation: the 1-year line is explicitly labeled `과거 시점 재구성 시나리오`. EPS 미발표 월은 최신 확인 EPS를 유지하고 `eps_basis_date`/carry-forward 상태를 노출한다. Strict as-known historical EPS backtest remains out of scope.

### Trailing-To-Forward Multiple Mismatch

Applying a trailing-multiple distribution to macro-implied NTM EPS creates a scenario band, not a statistically pure historical forward-PER band. UI copy must not call it an official fair value or confidence interval.

### FOMC Model Simplicity

Real GDP plus PCE does not fully explain S&P 500 EPS. Margins, wages, FX, taxes, interest expense, foreign revenue, and buybacks remain outside V1.

### Source Freshness

Shiller monthly, S&P earnings, SEP quarterly, and SPX/SPY EOD sources update at different cadences. Same-date evidence and stale-state behavior require explicit tests.

V1.2 retains this cadence mismatch visibly. SEP backfill is bounded to the official vintages needed by the 1-year view; a longer 5-year view would require expanding the historical release set and is not implemented.

V1.3 mitigation: Graph 1 no longer stops at the latest EPS month. April-July values are explicitly labeled provisional and use the latest March TTM EPS, but they remain excluded from the 60-month distribution and are not presented as completed historical PER observations.

### Longer Graph 2 Window

The current reconstructed flow is 1 year. A 3-year or 5-year selector is feasible, but requires a correspondingly older official SEP vintage backfill and must retain the non-strict-PIT Shiller EPS warning. It remains a separately approved follow-up, not part of V1.3.

### Existing Workspace Changes

The worktree contains unrelated untracked Market Movers research and generated QA screenshots. They must not be staged, modified, or deleted by this task.

### Pre-existing Sentiment Contract Failure

The full service-contract suite currently has one failure expecting `payload.summary.metrics.map` in the Sentiment React source. Market Context valuation changes do not touch that source; targeted valuation tests and later Market Context contracts remain the acceptance gate for this task.

### Non-isolated Market Movers Contract

The full suite can persist `limited_price_history` rows and a later Market Movers EOD repair test reads that DB state without patching it. In the final run this made the test consume only the 2-row quality repair instead of its isolated 65-row expectation. Market Context valuation code does not touch the Market Movers plan or issue table; this remains an external test-isolation gap.
