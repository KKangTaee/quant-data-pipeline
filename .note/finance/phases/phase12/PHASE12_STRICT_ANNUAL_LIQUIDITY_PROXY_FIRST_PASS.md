# Phase 12 Strict Annual Liquidity Proxy First Pass

## 목적

- `Strict Annual` 3종을 실전형 contract로 한 단계 더 보강한다.
- 기존 `Minimum Price`, `Minimum History (Months)`만으로는
  "가격은 충분하지만 실제 거래대금은 너무 작은 종목"을 걸러내기 어렵다.
- 그래서 이번 pass에서는 복잡한 spread/AUM 모델 대신,
  DB 일봉 가격과 거래량으로 계산 가능한 `20일 평균 거래대금` 필터를 먼저 붙인다.

## 이번에 추가된 것

- 적용 대상
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- 새 입력값
  - `Min Avg Dollar Volume 20D ($M)`
- 의미
  - 각 리밸런싱 날짜 직전 최근 `20`거래일의 평균 거래대금이
    입력한 임계값보다 낮은 종목은 해당 날짜 후보에서 제외한다.
  - 단위는 `백만 달러`다.
  - `0`이면 비활성화다.

## 구현 방식

- 월말/년말로 이미 압축된 snapshot price row만으로는 유동성을 읽기 부족하므로,
  strict annual ranking input과 별도로 DB 일봉 price history를 다시 읽는다.
- 계산:
  - `dollar_volume = close * volume`
  - `avg_dollar_volume_20d = 최근 20거래일 평균`
- 리밸런싱 날짜별 snapshot candidate filter에서
  `Minimum Price` / `Minimum History`와 같은 위치에서 같이 적용한다.

## 노출 위치

- single form / compare override
  - `Real-Money Contract`
- result row
  - `Minimum Avg Dollar Volume 20D ($M)`
  - `Liquidity Excluded Ticker`
  - `Liquidity Excluded Count`
- `Real-Money`
  - threshold metric
  - excluded total / active-row summary
- `Execution Context`
  - `Min Avg Dollar Volume 20D`
  - liquidity excluded summary
- `Compare > Strategy Highlights`
  - `Min ADV20D ($M)`
- history / `Load Into Form`
  - contract 값 복원

## 현재 경계

- 이건 `later-pass liquidity proxy first pass`다.
- 아직 하지 않은 것:
  - bid/ask spread
  - AUM-aware contract
  - richer liquidity regime policy
  - ETF/stock별 다른 실전 임계값 정책

## 해석

- 이번 단계는 실전형 판단을 위한 "최소한의 유동성 바닥"을 먼저 추가한 것이다.
- 즉 완전한 거래비용 모델은 아니지만,
  너무 작은 거래대금을 가진 후보가 annual strict 결과를 왜곡하는 문제는 줄일 수 있다.
