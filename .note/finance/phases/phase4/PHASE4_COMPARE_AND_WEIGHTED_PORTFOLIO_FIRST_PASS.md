# Phase 4 Compare And Weighted Portfolio First Pass

## 목적
이 문서는 Backtest 탭에

- 다중 전략 비교
- 가중 포트폴리오 결합

을 first-pass 수준으로 추가한 결과를 기록한다.

## 구조 결정

Backtest 탭은 이제 아래 2단 구조를 가진다.

- `Single Strategy`
- `Compare & Portfolio Builder`

이는 기존 단일 전략 실행 흐름을 유지하면서도,
비교/결합 기능을 별도 작업면으로 분리하기 위한 선택이다.

## 이번에 추가된 기능

### 1. 다중 전략 비교

비교 가능한 전략:

- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`

비교 범위:

- 최대 4개 전략 선택
- 공통 `start / end`
- 공통 `timeframe`
- 공통 `option`
- 전략별 advanced input override
  - `Equal Weight`: rebalance interval
  - `GTAA`: top assets, signal interval
  - `Risk Parity Trend`: rebalance interval, vol window
  - `Dual Momentum`: top assets, rebalance interval

표시 항목:

- summary comparison table
- equity curve overlay
- drawdown overlay
- total return overlay
- focused strategy drilldown
- execution meta table

추가 보정:

- `GTAA`처럼 리밸런싱 간격이 더 긴 전략은 데이터 포인트가 성기므로,
  compare chart는 단순 line chart 대신 `line + point` 표현으로 조정했다.
  이 보정으로 sparse 전략도 overlay 화면에서 더 잘 보이게 된다.

### 2. 가중 포트폴리오 결합

비교 실행이 끝난 뒤,
선택된 전략 결과를 다시 조합해서
월별 weighted portfolio를 만들 수 있다.

예시:

- `Dual Momentum 50 + GTAA 50`

현재 first-pass 기본값:

- weight 입력은 퍼센트 기준
- date alignment 기본값은 `intersection`

## 구현 파일

- `app/web/pages/backtest.py`

## 검증 결과

검증 입력:

- `Dual Momentum`
- `GTAA`
- weights: `50 / 50`
- start: `2016-01-01`
- end: `2026-03-20`
- date policy: `intersection`

검증 결과:

- `Dual Momentum End Balance = 24600.7`
- `GTAA End Balance = 22589.1`
- `Weighted Portfolio End Balance = 23594.9`

## 현재 한계

- 가중 포트폴리오 결과는 아직 단일 비교 실행 결과를 재사용하는 first-pass 구조다
- compare overlay 차트 자체에는 아직 top 3 marker를 직접 찍지 않는다
- 포지션 비중 변화나 rebalance event marker는 아직 없다

## 다음 자연스러운 확장

- compare overlay 위 직접 marker annotation 추가
- 더 풍부한 시각화
  - strategy highlight toggle
  - contribution / rebalance annotation
- compare 실행 이력 저장
