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

- The observed pattern polyline is never connected to a probability-zone center; this prevents a conditional distribution from looking like a single forecast path.
- Current observation cards do not accept or render probability rows. `UNAVAILABLE` future horizons show the reason and no fabricated percentage.
- The V1 `RecentFlowSection.tsx` and `HistoricalValidationPanel.tsx` were removed after reference count reached zero outside their own files.

## Actual QA Facts

- Read-only snapshot as of `2026-07-17`: `mixed` regime, `transition_attempt`.
- 5D: 120 independent episodes, Brier `0.7181676141` vs baseline `0.7155593658`, `PROVISIONAL`, direction edge not distinct.
- 20D: 42 independent episodes, Brier `0.6585791797` vs baseline `0.6936063270`, `PROVISIONAL`, direction edge not distinct.
- Runtime before optimization was 21.791s uncached. Profiling found 13,722 pandas-heavy path-stat calls; vectorizing the same as-of formulas reduced uncached runtime to 4.963s and cached reload to 0.031s.
- Browser QA found desktop and 420px layouts free of horizontal clipping; the actual payload had no unavailable horizon, while source contracts cover unavailable probability suppression.
