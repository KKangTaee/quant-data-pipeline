# Notes

## 2026-07-05 - Intake

User wants Practical Validation improvement to begin with V1 taxonomy analysis and roadmap refinement, not immediate implementation.

Main user goals:

- Practical Validation should be stage 2 evidence validation, not Final Review decision.
- Final Review selected-route judgment should not dominate the stage 2 screen.
- Current diagnostics / modules / audit boards / board map feel repetitive.
- `Monitoring Baseline` and `Tax / Account Scope` look more like stage 3 or Operations reference.
- React custom components should be used for high-interaction cards, not for a full app rewrite.

## Code Findings

Current file sizes:

- `app/web/backtest_practical_validation/page.py`: 2,586 lines.
- `app/web/backtest_practical_validation/components.py`: 500 lines.
- `source_summary.py`, `replay_panel.py`, `provider_actions.py`, `evidence_boards.py`: re-export only.
- `app/services/backtest_practical_validation_diagnostics.py`: 1,727 lines.
- `app/services/backtest_practical_validation_modules.py`: 744 lines.

Current data flow:

```text
source
  -> build_practical_validation_result
  -> 12 diagnostics
  -> data / construction / risk contribution / role-weight / realism / efficacy audits
  -> selected-route preflight
  -> validation module plan
  -> board map
  -> final review gate
```
## Stage Boundary Finding

The code already partially supports the desired boundary:

- `monitoring_baseline` is a `REFERENCE` module with `stage_owner="selected_dashboard"`.
- `tax_account_scope` is a `REFERENCE` module with `stage_owner="final_review"`.

The UI should make that distinction more visible by moving these out of the main 2단계 gate presentation.

## Selected-route Preflight Finding

`build_practical_validation_selected_route_preflight()` builds an investability evidence packet and runs Final Review selected-route policy before the user enters Final Review.

This is useful as a deterministic safety check, but the UI should not present it as the Final Review decision itself.

Recommended language:

- Good: `Final Review 준비 상태`
- Good: `선정 저장을 막을 명확한 근거 공백`
- Avoid: `Selected-route Gate` as the main stage-2 headline
- Avoid: `select_allowed` as a user-facing final decision state

## UI Duplication Finding

The current page shows:

- Final Review Gate
- Fix Queue
- validation modules
- board map
- diagnostics summary
- audit detail boards
- provider coverage
- look-through board
- robustness board
- raw diagnostics
- raw JSON

Most of this is valuable, but the first-read hierarchy should be reduced to:

```text
Gate Summary
Fix Queue
Core Evidence Workbench
Provider Actions
Save / Final Review Handoff
Technical Details
```

## 2026-07-05 - V1 Implementation Note

V1 adds `app/services/backtest_practical_validation_workspace.py`.

The service is intentionally UI-neutral and Streamlit-free. It consumes a Practical Validation result dict and returns:

- `gate_summary`
- `fix_queue`
- `core_evidence_groups`
- `conditional_evidence_groups`
- `downstream_reference_groups`
- `technical_details`

This keeps the existing validation module plan intact while giving V2-V4 a stable screen-oriented contract.

## 2026-07-05 - V2 Implementation Note

V2 changes user-facing stage boundary language:

- `selected_route_preflight` module label becomes `Final Review Readiness Preview`.
- The board previously labeled `Final Review Gate` becomes `Final Review Readiness Preview`.
- Gate wording now says the blocker is an evidence gap in Final Review readiness, not an early selected-route decision.

The blocker semantics remain unchanged: deterministic evidence gaps still block Final Review movement.

## 2026-07-05 - V3 Implementation Note

V3 attaches the workspace read model to every built Practical Validation result:

```python
result["practical_validation_workspace"] = build_practical_validation_workspace(result)
```

This keeps legacy result keys intact while allowing V4 page work to consume a single grouped contract.

## 2026-07-05 - V4 Implementation Note

V4 changes the visible Practical Validation page flow:

1. `후보 / 검증 프로필 확인`
2. `실전 검증 실행`
3. `2차 검증 결론 / Fix Queue`
4. `근거 Workbench`
5. `저장 / Final Review 이동`

The first-read section now consumes `practical_validation_workspace`. Existing module boards, raw diagnostics, and technical connection maps remain available inside collapsed details.

## 2026-07-05 - V5 Implementation Note

V5 adds `app/web/components/practical_validation_fix_queue` as a focused React component.

Design boundary:

- React renders only the Fix Queue, review count, and core evidence group read surface.
- Python still owns validation execution, gate calculation, registry writes, save / move controls, and Final Review handoff.
- `page.py` checks `is_practical_validation_fix_queue_available()` and falls back to the existing Streamlit cards when the frontend build is absent.

This keeps the React pass product-visible without turning the whole Practical Validation page into a second app.

## 2026-07-05 - V6 Implementation Note

V6 moves the Flow 3 first-read surface into `app/web/backtest_practical_validation/workspace_panel.py`.

Moved ownership:

- gate fix guidance
- Fix Queue display row builder
- core / conditional / downstream workspace group rendering
- React Fix Queue availability check and render call
- Streamlit fallback for the same surface

`page.py` still orchestrates the five flows, session state, source selection, replay execution, save / move controls, and technical detail expanders. This keeps the split behavior-preserving and avoids turning V6 into a broad mechanical rewrite.
