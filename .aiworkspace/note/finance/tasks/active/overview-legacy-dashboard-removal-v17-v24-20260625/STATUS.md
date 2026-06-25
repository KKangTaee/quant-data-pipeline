# Overview Legacy Dashboard Removal V17-V24 Status

## 2026-06-25

- Started V17-V24 after the user approved removing `legacy_dashboard.py` in phases.
- V17 audit / guard completed.
  - Added `LEGACY_DASHBOARD_REMOVAL_AUDIT.md`.
  - Added a contract test that locks the V17-V24 target modules and deletion guard.
  - QA passed with focused audit test, py_compile, and Overview contract suite.
- V18 market session/banner helper extraction completed.
  - Added `app/web/overview/session_helpers.py`.
  - Removed the direct `legacy_dashboard` dependency from `app/web/overview/page.py`.
  - Moved Market Context session-basis payload calculation to the new helper.
  - QA passed with focused session tests, py_compile, Overview contract suite, and browser QA.
- V19 Market Context refresh helper extraction completed.
  - Removed the `legacy_dashboard` dependency from `app/web/overview/market_context_helpers.py`.
  - Moved the refresh reflection, refresh bar, result summary, refresh plan panel, and cache clear behavior into the tab helper.
  - Kept the refresh action boundary in `app.jobs.overview_actions`; the helper only coordinates UI state and cache invalidation.
  - QA passed with focused Market Context tests, py_compile, Overview contract suite, and browser QA.
- V20 Events helper extraction completed.
  - Removed the `legacy_dashboard` dependency from `app/web/overview/events_helpers.py`.
  - Moved Events refresh toolbar, snapshot context loading, calendar frame transforms, agenda/quality sections, and month grid rendering into the Events tab helper.
  - Kept collection jobs in `app.jobs.overview_actions` and read-model loading in `app.web.overview_dashboard_helpers`.
  - QA passed with focused Events tests, py_compile, Overview contract suite, and browser QA.
- V21 Sentiment helper extraction completed.
  - Removed the `legacy_dashboard` dependency from `app/web/overview/sentiment_helpers.py`.
  - Moved Sentiment controls, job result rendering, analysis panel, step cards, driver cards, learning cards, status cards, and charts into the Sentiment tab helper.
  - Kept sentiment collection in `app.jobs.overview_actions` and snapshot loading in `app.web.overview_dashboard_helpers`.
  - QA passed with focused Sentiment tests, py_compile, Overview contract suite, and browser QA.
- Next step: V22 Market Movers helper extraction.
