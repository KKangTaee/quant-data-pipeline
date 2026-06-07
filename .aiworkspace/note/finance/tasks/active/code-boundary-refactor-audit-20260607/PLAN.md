# Code Boundary Refactor Audit 2026-06-07

Status: Complete
Last Updated: 2026-06-07

## 이걸 하는 이유?

1차~4차에서 master 병합 후 finance 문서, 구조 경계, active 상태, handoff를 정리했다.
5차는 기능 개발이나 리팩토링 구현 전에 실제 코드가 그 경계를 얼마나 지키는지 확인하고, 다음 구조정리 작업의 기준선을 만든다.

## Scope

- `app/web`, `app/services`, `app/runtime`, `app/jobs`, `finance/*`의 import 방향과 책임 경계를 점검한다.
- Streamlit UI와 service / runtime / data layer 분리가 유지되는지 확인한다.
- Overview, Ingestion, Backtest, Practical Validation, Final Review, Operations 흐름에서 refactor 우선순위를 분류한다.
- 대형 파일과 대형 함수 기준으로 리팩토링 후보를 정리한다.
- 다음 6차 이후 작업이 어떤 순서로 진행되어야 하는지 가이드라인을 남긴다.

## Out Of Scope

- 코드 동작 변경
- UI 레이아웃 변경
- DB schema / ingestion collector 변경
- registry / saved JSONL rewrite
- task / phase physical archive migration
- 외부 벤치마킹
- push / PR 생성

## Completion Criteria

- `AUDIT.md`에 confirmed boundary, findings, refactor priority, next-stage guide가 정리되어 있다.
- `RUNS.md`에 실행한 구조 점검 명령과 결과가 남아 있다.
- current docs / root handoff / task manifest가 5차 완료 상태를 가리킨다.
- generated artifact나 runtime JSONL을 stage하지 않는다.
- docs-only coherent commit을 만든다.
