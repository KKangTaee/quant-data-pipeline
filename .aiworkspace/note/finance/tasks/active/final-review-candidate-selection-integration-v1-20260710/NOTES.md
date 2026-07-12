# Notes

- The change is presentation-only in `app/web/backtest_final_review/page.py`.
- `build_final_review_candidate_board()` remains the read model source for candidate priority, review queue, and detail rows.
- The moved selector does not change score, gate, save readiness, registry writes, provider fetches, or Portfolio Monitoring handoff rules.
- The investment report remains the React-rendered section; the candidate queue / selector remains Streamlit/Python.
