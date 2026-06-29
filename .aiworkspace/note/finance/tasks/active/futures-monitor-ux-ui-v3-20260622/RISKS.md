# Futures Monitor UX/UI V3 Risks

- Streamlit layout changes can look acceptable in code but cramped in the browser; Browser QA is required.
- Macro wording must avoid sounding like a trading recommendation.
- Adding recent 1-week context should reuse stored 1D futures rows only; no provider fetch during render.
- Existing generated QA screenshots and `.DS_Store` must not be staged.

## Closeout

- Browser QA passed on desktop width with the evidence expander open; generated screenshot is retained only as local QA evidence.
- Streamlit / Altair still expose generic control text such as `Show data`, `Fullscreen`, and multiselect `Clear all`; these are framework controls rather than app copy.
- The current live data in QA was stale, so the screen correctly displayed a Korean stale warning rather than hiding the issue.
- Macro Context remains context-only: the wording says market backdrop / evidence strength / historical consistency, not trade signal or approval.
