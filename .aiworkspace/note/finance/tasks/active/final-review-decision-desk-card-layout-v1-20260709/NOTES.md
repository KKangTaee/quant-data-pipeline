# Notes

- This surface is not React. It is rendered by `app/web/backtest_final_review/components.py` via Streamlit `st.markdown` HTML/CSS.
- Keep the outer Decision Desk shadow because it gives useful depth without making every inner card compete.
- Avoid changing Final Review scoring, gate, persistence, provider fetch, or Portfolio Monitoring handoff logic.
- The route card now keeps a fallback `route_detail`, but normal rendering uses `featured_candidate` structured fields.
