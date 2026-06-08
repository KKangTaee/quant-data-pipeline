# Data Provenance / PIT Evidence Contract Notes

## Decisions

- Use a compact read model under `app/services`, not a DB migration, for the first slice.
- Reuse existing Practical Validation / Final Review compact evidence and attach provenance summaries to those records.
- Treat current provider snapshots as decision-time evidence with PIT review risk unless historical as-of proof is explicit.
- Treat current listing snapshots and SEC identity cross-check rows as survivorship review evidence, not historical universe PASS.
- Keep raw/full provider, holdings, macro, price rows in DB and out of workflow JSONL.
- Do not fabricate provenance rows from sparse legacy status stubs. The contract becomes a gate row only when explicit provenance metadata or attached run-set evidence exists.

## 1차 Audit Classification

| Evidence | Existing Metadata | Classification |
|---|---|---|
| ETF operability | source/source_type/as_of_date/coverage_status/collected_at | current provider snapshot; fresh actual can support decision-time review, not full historical PIT truth |
| ETF holdings | fund_symbol/source/source_type/as_of_date/coverage_status/collected_at | current holdings snapshot; full holdings stay in DB |
| ETF exposure | fund_symbol/source/source_type/as_of_date/derived_from/coverage_status/collected_at | derived / provider aggregate snapshot; proxy / bridge must remain visible |
| Macro | series/source/source_type/source_mode/observation_date/release_lag_days/coverage_status/collected_at/staleness | observation snapshot; revision vintage not controlled |
| Price window | DB window summary / runtime replay / period coverage | lower PIT risk only when requested period and runtime replay pass |
| Lifecycle | source_type/coverage_status/event_type/event_date/collected_at | historical/delisting actual can support survivorship; current / computed partial cannot |
| Robustness run-set | schema/run_set_id/non-pass rows/storage boundary | compact derived grouping layer; non-pass evidence must stay visible |
| Legacy packet stubs | status-only checks without provenance rows | neutral for the new provenance gate; still covered by existing Data Coverage / Validation Efficacy / Robustness policies |

## Boundaries

- UI may render provenance but must not fetch providers.
- The summary can be persisted inside existing compact validation/final decision snapshots only as compact metadata.
- Monitoring snapshot provenance extension can follow later if the selected monitoring registry schema needs a direct copy.
