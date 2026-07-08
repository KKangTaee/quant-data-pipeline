# Phase 6. Coverage Expansion And Source QA Risks

- The DB-backed reason `edgar_unavailable_or_cik_mapping_issue` is a candidate group, not a final issuer-level conclusion. Use targeted `Statement Coverage Diagnosis` before deciding source support or exclusion.
- `NASDAQ` coverage cannot be judged until the Nasdaq current snapshot universe resolves rows in this worktree.
- `TOP2000` coverage is materially weaker than `TOP1000`; broad expansion should be planned as targeted EDGAR annual refresh batches, not a yfinance statement fallback.
