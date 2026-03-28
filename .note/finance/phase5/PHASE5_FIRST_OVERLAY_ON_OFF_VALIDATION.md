# Phase 5 First Overlay On/Off Validation

## 목적

- strict family의 first overlay인
  `month-end MA200 trend filter + cash fallback`
  이 실제로 어떤 성격의 변화를 만드는지 baseline 대비로 확인한다.

## 검증 기준

- 기간:
  - `2016-01-01 ~ 2026-03-20`
- 리밸런싱:
  - `month_end`
- overlay window:
  - `200`
- canonical compare preset:
  - `US Statement Coverage 100`
- wide-preset sanity check:
  - `Quality Snapshot (Strict Annual)` + `US Statement Coverage 300`

## 결과 요약

### Canonical Compare: Coverage 100

| Strategy | Overlay | End Balance | CAGR | Sharpe | Max DD | Active Rebalances | Cash-Only Rows | Overlay Rejected Events | Overlay Hit Rebalances |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Quality Snapshot (Strict Annual) | off | 85,604.7 | 23.59% | 0.8442 | -33.16% | 123 | 0 | 0 | 0 |
| Quality Snapshot (Strict Annual) | on | 48,214.1 | 16.78% | 0.6681 | -35.23% | 103 | 20 | 69 | 49 |
| Value Snapshot (Strict Annual) | off | 157,885.3 | 31.28% | 1.4067 | -36.03% | 123 | 0 | 0 | 0 |
| Value Snapshot (Strict Annual) | on | 181,349.8 | 33.09% | 1.4490 | -34.84% | 122 | 1 | 364 | 112 |
| Quality + Value Snapshot (Strict Annual) | off | 137,522.1 | 29.50% | 1.3234 | -38.26% | 123 | 0 | 0 | 0 |
| Quality + Value Snapshot (Strict Annual) | on | 155,410.9 | 31.08% | 1.3662 | -35.34% | 122 | 1 | 341 | 111 |

### Wide-Preset Sanity Check: Quality Coverage 300

| Strategy | Overlay | End Balance | CAGR | Sharpe | Max DD | Active Rebalances | Cash-Only Rows | Overlay Rejected Events | Overlay Hit Rebalances |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Quality Snapshot (Strict Annual) | off | 415,463.3 | 44.43% | 1.4520 | -23.93% | 123 | 0 | 0 | 0 |
| Quality Snapshot (Strict Annual) | on | 203,350.0 | 34.60% | 1.2310 | -23.15% | 104 | 19 | 66 | 47 |

## 해석

### 1. Quality strict에서는 first overlay가 기본적으로 보수적으로 작동했다

- Coverage 100과 300 모두에서
  overlay on은
  - active rebalance 수를 줄였고
  - cash-only row를 늘렸고
  - 최종 수익과 CAGR, Sharpe를 낮췄다
- 즉 현재 quality strict family에서는
  `MA200` overlay가 방어적 성격은 분명하지만,
  성과 개선을 자동으로 보장하지는 않는다.

### 2. Value strict / Quality+Value strict에서는 overlay가 더 자연스럽게 작동했다

- Coverage 100 기준으로
  - `Value`
  - `Quality + Value`
  두 전략은 overlay on에서
  - End Balance 상승
  - CAGR 상승
  - Sharpe 소폭 상승
  - MDD 완화
  흐름을 보였다
- 이 결과는 현재 first overlay가
  quality-only보다
  valuation 또는 mixed ranking과 궁합이 더 좋을 수 있음을 시사한다.

### 3. overlay는 “항상 좋은 보호막”이 아니라 strategy-dependent한 도구다

- 현재 결과만 보면
  - `Quality` strict: research-only toggle로 유지하는 편이 낫다
  - `Value`, `Quality + Value` strict: public candidate로 계속 평가할 가치가 있다

## 현재 판단

- first overlay 구현은 유지한다
- 다만 public messaging은
  “trend filter를 켜면 무조건 더 좋다”가 아니라
  “strategy에 따라 성과/방어 효과가 다를 수 있다”
  로 가는 것이 맞다
- canonical compare preset에서는
  `Coverage 100`을 계속 baseline으로 삼는다

## 다음 연결

- selection interpretation을 통해
  어떤 월에 cash fallback이 많았는지 읽을 수 있게 유지한다
- second overlay는
  `Market Regime Overlay`
  를 우선 후보로 검토한다
- quarterly strict family는
  first overlay validation 이후 단계로 계속 defer한다
