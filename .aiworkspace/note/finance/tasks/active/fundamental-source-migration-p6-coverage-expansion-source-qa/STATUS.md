# Phase 6. Coverage Expansion And Source QA Status

## 2026-06-30

- Added `inspect_statement_universe_coverage()` as a DB-backed annual statement source QA summary.
- Added `run_statement_universe_coverage_qa()` service wrapper for the Ingestion UI.
- Added `Statement Universe Coverage QA` card under `Workspace > Ingestion > 수동 복구 / 진단`.
- The QA output groups missing coverage by reason and points broad gaps toward sampled `Statement Coverage Diagnosis`, targeted EDGAR refresh, or shadow rebuild.
- Updated EDGAR financial statement refresh runbook with universe QA procedure.

## Browser QA

- URL: `http://localhost:8525/ingestion`
- Opened `수동 복구 / 진단` and expanded `재무제표 universe coverage QA`.
- Confirmed card title, `EDGAR annual coverage by universe` copy, and no `yfinance financial statements fallback` language.
- Visible page had no `Traceback` or `ImportError` after restarting stale Streamlit port `8525`.
- Screenshot: `.aiworkspace/note/finance/run_artifacts/ingestion_statement_universe_coverage_qa_20260630.png`
