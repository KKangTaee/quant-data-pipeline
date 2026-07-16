# Economic Cycle Gold / Dollar Price Confirmation V1 Runs

- Design discovery confirmed stored `GC=F`, stale `UUP`, current `DX-Y.NYB` provider availability, and existing futures ledger/collector boundary.
- First five-year backfill wrote the price rows but the monitor-run insert rejected the overlong cadence label. The bounded retry used `cycle_asset_backfill` and completed idempotently.
- `DX-Y.NYB` actual backfill: 1,257 daily rows, 2021-07-16 through 2026-07-16, zero failed symbols.
- Focused Economic Cycle regression: 33 passed, 3 external-library deprecation warnings.
- Futures service contract selection: 1 passed, 805 deselected, 3 external-library deprecation warnings.
- React production build: 170 modules transformed; CSS/JS bundles generated successfully.
- Python compile and `git diff --check`: passed.
- Automated Browser screenshot could not be captured because the configured in-app Browser Node runtime was unavailable; HTTP/read-model/source-contract/build checks were used instead.
