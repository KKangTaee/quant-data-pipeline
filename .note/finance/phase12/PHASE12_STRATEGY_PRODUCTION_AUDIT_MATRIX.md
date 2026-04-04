# Phase 12 Strategy Production Audit Matrix

## 목적

- 현재 프로젝트에 있는 주요 전략군을
  실전형 승격 관점에서 다시 분류한다.
- 무엇을 먼저 production-grade로 끌어올릴지 우선순위를 고정한다.

## 분류 기준

### 1. production-priority

- 현재 코드/데이터 계약을 바탕으로
  real-money hardening을 적용할 가치가 크고,
  먼저 승격 후보로 볼 전략군

### 2. baseline / reference only

- 비교 기준이나 연구 기준선으로는 유용하지만,
  현재 우선순위 기준에서는 production promotion target이 아닌 전략군

### 3. research-only / hold

- 아직 contract 자체가 prototype이거나
  실전형으로 읽기엔 데이터/validation 경계가 남아 있어
  이번 phase에서 승격하지 않을 전략군

## 전략군별 audit

## A. ETF 전략군

### `GTAA`

- 현재 분류: `production-priority`
- 강점:
  - fixed ETF universe
  - universe ambiguity가 비교적 적음
  - 실전형 contract를 얹기 쉬움
- 남은 gap:
  - cost / slippage first pass
  - turnover summary
  - benchmark / drawdown / caution wording

### `Dual Momentum`

- 현재 분류: `production-priority`
- 강점:
  - ETF fixed set
  - 비교적 해석 가능한 rotation contract
- 남은 gap:
  - cost / turnover disclosure
  - benchmark / relative underperformance readout
  - investability / continuity wording

### `Risk Parity Trend`

- 현재 분류: `production-priority`
- 강점:
  - fixed ETF set
  - allocation logic가 비교적 명확함
- 남은 gap:
  - weight / rebalance change interpretation
  - turnover / cost disclosure
  - benchmark / drawdown readout

## B. Strict Annual Family

### `Quality Snapshot (Strict Annual)`

- 현재 분류: `production-priority`
- 강점:
  - strict annual data contract
  - dynamic PIT validation first/second pass 존재
- 남은 gap:
  - real-money caution wording
  - investability / stale handling rule
  - turnover / cost model
  - benchmark / drawdown / guardrail surface

### `Value Snapshot (Strict Annual)`

- 현재 분류: `production-priority`
- 강점:
  - strict annual family와 동일한 validation foundation
- 남은 gap:
  - quality annual과 동일한 promotion contract 보강 필요

### `Quality + Value Snapshot (Strict Annual)`

- 현재 분류: `production-priority`
- 강점:
  - multi-factor annual strict path
  - dynamic PIT validation foundation 존재
- 남은 gap:
  - annual strict single-factor와 동일한 real-money contract 보강 필요

## C. Baseline / Reference

### `Equal Weight`

- 현재 분류: `baseline / reference only`
- 이유:
  - 기준선으로는 유용하지만,
    현재 Phase 12에서 production hardening 우선 대상은 아님

### broad `Quality Snapshot`

- 현재 분류: `baseline / reference only`
- 이유:
  - research path로는 유용하지만
    strict / PIT / real-money contract 우선순위보다 뒤에 둔다

## D. Quarterly Strict Prototype Family

### `Quality Snapshot (Strict Quarterly Prototype)`
### `Value Snapshot (Strict Quarterly Prototype)`
### `Quality + Value Snapshot (Strict Quarterly Prototype)`

- 현재 분류: `research-only / hold`
- 이유:
  - current contract가 여전히 prototype
  - statement coverage / promotion semantics가 실전형으로 충분히 닫히지 않음
  - 실전 승격보다 hold rule을 유지하는 쪽이 더 합리적임

## 최종 우선순위

1. ETF 전략군 real-money hardening
2. strict annual family promotion
3. baseline/reference 전략은 비교 기준선 유지
4. quarterly strict prototype family는 hold

## 메모

- Phase 12는
  “무엇이 지금 투자 가능한가”를 과장하는 phase가 아니다.
- 목적은
  **현재 전략군을 실전형 후보 / 기준선 / research-only로 다시 나누고,
  가장 방어적인 순서로 승격하는 것**
  이다.
