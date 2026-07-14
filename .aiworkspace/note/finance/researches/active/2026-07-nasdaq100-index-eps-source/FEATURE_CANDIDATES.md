# Feature Candidates

Status: Research Handoff
Last Updated: 2026-07-14

## Post-V1 Recovery Candidates

| Candidate | Impact | Effort | Risk | Priority | Decision |
|---|---:|---:|---:|---|---|
| FY-to-Q4 TTM bug + split-aware drift 수정 | 5 | 2 | 2 | Now | 외부 source 추가 전 필수 |
| SEC CIK lifecycle + actual fallback 확대 | 5 | 4 | 3 | Now | canonical EPS 복구 경로 |
| Tiingo free EOD optional fallback | 5 | 3 | 3 | Next | 무료 계정/internal-only 승인 조건 |
| N-PORT implied-price anchor validator | 4 | 2 | 1 | Next | alias/split/source 검증에 사용 |
| 20-F annual actual quality tier | 3 | 4 | 4 | Later/conditional | strict TTM과 분리해 표시 |
| N-PORT anchor-held monthly proxy | 2 | 2 | 5 | Parking lot | 실제 monthly EOD가 아니므로 별도 방법론 승인 필요 |

우선순위는 `Impact 1~5`, `Effort 1~5`, `Risk 1~5`의 상대평가다. upper-bound는 119/119 통과 가능성을 보여주지만 actual payload spike 전에는 Tiingo 경로를 완료로 간주하지 않는다.

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

기존 P1~P4는 이미 구현됐다. 후속은 계산 정확도 수정과 source recovery를 먼저 수행한 뒤 119개월 coverage/calibration을 다시 통과시키는 작업이다. 이 연구는 구현 승인이 아니라 feasibility와 권장 순서 handoff다.

## Parking Lot

- strict PIT NDX constituent/divisor reconstruction
- GuruFocus 유료 Economic Data API 교차검증
- analyst consensus EPS와 FOMC 자체 시나리오 병렬 비교
- Nasdaq Composite(COMP) 별도 가치평가
