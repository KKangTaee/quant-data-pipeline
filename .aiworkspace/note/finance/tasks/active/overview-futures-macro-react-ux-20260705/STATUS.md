# Overview Futures Macro React UX Status

## 2026-07-05

- Scope accepted: proceed on `sub-dev` with staged implementation / QA / commit units.
- Phase 1 status: complete. Futures Macro tab entry now loads the current macro snapshot with `include_validation=False`; historical validation is loaded only by the explicit `과거 점검 불러오기` action and stored in Streamlit session state.
- Phase 1 QA complete: focused RED/GREEN unittest, Overview contract class, `py_compile`, `git diff --check`, service timing smoke, and Browser QA for lazy load / on-demand load / reload reset.
- Phase 2 status: complete. Added the `futures_macro_workbench` Streamlit custom component, Python wrapper, payload contract, and React workbench for command strip, macro brief, score chips, 1W flow, validation state, and evidence drawer. Python still owns DB reads, validation calculation, refresh actions, cache clearing, and reruns.
- Phase 2 QA complete: React package install/build, focused RED/GREEN contract tests, full Overview contract class, `py_compile`, `git diff --check`, snapshot payload smoke, and Browser QA visual render screenshot. Browser automation could not prove iframe button click dispatch to Python; event parsing is covered by unit contract and this remains a Phase 3/QA follow-up risk.
- Next: Phase 3 1W / 1M reading-flow expansion. Do not add DB materialization before the Phase 5 cache/materialization decision.
