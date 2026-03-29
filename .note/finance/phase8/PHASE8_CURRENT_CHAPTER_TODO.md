# Phase 8 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 8 방향 고정
  - quarterly strategy family expansion + promotion readiness를 이번 chapter의 메인 축으로 확정
- `completed` Phase 8 계획 문서 작성
  - `PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
- `completed` roadmap / doc index / 로그 동기화 검토

## 2. Quarterly Family Scope

- `completed` quarterly family role decision
  - quality / value / quality+value quarterly 모두 `research-only prototype` naming으로 고정
- `completed` compare exposure decision
  - quarterly family 3종 모두 compare first pass에 노출

## 3. Quarterly Value Prototype

- `completed` runtime wrapper first pass
  - quarterly strict value path 실행 함수 구현
- `completed` single strategy UI first pass
  - value quarterly prototype 입력 / 결과 / preflight 연결
- `completed` validation first pass
  - active date / selection history / factor semantics 확인

## 4. Quarterly Quality+Value Prototype

- `completed` runtime wrapper first pass
  - blended quarterly strict path 실행 함수 구현
- `completed` single strategy UI first pass
  - quality+value quarterly prototype 입력 / 결과 / preflight 연결
- `completed` validation first pass
  - active date / interpretation / combined factor semantics 확인

## 5. Quarterly Research Surface

- `completed` interpretation / history parity
  - selection history / interpretation / history drilldown quarterly parity 보강
- `completed` compare integration first pass
  - compare 지원과 exposure policy를 코드 + 문서 기준으로 고정

## 6. Promotion Readiness

- `completed` quarterly family validation rerun
  - quality/value/quality+value quarterly 경로 반복 검증
- `completed` promotion criteria draft
  - research-only 유지 기준 vs public candidate 진입 기준 정리
- `completed` manual test checklist 작성

## 7. Operator Diagnostics

- `completed` stale price diagnosis first pass
  - DB stale / provider gap / likely delisted를 구분하기 위한 read-only diagnosis card 추가
- `completed` statement shadow coverage gap drilldown
  - quarterly prototype preview에서 missing symbol / raw coverage 여부 / targeted statement refresh payload 확인 가능

## 8. Operator Tooling Polish

- `completed` runtime / build indicator
  - 현재 Streamlit 프로세스가 어떤 코드 상태로 떠 있는지 `Ingestion` 화면에서 바로 확인 가능
- `completed` statement shadow rebuild only helper
  - raw statement 재수집 없이 shadow rebuild만 수행하는 manual helper 추가
- `completed` coverage gap action bridge
  - quarterly preview에서 missing symbol을 `Extended Statement Refresh` / `Statement Shadow Rebuild Only`로 바로 넘기는 prefill bridge 추가
- `completed` run inspector and standardized artifacts first pass
  - persisted run에서 runtime marker / related logs / standardized JSON+failure CSV artifact를 확인 가능
