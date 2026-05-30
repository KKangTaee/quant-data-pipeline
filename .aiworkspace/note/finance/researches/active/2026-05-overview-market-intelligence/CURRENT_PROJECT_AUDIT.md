# Current Project Audit

## Snapshot

`Workspace > Overview` is currently a durable operations dashboard. It reads candidate registries, pre-live rows, portfolio proposals, saved portfolios, and backtest run history, then highlights review-priority candidates instead of broad market conditions.

The requested redesign adds a new market-intelligence role:

- top rising US stocks from managed coverage universes
- sector / industry leadership over the current monthly window
- market event calendar for FOMC and major earnings

Feasibility is split. Top movers and sector / industry leadership can be computed from the existing MySQL-backed price and asset-profile data. Event calendar support needs a new source boundary because there is no current market-event table or loader.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | The app is an evidence-first quant workspace, not live trading or order automation. |
| Architecture | `.aiworkspace/note/finance/docs/architecture/README.md` | UI must read data through ingestion, DB, loaders, runtime/service, then Streamlit. |
| Data flow | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` | Price, profile, provider, macro data are already DB-backed; UI should not directly fetch remote providers. |
| Overview UI | `app/web/overview_dashboard.py` | Current Overview renders KPIs, candidate Top 3, funnel, next actions, activity feed, and system snapshot. |
| Overview helper | `app/web/overview_dashboard_helpers.py` | Current Overview snapshot only aggregates registries and run history, not market-wide price/profile data. |
| Price loader | `finance/loaders/price.py` | DB-backed daily price history and latest price loaders already exist. |
| Universe/profile helpers | `finance/data/asset_profile.py`, `app/web/backtest_common.py` | `US Statement Coverage 1000` already uses US stock, profile filter, and market-cap ordering. |
| DB diagnosis | local MySQL, 2026-05-28 workspace check | `nyse_asset_profile` has 4,441 US active stock profiles, 4,316 with market cap, and `nyse_price_history` has daily data from 2006-02-07 to 2026-05-19. |

## Surface Classification

| Surface | User-facing / internal / mixed | Notes |
| --- | --- | --- |
| `Workspace > Overview` | User-facing | Current default landing page. Best place for a compact market-intelligence entry point. |
| `Workspace > Ingestion` | Mixed / ops | Should remain the place to refresh OHLCV, asset profiles, and future market-event snapshots. |
| `Backtest > Backtest Analysis` | User-facing research workflow | Existing candidate discovery should remain separate from broad market movers. |
| `Operations > Selected Portfolio Dashboard` | User-facing monitoring | Read-only selected-portfolio monitoring, not a source for broad market movers. |

## Strengths

- Existing DB has enough US stock profile coverage for Coverage 1000 and probably Coverage 2000.
- Existing daily price table is sufficient to compute daily, weekly, and monthly returns by selecting effective trading dates from daily rows.
- Existing asset profile already contains `sector`, `industry`, `market_cap`, `country`, `status`, and `is_spac`, which are enough for a first sector / industry leadership view.
- The product already has a clear ingestion -> DB -> loader/service -> UI boundary, which fits this feature well.
- Existing Overview is modular enough to add tabs without touching the top-level Streamlit navigation.

## Weaknesses

- No current `overview_market_intelligence` service or loader contract.
- `nyse_price_history` has no `1wk` or `1mo` rows, so weekly/monthly views should be derived from daily history instead of relying on timeframe-specific rows.
- Latest raw daily date is 2026-05-19, but that date has only one null price row. The effective market date for usable coverage is 2026-05-18. The UI must show this exact as-of date and staleness warning.
- Coverage 1000 returnable counts were 740-741 out of 1000 and Coverage 2000 returnable counts were 1460-1465 out of 2000 for the tested windows. Missing price rows need a coverage badge and diagnostics.
- `long_name` is incomplete for some symbols, so UI should tolerate missing names.
- No local source currently stores future FOMC or earnings events.
- Earnings dates are vendor data. A stable implementation needs a provider choice, API key handling, caching, and terms-of-use review.

## Product Boundaries

- Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
- Do not turn research output into roadmap commitment without user approval.
- Do not fetch provider / earnings / macro sources directly from Overview render code.
- Treat top movers as market scan context, not investment advice or automatic candidate promotion.

## Audit Conclusion

The first two requested features are feasible with a narrow implementation:

1. Add a Streamlit-free market intelligence service that computes effective as-of dates, coverage health, top stock movers, and sector / industry leadership from DB-backed daily prices and asset profiles.
2. Render that service in `Workspace > Overview` as tabs while keeping the existing candidate-priority view available.

The calendar feature is feasible in two levels:

1. FOMC calendar: feasible immediately from Federal Reserve official calendar data, ideally persisted as local static/source rows or a small DB-backed event snapshot.
2. Earnings calendar: feasible only after choosing a provider/API and adding ingestion plus persistence. It should not be implemented as live scraping inside Overview.
