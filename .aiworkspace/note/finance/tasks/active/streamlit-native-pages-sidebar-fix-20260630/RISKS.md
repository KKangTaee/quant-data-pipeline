# Risks

- Direct `/backtest` behavior was checked in Browser QA after removing the tracked `app/web/pages/` package. No native sidebar or `Page not found` text remained in the verified run.
- The fix intentionally removes native `pages/` discovery. Future user-facing pages should be registered through `streamlit_app.py` and should not recreate `app/web/pages/`.
