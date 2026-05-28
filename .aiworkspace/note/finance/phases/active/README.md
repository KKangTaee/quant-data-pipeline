# Active Finance Phases

Status: Active
Last Verified: 2026-05-28

이 폴더는 Main phase worktree가 관리하는 active phase 기록을 둔다.

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

현재 문서 체계 재구성 중에는 기존 `phases/phase*/` 문서를 바로 삭제하지 않는다.
3차 마이그레이션에서 필요한 요약만 남기고 정리한다.

## Current Active Phases

| Phase | Status | Notes |
|---|---|---|
| `ui-engine-boundary-foundation` | Implementation complete | Streamlit은 유지하고, `app/services`를 UI-engine boundary로 도입한 phase. audit, Single Backtest, Compare / Weighted / Saved Replay, Practical Validation handoff, Final Review / Selected Dashboard evidence read model, runtime package boundary 완료. |
| `ui-engine-boundary-cleanup` | Complete | Task 6~9 cleanup 완료. boundary lint는 `app.services/app.runtime -> app.web` import hard fail 기준으로 유지. |
| `investability-decision-foundation` | Active | Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 실전 검토 가능한 decision workflow로 강화하기 위한 저장 / gate / 데이터 수집 / task 순서 기준선. |
