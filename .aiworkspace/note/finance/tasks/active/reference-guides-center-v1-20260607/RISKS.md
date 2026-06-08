# Risks

- Browser screenshot capture timed out in the in-app Browser during 0차 audit. Implementation QA used in-app Browser DOM verification and supplemental Playwright screenshot capture.
- Reference landing can become too broad. Keep 1차 focused on task cards, journeys, status lookup, records map, and troubleshooting.
- Static guide catalog can drift from docs. Update `BACKTEST_UI_FLOW.md` and root logs after implementation.
- Direct `/guides` navigation on the supplemental Playwright browser logged Streamlit `_stcore` resource 404s briefly, but page content loaded and DOM QA passed. In-app Browser showed current content on the dedicated 8504 server.
