# Phase 5. Ingestion Workflow Cleanup Risks

- The UI relabels the existing `extended_statement_refresh` action rather than creating a new action; this preserves compatibility but means logs still use the internal historical job id.
- The broad yfinance package remains installed and usable for other non-financial-statement paths; this phase only legacy-labels the financial statement canonical path.
