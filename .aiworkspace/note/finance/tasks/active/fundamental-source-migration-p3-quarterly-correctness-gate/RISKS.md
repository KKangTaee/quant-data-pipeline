# Phase 3. Quarterly Correctness Gate Risks

- Synthetic Q4 is still not available. Year-end quarterly flow metrics remain blocked rather than reconstructed.
- Existing DB rows with quarterly `10-K` / `10-K/A` can still appear in direct SQL audits. Product/runtime loaders are the supported consumption boundary.
- If a future caller bypasses loaders and reads `nyse_fundamentals_statement` or `nyse_factors_statement` directly, it must apply the same quarterly form policy.
