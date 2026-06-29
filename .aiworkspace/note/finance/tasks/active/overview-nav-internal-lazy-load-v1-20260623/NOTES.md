# Overview Nav Internal Lazy Load V1 Notes

## Findings

- `st.pills` exists in the local Streamlit runtime (`1.57.0`) and can provide internal single-selection pill UI.
- The previous custom nav did not set `target="_blank"`, but it still used anchors. That made the control behave as navigation, not an internal tab widget.
- Initial Overview load enters `Market Context` by default and immediately executes `load_overview_macro_context_cockpit`.
- `load_overview_macro_context_cockpit` loads multiple read models before the user can interact with the page.
- User supplied the final visual direction as text tabs with a thin baseline and red active underline, not boxed pills.
