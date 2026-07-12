# Feature Candidates

Status: Research Handoff
Last Updated: 2026-07-12

## Candidate Implementation Units

### P0 Source Contract Spike

- Free GuruFocus token으로 indicators 6778/5870의 실제 API response/entitlement 확인
- history start, revision behavior, internal DB 저장/파생값 표시/attribution/retention 권한 확인
- 완료 조건: 60개월 이상 P/E와 분기 EPS가 합법적으로 저장 가능한 test fixture로 고정됨

### P1 Generic Index Valuation Storage

- `index_code`, observation date/month, index level, trailing P/E, derived EPS, source, quality를 저장하는 범용 계약
- raw provider observation과 derived monthly valuation을 구분

### P2 Nasdaq-100 Ingestion / Loader

- API -> DB -> loader 경로
- same-date NDX/P-E alignment와 EPS cross-check

### P3 Generic Service / React Selector

- S&P와 NDX가 같은 계산 엔진을 사용하되 source copy와 quality를 index config로 분리
- `S&P 500 / Nasdaq-100` 선택

### P4 QA / Documentation

- 60개월 log(PER), FOMC current scenario, 1/3/5년 reconstruction
- data-quality and basis-date Browser QA

## Priority

P0를 통과하기 전 P1~P4를 구현하지 않는다. 이 연구는 phase/task 승인이 아니라 source decision handoff다.

## Parking Lot

- strict PIT NDX constituent/divisor reconstruction
- analyst consensus EPS와 FOMC 자체 시나리오 병렬 비교
- Nasdaq Composite(COMP) 별도 가치평가
