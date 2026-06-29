# Risks

Status: Completed
Last Verified: 2026-06-08

## Residual Risks

- Reference contextual help now uses page targets only when `streamlit_app.py` configures them. Direct module execution may show a non-clickable fallback caption.
- Direct `/guides` or `/glossary` URL loading can still be affected by Streamlit relative `_stcore` behavior. Normal app navigation and `st.page_link` are the supported route.
- The generated 9차 QA screenshot `backtest-compare-9a-qa.png` remains untracked and should stay unstaged unless explicitly requested.

## Do Not Infer

- This task does not add Reference query deep-linking.
- This task does not change registry, saved setup, provider fetch, live approval, broker order, account sync, or auto rebalance behavior.
