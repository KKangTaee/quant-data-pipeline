# Active Finance Tasks

Status: Active
Last Verified: 2026-06-07

이 폴더는 현재 실행 중인 task 기록과, 아직 archive / done 이동을 하지 않은 retained task 기록을 함께 둔다.

현재 상태를 볼 때는 이 폴더의 모든 하위 폴더를 literal active work로 해석하지 않는다.
현재 작업은 [STATUS_MANIFEST.md](./STATUS_MANIFEST.md), 아래 `Current Active Tasks`, [Roadmap](../../docs/ROADMAP.md)을 우선 확인한다.

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
| none | - | 현재 새 active task는 없다. 최신 완료 task는 아래 retained record를 확인한다. |

## Recent Completed / Retained Current Work

| Task | Status | Notes |
|---|---|---|
| `runtime-backtest-real-money-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8B. `app/runtime/backtest.py`의 real-money / guardrail / benchmark / deployment readiness helper family를 `app/runtime/backtest_real_money.py`로 이동하고 public facade import를 유지한 기록이다. |
| `runtime-backtest-risk-on-momentum-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8A. `app/runtime/backtest.py`의 Risk-On Momentum 5D runtime slice를 `app/runtime/backtest_risk_on_momentum.py`로 이동하고 public facade import를 유지한 기록이다. |
| `streamlit-ingestion-console-split-20260607` | Completed record | 7차 대형 Streamlit 파일 분해 7A. `streamlit_app.py`를 Finance Console shell로 낮추고 `Workspace > Ingestion` render/state/job UI를 `app/web/ingestion_console.py`로 분리한 기록이다. |
| `overview-ingestion-action-boundary-20260607` | Completed record | 6차 수집 / 조회 경계 정리. Overview bounded refresh를 `app/jobs/overview_actions.py` action facade로 모으고, Overview UI의 직접 ingestion / automation / run-history import를 제거한 기록이다. |
| `code-boundary-refactor-audit-20260607` | Completed record | 5차 코드 구조 감사 / 리팩토링 기준선. UI / service / runtime / jobs / finance layer 경계, 대형 파일, 다음 refactor 우선순위를 정리한 기록이다. |
| `post-merge-verification-handoff-20260607` | Completed record | 4차 검증 및 handoff. 1차~3차 결과 검증과 다음 작업자 read order / remaining decisions를 정리한 기록이다. |
| `post-merge-active-state-cleanup-20260607` | Completed record | 3차 active task / phase 상태 정리. 대량 이동 없이 manifest / README / roadmap 기준으로 current state를 정리한 기록이다. |
| `post-merge-boundary-docs-alignment-20260607` | Completed record | 2차 구조 / 경계 문서 정리. UI / service / runtime / loader / DB / storage boundary를 durable docs에 맞춘 기록이다. |
| `post-merge-docs-alignment-20260607` | Completed record | 1차 post-merge docs alignment. 현재 제품 흐름 / 완료된 merged work / active 상태를 정리한 기록이다. |

## Retained Work Records

- 이 폴더에는 완료된 과거 task가 다수 남아 있다.
- 상세 구현 근거, 실행 로그, QA 결과를 찾을 때는 관련 task 폴더의 `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`를 확인한다.
- 2026-06-07 기준 177개 task folder가 retained record로 남아 있다. 대량 이동 / archive migration은 별도 승인된 migration task에서 처리한다.
