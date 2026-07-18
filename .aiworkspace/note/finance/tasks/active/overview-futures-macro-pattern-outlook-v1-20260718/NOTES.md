# Futures Macro Pattern Outlook V1 Notes

## Confirmed Decisions

- Futures Macro is a short-horizon macro radar, not a long-horizon economic-cycle replacement.
- Primary result: overall risk regime transition.
- Supporting result: equity risk, rates, dollar, safe-haven, and commodity / inflation families.
- Observation windows: 1D, 5D, 20D.
- Published outlook horizons: 5D and 20D.
- UI design follows the Market Context economic-cycle hierarchy: hero, horizons, path, evidence, ribbon, asset pathways, method disclosure.
- Existing today evidence remains visible and source / freshness caveats remain explicit.

## Local Audit Facts

- Actual stored daily futures coverage reached 17 symbols and about 5.4 years on 2026-07-18.
- Current legacy validation produced 1,175 validation dates.
- 915 dates were grouped as `혼재된 매크로 흐름`; that group had no directional target family or forward hit metrics.
- Historical replay built only 1D standardized moves; its 3D / 5D / 20D / 60D features were unset.
- Current UI rendered recent 1D / 1W / 1M flow as separate tabs and equal cards.

## Boundary Notes

- Cross-asset co-movement supports contextual attribution, not proven causality.
- Continuous futures include roll / maturity behavior and must retain visible caveats.
- Dedicated policy futures curves may provide longer-horizon expectations, but they are not part of this V1 source contract.

## React V2 Decisions

- The readable map downsamples the 60D path to `20D 전 / 5D 전 / 현재` anchors. The approved empirical follow-up removed fixed categorical endpoints: selected 5D / 20D now adds the historical-analog stepwise median standardized movement to the current coordinate, with one terminal q25~q75 arrival range. It remains a conditional reference path, not an absolute state, price target, or actual future path.
- The terminal range is an axis-aligned rectangle because x/y q25~q75 are computed separately; it is not a joint covariance ellipse or a full-path corridor.
- Direction arrows use fixed 9 SVG units on inset mid-line segments, while current/terminal circles remain radius 10/8, so marker scale cannot hide either endpoint.
- Scale ownership is independent of the selected card: both available horizons' median paths and terminal ranges define one visible-data bound, while hidden intermediate q25/q75 points are excluded. Therefore `관측만 / 5D / 20D` changes forecast content without moving observed anchors.
- Current observation cards do not accept or render probability rows. `UNAVAILABLE` future horizons show the reason and no fabricated percentage.
- The V1 `RecentFlowSection.tsx` and `HistoricalValidationPanel.tsx` were removed after reference count reached zero outside their own files.
- The horizon probability cards remain the primary numeric forecast surface. The path map reuses the same rows, status, edge label, episode count, and status reason rather than calculating a second forecast.

## Actual QA Facts

- Read-only snapshot as of `2026-07-17`: `mixed` regime, `transition_attempt`.
- 5D: 120 independent episodes, Brier `0.7181676141` vs baseline `0.7155593658`, `PROVISIONAL`, direction edge not distinct.
- 20D: 42 independent episodes, Brier `0.6585791797` vs baseline `0.6936063270`, `PROVISIONAL`, direction edge not distinct.
- Runtime before optimization was 21.791s uncached. Profiling found 13,722 pandas-heavy path-stat calls; vectorizing the same as-of formulas reduced uncached runtime to 4.963s and cached reload to 0.031s.
- Browser QA found desktop and 420px layouts free of horizontal clipping; the actual payload had no unavailable horizon, while source contracts cover unavailable probability suppression.
- Empirical-path actual QA retained `PROVISIONAL` for both horizons: 5D median error `0.905672` vs baseline `0.888603`, coverage `0.307692`; 20D median error `1.061827` vs baseline `0.942778`, coverage `0.304348`; both used 6 evaluated folds.
- The actual 5D path contains 5 forecast points and the 20D path contains 20; their terminal coordinates and SVG polylines differ. Browser QA also confirmed `관측만` removes every forecast visual and 420px has no horizontal overflow.
- Readability QA confirmed exactly one step-5/step-20 terminal range per selected horizon, no circle/label overlap, preserved 5D `38/5/23/34%` and 20D `43/10/21/26%` probability rows, and zero browser console errors.
- Stable-coordinate QA measured identical observed anchor SVG tuples across all three states: `(456.8966, 175.9529)`, `(306.1657, 130.9592)`, `(193.1737, 206.1591)`. The 5D and 20D forecast polylines and terminal coordinates remained distinct.
