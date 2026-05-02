# Phase 6 Market Regime Overlay Requirements

## 목적

- strict family의 기존 `Trend Filter Overlay`가 개별 종목 단위 방어였다면,
  이번 overlay는 시장 전체 상태를 보고 포트폴리오 전체 노출을 줄이는 상위 방어 레이어를 추가하는 데 목적이 있다.
- first pass에서는 복잡한 defensive rotation보다
  **cash fallback first pass**를 우선한다.

## first-pass 규칙

### benchmark

- 기본 benchmark:
  - `SPY`
- 선택 가능 benchmark:
  - `SPY`
  - `QQQ`
  - `VTI`
  - `IWM`

### signal

- rebalance date 기준 benchmark `Close`와 `MA(window)`를 비교한다.
- first-pass 기본 window:
  - `200`
- 판정:
  - `Close >= MA(window)`:
    - `risk_on`
  - `Close < MA(window)`:
    - `risk_off`
  - 필요한 benchmark row가 없으면:
    - `unknown`

### 적용 순서

1. strict factor ranking으로 raw top N 후보를 뽑는다.
2. trend filter overlay가 켜져 있으면 개별 종목 `Close vs MA(window)`를 적용한다.
3. market regime overlay가 켜져 있으면 benchmark 상태를 본다.
4. `risk_off`면 남아 있는 후보 전체를 현금으로 전환한다.

즉 first pass는 다음 구조다.

- factor ranking
- per-symbol trend filter
- whole-portfolio market regime filter

## cash fallback

- `risk_off`인 rebalance에서는 strict factor 후보가 있어도 최종 보유 종목은 `0`개가 될 수 있다.
- 이 경우 그 리밸런싱의 포트폴리오는 전액 현금으로 유지된다.
- intramonth daily trigger는 아직 지원하지 않는다.
- 판정은 `month_end` 기준 rebalance date에서만 수행한다.

## 노출 위치

- `Single Strategy`
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
  - `Quality Snapshot (Strict Quarterly Prototype)`
- `Compare & Portfolio Builder`
  - strict annual family 3종
- `History / Drilldown`
  - meta, selection history, interpretation에서 확인 가능

## 결과 스키마

first pass는 result row에 아래 regime 컬럼을 남긴다.

- `Market Regime Enabled`
- `Market Regime Benchmark`
- `Market Regime Column`
- `Market Regime State`
- `Market Regime Close`
- `Market Regime Trend`
- `Regime Blocked Ticker`
- `Regime Blocked Count`

## 해석 포인트

- `Regime Blocked Count`
  - risk-off로 인해 포트폴리오 전체가 현금으로 이동한 종목 수
- `Regime Blocked Events`
  - 전체 기간에서 regime overlay가 개입한 총 종목-event 수
- `Regime Cash Rebalances`
  - risk-off로 인해 실제 cash-only rebalance가 발생한 횟수

## 범위 밖

- intramonth daily regime monitoring
- defensive rotation ETF 자동 전환
- volatility / drawdown / macro signal 결합
- strategy별 다른 regime benchmark 체계

## first-pass 판단

- 이 overlay는 strict family를 “실전형 research environment”로 한 단계 더 확장하는 데 적절하다.
- 다만 first pass에서는 시장 상태를 단순하게 정의했기 때문에,
  해석 가능성과 운영 안정성을 우선한 conservative layer로 이해하는 것이 맞다.
