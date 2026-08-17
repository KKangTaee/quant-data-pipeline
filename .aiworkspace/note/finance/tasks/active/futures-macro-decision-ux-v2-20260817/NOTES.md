# Futures Macro Decision UX V2 Notes

Last Updated: 2026-08-17

## Confirmed Facts

- Before this task, `run_overview_futures_daily_ohlcv()` gated 5m collection on daily probe
  `status == pending`; it now uses the independent active trade-date resolver.
- `active_futures_session_date()` independently resolves Sunday evening to the Monday trade-date.
- Current stored 5D validation has 120 independent episodes and 325 chronological evaluations.
- Model Brier 0.558212 is worse than unconditional baseline 0.556655, so `NO_EDGE` is a completed
  negative result rather than missing data.
- Shared header bottom alignment plus a four-row fact rail creates the large left-side blank area.

## Decisions

- Keep the negative validation gate visible and make its completed conclusion explicit.
- Do not weaken forecast validation thresholds.
- Remove Next Check from the primary surface and preserve calculation scope under methodology.
- Apply layout changes only to the Futures header variant.

## Implemented Result

- The final 2026-08-17 actual refresh wrote 4,175 five-minute rows even though the same trade date was
  not eligible for completed-daily finalization, returned overall `success`, and the screen promoted it
  to `장중 잠정 관측`.
- When no eligible current observation exists, the hero names the completed date and fallback instead
  of implying that refresh itself stopped at the prior day.
- The stored five-day validation remains `NO_EDGE`: 120 independent episodes, 325 chronological
  evaluations, model Brier 0.558212 versus baseline 0.556655.
- Browser inspection at desktop and 420px verified the primary conclusions, absence of `Next Check`,
  no horizontal page overflow, and no console warnings or errors.
