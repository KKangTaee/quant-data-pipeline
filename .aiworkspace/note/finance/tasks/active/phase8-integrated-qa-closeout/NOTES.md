# Phase 8 Integrated QA Closeout Notes

Status: Active
Created: 2026-05-29

## Phase 8 Evidence Path

Implemented path:

```text
NYSE / Nasdaq / SEC sources
  -> finance.data.* lifecycle collectors
  -> finance_meta.nyse_symbol_lifecycle
  -> finance.loaders.universe.load_symbol_lifecycle_coverage_summary()
  -> app.services.backtest_data_coverage_audit.build_data_coverage_audit()
```

Important semantics:

- current listing snapshots are partial `listing_observed` evidence.
- SEC CIK / exchange rows are identity cross-check evidence.
- computed snapshot lifecycle rows are partial observed-window evidence.
- SEC Form 25 rows are actual delisting evidence but not complete membership proof.
- Data Coverage Audit requires requested-period `coverage_status=actual` lifecycle evidence for survivorship PASS.
