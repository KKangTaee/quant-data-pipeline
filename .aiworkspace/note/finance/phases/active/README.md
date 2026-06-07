# Active Finance Phases

Status: Active
Last Verified: 2026-06-07

이 폴더는 Main phase worktree가 관리하는 phase 기록을 둔다.
현재는 완료된 phase board도 handoff / trace 용도로 남아 있으므로, 이 폴더의 하위 폴더가 모두 현재 active phase라는 뜻은 아니다.

권장 구조:

```text
phases/active/<phase-name>/
  PLAN.md
  DESIGN.md
  TASKS.md
  STATUS.md
  RISKS.md
  INTEGRATION.md
```

완료된 phase는 `phases/done/` closeout summary를 canonical 완료 기록으로 둔다.
active 폴더에 남아 있는 완료 phase board는 과거 task 추적과 handoff 확인 용도다.

## Current Active Phases

| Phase | Status | Notes |
|---|---|---|
| `none` | No active phase | 새 phase는 사용자가 구체적인 scope를 승인한 뒤 연다. |

## Implementation-Complete Boards Retained In Active Folder

| Phase | Status | Notes |
|---|---|---|
| `ui-engine-boundary-foundation` | Implementation complete | Streamlit은 유지하고, `app/services`를 UI-engine boundary로 도입한 phase. |
| `ui-engine-boundary-cleanup` | Complete | Task 6~9 cleanup 완료. boundary lint는 `app.services/app.runtime -> app.web` import hard fail 기준으로 유지. |
| `investability-decision-foundation` | Implementation complete | Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 실전 검토 가능한 decision workflow로 강화한 기준선. |
| `overview-market-intelligence` | Implementation complete / retained board | Overview Market Intelligence 초기 production baseline 이력 board. |
| `overview-market-intelligence-productionization` | Production baseline complete / retained board | Overview refresh, diagnostics, earnings lifecycle, visuals/calendar UX productionization 이력 board. |

## Recently Closed Boards Retained In Active Folder

| Phase | Closeout |
|---|---|
| `phase8-investability-data-evidence-expansion` | [Phase 8 closeout](../done/phase8-investability-data-evidence-expansion.md) |
| `phase9-cost-slippage-liquidity-realism` | [Phase 9 closeout](../done/phase9-cost-slippage-liquidity-realism.md) |
| `phase10-walkforward-oos-regime-validation` | [Phase 10 closeout](../done/phase10-walkforward-oos-regime-validation.md) |
| `phase11-portfolio-construction-risk-controls` | [Phase 11 closeout](../done/phase11-portfolio-construction-risk-controls.md) |
| `phase12-selected-monitoring-recheck-operations` | [Phase 12 closeout](../done/phase12-selected-monitoring-recheck-operations.md) |
| `phase13-hardening-cycle-closeout` | [Phase 13 closeout](../done/phase13-hardening-cycle-closeout.md) |
