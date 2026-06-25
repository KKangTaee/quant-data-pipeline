# Overview Legacy Dashboard Removal Audit

## Remaining Direct Dependencies

Current direct import paths:

| File | Direct dependency | Why it remains |
|---|---|---|
| `app/web/overview/futures_macro_helpers.py` | `legacy_dashboard` | futures macro fragment / panel bridge |
| `app/web/overview/market_movers_helpers.py` | `legacy_dashboard` | controls, auto-refresh, snapshot load, refresh bar, snapshot panel |
| `app/web/overview_dashboard.py` | `legacy_dashboard` | compatibility re-export of legacy private helpers |
| `tests/test_service_contracts.py` | `overview_dashboard` private imports | tests still import old private helper names from wrapper |

## Completed Extractions

| Step | Extracted |
|---|---|
| V18 | `app/web/overview/session_helpers.py` now owns market session dataclass, NYSE calendar helpers, market session banner model, Market Context session payload, and snapshot status model helpers. `app/web/overview/page.py` no longer imports `legacy_dashboard`. |
| V19 | `app/web/overview/market_context_helpers.py` now owns Market Context header, refresh reflection, cockpit model load bridge, refresh status panel, refresh result summary, and refresh action buttons. It calls `app.jobs.overview_actions` and `app.web.overview_dashboard_helpers` directly instead of `legacy_dashboard`. |
| V20 | `app/web/overview/events_helpers.py` now owns Events toolbar, event snapshot context loading, event calendar frame transforms, summary/source item models, agenda/quality sections, chart model, and calendar month grid rendering. It calls Overview action and helper modules directly instead of `legacy_dashboard`. |
| V21 | `app/web/overview/sentiment_helpers.py` now owns Sentiment controls, job result rendering, snapshot loading bridge, analysis panel, 6-step reading flow, status cards, driver cards, learning cards, next checks, and trend/component charts. It calls Overview action and helper modules directly instead of `legacy_dashboard`. |

## Removal Phases

| Step | Target |
|---|---|
| V18 | Move market session/banner helpers to `session_helpers.py` and remove page dependency |
| V19 | Move Market Context refresh helpers into `market_context_helpers.py` |
| V20 | Move Events helper body into `events_helpers.py` |
| V21 | Move Sentiment helper body into `sentiment_helpers.py` |
| V22 | Move Market Movers helper body into `market_movers_helpers.py` |
| V23 | Move Futures Macro / remaining futures helper body into `futures_macro_helpers.py` |
| V24 | Update `overview_dashboard.py`, tests, docs, then delete `legacy_dashboard.py` |

## Migration Targets

- `app/web/overview/session_helpers.py`: market session dataclass, NYSE calendar helpers, market session banner model, session payload, snapshot status helpers.
- `app/web/overview/market_context_helpers.py`: Market Context refresh plan/result/bar and historical analog repair controls.
- `app/web/overview/events_helpers.py`: event refresh toolbar, calendar row transforms, agenda/quality/source/summary helpers, event chart/grid helpers.
- `app/web/overview/sentiment_helpers.py`: sentiment panel, steps, driver groups, learning cards, charts, tone helpers.
- `app/web/overview/market_movers_helpers.py`: controls, snapshot load, browser auto refresh, refresh bars, charts, Why It Moved metadata helpers.
- `app/web/overview/futures_macro_helpers.py`: futures macro panel, refresh controls, score/validation/evidence helpers, retained futures chart model helpers still covered by tests.
- `app/web/overview_dashboard.py`: should export `render_overview_dashboard` only unless a small compatibility export is explicitly retained.

## Deletion Guard

- Add and maintain tests that prevent active Overview modules and helper modules from importing `app.web.overview.legacy_dashboard`.
- V24 should assert that `app/web/overview/legacy_dashboard.py` no longer exists.
- Do not replace the file with another monolithic renamed legacy file.
