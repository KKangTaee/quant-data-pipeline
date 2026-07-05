# Status

Status: Complete
Last Updated: 2026-07-05

## Current State

V8 closeout is complete. V1-V8 were developed, QA'd, and committed as separate implementation units.

Completed in this task:

- Read project instructions, finance docs, Backtest UI flow docs, and Practical Validation core files.
- Classified the request as Backtest UI / Practical Validation roadmap work.
- Created this active task bundle.
- Drafted Practical Validation taxonomy and V1-V8 implementation direction.
- Updated active task pointers and root handoff logs.
- Ran documentation verification checks.
- Added `app/services/backtest_practical_validation_workspace.py`.
- Added a service contract test for Practical Validation workspace grouping.
- Verified V1 with targeted unittest, service import boundary check, py_compile, and diff check.
- Reworded selected-route preflight user-facing module / board language as Final Review readiness preview.
- Preserved blocker behavior for deterministic evidence gaps.
- Verified V2 with targeted module, board, preflight, py_compile, and service contract checks.
- Attached `practical_validation_workspace` to `build_practical_validation_result()` output.
- Verified V3 with diagnostics result contract, import boundary, py_compile, and diff check.
- Reworked the Practical Validation page first-read flow from 7 steps to 5 flows.
- Added workspace overview rendering for `2차 검증 결론 / Fix Queue` and core evidence groups.
- Kept detailed module / board evidence under collapsed technical details.
- Verified V4 with source contract tests, py_compile, Browser QA, and screenshot.
- Added a focused read-only React component for the Practical Validation Fix Queue and core evidence groups.
- Connected the component behind an availability check while preserving the existing Streamlit fallback.
- Verified V5 with component build, focused contracts, py_compile, Browser QA, and screenshot.
- Split the Flow 3 first-read surface into `app/web/backtest_practical_validation/workspace_panel.py`.
- Kept `page.py` responsible for orchestration while the workspace panel owns Fix Queue, core evidence group rendering, and the React component integration.
- Verified V6 with RED/GREEN boundary tests, py_compile, contract tests, Browser QA, and screenshot.
- Added a shared Practical Validation status display helper.
- Normalized user-facing route statuses such as `BLOCKED_FOR_FINAL_REVIEW`, `READY_WITH_REVIEW`, and `READY_FOR_FINAL_REVIEW` into `BLOCKED`, `REVIEW`, and `PASS`.
- Verified V7 with RED/GREEN status tests, py_compile, contract tests, Browser QA, and screenshot.
- Aligned durable roadmap, flow docs, project map, script structure map, root handoff logs, and this active task bundle with the implemented V1-V8 structure.
- Verified V8 with final py_compile, focused unittest suites, diff check, and Browser QA.

## Current Conclusion

The Practical Validation problem is not a lack of validation logic. The main issue is that diagnostics, audits, modules, board map, and selected-route preflight are all visible as peer concepts.

V1 introduced a screen-oriented workspace read model so later UI changes can consume grouped evidence instead of recomputing screen hierarchy from every lower-level service.

V2 keeps selected-route preflight as a safety check, but no longer presents it as the Final Review decision itself in module / board labels.

V3 makes the workspace read model part of the built Practical Validation result, so UI work can read grouped evidence directly from one result key.

V4 makes that contract visible in the page: the first-read path is now candidate/profile, practical replay, second-stage conclusion/Fix Queue, evidence workbench, and Final Review handoff.

V5 makes the most decision-heavy part of that first-read path feel like one product surface: Fix Queue, review count, and core evidence groups render together in a read-only React component, while Python still owns validation execution, gate calculation, persistence, and handoff.

V6 starts the physical split at the highest-value ownership seam: Flow 3's first-read workspace panel moved out of `page.py`. This avoids a giant mechanical refactor while making the React Fix Queue and Streamlit fallback live beside their workspace read-model rendering.

V7 removes the most visible raw route leakage from the first-read Practical Validation surface. Raw route IDs remain available in detailed JSON/technical context, but the primary UI now speaks the standard validation status language.

V8 closes the task by making durable docs match the code ownership: `page.py` orchestrates the 5-flow screen, `workspace_panel.py` owns Flow 3, the React Fix Queue component is read-only, and Python still owns validation execution, gate calculation, persistence, provider actions, and handoff.

## Next Action

No immediate follow-up is required for this task.

Possible future tasks, if approved separately:

1. Split remaining Flow 1 / Flow 2 / Flow 4 / Flow 5 renderers out of `page.py`.
2. Clean up the unrelated policy-signal contract drift around `second_stage_review_rows`.
3. Decide whether any raw route IDs should be hidden from additional technical tables while preserving JSON auditability.

## Verification State

V1-V3 changed service/test layers; V4 changed visible Streamlit UI.

Completed checks:

- RED: workspace grouping contract test failed with missing service module before implementation.
- GREEN: the same test passed after implementing `build_practical_validation_workspace`.
- service import boundary test
- py_compile for Practical Validation service files
- `PracticalValidationServiceContractTests`
- `git diff --check`
- V2 RED/GREEN selected-route readiness preview contract test
- targeted board / selected-route preflight tests
- V2 py_compile and diff check
- V3 RED/GREEN result workspace contract test
- V3 diagnostics service contract tests
- V3 py_compile and diff check
- V4 RED/GREEN page source contract test
- V4 Backtest refactor boundary tests and Practical Validation queue source test
- V4 py_compile and diff check
- V4 Browser QA against `http://localhost:8515/backtest`
- V4 screenshot: `backtest-practical-validation-v4-five-flow-final-qa.png`
- V5 RED/GREEN React component contract test
- V5 frontend build with Vite
- V5 Practical Validation service contract suite
- V5 py_compile and diff check
- V5 Browser QA against `http://localhost:8525/backtest`
- V5 screenshot: `backtest-practical-validation-v5-react-fix-queue-card-qa.png`
- V6 RED/GREEN workspace panel ownership boundary test
- V6 React component contract update for new panel ownership
- V6 py_compile and diff check
- V6 Backtest refactor boundary tests and Practical Validation service contract suite
- V6 Browser QA against `http://localhost:8525/backtest`
- V6 screenshot: `backtest-practical-validation-v6-workspace-panel-qa.png`
- V7 RED/GREEN status display normalization test
- V7 py_compile and diff check
- V7 Backtest refactor boundary tests and Practical Validation service contract suite
- V7 Browser QA against `http://localhost:8525/backtest`
- V7 screenshot: `backtest-practical-validation-v7-status-display-qa.png`
- V8 durable docs alignment
- V8 py_compile for Practical Validation page, workspace panel, status display, React component wrapper, workspace service, diagnostics service
- V8 focused Backtest refactor boundary tests
- V8 Practical Validation service contract tests plus React component UI-only contract
- V8 git diff check
- V8 Browser QA against `http://localhost:8525/backtest`
- V8 screenshot: `backtest-practical-validation-v8-final-qa.png`

Browser QA was not run for V1 because no Streamlit UI changed.
Browser QA was not run for V2 because no Streamlit UI changed.
Browser QA was not run for V3 because no Streamlit UI changed.
Browser QA was run for V4.
Browser QA was run for V5.
Browser QA was run for V6.
Browser QA was run for V7.
Browser QA was run for V8.
