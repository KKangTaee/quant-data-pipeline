# Recommendation

## Answer

Yes. S&P 500 and high-quality company earnings should be first-class Events calendar coverage. They should not be mixed into a generic "latest movers only" earnings set.

The Events tab should evolve into a market background calendar with three visible lanes of coverage:

1. Official macro and central bank events.
2. Corporate earnings and issuer events, clearly labeled as official or provider-estimated.
3. Market structure events such as holidays, options expiration, and index rebalances.

## Collection Priority

### First

- FOMC meetings, statements, minutes, SEP meetings, and major Fed calendar items.
- BLS: CPI, PPI, Employment Situation, JOLTS, ECI.
- BEA: GDP and Personal Income and Outlays/PCE.
- Census: retail sales, durable goods, housing, construction, trade.
- ISM Manufacturing and Services PMI.
- Treasury auctions and quarterly refunding context.
- NYSE/Nasdaq holidays and early closes.
- Options expiration and quarterly expiration/witching dates.
- S&P 500, Nasdaq-100, portfolio/watchlist, and major market-cap earnings.

### Next

- Weekly jobless claims.
- University of Michigan sentiment and Conference Board consumer confidence.
- EIA weekly petroleum and major energy inventory releases.
- Dividends, splits, IPOs, and other scheduled corporate actions.

### Later

- Investor days, conferences, M&A, global central banks, and global macro calendars.

## Data Model Guidance

Before adding many event families, the read model should expose these normalized fields:

- `event_family`: macro, central_bank, earnings, corporate_action, market_structure, fixed_income.
- `event_subtype`: CPI, PPI, FOMC, earnings, dividend, opex, index_rebalance, etc.
- `event_datetime_utc` plus `display_timezone`, or at least `event_date` plus `event_time_label`.
- `universe_scope`: S&P500, Nasdaq100, portfolio, watchlist, latest_movers, all_us, official_macro.
- `source_authority`: official, provider_estimate, issuer_confirmed, cross_checked, not_confirmed.
- `freshness_status`: current, stale, unknown.
- `evidence_url`, `collected_at`, `confidence`, and raw payload pointer.

## Product Boundary

Events should remain a market background and investigation aid. Even when event density is high, the UI should avoid signal words such as buy, sell, validation pass/fail, alert, trigger, or action.
