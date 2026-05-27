# Overview Market Intelligence Tasks

## Task List

| Task | Status | Owner | Notes |
| --- | --- | --- | --- |
| Scope Lock | Complete | `sub-dev` | Phase/task docs and first build boundary. |
| Market Data Service | Complete | `sub-dev` | DB-backed movers and group leadership service. |
| Overview Tabs UI | Complete | `sub-dev` | Market Movers, Sector / Industry, Events, Candidate Ops. |
| QA / Docs Sync | Complete | `sub-dev` | Tests, compile, DB smoke, browser smoke, durable docs. |
| FOMC Events | Later | future task | Official Fed source collection and Events tab display. |
| Earnings Free Source Prototype | Later | future task | yfinance/OpenBB/web parsing decision and ingestion prototype. |

## First Implementation Unit

Active task:

```text
.aiworkspace/note/finance/tasks/active/overview-market-intelligence-first-slice/
```

## Dependency Notes

- Market movers do not depend on new ingestion.
- FOMC and earnings calendar data require a later data/ingestion task.
- Overview refresh button in first slice is a DB snapshot reload, not remote collection.
