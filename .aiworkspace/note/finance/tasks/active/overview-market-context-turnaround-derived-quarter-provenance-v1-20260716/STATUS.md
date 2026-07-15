# Overview Market Context Turnaround Derived Quarter Provenance V1 Status

Last Updated: 2026-07-16

## Current Stage

- 전체 roadmap: 1차 데이터 RED/GREEN -> 2차 provenance -> 3차 UI -> 4차 QA/docs
- 현재: 1차~3차 구현 완료, 4차 actual/Browser QA 준비
- 구현 완료 차수: 3/4

## Completed

- MRNA actual DB와 resolver/UI code를 read-only로 추적했다.
- 선 단절 자체는 결측 보존 UI 계약이며 CSS clipping이 아님을 확인했다.
- 2023-Q4 매출 결측 원인을 Q1/Q2와 Q3/FY 사이 revenue concept rename으로 확정했다.
- 보간, strict missing 유지, explicit concept-family fallback 세 접근을 비교했다.
- 사용자는 concept-family fallback과 `공시 기반 산출` 표기 방향을 승인했다.
- authoritative design과 안전 조건을 `DESIGN.md`에 기록했다.
- 사용자가 written spec을 확인하고 구현 진행을 승인했다.
- TDD/commit/QA 단위를 4개 task로 나눈 implementation plan을 `PLAN.md`에 확정했다.
- MRNA-like fixture가 기존 코드에서 Q4 `StopIteration`으로 실패하는 RED를 확인했다.
- exact-concept selection 뒤에만 실행되는 explicit family fallback을 추가했다.
- direct Q4 우선, allowlist 밖 concept 제외, future FY cutoff guard를 회귀 테스트로 고정했다.
- resolver 9/9, turnaround 40/40, target py_compile과 diff check를 통과했다.
- quarterly/TTM provenance test가 missing keys로 실패하는 RED를 확인했다.
- timeline에 metric별 `REPORTED/FILING_DERIVED`, rule, operands와 derived metric lists를 추가했다.
- MRNA-like Q4는 revenue `2.811B`, GP `1.882B`, operating income `0.006B`와 구조화 근거를 노출한다.
- 기존 service `_json_safe`가 nested provenance를 별도 수정 없이 보존함을 검증했다.
- turnaround/Market Context 70/70, service focused test, target py_compile과 diff check를 통과했다.
- React source contract가 provenance types/copy/styles 부재로 실패하는 RED를 확인했다.
- 영업·현금 chart에 neutral source-quarter marker와 `공시 기반 산출` legend를 추가했다.
- active inspector에 derived badge, known-rule 계산식, TTM derived-input notice를 추가했다.
- 420px에서 derived heading/badge가 세로 wrapping되도록 보강했다.
- 관련 테스트 71/71과 Vite production build를 통과했다.

## Next Action

- Task 4의 actual MRNA DB-only 검증과 Browser QA를 수행한다.
