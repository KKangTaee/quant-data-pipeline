# Data Provenance / PIT Evidence Contract Design

Status: Active

## Audit Summary

- `finance/loaders/provider.py` already returns ETF operability / holdings / exposure rows with `source`, `source_type`, `source_ref`, `as_of_date`, `coverage_status`, `collected_at`.
- `finance/loaders/macro.py` returns macro rows with `source`, `source_type`, `source_mode`, `observation_date`, `coverage_status`, `collected_at`, plus snapshot `staleness_days` / `snapshot_status`.
- `finance/loaders/universe.py` returns lifecycle rows with `source_type=current_listing_snapshot / historical_listing / delisting_feed / computed_from_snapshots`, `coverage_status`, event dates, and `collected_at`.
- `app/services/backtest_practical_validation_provider_context.py` already summarizes provider freshness / source mix / as-of ranges without storing full holdings rows.
- `app/services/backtest_data_coverage_audit.py` already separates DB price window, provider freshness, PIT replay, universe listing, survivorship control.
- `app/services/backtest_validation_efficacy.py` and `app/services/backtest_evidence_read_model.py` read those compact rows into Final Review policy, but there is no single row-level provenance schema.
- `app/services/backtest_robustness_run_set.py` already provides run-set grouping and storage boundary, but not the broader data provenance contract.

## Schema Decision

No new DB schema is needed for this slice. Existing DB tables already carry source and timing metadata. The missing piece is a compact read model contract in `app/services`, not raw storage.

New read model:

```text
app/services/backtest_data_provenance.py
  -> build_evidence_provenance_summary(validation)
```

Each row carries:

- `source_name`
- `source_type`
- `source_date`
- `collected_at`
- `as_of_date`
- `available_at_assumption`
- `snapshot_kind`
- `coverage_status`
- `freshness_status`
- `staleness_days`
- `is_point_in_time_safe`
- `pit_risk`
- `lookahead_risk`
- `survivorship_risk`
- `proxy_status`
- `decision_effect`
- `evidence_owner`
- `storage_location`
- `schema_version`

## Integration Points

- `app/services/backtest_practical_validation_diagnostics.py`: attach `data_provenance_summary` and display rows to Practical Validation result after data coverage / robustness summaries are available.
- `app/services/backtest_evidence_read_model.py`: include provenance in investability packet, packet checks, summary, and selection policy input.
- `app/web/backtest_practical_validation.py`: show provenance summary in the Data tab.
- `app/web/backtest_final_review.py`: show provenance summary in the Investability Packet and Evidence Appendix.

## Risk Handling

- Provider / holdings / exposure rows are current provider snapshots unless the row explicitly proves otherwise, so they default to PIT review risk even when fresh.
- Macro observations are not ALFRED vintage-controlled, so macro provenance defaults to revision-vintage review risk.
- Current listing snapshot / SEC identity cross-check / computed partial lifecycle rows cannot control survivorship by themselves.
- Runtime replay / DB price window can be lower PIT risk only when data coverage audit rows pass.
- Robustness run-set is derived compact evidence, not a raw data source; it inherits non-pass status from underlying evidence.
