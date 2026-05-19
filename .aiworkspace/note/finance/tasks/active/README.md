# Active Finance Tasks

Status: Active
Last Verified: 2026-05-19

이 폴더는 현재 실행 중인 task 기록을 둔다.

권장 구조:

```text
tasks/active/<task-name>/
  PLAN.md
  DESIGN.md
  STATUS.md
  NOTES.md
  RUNS.md
  RISKS.md
```

작은 단일 파일 수정에는 task 문서를 만들지 않아도 된다.
여러 파일을 건드리거나, 조사 / 설계 / QA가 필요한 작업은 active task로 관리한다.

## Current Active Tasks

| Task | Status | Notes |
|---|---|---|
| `ui-engine-boundary-audit` | Complete | `ui-engine-boundary-foundation` phase의 첫 audit task. 다음 구현 후보는 `backtest-execution-service-boundary`. |
| `backtest-execution-service-boundary` | Complete | Single Strategy runtime dispatch와 error normalization을 `app/services/backtest_execution.py`로 분리 완료. |
