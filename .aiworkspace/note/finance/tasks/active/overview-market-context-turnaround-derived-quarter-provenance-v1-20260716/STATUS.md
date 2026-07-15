# Overview Market Context Turnaround Derived Quarter Provenance V1 Status

Last Updated: 2026-07-16

## Current Stage

- 전체 roadmap: 설계 승인 -> 1차 데이터 RED/GREEN -> 2차 provenance -> 3차 UI -> 4차 QA/docs
- 현재: written spec review
- 구현 완료 차수: 0/4

## Completed

- MRNA actual DB와 resolver/UI code를 read-only로 추적했다.
- 선 단절 자체는 결측 보존 UI 계약이며 CSS clipping이 아님을 확인했다.
- 2023-Q4 매출 결측 원인을 Q1/Q2와 Q3/FY 사이 revenue concept rename으로 확정했다.
- 보간, strict missing 유지, explicit concept-family fallback 세 접근을 비교했다.
- 사용자는 concept-family fallback과 `공시 기반 산출` 표기 방향을 승인했다.
- authoritative design과 안전 조건을 `DESIGN.md`에 기록했다.

## Next Action

- written spec 사용자 확인 후 implementation plan을 작성한다.
