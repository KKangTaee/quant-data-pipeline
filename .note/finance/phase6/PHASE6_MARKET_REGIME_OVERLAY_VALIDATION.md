# Phase 6 Market Regime Overlay Validation

## validation scope

- small strict smoke universe:
  - `AAPL`
  - `MSFT`
  - `GOOG`
- period:
  - `2024-01-01 -> 2026-03-28`
- benchmark:
  - `SPY`
- market regime rule:
  - `SPY Close < MA200 => cash`

## smoke result

### Annual strict quality

- overlay off
  - `End Balance = 7350.6`
  - `CAGR = -0.1333`
  - `Sharpe = -1.4983`
  - `MDD = -0.2649`
  - `Overlay Rejections = 0`
  - `Regime Blocked = 0`
  - `Selected Events = 14`
- overlay on
  - `End Balance = 7743.4`
  - `CAGR = -0.1121`
  - `Sharpe = -1.2280`
  - `MDD = -0.2257`
  - `Overlay Rejections = 1`
  - `Regime Blocked = 2`
  - `Selected Events = 11`

### Annual strict value

- overlay off
  - `End Balance = 7350.6`
  - `CAGR = -0.1333`
  - `Sharpe = -1.4983`
  - `MDD = -0.2649`
- overlay on
  - `End Balance = 7743.4`
  - `CAGR = -0.1121`
  - `Sharpe = -1.2280`
  - `MDD = -0.2257`

### Annual strict quality + value

- overlay off
  - `End Balance = 7350.6`
  - `CAGR = -0.1333`
  - `Sharpe = -1.4983`
  - `MDD = -0.2649`
- overlay on
  - `End Balance = 7743.4`
  - `CAGR = -0.1121`
  - `Sharpe = -1.2280`
  - `MDD = -0.2257`

## interpretation

- small 3-name smoke에서는 annual strict quality / value / quality+value가 같은 selection path를 만들었다.
- 이 때문에 on/off 비교 결과도 세 전략이 동일하게 나왔다.
- 중요한 확인 포인트는 성과 숫자 자체보다 아래다.
  - overlay on일 때 `Regime Blocked Count`가 실제로 증가했다
  - `Market Regime State`가 `risk_on / risk_off`로 row-level에 기록되었다
  - selected events가 줄어들면서 cash fallback이 실제로 작동했다

## validation judgment

- first-pass market regime overlay는 strict family runtime / UI / interpretation에 일관되게 연결되었다.
- rebalance-date-only market filter라는 의도와 현재 구현이 일치한다.
- first pass 기준으로는
  - `implemented`
  - `smoke-validated`
  - `ready for manual UI testing`
  상태로 본다.
