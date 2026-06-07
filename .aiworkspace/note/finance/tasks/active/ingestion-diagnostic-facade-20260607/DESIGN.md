# Design

Status: Completed
Last Verified: 2026-06-07

## Module Boundary

`app/web/ingestion_console.py` remains the Streamlit render and session-state owner.
It still owns:

- job form controls
- explicit button actions
- pending / running job session state
- result display and diagnostic table rendering

`app/services/ingestion_diagnostics.py` owns read-only diagnostic orchestration:

- `load_price_window_preflight_summary`
- `run_price_stale_diagnosis`
- `run_statement_coverage_diagnosis`
- `run_statement_pit_inspection`

## Data Flow

```text
app/web/ingestion_console.py
  -> app/services/ingestion_diagnostics.py
  -> app/jobs/diagnostics.py / finance/loaders/* / finance/data/financial_statements.py
  -> read-only payload / DataFrame
  -> Streamlit table render
```

No new DB writes are introduced by this facade.
The live EDGAR source sample in PIT inspection remains read-only field inspection and keeps the existing UI wording that it does not collect or persist statement rows.

## Compatibility Contract

The existing session-state payload names remain unchanged:

- `price_stale_diagnosis_result`
- `statement_coverage_diagnosis_result`
- `statement_pit_inspection_result`

The PIT inspection result keeps `coverage_df`, `audit_df`, `audit_scope`, `source_symbol`, and `source_payload` keys so existing render code stays compatible.

## Relationship To 7A / 8C

7A physically moved the Ingestion UI out of `streamlit_app.py`.
7B completes the remaining read-only diagnostic boundary cleanup.
8C strict runtime split remains valid and independent; this task only closes the earlier 7차 follow-up.
