# Status

Status: Active
Last Updated: 2026-07-05

## Current State

V6 implementation is complete and ready to commit.

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

## Current Conclusion

The Practical Validation problem is not a lack of validation logic. The main issue is that diagnostics, audits, modules, board map, and selected-route preflight are all visible as peer concepts.

V1 introduced a screen-oriented workspace read model so later UI changes can consume grouped evidence instead of recomputing screen hierarchy from every lower-level service.

V2 keeps selected-route preflight as a safety check, but no longer presents it as the Final Review decision itself in module / board labels.

V3 makes the workspace read model part of the built Practical Validation result, so UI work can read grouped evidence directly from one result key.

V4 makes that contract visible in the page: the first-read path is now candidate/profile, practical replay, second-stage conclusion/Fix Queue, evidence workbench, and Final Review handoff.

V5 makes the most decision-heavy part of that first-read path feel like one product surface: Fix Queue, review count, and core evidence groups render together in a read-only React component, while Python still owns validation execution, gate calculation, persistence, and handoff.

V6 starts the physical split at the highest-value ownership seam: Flow 3's first-read workspace panel moved out of `page.py`. This avoids a giant mechanical refactor while making the React Fix Queue and Streamlit fallback live beside their workspace read-model rendering.

## Next Action

V7 should unify user-facing validation status language across the split renderers:

1. Normalize visible status labels around `PASS / REVIEW / NEEDS_INPUT / BLOCKED / NOT_RUN / NOT_APPLICABLE`.
2. Keep raw route IDs available only in technical/detail surfaces.
3. Preserve existing gate behavior.
4. Add focused tests for status mapping and page/panel ownership.

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

Browser QA was not run for V1 because no Streamlit UI changed.
Browser QA was not run for V2 because no Streamlit UI changed.
Browser QA was not run for V3 because no Streamlit UI changed.
Browser QA was run for V4.
Browser QA was run for V5.
Browser QA was run for V6.
