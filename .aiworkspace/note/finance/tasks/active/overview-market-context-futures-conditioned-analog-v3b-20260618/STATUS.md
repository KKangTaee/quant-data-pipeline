# Status

Status: Complete
Last Updated: 2026-06-18

## Progress

- Opened the 3차-B task record for the approved stored-futures conditioned analog pilot extension.
- Confirmed this task stays inside the existing Overview historical analog service/UI boundary.
- Added failing service/UI contract tests before implementation and verified the red state.
- Added stored futures daily OHLCV Rate Pressure proxy conditioning using `ZN=F` / `ZB=F`.
- Kept GLD price proxy as the first extra condition and appended futures only when current/as-of and anchor buckets are computable.
- Rendered GLD and futures conditions as separate rows inside the existing `Macro 조건 포함 pilot` block.
- Preserved broad analog rows, sample quality, sample reduction reason, selected as-of, and pattern window controls.
- Completed compile, full service contract tests, Streamlit run, and Browser QA screenshot.

## Completed Scope

- `app/services/overview_market_context_analog.py`
- `app/web/overview_ui_components.py`
- `app/web/overview_dashboard_helpers.py`
- `tests/test_service_contracts.py`
- Task docs and durable handoff pointers.

## Actual Futures Condition

- Condition: `Rate Pressure futures proxy (ZN=F/ZB=F)`.
- Source: stored `finance_price.futures_ohlcv` daily rows through `finance/loaders/futures.py::load_futures_ohlcv`.
- Window: same pattern window as the broad analog, 5D / 20D / monthly.
- Local Browser QA 20D path: broad sample 69 -> macro-conditioned sample 1, with GLD and Rate Pressure futures proxy both used.

## Not Doing

- No FRED rates, events, sentiment, new provider, new DB schema, new loader, registry/saved write, or render-time provider fetch.
