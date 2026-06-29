# Overview Market Movers Detail V3 Status

## 2026-06-29

- Scope aligned to 3차 only: selected-symbol detail pane and Why It Moved integration.
- RED tests added for relative volume context in the read model, selected detail panel model, and UI workflow source contract.
- RED confirmed: tests failed because relative volume movement fields and `_market_mover_detail_panel_model` were missing.
- Implementation added detail panel model, peer context, metadata status strip rendering, metadata clue tabs, and selected-symbol-only compact metadata button.
- GREEN confirmed for the new targeted tests.

## Next

- Final verification completed with the documented pytest fallback because pytest is not installed in the local uv environment.
- Browser QA completed on `localhost:8525` for S&P 500 Daily, S&P 500 Weekly, NASDAQ coverage, and a narrow viewport.
- Screenshot captured at `.aiworkspace/note/finance/run_artifacts/overview-market-movers-detail-v3-qa.png`.
- Stage intended source/test/task docs/root logs only and commit 3차.
