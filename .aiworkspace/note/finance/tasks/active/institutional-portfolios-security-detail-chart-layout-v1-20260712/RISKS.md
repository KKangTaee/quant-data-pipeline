# Institutional Portfolios Security Detail Chart Layout V1 Risks

## Remaining Risks

- This task improves the existing custom SVG chart; it does not introduce a full TradingView-compatible engine.
- Stored price DB coverage still determines whether chart points are available.
- Browser QA could visually capture the selected-security overview and chart row; the holder-list row was confirmed by DOM because the in-app browser reported a nonstandard page scroll height for the embedded Streamlit component.
- The holder list remains latest-filing based. True holding-duration / multi-quarter holding period metrics are outside this task.
- Follow-up Browser QA on direct `/institutional-portfolios` URL logged Streamlit's route fallback message once, while the page still rendered the intended Institutional Portfolios view and chart interactions. This is not caused by the chart component change.
