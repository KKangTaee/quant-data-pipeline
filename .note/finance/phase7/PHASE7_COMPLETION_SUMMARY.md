# Phase 7 Completion Summary

## 목적

- Phase 7에서 진행한
  - quarterly coverage hardening
  - statement PIT inspection / loader semantics repair
  workstream을 closeout 관점에서 정리한다.
- manual validation은 뒤로 미루더라도,
  현재 코드/문서 기준으로 어디까지 구현 완료되었는지 한 번에 확인할 수 있게 한다.

## Phase 7에서 완료된 것

### 1. statement source payload reality check

EDGAR source inspection을 다시 수행했고,
late-start의 근본 원인이 source 부족이 아니라는 점을 고정했다.

확인된 내용:
- facts layer는 이미 long-history를 제공함
- filing layer는
  - `filing_date`
  - `accepted_at`
  - `available_at`
  - `report_date`
  를 제공함
- quarterly path에서 `FY` / `10-K`를 버리면 Q4-like coverage가 크게 손실됨

즉 문제는 source 교체가 아니라
loader / ingestion / shadow semantics였다.

### 2. raw statement ledger decision 정리

`nyse_financial_statement_*` 계열 raw ledger는
이번 phase에서 drop/recreate하지 않았다.

결정:
- `keep tables`
- `patch loader semantics`
- `patch quarterly shadow semantics`

이유:
- 현재 raw ledger는 이미 PIT-friendly field를 충분히 담고 있었음
- late-start의 직접 원인은 schema 부재보다
  - quarterly form/fiscal-period exclusion
  - 짧은 ingestion depth
  - 잘못된 shadow anchor
  에 있었음

### 3. quarterly ingestion depth / semantics hardening

Phase 7 first pass에서 아래가 바뀌었다.

- quarterly path가 `10-Q`뿐 아니라 `10-K`도 받도록 수정
- quarterly fiscal periods에 `FY` 포함
- statement ingestion에 `periods=0`을 공식 입력으로 열어
  `all available periods`를 허용
- quarterly shadow builder에서 old `report_date`-anchor filter 제거

즉 quarterly raw ledger와 shadow path가
더 긴 history를 다시 통과할 수 있는 기반이 마련되었다.

### 4. quarterly coverage recovery

sample symbols:
- `AAPL`
  - min quarterly period recovered to `2006`
- `MSFT`
  - `2007`
- `GOOG`
  - `2012`

`US Statement Coverage 100` quarterly rebuild 결과:
- raw values:
  - `100 symbols`
  - `876,657 rows`
  - `min_period_end = 2000-01-01`
- shadow:
  - `100 symbols`
  - `6,796 rows`
  - `min_period_end = 2006-09-24`

### 5. quarterly strict prototype rerun recovery

`Quality Snapshot (Strict Quarterly Prototype)`는
Phase 7 이후 다시 longer-history에서 열리게 되었다.

확인:
- manual `AAPL,MSFT,GOOG`
  - `first_active_date = 2016-01-29`
- preset `US Statement Coverage 100`
  - `first_active_date = 2016-01-29`

즉 Phase 6에서 보였던
`2025` 부근 late-start 문제는
Phase 7 first pass 기준으로 실질적으로 완화되었다.

### 6. supplementary polish pass

Phase 7 후반에는 later validation을 쉽게 하기 위한 실사용성 보강도 추가했다.

- weekend / holiday-aware `Price Freshness Preflight`
  - selected end 대신 `effective trading end` 기준 stale 판정
- quarterly `Statement Shadow Coverage Preview`
  - 실행 전 coverage bounds를 UI에서 확인 가능
- `Statement PIT Inspection` UI card
  - coverage summary
  - timing audit
  - source payload inspection
  을 notebook 없이 UI에서 확인 가능

## 핵심 결과

### quarterly late-start의 주원인은 전략이 아니라 data path였다

이번 phase에서 분명해진 것은:
- source는 충분히 길고
- raw ledger도 유지 가능했으며
- blocker는 quarterly ingestion / shadow semantics에 있었다는 점이다

즉 Phase 7은 새로운 전략을 추가한 phase라기보다,
**quarterly strict family가 실제로 연구 가능한 기반을 복구한 data foundation phase**
였다.

### quarterly strict prototype는 이제 “실행 가능한 research path”가 되었다

아직 public candidate로 승격한 것은 아니지만,
최소한 longer-history에서
prototype이 실제로 움직이는 단계까지는 복구되었다.

## 남겨둔 것

이번 phase에서 의도적으로 다음으로 넘긴 항목:

- quarterly `Value Snapshot` prototype
- quarterly `Quality + Value` prototype
- quarterly compare / portfolio integration
- quarterly family promotion criteria / public role 판단

즉 Phase 7은 foundation repair까지를 범위로 보고 닫는 것이 맞다.

## manual validation 상태

현재 상태:
- implementation scope:
  - `completed`
- assistant-side precheck:
  - `completed`
- user manual validation:
  - `deferred`

사용자 검증은
`PHASE7_TEST_CHECKLIST.md`
기준으로 나중에 진행하면 된다.

이번 closeout에서는
**Phase 7 구현을 닫고, manual validation은 Phase 8 검수와 함께 묶어서 진행하는 운영 방식**
으로 정리한다.

## Phase 7 종료 판단

현재 기준으로는:
- code / docs / checklist / polish:
  - `completed`
- manual validation:
  - `pending but intentionally deferred`
- next-phase kickoff:
  - `ready`

즉 지금은
**Phase 7을 implementation-complete 상태로 닫고, 다음 Phase 8을 여는 것이 자연스러운 시점**
이다.
