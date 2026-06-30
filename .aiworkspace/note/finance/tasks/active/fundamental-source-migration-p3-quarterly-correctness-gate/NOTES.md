# Phase 3. Quarterly Correctness Gate Notes

- Synthetic Q4 is not implemented in this phase.
- Existing DB rows are not deleted. Historical quarterly `10-K` / `10-K/A` rows may remain for audit, but loaders no longer return them as usable quarterly statement/factor rows.
- `nyse_factors_statement` has no stored form type column. The loader recovers it by joining `nyse_fundamentals_statement` on `symbol`, `freq`, `period_end`, and accession number.
- The raw value ledger can still contain 10-K/FY facts. The policy applies when building/reading statement shadow rows.
