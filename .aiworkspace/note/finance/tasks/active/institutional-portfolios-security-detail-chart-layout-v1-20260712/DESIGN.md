# Institutional Portfolios Security Detail Chart Layout V1 Design

## Current Shape

- `SecurityDetail` summary row contains ticker / issuer and three stat cards.
- body is 2-column: `ip-chart-panel` and `ip-holder-panel`.
- `InteractiveSecurityChart` uses SVG chart + axis labels + native range input.
- holder list renders `holders.slice(0, 24)`, so the UI cannot scroll through the full payload.

## Target Shape

1. `ip-security-overview`
   - left: selected security identity / metadata.
   - right: `ip-security-context-card` titled with selected portfolio context.
   - copy explains that portfolio weight and reported value are for the currently selected 13F manager portfolio, not a market-wide metric.
2. `ip-security-chart-row`
   - full-width chart panel.
   - chart toolbar keeps period and line/candle controls.
   - chart body adds OHLC strip, price scale, volume bars, time scale, and navigator window.
3. `ip-holder-panel ip-holder-panel--scroll`
   - full-width lower panel.
   - header shows total holders and visible loaded count.
   - `.ip-holder-scroll` owns max-height and vertical overflow.

## Boundary

The UI still renders existing `SelectedSecurity`, `ChartPoint`, and holder payloads. No Python read model or ingestion code changes are required.
