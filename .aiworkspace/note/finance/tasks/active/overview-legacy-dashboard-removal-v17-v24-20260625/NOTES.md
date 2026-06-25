# Overview Legacy Dashboard Removal V17-V24 Notes

## 2026-06-25

- V11-V16 made each primary tab entrypoint thin and moved tab-local bridge code into `*_helpers.py`.
- This task goes further: helper modules should stop importing `legacy_dashboard.py`, and the wrapper should stop re-exporting it.
- V18 confirms the top-level Overview page can render its session banner through a dedicated model helper instead of the monolithic legacy dashboard.
- V19 keeps the Market Context screen read-only-by-default: the tab helper owns the refresh UI, while actual collection jobs stay in `app.jobs.overview_actions`.
- V20 keeps Events domain logic tab-local rather than moving it into shared components; the reusable visual pieces remain under `app/web/overview/components/events.py`.
- V21 keeps Sentiment as tab-local UI/model glue because no separate Sentiment component package exists yet; the extraction still removes the monolithic legacy bridge.
