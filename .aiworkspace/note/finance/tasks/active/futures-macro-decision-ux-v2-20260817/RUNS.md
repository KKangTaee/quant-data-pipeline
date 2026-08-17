# Futures Macro Decision UX V2 Runs

Last Updated: 2026-08-17

| Run | Result |
|---|---|
| Baseline focused pytest: refresh + short horizon | 37 passed, 3 existing edgar deprecation warnings |
| Refresh routing red/green test | Sunday evening future-session case failed before the change, then passed with 5m collection independent of daily finalization |
| Narrative and validation copy red/green tests | Instructional detail, ambiguous `NO_EDGE`, compact hero, and removed `Next Check` expectations failed first, then passed |
| Production React build | Vite build passed; 180 modules transformed |
| Actual DB refresh at 2026-08-17 active trade date | Daily finalization `future_session_not_eligible`; 5m `active_session_refresh` succeeded with 4,175 rows; overall `success`; no failed symbols |
| Actual screen reload after refresh | `장중 잠정 관측`, 2026-08-17 session, completed validation as-of 2026-08-14, and deterministic 1D/5D/20D conclusions rendered |
| Browser QA desktop | Compact hero rendered; `Next Check` absent; console warnings/errors empty |
| Browser QA 420px | Outer 420/420 and component 377/377 client/scroll widths; no horizontal overflow |
| Final focused regression | 119 passed, 15 subtests passed, 3 existing edgar deprecation warnings |
| Python compile | `overview_actions.py` and `futures_macro_helpers.py` passed |
| Final production bundle | Vite build passed; `index-PDv9GCzX.css` and `index-isEXwZqt.js` generated |
| QA screenshot | `futures-macro-decision-ux-v2-qa.png`; generated artifact intentionally left untracked |
