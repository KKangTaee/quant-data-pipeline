# UI Patterns

Status: Active
Last Updated: 2026-06-29

## Summary

The desired Market Movers surface should feel like a compact market board, not a diagnostic dashboard. Metric cards can remain for trust/status summaries, but the main scan area should be ranking rows, visual magnitude, volume context, and sector breadth.

## Pattern Catalog

### Ranking Intent First

- Seen in: StockAnalysis, MarketWatch / Nasdaq conceptual pattern, Toss / Upbit list-style discovery.
- User problem: users need to pick the kind of mover before reading rows.
- Interaction shape: tabs / segmented control / compact pills with labels like 상승, 하락, 거래량, 이상 거래량, 섹터.
- Fit: starts in 1차 with language reset, then becomes a visual tape/list in 2차.

### Market Board Density

- Seen in: Upbit, Toss, StockAnalysis.
- User problem: metric cards slow down scan speed.
- Interaction shape: compact rows with symbol, name, sector, price / return / volume facts, and color-coded direction.
- Fit: 2차 and 3차.

### Sector Breadth Map

- Seen in: TradingView, Finviz.
- User problem: user needs to know whether movers are isolated or sector-wide.
- Interaction shape: sector heatmap / strip / compact bar with advancers and decliners.
- Fit: 4차.

### Investigation Pane

- Seen in: Seeking Alpha / Koyfin-style research workflows as a pattern, adapted locally.
- User problem: after finding a mover, user needs a manual research start point.
- Interaction shape: selected symbol detail panel with context-only links and metadata status.
- Fit: 5차.

### Trust Strip, Not Ops Dashboard

- Seen in: finance sites separate market content from data footnotes.
- User problem: stale / missing state must be clear without dominating the screen.
- Interaction shape: compact trust strip, empty state, and expandable raw diagnostics.
- Fit: 6차.
