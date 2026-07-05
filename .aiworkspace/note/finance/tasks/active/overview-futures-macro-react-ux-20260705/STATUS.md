# Overview Futures Macro React UX Status

## 2026-07-05

- Scope accepted: proceed on `sub-dev` with staged implementation / QA / commit units.
- Phase 1 status: complete. Futures Macro tab entry now loads the current macro snapshot with `include_validation=False`; historical validation is loaded only by the explicit `과거 점검 불러오기` action and stored in Streamlit session state.
- Phase 1 QA complete: focused RED/GREEN unittest, Overview contract class, `py_compile`, `git diff --check`, service timing smoke, and Browser QA for lazy load / on-demand load / reload reset.
- Phase 2 status: complete. Added the `futures_macro_workbench` Streamlit custom component, Python wrapper, payload contract, and React workbench for command strip, macro brief, score chips, 1W flow, validation state, and evidence drawer. Python still owns DB reads, validation calculation, refresh actions, cache clearing, and reruns.
- Phase 2 QA complete: React package install/build, focused RED/GREEN contract tests, full Overview contract class, `py_compile`, `git diff --check`, snapshot payload smoke, and Browser QA visual render screenshot. Browser automation could not prove iframe button click dispatch to Python; event parsing is covered by unit contract and this remains a Phase 3/QA follow-up risk.
- Phase 3 status: complete. Futures Macro service now keeps `weekly_context` for compatibility and adds `flow_context.periods` for `1W` / `1M` reading flow, with 1W based on `5D %` and 1M based on `20D %`. React payload and workbench render period tabs while Python continues to own DB reads, refresh, validation, and raw tables.
- Phase 3 QA complete: RED/GREEN focused tests, FuturesMacroThermometer contract class, OverviewAutomation contract class, `py_compile`, React `npm run build`, snapshot payload smoke, and `git diff --check` passed. In-app Browser tab APIs timed out during Phase 3, so no new Browser screenshot was captured.
- Phase 4 status: complete. Mixed top-level interpretation still remains `혼재된 매크로 흐름`, but the service now distinguishes richer `sub_scenario` / `regime_hint` / `mixed_reason` cases for rate-easing growth weakness, dollar-pressure risk-off candidates, commodity weakness / demand slowdown candidates, risk-on plus safe-haven transition zones, and low-signal watch states.
- Phase 4 QA complete: RED/GREEN focused subtype tests, FuturesMacroThermometer contract class, OverviewAutomation contract class, `py_compile`, and `git diff --check` passed. The existing in-app Browser tab API timeout remains, so no new Browser screenshot was captured for this phase.
- Next: Phase 5 validation cache/materialization decision. Do not add DB materialization until process cache vs compact persisted summary is compared explicitly.
