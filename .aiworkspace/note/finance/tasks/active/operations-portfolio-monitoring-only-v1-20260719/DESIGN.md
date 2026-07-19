# Operations Portfolio Monitoring Only V1 Design

Status: Approved / Written Spec Review Pending
Last Updated: 2026-07-19

## Problem

`Operations Overview`는 Portfolio Monitoring 요약과 system run 상태를 다시 조합한 landing page지만 사용자가 그 화면에서 독립적인 업무를 끝낼 수 없다. `System / Data Health`는 run history, failure CSV, raw log, artifact path, runtime marker를 검사하는 내부 운영 콘솔이며 사용자의 포트폴리오 판단 흐름과 직접 연결되지 않는다.

Portfolio Monitoring React Command Center V1은 이미 포트폴리오 그룹·항목 lifecycle, 공통 기준 가치와 성과, contribution, 개별 상세, 진단, macro/history/calibration을 하나의 제품 화면에서 제공한다. 또한 `Workspace > Ingestion > 실행 기록 / 결과`가 session result, persistent run history, recent logs, failure CSV를 이미 제공한다. 두 Operations 보조 화면은 최신 제품 구조에서 각각 중복 landing과 중복 진단 화면이 됐다.

## Approved Design

1. 상단 `Operations` group에는 `Portfolio Monitoring` 한 페이지만 남긴다.
2. `Operations Overview`와 `System / Data Health`의 Streamlit page 등록, imports, wrapper, page-target 연결을 제거한다.
3. 두 전용 UI 파일과 그 surface만 검증하던 테스트를 제거한다. 대신 Operations navigation이 Portfolio Monitoring만 포함하고 Ingestion 기록 기능이 보존되는 계약을 검증한다.
4. run history, recent logs, failure CSV, artifact 원본은 삭제하지 않는다. 사용자 대체 경로는 기존 `Workspace > Ingestion > 실행 기록 / 결과`다.
5. Portfolio Monitoring에는 run count, raw status table, log viewer, artifact path 같은 진단 UI를 이식하지 않는다.
6. Portfolio Monitoring이 실제 데이터 부족으로 계산할 수 없는 경우에는 기존 workspace/item 상태 표현을 유지한다. 새 안내가 꼭 필요한 경우 기존 React card/pill/copy 계층 안에서 Ingestion 이동 의미만 짧게 표시한다.
7. 현재 제품 문서와 Reference copy에서 `Operations Overview`, `Operations Console`, `System / Data Health`를 사용자-facing destination으로 설명하는 부분을 `Operations > Portfolio Monitoring` 또는 `Workspace > Ingestion > 실행 기록 / 결과`로 정렬한다. 과거 task 기록은 역사 자료이므로 재작성하지 않는다.

## Architecture And Ownership

| Area | Change |
| --- | --- |
| `app/web/streamlit_app.py` | 두 page/import/wrapper를 제거하고 Operations group에 Portfolio Monitoring만 등록한다. |
| `app/web/operations_overview.py` | 전용 summary/read-model/renderer 전체를 삭제한다. |
| `app/web/ops_review.py` | 전용 internal diagnostics renderer 전체를 삭제한다. |
| `app/web/ingestion/*` | 기존 기록·로그·failure 기능을 보존한다. 새 기능은 추가하지 않는다. |
| Portfolio Monitoring Python/React | 기존 제품 UI를 유지한다. 제거 route 참조가 발견될 때만 최소 copy/navigation 정리를 한다. |
| tests | 제거 surface 계약을 삭제하고 navigation 단순화와 Ingestion 기능 보존을 검증한다. |
| durable docs/reference services | 현재 사용자 흐름과 목적지 명칭만 정렬한다. |

## User Flow After Change

```text
Backtest > Final Review
  -> Operations > Portfolio Monitoring
     -> 포트폴리오 선택
     -> 성과·기여도·개별 추적 결과 확인
     -> 필요한 변화와 review context 확인

데이터 수집 또는 실행 실패 확인이 필요한 예외 상황
  -> Workspace > Ingestion
     -> 실행 기록 / 결과
```

Operations를 열었을 때 사용자는 중간 Overview를 거치지 않고 Portfolio Monitoring에서 바로 추적 업무를 시작한다.

## Data And Error Boundary

- DB, registry, saved setup, run history, artifact 저장 계약은 바꾸지 않는다.
- Portfolio Monitoring의 DB-only loader/service 경계와 common-basis 계산을 바꾸지 않는다.
- System/Data Health 전용 화면 삭제가 ingestion job 실행이나 history 기록을 중단시키지 않게 import dependency를 확인한다.
- 수집 실패의 원인 검사는 Ingestion의 기존 history/log/failure section이 소유한다.
- `/operations`, `/ops-review` 직접 경로는 제거된다. `/selected-portfolio-dashboard` Portfolio Monitoring route는 유지한다.

## Visual Design

새 화면이나 진단 패널을 만들지 않는다. 유지되는 Portfolio Monitoring은 현재 React one-shell의 연한 청회색 surface, 명확한 section eyebrow, KPI card, context drawer, status pill 계층을 그대로 사용한다. 제거로 인해 작은 안내가 필요할 때도 이 시스템을 재사용하고 Streamlit metric/status-card 스타일을 새로 섞지 않는다.

## Testing And QA

- navigation source/contract: Operations group에는 Portfolio Monitoring만 존재한다.
- import/compile: 제거된 모듈 import나 wrapper 참조가 없다.
- Ingestion records: session result, persistent history, recent log, failure CSV renderer가 유지된다.
- Portfolio Monitoring focused Python/React regression을 통과한다.
- `git diff --check`, UI/engine boundary, finance refinement hygiene를 통과한다.
- 실제 top navigation에서 Operations 아래 Portfolio Monitoring만 보이는지 확인한다.
- Portfolio Monitoring desktop 또는 mobile 화면을 열어 기존 React layout이 유지되는지 확인하고 QA 스크린샷 1장을 남긴다.

## Tradeoffs

- 기존 `/operations`, `/ops-review` bookmark는 더 이상 유효하지 않다. 사용자가 해당 화면을 사용하지 않고 대체 경로가 명확하므로 compatibility alias는 유지하지 않는다.
- 개발자가 앱에서 raw log와 artifact를 한 화면에 보던 편의는 사라진다. 동일 정보는 Ingestion에 남고 파일/CLI도 보존되므로 제품 navigation 단순화 이익이 더 크다.
- Operations group에 한 페이지만 남지만, `Portfolio Monitoring`은 Backtest 이후 사후 추적이라는 독립 제품 단계이므로 Workspace로 이동하지 않는다.

## Success Criteria

- 사용자가 Operations의 목적을 Portfolio Monitoring으로 즉시 이해한다.
- 중복 landing과 사용하지 않는 개발 진단 화면이 보이지 않는다.
- 수집 실행 결과와 실패 확인 기능은 Ingestion에서 손실 없이 사용할 수 있다.
- Portfolio Monitoring에 raw 운영 진단값이 새로 추가되지 않는다.
- 관련 자동 회귀와 Browser QA가 통과한다.
