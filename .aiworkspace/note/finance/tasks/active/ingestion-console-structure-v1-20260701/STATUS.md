# Ingestion Console Structure V1 Status

Status: Active
Started: 2026-07-01

## Current

- 1차 완료: `실행 기록 / 결과` 탭을 추가하고 기존 우측 column의 기록 / 로그 / failure CSV 기능을 새 탭으로 이동.

## Done

- 0차 코드 파악과 단계별 가이드 완료.
- 1차 기록 탭 신설, 우측 column 제거, 구조 테스트 추가.

## Next

- 2차: 운영 / 수동 / 기록 탭 렌더 함수를 분리해 `render_ingestion_console()`의 조건문 덩어리를 줄인다.
