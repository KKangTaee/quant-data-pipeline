# Ingestion Console Structure V1 Status

Status: Active
Started: 2026-07-01

## Current

- 3차 완료: 공용 최근 실행 요약을 추가하고 운영 alias / 수동 복구 entry 관계를 job brief에서 설명.

## Done

- 0차 코드 파악과 단계별 가이드 완료.
- 1차 기록 탭 신설, 우측 column 제거, 구조 테스트 추가.
- 2차 탭별 renderer 함수 추출, selected section dispatch 함수 추가, 구조 테스트 추가.
- 3차 `recent_results` 기반 공용 실행 요약 추가, collection entry relationship note 추가.

## Next

- 4차: durable docs와 handoff log를 새 Ingestion 3탭 구조에 맞춰 정렬하고 Browser QA를 수행한다.
