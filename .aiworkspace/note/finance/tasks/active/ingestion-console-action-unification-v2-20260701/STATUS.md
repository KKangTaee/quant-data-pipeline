# Ingestion Console Action Unification V2 Status

Status: Active
Started: 2026-07-01

## Current

- 2차 완료: read-only 진단 카드를 공용 scheduled job / 화면 고정 / progress / result history 흐름에 통합했다.

## Done

- 0차 코드 파악과 1~6차 roadmap 정리.
- 1차 action registry 추가, active / compatibility / read-only diagnostic action 분류, section inference registry 우선 사용.
- 2차 diagnostic action dispatcher 추가, 네 개 진단 카드의 inline 실행 제거, 기존 진단 result renderer와 run history 저장 흐름 연결.

## Next

- 3차: 가격 / asset profile / EDGAR 수집 입력 helper를 통합하고 화면 문구를 수집 범위에 맞게 정리한다.
