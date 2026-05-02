# Phase 4 Visualization Enhancement First Pass

## 목적
이 문서는 Backtest 탭의 first-pass 시각화 강화를 기록한다.

이번 단계의 초점:

- 단일 전략 결과를 더 읽기 쉽게 만들기
- 비교 결과에서 단순 end balance 외의 움직임을 더 보이게 만들기

## 추가된 시각화

### 1. Single Strategy - Equity Curve 보강

기존:

- 단순 `Total Balance` line chart

현재:

- equity curve line
- `High / Low / End` marker
- `Best Period / Worst Period` marker
- marker label
- tooltip

의미:

- 최고점 / 최저점 / 종료점을 바로 읽을 수 있다
- 그래프 위에서 가장 좋은 구간과 가장 나쁜 구간도 바로 식별할 수 있다

### 2. Single Strategy - Top 3 Best / Worst Period

추가된 것:

- `Period Extremes` 탭
- `Top 3 Best Periods`
- `Top 3 Worst Periods`

기준:

- `Total Return`

의미:

- 단순 누적 성과뿐 아니라
  어떤 시기가 실제로 가장 좋았고 나빴는지 빠르게 확인할 수 있다

### 3. Compare - Total Return Overlay

기존:

- summary compare
- equity overlay
- drawdown overlay

현재:

- `Return Overlay` 탭 추가

의미:

- 전략 간 period-by-period 움직임 차이를 더 직접적으로 볼 수 있다
- 공격성, 회복 속도, 변동성이 더 잘 드러난다

### 4. Compare - Focused Strategy Drilldown

추가된 것:

- `Focused Strategy` 탭
- 선택 전략 1개에 대한:
  - summary KPI
  - marker equity curve
  - `Top 3 Balance Highs / Lows`
  - `Top 3 Best / Worst Periods`

의미:

- overlay chart는 전체 비교용으로 유지하면서,
  실제 해석은 선택 전략 하나를 깊게 읽는 방식으로 보완할 수 있다
- sparse 전략과 dense 전략이 섞여도 한 전략씩 자세히 확인하기 쉬워진다

### 4. Weighted Portfolio - 시각화 재사용

추가된 것:

- weighted portfolio 결과에도
  - `Equity Curve`
  - `Balance Extremes`
  - `Period Extremes`
  - 동일 marker 언어
  가 적용됨

의미:

- 단일 전략과 결합 포트폴리오를 같은 읽기 방식으로 비교할 수 있다
- weighted portfolio도 별도 특수 화면이 아니라 같은 분석 surface로 다룰 수 있다

## 구현 파일

- `app/web/pages/backtest.py`

## 검증

single strategy 검증:

- `Equal Weight`
- top 3 best / worst period helper 정상 동작 확인

예시:

- best:
  - `2020-04-30`, `Total Return = 0.102`
- worst:
  - `2020-03-31`, `Total Return = -0.089`

marker helper 검증:

- `High`: `2026-02-27`, `32839.5`
- `Low`: `2016-01-29`, `10000.0`
- `End`: `2026-03-20`, `30188.4`
- `Best Period`: `2020-04-30`, `14535.1`
- `Worst Period`: `2020-03-31`, `13195.3`

compare 검증:

- `Equal Weight`
- `GTAA`
- total return overlay view 생성 확인
- focused strategy drilldown view 생성 확인

weighted portfolio 검증:

- weighted portfolio result에도 동일 marker helper / period extremes / balance-extremes 표 연결 확인

## 현재 한계

- top/bottom period는 아직 `Top 1` marker + 표 조합 중심이다
- compare 차트는 여전히 1차 시각화 수준이며,
  style / annotation / interaction은 더 강화 가능하다
- weighted portfolio는 현재 single-strategy와 같은 요약 시각화까지만 열려 있고,
  strategy contribution 분해나 rebalance event marker는 아직 없다

## 다음 자연스러운 확장

- graph 위 top 3 best / worst marker 확장
- compare chart에 strategy별 highlight toggle
- weighted portfolio contribution / weight-change view
- compare overlay 위 직접 marker annotation 추가 여부 검토
