# Phase 5 First Overlay Requirements And Selection

## 목적

- strict annual factor family 위에 어떤 risk overlay를 first-pass로 얹을지 고정한다.

## 요구사항 정리

first overlay는 다음 요구를 만족해야 한다.

1. factor selection layer를 바꾸지 않아야 한다
2. point-in-time 복잡도를 불필요하게 늘리지 않아야 한다
3. public UI에서 설명하기 쉬워야 한다
4. single / compare / history / interpretation에 함께 노출될 수 있어야 한다

## 범위 결정

### 이번 first pass에서 포함

- 대상 전략:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- 판단 시점:
  - month-end only
- 행동:
  - overlay 조건을 통과하지 못한 selected name은 cash로 이동

### 이번 first pass에서 제외

- intramonth risk-off
- benchmark regime overlay
- defensive asset rotation
- partial de-risk
- drawdown-triggered stop

## 선정 결과

first overlay는 아래로 고정한다.

- `Trend Filter Overlay`
- 규칙:
  - rebalance 시점에 selected name의 `Close >= MA200` 이어야 보유
  - `Close < MA200`이면 그 name은 cash로 이동

## 선정 이유

- 이미 price-only 전략군에 유사한 `MA200` 해석 경험이 있다
- strict factor family 위에 얹었을 때 사용자가 이해하기 쉽다
- intramonth overlay보다 구현/운영 리스크가 낮다
- selection history에서 raw selection과 overlay rejection을 분리해 해석하기 좋다

## input contract

- `trend_filter_enabled: bool`
- `trend_filter_window: int`

first-pass 기본값:

- `trend_filter_enabled = False`
- `trend_filter_window = 200`

## result schema 영향

overlay가 켜진 strict family result에는 아래 정보가 추가된다.

- `Raw Selected Ticker`
- `Raw Selected Count`
- `Raw Selected Score`
- `Overlay Rejected Ticker`
- `Overlay Rejected Count`
- `Trend Filter Enabled`
- `Trend Filter Column`

## UI / compare / history 반영 원칙

- single 전략 Advanced Inputs에서 on/off와 window를 조절할 수 있어야 한다
- compare에서도 전략별 override로 조절할 수 있어야 한다
- history에 overlay on/off와 window가 저장되어야 한다
- selection interpretation에서 raw selection과 overlay rejection이 함께 보여야 한다

## 결론

- Phase 5 first overlay는
  `month-end MA200 trend filter + cash fallback`
  으로 고정한다.
- 이후 second overlay는 이 first-pass 운용 결과를 본 뒤 검토한다.
