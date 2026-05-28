# Overview Market Intelligence Tasks

## Task List

| Task | Status | Owner | Notes |
| --- | --- | --- | --- |
| Scope Lock | Complete | `sub-dev` | Phase/task docs and first build boundary. |
| Market Data Service | Complete | `sub-dev` | DB-backed movers and group leadership service. |
| Overview Tabs UI | Complete | `sub-dev` | Market Movers, Sector / Industry, Events, Candidate Ops. |
| QA / Docs Sync | Complete | `sub-dev` | Tests, compile, DB smoke, browser smoke, durable docs. |
| S&P 500 Intraday Daily | Complete | `sub-dev` | Current S&P 500 universe, previous-close daily snapshot path, diagnostics. Full provider run can be operated manually. |
| Market Event DB Structure | Complete | `sub-dev` | `finance_meta.market_event_calendar` schema and common UPSERT/read helpers. |
| FOMC Events | Complete | `sub-dev` | Official Fed source collection, ingestion button, DB-backed Events tab display. |
| Earnings Free Source Prototype | Later | future task | yfinance/OpenBB/web parsing decision and ingestion prototype. |

## First Implementation Unit

Active task:

```text
.aiworkspace/note/finance/tasks/active/overview-market-intelligence-first-slice/
.aiworkspace/note/finance/tasks/active/overview-market-intelligence-sp500-intraday/
.aiworkspace/note/finance/tasks/active/overview-market-events-schema/
.aiworkspace/note/finance/tasks/active/overview-fomc-collector/
```

## Dependency Notes

- Market movers do not depend on new ingestion.
- S&P 500 intraday daily movers depend on the S&P 500 universe / intraday snapshot collectors.
- FOMC calendar data now uses `market_event_calendar`; earnings collector remains a later task.
- Overview refresh button in first slice is a DB snapshot reload, not remote collection.
