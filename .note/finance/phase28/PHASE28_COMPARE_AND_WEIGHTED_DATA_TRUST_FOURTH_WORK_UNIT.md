# Phase 28 Compare And Weighted Data Trust Fourth Work Unit

## 어떤 문서인가

Phase 28의 네 번째 작업 단위 기록이다.
이번 작업은 single strategy 결과에서만 보이던 Data Trust 개념을
compare, weighted portfolio, saved replay 흐름에서도 확인할 수 있게 확장한 작업이다.

## 쉽게 말하면

전략 하나를 실행할 때는 `Data Trust Summary`로 실제 결과 기간, 가격 최신성, 제외 ticker를 확인할 수 있었다.

하지만 여러 전략을 compare하거나 weighted portfolio로 섞을 때는
각 전략이 서로 같은 데이터 조건에서 계산됐는지 바로 보기 어려웠다.

이번 작업은 compare와 weighted portfolio에서도
“각 구성 전략의 데이터 상태가 어떤가?”를 먼저 확인할 수 있게 만든다.

## 왜 필요한가

Phase 28의 목표는 전략 family별 차이를 헷갈리지 않게 만드는 것이다.
annual strict, quarterly prototype, GRS, GTAA 같은 전략은 사용하는 데이터와 결과 기간이 다를 수 있다.

특히 compare나 saved replay에서는 결과가 좋아 보여도,
한 전략은 최신 가격까지 계산됐고 다른 전략은 특정 ticker 결측 때문에 더 짧은 기간으로 계산됐을 수 있다.
이 차이가 보이지 않으면 비교 자체를 잘못 해석할 수 있다.

## 이번 작업에서 한 일

- `Backtest > Compare & Portfolio Builder > Strategy Comparison`에 `Data Trust` 탭을 추가했다.
- compare 결과의 각 전략별로 아래 값을 표로 보여준다.
  - Requested End
  - Actual Result End
  - Result Rows
  - Price Freshness
  - Common Latest Price
  - Newest Latest Price
  - Latest-Date Spread
  - Excluded Tickers
  - Malformed Tickers
  - Warnings
  - Interpretation
- `Weighted Portfolio Result`에 `Component Data Trust` 탭을 추가했다.
- weighted portfolio history context에도 component별 data trust snapshot을 남긴다.
- saved portfolio replay로 생성되는 compare / weighted history에도 data trust rows를 남긴다.
- History의 selected record context에서도 compare / weighted data trust rows를 표로 다시 볼 수 있게 했다.

## 기대 효과

- compare 결과를 보기 전에 각 전략의 실제 결과 기간이 같은지 확인할 수 있다.
- weighted portfolio는 composite 결과이므로, 구성 전략별 데이터 상태를 먼저 볼 수 있다.
- saved replay로 다시 실행한 결과도 history에서 데이터 신뢰 조건을 다시 확인할 수 있다.
- Phase 29 후보 검토로 넘어갈 때 “이 후보 비교가 같은 데이터 조건에서 나온 것인가?”를 더 쉽게 확인할 수 있다.

## 주의할 점

- 이 표는 성과 비교표가 아니라 데이터 조건 확인표다.
- `Price Freshness = -`라고 해서 무조건 오류는 아니다. 해당 전략에 아직 전용 freshness surface가 없거나 기록이 없는 경우일 수 있다.
- `Actual Result End`가 요청 종료일보다 짧다면 전략 문제인지 데이터 문제인지 먼저 확인해야 한다.

## 확인 위치

- UI:
  - `Backtest > Compare & Portfolio Builder > Strategy Comparison > Data Trust`
  - `Backtest > Compare & Portfolio Builder > Weighted Portfolio Result > Component Data Trust`
  - `Backtest > History > Selected History Run > Saved Input & Context`
- 코드:
  - `app/web/pages/backtest.py`

## 한 줄 정리

Phase 28 네 번째 작업은 compare와 weighted portfolio에서도
각 구성 전략의 데이터 신뢰 조건을 먼저 확인할 수 있게 만든 작업이다.
