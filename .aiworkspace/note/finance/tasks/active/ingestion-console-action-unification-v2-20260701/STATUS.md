# Ingestion Console Action Unification V2 Status

Status: Completed
Started: 2026-07-01
Completed: 2026-07-01

## Current

- 1~6차 완료: Ingestion action registry / diagnostic scheduling / shared progress / legacy compatibility boundary / durable docs / Browser QA까지 닫았다.

## Done

- 0차 코드 파악과 1~6차 roadmap 정리.
- 1차 action registry 추가, active / compatibility / read-only diagnostic action 분류, section inference registry 우선 사용.
- 2차 diagnostic action dispatcher 추가, 네 개 진단 카드의 inline 실행 제거, 기존 진단 result renderer와 run history 저장 흐름 연결.
- 3차 daily/manual OHLCV params builder 추가, metadata/manual asset profile job builder 통합, 수동 asset profile run_metadata 보강.
- 4차 stage progress event helper 추가, futures/calendar/profile/lifecycle/source-map job callback 시그니처 보강, dispatcher와 UI progress allowlist 연결.
- 5차 active / compatibility action helper 추가, legacy broad action이 active action 목록에 섞이지 않도록 테스트 고정.
- 6차 durable docs, root handoff logs, Browser QA, final focused regression verification 완료.

## Next

- 다음 후속이 필요하면 실제 provider 실행 smoke는 소수 symbol / short window로 별도 task에서 수행한다.
