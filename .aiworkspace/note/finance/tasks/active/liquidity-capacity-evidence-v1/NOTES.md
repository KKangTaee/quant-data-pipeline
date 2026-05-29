# Notes

## Initial Source Map

- Provider operability context is built in `app/services/backtest_practical_validation_provider_context.py`.
- The context reads DB/provider snapshots through `finance/loaders/provider.py`.
- Practical Validation diagnostics already prefer provider operability context over price/volume proxy.
- Backtest Realism Audit currently reads only provider `diagnostic_status`, `coverage_weight`, and summary.

## Principle

- A `PASS` string alone should not prove investable liquidity.
- Liquidity evidence should expose coverage, freshness, source strength, and compact capacity metrics.
- Raw provider rows and full holdings remain DB-backed; audit evidence stays compact.

## Implementation Notes

- Provider context still reads only through existing DB-backed provider loaders.
- The new capacity metrics are compact values derived from the best provider rows, not raw provider row persistence.
- `status=actual`, high coverage, fresh provenance, official source weight, actual coverage weight, and no review symbols are required for the strong liquidity PASS path.
- Legacy validation rows with only `diagnostic_status=PASS` and no provenance are now `REVIEW` in Backtest Realism Audit.
