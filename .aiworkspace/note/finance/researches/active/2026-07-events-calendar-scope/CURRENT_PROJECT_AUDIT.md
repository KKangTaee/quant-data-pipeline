# Current Project Audit

## Current Events Coverage

The local Events read model currently supports the `market_event_calendar` table and exposes rows, coverage counts, and warnings through `build_market_events_snapshot()`.

Observed local snapshot on 2026-07-07:

- Total rows: 139.
- Date window: 2026-06-30 to 2027-12-29.
- Event types present: `EARNINGS` 121, `FOMC_MEETING` 12, `MACRO_GDP` 6.
- Source types present: Provider Estimate 121, Official 18.
- Validation states present: Not confirmed 86, Cross-checked 32, Official 18, Estimate only 3.
- Warnings: stale earnings estimates and not-confirmed earnings estimates dominate the quality issues.

## Gap

The current system already has the right boundary: ingestion writes DB rows, Python service builds interpretation-ready read models, and Streamlit/React should render only structured payloads. The gap is not only UI layout. The calendar universe is too narrow for a market event brief.

Missing or incomplete categories:

- Core macro releases beyond GDP, including CPI, PPI, Employment Situation, jobless claims, retail sales, durable goods, housing, trade, PCE, ISM PMI, and sentiment/confidence.
- Fixed income calendar context, especially Treasury auctions and refunding.
- Market structure calendar context, including exchange holidays, early closes, options expiration, and index rebalances.
- S&P 500, Nasdaq-100, portfolio, watchlist, and large-cap earnings as explicit coverage groups.
- Corporate actions and issuer events such as dividends, splits, IPOs, investor days, and M&A, likely as lower-priority or paid-data candidates.

