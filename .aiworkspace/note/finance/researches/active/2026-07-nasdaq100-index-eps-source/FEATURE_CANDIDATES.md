# Feature Candidates

Status: Research Handoff
Last Updated: 2026-07-12

## Candidate Implementation Units

### P0 Public Reconstruction Coverage Spike

- QQQ N-PORT 22개 분기의 holdings parser와 security identifier mapping 구현
- SEC filing-aware TTM actual coverage, ADR/복수 클래스/적자 종목 처리율 측정
- 공개 Nasdaq P/E 관측값을 calibration fixture로 고정
- 완료 조건: 60개월 중 최소 95% coverage와 허용 오차 threshold를 만족하는 재구성 test fixture

### P1 Generic Index Valuation Storage

- `index_code`, observation date/month, index level, trailing P/E, derived EPS, source, quality를 저장하는 범용 계약
- raw provider observation과 derived monthly valuation을 구분

### P2 Nasdaq-100 Proxy Ingestion / Loader

- SEC N-PORT + SEC actual + QQQ EOD -> DB -> loader 경로
- quarterly anchor/monthly drift와 filing available-at alignment

### P3 Generic Service / React Selector

- S&P와 NDX가 같은 계산 엔진을 사용하되 source copy와 quality를 index config로 분리
- `S&P 500 / Nasdaq-100 (QQQ proxy)` 선택과 source-quality 설명

### P4 QA / Documentation

- 60개월 log(PER), FOMC current scenario, 1/3/5년 reconstruction
- data-quality and basis-date Browser QA

## Priority

P0 coverage/calibration을 통과하기 전 P1~P4를 구현하지 않는다. 이 연구는 phase/task 승인이 아니라 source decision handoff다.

## Parking Lot

- strict PIT NDX constituent/divisor reconstruction
- GuruFocus 유료 Economic Data API 교차검증
- analyst consensus EPS와 FOMC 자체 시나리오 병렬 비교
- Nasdaq Composite(COMP) 별도 가치평가
