# Overview Market Context S&P 500 Valuation V1 Risks

Status: Active
Last Updated: 2026-07-12

## Open Risks

### S&P Workbook Access

Official Index Earnings workbook automation may be blocked or subject to usage terms. V1 must support deterministic local/uploaded source ingestion and preserve source identity.

Mitigation implemented in 1차: deterministic local `.xlsx` import with mandatory source release date and explicit status columns. Fully automated official download remains open for 5차 refresh integration.

### Monthly Earnings PIT

Shiller monthly earnings are interpolated research data. They support current descriptive valuation bands but not strict historical signal timing claims.

### Trailing-To-Forward Multiple Mismatch

Applying a trailing-multiple distribution to macro-implied NTM EPS creates a scenario band, not a statistically pure historical forward-PER band. UI copy must not call it an official fair value or confidence interval.

### FOMC Model Simplicity

Real GDP plus PCE does not fully explain S&P 500 EPS. Margins, wages, FX, taxes, interest expense, foreign revenue, and buybacks remain outside V1.

### Source Freshness

Shiller monthly, S&P earnings, SEP quarterly, and SPX/SPY EOD sources update at different cadences. Same-date evidence and stale-state behavior require explicit tests.

### Existing Workspace Changes

The worktree contains unrelated untracked Market Movers research and generated QA screenshots. They must not be staged, modified, or deleted by this task.
