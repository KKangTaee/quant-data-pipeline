# Status

Status: Active
Last Updated: 2026-07-05

## Current State

V3 implementation is complete and ready to commit.

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

## Current Conclusion

The Practical Validation problem is not a lack of validation logic. The main issue is that diagnostics, audits, modules, board map, and selected-route preflight are all visible as peer concepts.

V1 introduced a screen-oriented workspace read model so later UI changes can consume grouped evidence instead of recomputing screen hierarchy from every lower-level service.

V2 keeps selected-route preflight as a safety check, but no longer presents it as the Final Review decision itself in module / board labels.

V3 makes the workspace read model part of the built Practical Validation result, so UI work can read grouped evidence directly from one result key.

## Next Action

V4 should start the visible Practical Validation flow restructure:

1. Use `practical_validation_workspace` in the page.
2. Move Gate Summary / Fix Queue / Core Evidence hierarchy earlier.
3. Keep raw diagnostics and board map under technical details.
4. Run Browser QA because visible Streamlit UI changes begin in V4.

## Verification State

V1-V3 code changed only in service/test layers; no visible UI changed yet.

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

Browser QA was not run for V1 because no Streamlit UI changed.
Browser QA was not run for V2 because no Streamlit UI changed.
Browser QA was not run for V3 because no Streamlit UI changed.
