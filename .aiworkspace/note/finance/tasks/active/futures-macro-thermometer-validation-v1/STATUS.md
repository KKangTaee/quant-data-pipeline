# Futures Macro Thermometer Validation V1 Status

## 2026-06-02

- Started after user requested historical validation and reliability display for `Overview > Futures Monitor > Macro Thermometer`.
- Classified as focused multi-step implementation task with Overview UI and futures / ETF price read-model scope.
- Existing dirty worktree items observed and left untouched: `finance/.DS_Store`, futures QA screenshots.
- Initial design direction:
  - keep current snapshot logic in `app/services/futures_macro_thermometer.py`;
  - add separate validation service in `app/services/futures_macro_validation.py`;
  - avoid new DB tables or JSONL persistence;
  - widen daily macro backfill from 1y to 5y where supported;
  - surface confidence and historical caveats in the Macro Thermometer tab.
- Implemented:
  - `app/services/futures_macro_thermometer.py` now exposes reusable candle/read-model helpers, separated evidence groups, cautious interpretation copy, and optional validation/confidence attachment.
  - `app/services/futures_macro_validation.py` builds point-in-time historical validation from stored futures daily rows and labeled ETF proxy fallback targets.
  - `app/web/overview_dashboard.py` renders confidence, current scenario sample / hit rate, validation summary, score relationships, threshold sensitivity, and evidence groups inside `Macro Thermometer`.
  - Daily macro refresh now requests `5y / 1d`; `Workspace > Ingestion > 선물 OHLCV 수집` also exposes `2y` and `5y` futures periods.
