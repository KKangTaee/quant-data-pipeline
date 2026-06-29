# Overview Legacy Dashboard Removal V17-V24 Notes

## 2026-06-25

- V11-V16 made each primary tab entrypoint thin and moved tab-local bridge code into `*_helpers.py`.
- This task goes further: helper modules should stop importing `legacy_dashboard.py`, and the wrapper should stop re-exporting it.
- V18 confirms the top-level Overview page can render its session banner through a dedicated model helper instead of the monolithic legacy dashboard.
- V19 keeps the Market Context screen read-only-by-default: the tab helper owns the refresh UI, while actual collection jobs stay in `app.jobs.overview_actions`.
- V20 keeps Events domain logic tab-local rather than moving it into shared components; the reusable visual pieces remain under `app/web/overview/components/events.py`.
- V21 keeps Sentiment as tab-local UI/model glue because no separate Sentiment component package exists yet; the extraction still removes the monolithic legacy bridge.
- V22 keeps Market Movers job execution and DB read boundaries unchanged; the tab helper now owns the user-facing scan controls, refresh state, ranking visuals, and manual Why It Moved search links without relying on `legacy_dashboard.py`.
- V23 gives futures-related private helper models a new home in `futures_macro_helpers.py`; this keeps the V24 wrapper cleanup mechanical instead of leaving those functions stranded in the legacy file.
- V24 deletes the legacy file rather than renaming it. The remaining `overview_dashboard.py` compatibility surface is explicit and should be trimmed later only if downstream tests/imports stop using those private helper names.
