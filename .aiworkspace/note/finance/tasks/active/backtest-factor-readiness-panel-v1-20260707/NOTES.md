# Backtest Factor Readiness Panel V1 Notes

## Notes

- The current strict annual form surface shows `Base Universe` copy through Streamlit captions, price freshness through an existing React component, and statement coverage through a separate Streamlit preview.
- The improved first-read target is one readiness panel that answers: selected candidate pool, whether data is runnable, what is blocking or review-worthy, and the next action.
- Single Strategy strict annual factor forms now keep the Streamlit selector/form structure, but replace the price-only issue card with the combined readiness panel so CUK/BK-like cases are framed as either refreshable price lag or likely provider/source gaps.
- Strict annual factor strategies now default to a maximum five-year window and block longer submissions before runtime. This is a UX guardrail for expensive factor ranking, not a statement about long-horizon PIT correctness.
- Portfolio Mix Builder reuses the same readiness panel and window guard for annual strict factor components. Its global shared date inputs stay in place; the guard only blocks execution when a selected concrete component is one of the annual strict factor strategies.
