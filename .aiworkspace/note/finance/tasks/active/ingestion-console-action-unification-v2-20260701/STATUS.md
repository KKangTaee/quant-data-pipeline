# Ingestion Console Action Unification V2 Status

Status: Active
Started: 2026-07-01

## Current

- 4차 완료: futures / event / lifecycle / profile 계열 job의 progress callback coverage를 보강했다.

## Done

- 0차 코드 파악과 1~6차 roadmap 정리.
- 1차 action registry 추가, active / compatibility / read-only diagnostic action 분류, section inference registry 우선 사용.
- 2차 diagnostic action dispatcher 추가, 네 개 진단 카드의 inline 실행 제거, 기존 진단 result renderer와 run history 저장 흐름 연결.
- 3차 daily/manual OHLCV params builder 추가, metadata/manual asset profile job builder 통합, 수동 asset profile run_metadata 보강.
- 4차 stage progress event helper 추가, futures/calendar/profile/lifecycle/source-map job callback 시그니처 보강, dispatcher와 UI progress allowlist 연결.

## Next

- 5차: legacy compatibility action 경계를 helper로 정리하고 active UI에서 불필요 broad job이 노출되지 않도록 검증한다.
