# Phase 5. Ingestion Workflow Cleanup Status

## 2026-06-30

- Reordered `Workspace > Ingestion` operational refresh cards so `EDGAR annual 재무제표 갱신` is the first financial statement refresh path.
- Renamed weekly broad fundamentals / factors to `Legacy broad yfinance fundamentals / factors`.
- Preserved existing action IDs and run metadata compatibility while changing the visible workflow language.
- Added statement refresh interpretation summary for coverage, freshness, failed count, row count, and next action.
- Added EDGAR financial statement refresh runbook.

## Browser QA

- URL: `http://localhost:8525/ingestion`
- `EDGAR annual 재무제표 갱신` appeared before `Legacy broad yfinance fundamentals / factors`.
- Expanded panels exposed `primary financial statement refresh` and `not the canonical financial statement source` source-boundary language.
- Visible page had no `Traceback` or `ImportError`.
- Screenshot: `.aiworkspace/note/finance/run_artifacts/ingestion_edgar_statement_primary_20260630.png`
