# Benchmarks

Status: Active
Last Updated: 2026-06-08

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Research Question

Which current macro / market-context dashboard patterns should inform future `sub-dev` development for `Workspace > Overview`, `Workspace > Ingestion`, and supporting `Operations` data-health surfaces?

## Selection Criteria

- Prefer official product or documentation pages.
- Prefer patterns that apply to market context, macro indicators, data freshness, calendar events, screeners, heatmaps, or analyst dashboards.
- Exclude live brokerage execution patterns from recommendations because the current finance product boundary is no live approval / broker order / auto rebalance.

## Benchmark Matrix

| Product / Service | Category | Target user | Relevant workflow | Evidence | Applicability |
| --- | --- | --- | --- | --- | --- |
| Koyfin Market Dashboards | Investment research dashboard | Investors / analysts | Curated dashboards for equities, yields, economics, currencies, commodities, credit, and economic calendar context | Claimed / Documented | Strong pattern for `Overview Macro Context Cockpit` and thematic dashboard presets |
| Koyfin My Dashboards | Custom dashboard workspace | Investors / analysts | User-built dashboards with watchlist, table, chart, news, resizable widgets, and linked dashboard groups | Documented | Useful later for custom Overview presets, not first build |
| TradingView Features / Economic Calendar / Macro Maps | Charting, macro, calendar, heatmap platform | Traders / investors | Economic calendar, earnings / dividend calendar, macro maps, heatmaps, chart-adjacent macro context | Documented / Claimed | Strong pattern for calendar quality lanes, macro heatmaps, breadth visuals |
| FRED API and Dashboards | Official macro data source / graphing | Researchers / developers / educators | Series observations API, JSON / CSV / xlsx output, dashboards with saved graphs | Documented | Strong pattern for source-first macro series catalog and PIT / vintage caution |
| OpenBB Workspace | Analyst dashboard / data app layer | Analysts / dev teams | Widget dashboards, folders, refresh actions, data visualization, macro scenario planning | Claimed / Documented | Useful for future API / widgetized surface direction, but heavier than first Streamlit pass |

## Product Notes

### Koyfin Market Dashboards

- Category: market and macro dashboard platform.
- Relevant features: curated dashboards for world equity indices, US sectors, countries, factors, global yields, currencies, commodities, corporate credit, fixed income factors, global yield curves, world economics, and economic calendar context.
- UI / workflow pattern: start from a curated dashboard, then drill into a market theme.
- Data / evidence model: Koyfin states it aggregates and organizes data from multiple sources; its data overview distinguishes live, delayed, and end-of-day data by asset class.
- Strong idea for this project: Overview should have a curated "market pulse" cockpit before deep tabs.
- Idea to avoid: copying broad commercial coverage claims without provider rights or source-quality labels.
- Sources: https://www.koyfin.com/features/market-dashboards/, https://www.koyfin.com/help/data-overview/

### Koyfin My Dashboards

- Category: customizable dashboard workspace.
- Relevant features: dashboards can contain watchlists, charts, news, table templates, historical graph widgets, performance graph widgets, and grouped components.
- UI / workflow pattern: users organize repeated analysis into reusable dashboard layouts.
- Strong idea for this project: later custom Overview presets could group macro, sector, futures, and watchlist context by workflow.
- Fit warning: this is not a `Now` candidate because the current priority is global product clarity, not layout customization.
- Source: https://www.koyfin.com/help/mydashboards-myd/

### TradingView

- Category: charting, calendar, macro, heatmap, screener platform.
- Relevant features: economic and corporate events in one calendar, macro maps, heatmaps, global economic indicators, charts / maps / tables, region and category filtering.
- UI / workflow pattern: event and macro context can sit near charting / market views, but the user still chooses what to inspect.
- Strong idea for this project: turn `Events` and `Sector / Industry` into stronger visual context with impact / quality filters and heatmap-style breadth.
- Idea to avoid: anything that implies trade execution, alerts, or brokerage behavior.
- Sources: https://www.tradingview.com/features/, https://www.tradingview.com/support/solutions/43000759911-economic-calendar-track-all-major-market-events/, https://www.tradingview.com/support/solutions/43000764925-macro-maps-on-tradingview-explore-compare-track/

### FRED

- Category: official macro data / API / graphing.
- Relevant features: FRED / ALFRED API can query economic data by source, release, category, and series; `series/observations` returns data values and supports JSON / xlsx / CSV output and real-time / vintage-related parameters; FRED dashboards let users add saved graphs.
- UI / workflow pattern: macro data should be source-first, series-first, and explicit about observation date, vintage / real-time period, transformation, and frequency.
- Strong idea for this project: build a local macro indicator catalog before expanding macro interpretation.
- Idea to avoid: treating latest macro values as point-in-time validation evidence without release / vintage handling.
- Sources: https://fred.stlouisfed.org/docs/api/fred/overview.html, https://fred.stlouisfed.org/docs/api/fred/series_observations.html, https://fredhelp.stlouisfed.org/fred/account/dashboard-features/add-a-graph-to-a-dashboard/

### OpenBB Workspace

- Category: analyst data visualization workspace.
- Relevant features: dashboard canvas, widgets, refresh data actions, folders, sharing, multi-source data visualization, macro research and scenario planning.
- UI / workflow pattern: analyst workspaces should reduce context switching and make repeated research flows reusable.
- Strong idea for this project: future Overview / Operations could become a widgetized dashboard only after current Streamlit surfaces stabilize.
- Fit warning: too broad for the first `sub-dev` build; use as a platform-direction reference.
- Sources: https://docs.openbb.co/workspace/analysts/dashboards, https://www.openbb.co/products/workspace

## Cross-Product Patterns

- Curated summary first: dashboards open with an opinionated overview before deep exploration.
- Thematic drilldowns: economics, yields, sectors, futures, events, and news are separated but visually connected.
- Source / freshness matters: data platforms distinguish live, delayed, end-of-day, official, provider estimate, or historical data.
- Events are filters and context, not automatic decisions.
- Heatmaps and breadth views help users see distribution, not only top-ranked rows.
- Reusable workspaces / widgets are valuable later, but only after the core workflow is clear.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| No single Overview market pulse | Koyfin curated dashboards, OpenBB analyst dashboards | Add an `Overview Macro Context Cockpit V1` from existing DB-backed read models. |
| Macro indicators lack a local source catalog | FRED source / series model | Document local macro series, cadence, freshness threshold, interpretation, and no-signal boundary. |
| Events are useful but could be more scan-first | TradingView economic calendar | Strengthen event source / validation / importance lanes and next-event summary. |
| Sector / industry leadership is row/chart based, not heatmap-first | TradingView heatmaps / macro maps | Add heatmap / breadth visualization after summary cockpit. |
| Data Health is status-heavy, not action-first | OpenBB refresh actions, current project ingestion boundary | Convert stale / missing / failed rows into guided next refresh actions without direct UI fetch. |
