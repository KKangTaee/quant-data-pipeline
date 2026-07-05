# Overview Market Movers Sector V4 Status

## 2026-06-29

- Scope aligned to 4차 only: sector / heatmap / breadth context.
- RED tests added for snapshot-level `sector_breadth` and UI heatmap workflow source contract.
- RED confirmed: tests failed because `sector_breadth` and UI `render_breadth_heatmap_summary` wiring were missing.
- Implementation added full sector breadth model, heatmap tiles, and fallback detail table.
- GREEN confirmed for new targeted tests and broader Market Movers contract fallback.

## Next

- Final verification completed with the documented unittest fallback because pytest is not installed in the local uv environment.
- Browser QA completed on `localhost:8525` for S&P 500 Daily, S&P 500 Weekly, NASDAQ coverage, and 390px narrow viewport.
- Screenshot captured at `.aiworkspace/note/finance/run_artifacts/overview-market-movers-sector-v4-qa.png`.
- Stage intended source/test/task docs/root logs only and commit 4차.

## 2026-07-05 Follow-up

- Adjusted the sector breadth lane layout from 2 columns to a 4-column desktop grid with a 3-column intermediate breakpoint and 1-column mobile fallback.
- Changed sector lane bars to always grow left-to-right; negative lanes are distinguished by danger/red tone instead of a centered zero split.
- Confirmed the current detailed `섹터 breadth 상세 표` is still a Streamlit expander outside the sector HTML component. Folding it into the same visual unit is feasible, but a true React treatment requires a separate migration of this sector map from markdown HTML to a React component.
