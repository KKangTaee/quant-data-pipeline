# Benchmarks

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Product / Service | Category | Evidence | Relevant pattern |
| --- | --- | --- | --- |
| TradingView Heatmaps | Market overview / visual scan | Documented | Uses heatmap views to identify leaders, laggards, trends, sector grouping, tile size by market cap/volume, color by change/performance/volatility. |
| TradingView Heatmap Widgets | Embeddable market overview | Documented | Stock heatmap is positioned for segmenting global stocks by sector, country, or market cap. ETF heatmap supports performance, dividend yield, volume, and country filters. |
| Federal Reserve FOMC calendar | Official macro event source | Observed | Official FOMC meeting calendar includes 2026 and 2027 meeting dates, statement/minutes links, and Summary of Economic Projections markers. |
| Alpha Vantage Earnings Calendar | Earnings calendar API | Documented | Provides CSV endpoint for upcoming earnings calendar with `horizon` options such as 3 months. Requires API key. |
| Financial Modeling Prep Earnings Calendar | Earnings calendar API | Documented | Provides earnings calendar endpoint for upcoming/past announcements with date, estimated EPS, and actual EPS where available. Requires API plan/key. |
| Nasdaq Earnings Calendar | Public earnings calendar page | Observed | Shows an earnings calendar experience and states expected release lists are derived by an algorithm based on historical reporting dates, with Zacks as data provider. |

## Key Findings

### 1. Broad market overview should be visual and sortable

TradingView treats heatmaps and screeners as complementary: the heatmap gives instant outlier detection, while screeners give detailed filtering. For this Streamlit product, a first pass can use sortable tables and compact bar charts before adding a true heatmap.

### 2. Sector / industry grouping is a first-class scan dimension

TradingView stock heatmaps group stocks by sector and allow drilling into the included symbols. This maps directly to the existing `sector` and `industry` fields in `nyse_asset_profile`.

### 3. Macro events and earnings events have different source quality

FOMC dates have an official source and are stable enough to seed a calendar. Earnings calendars are vendor datasets and can be algorithmic or estimated. The UI must label source and confidence.

### 4. Calendar data should be ingested, not fetched in the UI

Every viable external calendar source is remote and time-sensitive. The current finance architecture requires ingestion and persistence before UI display, so a market event calendar should have a data/job boundary.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| No market scan surface | TradingView heatmaps and screeners | Overview should gain market scan tabs without removing current candidate operations. |
| No sector / industry leadership aggregation | TradingView sector grouping | Add equal-weight and market-cap-weighted group return calculations. |
| No event calendar source model | Fed official calendar, Alpha Vantage/FMP/Nasdaq earnings sources | Add a read-only event model with source/confidence labels before showing earnings dates. |
| No stale-data UX for broad scans | Current DB diagnosis | Overview must show effective market date and row coverage, not imply true same-day freshness. |
