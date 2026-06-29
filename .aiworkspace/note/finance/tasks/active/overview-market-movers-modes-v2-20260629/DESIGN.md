# Overview Market Movers Modes V2 Design

## Ownership

- UI entrypoint: `app/web/overview/market_movers.py`
- UI helper/rendering: `app/web/overview/market_movers_helpers.py`
- Snapshot/read model service: `app/services/overview/market_movers.py`
- Why It Moved service boundary: `app/services/overview/why_it_moved.py`
- Contract tests: `tests/test_service_contracts.py`

## Read Model Direction

The existing `build_market_movers_snapshot` payload keeps legacy `rows` and `volume_rows` for compatibility. V2 adds `mover_views` as an ordered dict:

- `top_gainers`: symbol rows sorted by `Return %` descending.
- `top_losers`: symbol rows filtered to negative returns and sorted ascending.
- `volume_leaders`: existing share/dollar volume ranking.
- `unusual_volume`: current volume divided by prior 10-day average stored EOD volume.
- `sector_leaders`: existing sector leadership row shape, sorted by market-cap weighted return.

Every view carries `label`, `kind`, `status`, `sort_basis`, `empty_reason`, `rows`, and a context-only `boundary_note`.

## UI Direction

- Add an exploration mode selector beside Coverage / Period / Sector / Top N.
- Reflect the selected mode in the command strip `Mode` item.
- Render the selected mode table and matching chart as the primary first-screen flow.
- Keep all mode tables available in a collapsed detail expander so existing Return/Volume functionality remains discoverable.
- Keep Coverage Diagnostics as a secondary expander, not the main UX.
- Keep Why It Moved as a manual investigation start point and avoid automatic cause/recommendation semantics.

## Data Boundary

Unusual Volume uses only stored DB EOD rows from `finance_price.nyse_price_history`. It does not call yfinance/provider/news/SEC from the UI and does not write new persistence artifacts.
