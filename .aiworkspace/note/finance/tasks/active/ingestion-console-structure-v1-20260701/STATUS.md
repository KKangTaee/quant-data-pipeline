# Ingestion Console Structure V1 Status

Status: Active
Started: 2026-07-01

## Current

- 2차 완료: 운영 / 수동 / 기록 section renderer를 분리하고 `render_ingestion_console()`를 selector + dispatch 중심으로 축소.

## Done

- 0차 코드 파악과 단계별 가이드 완료.
- 1차 기록 탭 신설, 우측 column 제거, 구조 테스트 추가.
- 2차 탭별 renderer 함수 추출, selected section dispatch 함수 추가, 구조 테스트 추가.

## Next

- 3차: 운영 alias / 수동 수집 alias 관계를 화면에서 더 분명히 하고 공용 결과 요약을 보강한다.
