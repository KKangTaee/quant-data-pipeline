# Risks

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Market movers look like recommendations | High | Frame them as market context and keep candidate promotion separate. |
| Event calendar implies trade timing | Medium | Keep it read-only with source/confidence labels. |
| Existing candidate Overview value is lost | Medium | Preserve current dashboard under `Candidate Ops`. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Sparse latest price date creates false "today" rankings | High | Select effective market date by usable row count and non-null prices. |
| Large price table query becomes slow | Medium | Use targeted date selection and indexed joins, not broad CTE scans. |
| Coverage 2000 has missing price rows | Medium | Show returnable count and missing-count diagnostics. |
| Sector / industry fields are stale or incomplete | Medium | Display unknown groups separately and keep source date visible. |
| Earnings API source has licensing/rate-limit constraints | High | Choose provider before implementation and persist fetched rows. |
| UI directly fetches external data | High | Enforce ingestion -> DB -> loader/service -> UI boundary. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| Earnings provider not selected | Determines schema, API key handling, and redistribution constraints | Decide between Alpha Vantage, FMP, Finnhub, Nasdaq-derived source, or another provider. |
| Effective market date threshold | Controls freshness vs coverage tradeoff | Pick default threshold: selected universe limit, fixed 1000, or configurable. |
| Weighting method for group leadership | Equal-weight and market-cap-weighted answer different questions | Show both in first table if space allows. |
| Coverage 2000 naming | Could be an Overview-only control or a global managed universe | Decide during implementation planning. |
