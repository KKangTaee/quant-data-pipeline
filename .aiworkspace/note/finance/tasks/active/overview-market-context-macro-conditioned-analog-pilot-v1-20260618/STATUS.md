# Status

Status: Complete
Last Updated: 2026-06-18

## Progress

- Opened this task record for the approved 3차-A macro-conditioned historical analog pilot.
- Added failing contract tests for the service payload and renderer before implementation.
- Added `macro_conditioned_analog` as an additive nested read model under the existing historical analog snapshot.
- Implemented GLD price proxy safe-haven / gold context as the only additional macro condition in this 차수.
- Rendered a separate `Macro 조건 포함 pilot` block with used / insufficient / excluded conditions and sample quality.
- Kept broad historical analog rows and controls intact.

## Completed Scope

- `app/services/overview_market_context_analog.py`
- `app/web/overview_ui_components.py`
- `app/web/overview_dashboard_helpers.py`
- `tests/test_service_contracts.py`
- task docs and durable handoff pointers.

## Actual Macro Conditions Used

- Sector ETF vs SPY relative strength: required broad analog condition.
- GLD price proxy safe-haven / gold context: additional pilot condition.

## Excluded Or Insufficient Conditions

- Stored futures daily OHLCV rate / safe-haven context: explicitly deferred to a possible 3차-B.
- 2Y / 10Y FRED rates: disabled; no new collection or render-time fetch.
- Events / sentiment historical conditioning: disabled for this pilot.
- GLD itself can show `조건 부족` if stored GLD price coverage is missing or too short.
