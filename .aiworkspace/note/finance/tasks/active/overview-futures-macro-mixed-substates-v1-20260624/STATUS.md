# Overview Futures Macro Mixed Substates V1 Status

## 2026-06-24

- Task opened after user approved the recommended 1차 improvement only.
- Added RED tests for mixed sub-scenario behavior in `tests/test_service_contracts.py`.
- Implemented fallback-only mixed context classification in `app/services/futures_macro_thermometer.py`.
- Updated the Futures Macro brief model/rendering so `sub_scenario`, `regime_hint`, and `mixed_reason` can appear under the stable top-level scenario.
- Updated durable docs and handoff logs for the new read-model boundary.
- Verification completed: focused service/UI contract tests, py_compile, `git diff --check`, current DB snapshot check, and Browser QA.
- Status: Complete for recommended 1차. 2차 macro 전문성 보강 remains open and would require explicit macro source / ingestion / scoring design.
