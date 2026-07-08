# Phase 6. Coverage Expansion And Source QA Plan

## 이걸 하는 이유?

EDGAR annual refresh is now the primary financial statement path, but operators still need to know whether SP500 / Top1000 / Top2000 / Nasdaq workflows have enough annual statement shadow coverage and why the missing symbols are missing.

This phase adds DB-backed source QA that explains coverage gaps without using yfinance financial statements as a fallback.

## Scope

- Universe-level annual statement coverage QA for `SP500`, `TOP1000`, `TOP2000`, and `NASDAQ`.
- Missing reason grouping from stored raw/shadow/profile/universe evidence.
- Ingestion diagnostics service wrapper and UI card.
- Focused tests and Browser QA.

## Done Conditions

- Universe QA reports shadow-ready count, raw-present count, not-ready count, coverage percent, and reason groups.
- Reason groups separate raw-present/shadow-missing, stale/no recent annual period, non-US / foreign-form expectation, profile/universe metadata gaps, and EDGAR unavailable / CIK mapping candidates.
- The path is DB-backed and does not live-probe EDGAR for broad universes.
- Docs/runbook explain how to use the QA before targeted refresh.

## Out Of Scope

- Paid provider integration.
- SEC live-probing across broad universes.
- yfinance financial statement fallback.
- Table drops or destructive cleanup.
