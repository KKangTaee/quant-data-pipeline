# Risks

Status: Active
Last Updated: 2026-07-05

## Open Risks

### Selected-route preflight wording may still confuse stage boundaries

Risk: Keeping selected-route preflight inside Practical Validation can still feel like Final Review is happening early.

Mitigation: V2 should rename and reposition it as `Final Review readiness preview`, with raw policy rows collapsed.

### React-first implementation would only polish the current repetition

Risk: Building React components before read-model grouping could make the existing taxonomy confusion look nicer without fixing workflow clarity.

Mitigation: V1/V3 should establish grouping contracts before V5 React work.

### Physical split of `page.py` can create churn without product clarity

Risk: Moving render functions into files before deciding ownership can produce mechanical refactor churn.

Mitigation: V4 should first define 5-flow UI ownership, then V6 should split files by that ownership.

### `Tax / account scope` and `Monitoring Baseline` may be policy-relevant later

Risk: Demoting these from stage-2 visual priority could hide useful downstream context.

Mitigation: Keep them in downstream reference / technical detail, not deleted.

### Browser QA is not needed for planning but will be mandatory for UI implementation

Risk: This planning task can close without screenshot, but V4/V5/V6 UI work must include Browser QA and screenshot.

Mitigation: Each implementation version should have its own QA / commit unit.

## Approval Required Before Implementation

V1 implementation started after user approval:

- selected-route preflight should be retained as readiness preview
- `Monitoring Baseline` should move to downstream reference
- `Tax / Account Scope` should move to Final Review reference
- V1 should start with read-model grouping, not visual React work

## 2026-07-05 - V1 Residual Risk

V1 only creates the workspace read-model contract. The Practical Validation page does not consume it yet, so user-visible duplication remains until V4.

V2 should be careful to change language without weakening deterministic blocker behavior for selected-route evidence gaps.

## 2026-07-05 - V2 Residual Risk

The service-level labels now say `Final Review Readiness Preview`, but some existing UI copy in `app/web/backtest_practical_validation/page.py` still says `Final Review Gate`. That visible screen hierarchy is intentionally left for V4, where the page flow changes happen together with Browser QA.

## 2026-07-05 - V3 Residual Risk

`practical_validation_workspace` is now available in result payloads, but the page still renders from older lower-level keys. V4 must switch the first-read hierarchy to the workspace contract without hiding existing technical evidence.

## 2026-07-05 - V4 Residual Risk

The first-read page hierarchy now uses the workspace contract, but the detailed module board still contains legacy table structure inside collapsed technical details. V6 should split ownership after V5 decides which action surfaces need richer components.

Browser QA showed existing Streamlit dataframe serialization warnings in the server log for mixed-type legacy tables. They did not block rendering, and they are outside the V4 flow restructure.

## 2026-07-05 - V5 Residual Risk

V5 introduces another small React component with its own frontend package and build artifacts. This is acceptable for the focused Fix Queue surface, but V6 should avoid multiplying components until `page.py` ownership is physically split.

Browser QA showed known Streamlit relative `_stcore` 404 checks and iframe sandbox warnings. The Practical Validation Fix Queue iframe rendered correctly and the warnings did not block the target view.

`BacktestRuntimeContractTests` has an unrelated policy-signal source contract drift around `second_stage_review_rows`. The V5 targeted tests passed, but the full Backtest runtime contract suite remains blocked by that pre-existing inconsistency until a separate policy-signal cleanup resolves it.
