# Futures Monitor UX/UI V3 Design

## Current Code Shape

- `app/web/overview_dashboard.py` owns the visible Futures Monitor UI controls, command center, Macro Context panel, Live Futures Charts, and diagnostics disclosure.
- `app/services/futures_market_monitoring.py` builds the 1m live monitor read model from `finance_price.futures_ohlcv`.
- `app/services/futures_macro_thermometer.py` builds daily futures score, scenario, evidence groups, and optional historical validation.
- `app/services/futures_macro_validation.py` attaches historical consistency evidence; this is not a prediction guarantee.
- `finance_price.futures_ohlcv` stores both 1m chart rows and 1D macro rows.

## UI Direction

The first screen should answer, in order:

1. Which futures set am I watching?
2. Is live 1m data fresh enough?
3. What is the current macro read?
4. What did the recent 1-week futures backdrop do?
5. Which evidence supports, weakens, or conflicts with that read?
6. Where can I inspect raw tables if needed?

## Data Direction

No new persistence is needed. The daily macro service already computes `1D %`, `3D %`, `5D %`, `20D %`, `60D %`, standardized moves, score rows, and component rows. V3 should add a compact `weekly_context` read model from existing `5D %` values and a compact `evidence_reading` model from existing evidence groups.

## Boundary

The UI can say "현재 시장 배경은..." or "최근 1주 흐름은..." but must not say "매수", "매도", "승인", "선정", "통과", or any trade / validation gate wording.
