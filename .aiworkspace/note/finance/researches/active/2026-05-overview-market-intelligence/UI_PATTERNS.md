# UI And Workflow Patterns

## Product Goal

Turn `Workspace > Overview` into a compact market-intelligence entry point while preserving the existing candidate operations dashboard.

## Patterns

| Pattern | Evidence | Applicability |
| --- | --- | --- |
| Market scan tabs | Inferred | Keep the landing page dense and work-focused: `Market Movers`, `Sector / Industry`, `Events`, `Candidate Ops`. |
| Effective as-of badge | Inferred | Show `Effective market date`, `latest DB date`, `coverage`, and `stale days` before rankings. |
| Universe controls | Inferred | Use controls for Coverage 1000 / 2000, period daily / weekly / monthly, and Top N. |
| Sortable ranking table | Inferred | First implementation should prioritize a reliable table over a decorative heatmap. |
| Sector / industry drilldown | Documented | Group rows by sector or industry, then let the user inspect representative top/bottom symbols. |
| Market-cap weighted and equal-weight returns | Inferred | Equal-weight shows breadth; market-cap-weighted shows index-like leadership. Both should be visible. |
| Source/confidence labels for events | Inferred | FOMC can be `official`; earnings can be `vendor`, `estimated`, or `unknown`. |
| Existing candidate ops preserved | Local audit | Current Overview has operational value and should become a tab, not disappear. |

## Recommended Product Shape

First screen:

- `Market Movers` tab selected by default if data is fresh enough, otherwise show stale-data warning and keep `Candidate Ops` usable.
- Compact KPI strip: effective market date, coverage universe, returnable symbols, stale days.
- Ranking table with symbol, name, return %, latest price, sector, industry, market cap, start date, end date.
- Optional small bar chart for Top N returns.

Tabs:

| Tab | Purpose | First version contents |
| --- | --- | --- |
| `Market Movers` | Which covered stocks are moving most now? | Daily / weekly / monthly Top N from Coverage 1000 or 2000. |
| `Sector / Industry` | Which groups are leading this month? | Monthly sector and industry tables with count, equal-weight return, market-cap-weighted return. |
| `Events` | What scheduled market events may affect interpretation? | FOMC rows first, earnings only after provider ingestion is added. |
| `Candidate Ops` | Existing Overview behavior | Current candidate Top 3, funnel, next actions, recent activity. |

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Real-time market dashboard | Current UI should not fetch providers directly | Use DB-backed latest available data and show as-of date. |
| Earnings calendar | Vendor data and API key required | Add ingestion/persistence before UI display. |
| Heatmap | Can become layout-heavy in Streamlit | Ship sortable tables first, add heatmap later if needed. |
