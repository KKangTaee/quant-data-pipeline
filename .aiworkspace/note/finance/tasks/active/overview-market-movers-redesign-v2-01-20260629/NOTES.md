# Notes

Status: Active
Last Updated: 2026-06-29

## Benchmark Notes

- Toss Securities: official screener page is reachable and exposes the user-facing concept as `주식 골라보기`; dynamic details are app-rendered, so direct label evidence is partial.
- Upbit: official exchange page is reachable and represents a market list / exchange workflow; dynamic market columns are app-rendered.
- StockAnalysis: market mover pages expose `Top Stock Gainers`, `Market Movers`, `Losers`, and `Active` in inspectable HTML.
- TradingView: stock heatmap page exposes `Stock Heatmap`, `performance`, and `sector` language in inspectable HTML.
- Finviz: map page is reachable and remains a useful reference for sector heatmap / breadth scan density.
- MarketWatch / Nasdaq were considered but access from CLI was limited by anti-bot / timeout behavior; keep them as secondary conceptual references, not primary evidence for this task.

## 1차 Product Takeaway

The first user-visible fix is not more metrics. It is to stop making users decode implementation nouns before they can scan movers. The UI should say what market users came to do: see rising names, falling names, active names, unusual volume, and sector context.
