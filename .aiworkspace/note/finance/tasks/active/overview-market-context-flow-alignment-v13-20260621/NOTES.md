# Overview Market Context Flow Alignment V13 Notes

## Decisions

- `pattern_window` controls the similarity window, not the sector leadership source.
- The default historical analog anchor sector should follow the same sector snapshot visible in the top Market Context.
- Sector pressure tiles should use equal sizing; magnitude should be represented by value/color, not tile area.
- Market Context should not teach the user how to read the screen with separate guide labels when the same meaning can be expressed by the data summary itself.

## Discoveries

- `load_overview_market_context_historical_analog()` previously derived `leadership_period` from `pattern_window` and loaded a separate weekly/monthly sector snapshot.
- `build_overview_macro_context_cockpit()` capped sector pressure at 8 rows and `_sector_pressure_map_html()` capped again with `rows[:8]`.
- Provider-style sector labels can create 12 rows if aliases such as `Financials` and `Financial Services` are not normalized before display.
- Local live QA after the change showed the latest visible sector leader as `Consumer Cyclical`; the latest historical analog now uses `Consumer Cyclical` / `XLY`.
- The final live model state had XLY broad analog status `OK`, sample count 81, and current as-of `2026-06-18`. Macro comparison rendered in compact form because broad rows were available.
- Selected as-of remains bounded by the available stored price basis. For example, selected `2026-06-18` can calculate with an effective common price basis of `2026-06-16` when later rows are not available for all required symbols.

## Boundary Notes

- Latest mode now reuses the sector leadership snapshot already visible in the Market Context cockpit.
- Selected as-of mode intentionally loads a selected-date daily sector snapshot so changing the date can change the anchor sector.
- `pattern_window` now changes the similarity rule / historical distribution window, not the source of the leadership sector.
