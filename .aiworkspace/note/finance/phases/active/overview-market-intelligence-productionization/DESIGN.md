# Overview Market Intelligence Productionization Design

## Current Baseline

1차 구현은 아래를 제공한다.

- DB-backed Market Movers: S&P 500 / Top1000 / Top2000, daily / weekly / monthly / yearly
- Sector / Industry leadership: monthly equal-weight and market-cap-weighted ranking
- Events: FOMC official rows and bounded yfinance earnings prototype rows
- Refresh buttons: Market Snapshot, FOMC, Earnings
- Runbook: manual refresh order and failure handling

## Target Product Shape

정식화 후 Overview는 세 가지 질문에 안정적으로 답해야 한다.

| 질문 | 필요한 상태 |
|---|---|
| 지금 무엇이 강한가? | Market Movers / Sector ranking이 최신 snapshot과 stale status를 함께 보여준다. |
| 왜 일부 row가 비어 있는가? | Coverage diagnostics가 missing reason, provider status, recommended action을 보여준다. |
| 앞으로 어떤 이벤트가 중요한가? | Events가 FOMC / earnings를 source confidence와 stale estimate lifecycle까지 보여준다. |

## Data Flow

```text
Free source / DB source
  -> ingestion job wrapper
  -> finance_meta / finance_price tables
  -> app.services.overview_market_intelligence
  -> app.web.overview_dashboard
```

Rules:

- Overview render path never fetches remote providers.
- Heavy collection belongs in Ingestion or scheduled jobs, not regular UI render.
- Data rows must retain source, confidence, collected_at, and diagnostics evidence.

## Event Lifecycle Model

`market_event_calendar` currently stores normalized rows with a stable `event_key`.

Productionization should add lifecycle semantics without breaking existing rows:

- active row: currently valid event estimate / official event
- superseded estimate: older provider estimate replaced by newer date
- stale row: collected too long ago for provider-estimated earnings
- official row: event from official source or verified source

The first implementation can model lifecycle in service/read-model metadata before adding schema columns. Schema changes should be added only if the UI and cleanup behavior need persisted state.

## UX Direction

- Keep the UI dense and operational, not a marketing dashboard.
- Use status chips, concise captions, and diagnostics expanders.
- Add visual ranking only when it helps comparison: heatmap/treemap for sector/industry or movers.
- Do not make events look like buy/sell recommendations.

## Verification Shape

- service contract tests for read model and event lifecycle interpretation
- collector tests for bounded earnings behavior and cleanup
- Browser smoke for Overview Events / Market Movers
- DB smoke for small manual earnings symbols
- UI-engine boundary check
