# Benchmarks

## Official Source Pattern

Official calendars are strongest for government, central bank, exchange, and index events. They should be marked as `official` when collected directly.

- Federal Reserve: FOMC meetings, statements, minutes, SEP-associated meetings, press conferences, and broader Fed calendar items.
- BLS: CPI, PPI, Employment Situation, JOLTS, ECI, productivity, import/export prices, and related labor/inflation releases.
- BEA: GDP, Personal Income and Outlays/PCE, international trade, corporate profits, and related national account releases.
- Census: retail sales, durable goods, housing, construction, manufacturing, wholesale, and trade indicators.
- TreasuryDirect: Treasury auction schedule, announcements, results, and refunding-related calendars.
- ISM: Manufacturing and Services PMI release dates.
- EIA: weekly petroleum and energy inventory schedules.
- NYSE/Nasdaq/SIFMA/FINRA: holidays, early closes, and market session calendars.
- S&P DJI, Nasdaq, FTSE Russell, Cboe/OCC: index rebalances and options expiration calendars.

## Product Calendar Pattern

Market calendar products converge on the same product pattern:

- Economic calendar with country, time, importance, previous, forecast, and actual fields.
- Earnings calendar with symbol, company, report time, EPS/revenue estimate, actual result, and market-cap or universe filter.
- Separate calendars for dividends, splits, IPOs, holidays, and sometimes options/index events.
- Filters by type, date range, region, importance, and watchlist/universe.

This supports the Events tab direction: show schedule density and evidence status, not trading interpretation.

## Corporate Event Provider Pattern

Corporate events are less official before the event date. Nasdaq states its earnings list can be algorithmically derived from historical dates and identifies Zacks as a data provider. Wall Street Horizon positions itself as a corporate event data provider with many event classes. This means earnings and issuer events need source labeling:

- `official`: company IR, SEC filing, exchange/issuer source.
- `provider_estimate`: estimated or vendor-provided future date.
- `cross_checked`: multiple providers agree.
- `not_confirmed`: future date not verified by an official or second source.

