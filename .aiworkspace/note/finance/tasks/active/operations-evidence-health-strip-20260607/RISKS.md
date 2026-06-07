# Risks

## 2026-06-07

- Provider / holdings / exposure detail evidence can require DB-backed provider context reads. 3차 keeps the Operations Overview strip lightweight and uses persisted selected decision / portfolio setup / run history payloads only.
- The expected local hygiene scripts `scripts/check_ui_engine_boundary.py` and `scripts/check_finance_refinement_hygiene.py` are absent from this worktree, so the 3차 closeout relies on focused unittest, py_compile, diff check, and Browser QA.
- Streamlit local QA still emits `_stcore/host-config` and `_stcore/health` 404 console entries under the `/operations` path. The page content renders, but this remains a local routing noise item rather than a 3차 evidence strip blocker.
