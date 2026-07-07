# Risks

- Browser QA confirmed the panel layout and action buttons render in Streamlit.
- Extended Statement Refresh can still fail for symbols with no EDGAR/provider coverage; the panel will show the job result but does not replace Data Trust investigation.
- The panel triggers data repair jobs and then reruns the page; it does not automatically submit the backtest form after repair.
