# Notes

- The strategy selector and lower strategy-specific form switching stay Streamlit-owned.
- React should not be introduced for the general strategy selector/detail switching in this task.
- Price Freshness Preflight remains a narrow React component because it already owns a specific visual pre-run check.
- Portfolio Mix Builder strategy multiselect and annual / quarterly variant controls also stay Streamlit-owned; strict preset copy is shared through `backtest_common.py`.
