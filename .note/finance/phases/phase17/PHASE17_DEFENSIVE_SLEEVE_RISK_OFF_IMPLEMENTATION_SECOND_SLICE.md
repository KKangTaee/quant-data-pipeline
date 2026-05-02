# Phase 17 Defensive Sleeve Risk-Off Implementation Second Slice

## 목표

strict annual family에서
full risk-off를 `cash only`가 아니라
optional defensive sleeve로 처리할 수 있게 만든다.

## 구현 범위

- strict annual family 3종:
  - `Quality`
  - `Value`
  - `Quality + Value`
- single / compare UI
- runtime wrapper
- sample helper
- core strategy

## 추가된 contract

- `risk_off_mode`
  - `cash_only`
  - `defensive_sleeve_preference`
- `defensive_tickers`
  - first slice default:
    - `BIL`
    - `SHY`
    - `LQD`

## 동작 규칙

- `Trend Filter`의 partial rejection은
  기존 `partial cash retention` 규칙을 따른다
- full risk-off state:
  - `market regime`
  - `underperformance guardrail`
  - `drawdown guardrail`
  에서만 defensive sleeve가 사용된다
- defensive sleeve ticker가 유효하지 않으면
  fallback은 기존처럼 cash다

## 코드 경로

- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py)
  - strict annual core simulation에
    `risk_off_mode`, `defensive_tickers` 추가
- [sample.py](/Users/taeho/Project/quant-data-pipeline/finance/sample.py)
  - strict annual DB-backed helper에 contract 전달
  - candidate universe와 sleeve ticker를 분리
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py)
  - runtime preflight / meta / warning / representative rerun wiring 추가
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/pages/backtest.py)
  - strict annual single / compare form에 `Risk-Off Fallback`, `Defensive Sleeve Tickers` 추가

## 구현 중 수정한 회귀

초기 wiring에서는 defensive sleeve ticker가
strict annual candidate universe filtering에 섞여
`Liquidity Excluded Count`를 오염시키는 문제가 있었다.

이번 second slice에서:

- candidate universe ticker
- sleeve ticker

를 분리해 이 문제를 수정했다.

## 현재 상태

- 코드 구현 완료
- compile / import smoke 통과
- representative rerun까지 완료
- representative rerun 결론은
  `same-gate lower-MDD rescue 없음`

## 다음 단계

- representative rerun 결과를 기준으로
  next structural lever는
  `concentration-aware weighting`
  으로 넘긴다
