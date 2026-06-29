# Overview Market Movers Sector V4 Design

## Ownership

- Snapshot/read model: `app/services/overview/market_movers.py`
- Market Movers UI glue: `app/web/overview/market_movers_helpers.py`
- Visual component: `app/web/overview/components/market_movers.py`
- Contract tests: `tests/test_service_contracts.py`

## Read Model Direction

`build_market_movers_snapshot` now includes `sector_breadth`.

The model is built only from the same returnable rows already loaded for the selected coverage / period. It does not fetch new data and does not write persistence artifacts.

The model includes:

- full sector heatmap rows, independent of the selected `top_n`
- participation / concentration cards
- advancers / decliners
- equal weight, median, and market-cap weighted return
- market-cap share as a size proxy when market cap exists
- top gainer and top loser per sector
- context-only boundary note

## UI Direction

After the selected exploration mode table and chart, Market Movers renders `섹터 / 시장 확산 맥락`.

The section uses:

- compact breadth summary cards
- sector pressure heatmap tiles
- top sector row strip
- `섹터 breadth 상세 표` expander as the narrow-screen / table fallback

Coverage diagnostics and selected-symbol investigation remain below this context so raw diagnostics do not become the main screen.

## Boundary

This is context-only sector breadth. It does not infer future sector rotation, rank buy candidates, connect to Backtest / Practical Validation / Final Review, or produce operations monitoring guidance.
