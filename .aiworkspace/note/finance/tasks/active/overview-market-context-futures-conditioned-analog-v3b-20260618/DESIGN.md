# Design

Status: Complete
Last Updated: 2026-06-18

## Existing Boundary

`app/services/overview_market_context_analog.py` owns the broad analog and the nested `macro_conditioned_analog` pilot payload.
The parent broad result remains unchanged: sector ETF vs SPY relative strength chooses anchor dates, and forward distributions are calculated only from those broad anchors.

`finance/loaders/futures.py::load_futures_ohlcv()` already supports `symbols`, `interval_code`, and `end`, so the service can read stored `finance_price.futures_ohlcv` daily rows through selected as-of without adding schema, provider, or loader code.

## Futures Condition

The added condition is `Rate Pressure futures proxy`.

- Symbols: `ZN=F`, `ZB=F`.
- Source: stored futures daily OHLCV only.
- Window: the same normalized pattern window as the broad analog, 5D / 20D / monthly.
- Bucket: average signed bond futures return is inverted so falling ZN / ZB prices map to rate-pressure-up, rising prices map to rate-pressure-easing, and small movement maps to mixed.
- Anchor selection: only existing broad anchors whose anchor-date futures bucket matches the selected as-of futures bucket remain in the macro-conditioned sample.

## Look-Ahead Guard

- The selected futures frame is loaded with `end=selected_as_of` when selected, otherwise the service uses the broad analog current as-of date.
- Anchor buckets use futures rows at or before each broad anchor date.
- Anchor selection does not use anchor-after futures movement.
- Forward return rows still come from the existing broad analog price matrix and are not mixed into the futures condition.

## Payload / UI

- Existing GLD condition remains in `used_conditions` when available.
- Futures condition is appended to `used_conditions` when coverage is sufficient.
- Futures coverage or bucket gaps go to `insufficient_conditions`.
- `excluded_conditions` keeps FRED rates and events / sentiment disabled, but no longer lists stored futures as deferred once attempted.
- UI renders the existing `Macro 조건 포함 pilot` block and uses each condition label/detail to separate GLD and futures proxy context.

## Tradeoff

This is a futures price proxy, not a full rates curve or exchange-grade continuous contract model.
Keeping it in the existing analog service avoids expanding data/storage boundaries, but it means the condition should remain labeled as a proxy and read alongside the broad sample quality.
