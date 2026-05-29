# Status

- 2026-05-29: Task opened after user approved browser-session gated Overview auto refresh.
- 2026-05-29: Step 1 complete: added `browser_safe` automation profile for S&P 500 daily snapshot only.
- 2026-05-29: Step 2/3 complete: added Overview auto-refresh toggle/status panel and Streamlit fragment heartbeat that calls `browser_safe` while the page is open.
- 2026-05-29: Step 4 complete: browser auto runs now record `execution_mode=browser_auto`, and Data Health displays `Last Auto Run`, `Auto Source`, and `Next Auto Due`.
- 2026-05-29: Added soft-loading UX for browser auto refresh: checking / collecting status and progress indicator inside the Overview auto-refresh panel.
- 2026-05-30: Localized browser auto-refresh status / progress messages and internal skip reasons to Korean.
- 2026-05-30: Replaced expandable loading status/progress with a compact next-refresh timing panel and cadence progress bar.
- 2026-05-30: Integrated browser auto refresh into the Market Movers `Data Refresh` panel, removed the separate top panel, and added browser-side second-by-second countdown/progress updates.
- 2026-05-30: Started Market Movers UI redesign pass 1: replaced repeated badge/card refresh layout with a compact `데이터 갱신` command surface that prioritizes current data status, refresh mode, and actions.
