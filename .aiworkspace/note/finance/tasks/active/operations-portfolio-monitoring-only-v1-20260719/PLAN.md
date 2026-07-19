# Operations Portfolio Monitoring Only V1 Plan

## 이걸 하는 이유?

현재 Operations에는 실제 포트폴리오 추적 화면 외에도 Portfolio Monitoring과 run health를 다시 요약하는 `Operations Overview`, 개발자용 로그·artifact 검사 화면인 `System / Data Health`가 함께 노출된다. 사용자는 두 화면을 사용하지 않고 목적도 이해하기 어렵다고 확인했다. 필요한 수집 실행 기록과 실패 확인 기능은 이미 `Workspace > Ingestion > 실행 기록 / 결과`에 있으므로, Operations를 실제 사용자 업무인 Portfolio Monitoring 하나로 좁힌다.

## Goal

- 상단 Operations에서 Portfolio Monitoring만 사용자-facing 화면으로 유지한다.
- `Operations Overview`와 `System / Data Health`의 전용 route와 UI 코드를 제거한다.
- 수집 결과, run history, 로그, failure CSV 확인 기능은 기존 Ingestion 화면에 그대로 보존한다.
- 현재 Portfolio Monitoring의 React one-shell 디자인과 사용자 흐름을 유지한다.

## Overall Roadmap

| 차수 | 목적 | 완료 조건 |
| --- | --- | --- |
| 1차 | 기능 감사와 제거 경계 확정 | 중복 surface와 대체 경로를 확인하고 사용자 승인을 받는다. |
| 2차 | navigation·전용 코드·현재 문서 정리 | Operations에는 Portfolio Monitoring만 남고 제거된 route/import/reference가 없다. |
| 3차 | 자동 회귀·Browser QA·문서 closeout | Ingestion 기록 기능과 Portfolio Monitoring이 정상이며 실제 navigation QA가 끝난다. |

현재 위치는 `3/3차 완료`다. 승인된 제거 경계의 구현, 자동 회귀, 실제 Browser QA, 문서 closeout을 마쳤다.

## Scope

- Operations navigation 단순화
- `app/web/operations_overview.py`, `app/web/ops_review.py` 제거
- 제거 surface 전용 테스트 삭제 또는 새 navigation/보존 계약 테스트로 교체
- 현재 product docs, flow docs, reference copy, QA runbook 정리
- Portfolio Monitoring과 Ingestion 기록 화면 회귀 검증

## Out Of Scope

- Portfolio Monitoring 성과·진단·차트·저장 계약 재설계
- Ingestion에 새 run/job/status 패널 추가
- run history, log, failure CSV, artifact 파일 삭제
- registry 또는 saved JSONL 변경
- provider fetch, broker 연동, 주문, 자동 리밸런싱

## Stop Condition

Operations 상단에는 Portfolio Monitoring만 보이고, 기존 진단 화면의 사용자-facing 참조가 제거되며, Ingestion의 실행 기록/로그/failure 확인 기능과 Portfolio Monitoring이 자동 테스트 및 Browser QA에서 정상 동작하면 완료한다.
