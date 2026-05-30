# Overview Market Intelligence Design

## Product Shape

`Workspace > Overview`는 네 개 탭으로 나눈다.

| Tab | Responsibility |
| --- | --- |
| `Market Movers` | S&P 500 / Coverage 1000 / 2000에서 daily / weekly / monthly / yearly 상승률 Top N을 보여준다. |
| `Sector / Industry` | 월별 sector 또는 industry leadership을 보여준다. |
| `Events` | DB에 저장된 FOMC / earnings calendar row를 보여주고 ingestion wrapper 기반 refresh를 제공한다. |
| `Candidate Ops` | 기존 Overview의 candidate Top 3, funnel, next actions, recent activity를 보존한다. |

## Data Flow

```text
finance_meta.nyse_asset_profile
finance_price.nyse_price_history
  -> app/services/overview_market_intelligence.py
  -> app/web/overview_dashboard_helpers.py
  -> app/web/overview_dashboard.py
```

Calendar 흐름은 아래를 따른다.

```text
free official/vendor source
  -> app/jobs ingestion wrapper
  -> finance_meta.market_event_calendar
  -> loader/service
  -> Overview Events tab
```

## Service Contract

`app/services/overview_market_intelligence.py` owns:

- effective market date selection
- managed universe loading
- period return calculation
- market movers ranking
- sector / industry aggregation
- market event calendar read model
- coverage and warning payload

The service must stay Streamlit-free.

## Period Semantics

First build uses eligible daily trading rows.

| Period | Meaning |
| --- | --- |
| `daily` | latest effective market date vs previous eligible trading date |
| `weekly` | latest effective market date vs five eligible trading sessions prior |
| `monthly` | latest effective market date vs twenty-one eligible trading sessions prior |
| `yearly` | latest effective market date vs roughly one trading year prior |

`1wk` and `1mo` DB timeframes are not required.

## UX Rules

- Show effective market date and latest raw DB date separately.
- Show returnable symbol count and missing count.
- Do not present movers as recommendations.
- Keep candidate operations visible.
- Events tab reads stored DB rows and only refreshes through ingestion job wrappers.
