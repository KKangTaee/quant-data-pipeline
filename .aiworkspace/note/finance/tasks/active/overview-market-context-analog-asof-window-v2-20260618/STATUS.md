# Status

Status: Complete
Last Updated: 2026-06-18

## Progress

- Created 2차 task record after user approval to implement within existing DB / loader / service read model boundaries.
- Confirmed current historical analog source: latest group leadership top sector -> sector ETF proxy -> SPY-relative sector ETF analog.
- Implemented `as_of_date` and `pattern_window` support in historical analog read model.
- Extended group leadership date resolver to use DB price dates at or before selected as-of.
- Added Market Context controls for 기준 시점 and 패턴 기간 while preserving the top cockpit first.
- Kept positive rate / median / best / worst / sample table contract.
- Removed Market Context visible `예측` copy from the next-check section note.
- Browser QA confirmed latest, selected 기준 시점, 20D pattern, and early 기준일 insufficient-data states.

## Current Decision

- As-of replay is possible with existing DB only as bounded replay: current universe / sector metadata + DB prices through selected as-of.
- Full PIT replay is not possible without an approved historical universe / sector metadata storage or read path.

## Completed Scope

- `app/services/overview_market_context_analog.py`
- `app/services/overview_market_intelligence.py`
- `app/services/futures_macro_thermometer.py`
- `app/web/overview_dashboard_helpers.py`
- `app/web/overview_ui_components.py`
- `app/web/overview_dashboard.py`
- `tests/test_service_contracts.py`
- task / roadmap / project-map documentation.
