# Notes

- Root cause: `app/web/streamlit_app.py` used explicit `st.navigation(..., position="top")`, but `app/web/pages/backtest.py` still triggered Streamlit's legacy native multipage discovery. On cold/direct `/backtest` load, Streamlit could render the native sidebar before the intended Finance Console shell.
- Keeping the Backtest shell importable outside `pages/` preserves the existing `render_backtest_tab()` implementation while removing the native sidebar trigger. The tracked `app/web/pages/` package is removed entirely so a fresh checkout does not create a native pages directory.
