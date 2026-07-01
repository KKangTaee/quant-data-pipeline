# Ingestion Console Action Unification V2 Status

Status: Active
Started: 2026-07-01

## Current

- 3차 완료: 가격 / asset profile 수집 payload helper를 통합하고 EDGAR refresh 화면 언어를 annual-only에서 frequency-neutral로 정리했다.

## Done

- 0차 코드 파악과 1~6차 roadmap 정리.
- 1차 action registry 추가, active / compatibility / read-only diagnostic action 분류, section inference registry 우선 사용.
- 2차 diagnostic action dispatcher 추가, 네 개 진단 카드의 inline 실행 제거, 기존 진단 result renderer와 run history 저장 흐름 연결.
- 3차 daily/manual OHLCV params builder 추가, metadata/manual asset profile job builder 통합, 수동 asset profile run_metadata 보강.

## Next

- 4차: futures / event / lifecycle / profile 계열 job에도 progress callback coverage를 보강한다.
