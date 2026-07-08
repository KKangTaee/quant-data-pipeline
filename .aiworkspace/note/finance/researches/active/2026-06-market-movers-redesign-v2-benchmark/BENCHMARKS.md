# Market Movers Redesign V2 Benchmarks

Status: Active
Last Updated: 2026-06-29

## Research Question

How should `Workspace > Overview > Market Movers` move from a prototype-like Streamlit panel to a finance-site-style market mover surface while remaining DB-backed and context-only?

## Benchmark Matrix

| Product | Category | Relevant Workflow | Evidence Label | Applicability |
| --- | --- | --- | --- | --- |
| Toss Securities | Retail brokerage UI | Korean user-language stock discovery / screener | Observed partial | Prefer direct Korean market terms over internal nouns. |
| Upbit | Crypto exchange | Fast market list / market movement scan | Observed partial | Dense market-list scanning pattern; avoid recommendation framing. |
| StockAnalysis | Public market data site | Gainers / losers / active market movers | Observed | Separate ranking modes by user intent. |
| TradingView | Charting / heatmap platform | Sector heatmap and performance scan | Observed | Use heatmap / sector grouping as context, not signal. |
| Finviz | Screener / heatmap platform | Map-based sector breadth scan | Observed partial | Compact heatmap density; avoid decorative card grids. |

## Cross-Product Patterns

- Users first choose a ranking intent: gainers, losers, active volume, unusual volume, or sector movement.
- Market data pages use compact rows, tabs, heatmaps, and scan-oriented grouping instead of large metric cards for every fact.
- The data-status layer exists, but it is secondary to the market list and chart / sector context.
- Heatmaps communicate breadth and concentration when grouped by sector and colored by return direction.

## Boundary For This Project

- Keep Market Movers context-only.
- Do not add external UI fetches, provider calls, broker actions, trade signals, or validation gates.
- The right implementation path is DB snapshot / service read model / UI renderer, not direct site-style live scraping.
