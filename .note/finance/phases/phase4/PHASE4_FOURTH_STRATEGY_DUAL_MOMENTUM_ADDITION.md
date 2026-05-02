# Phase 4 Fourth Strategy Dual Momentum Addition

## 목적
이 문서는 Phase 4 첫 공개 price-only 전략 세트에
`Dual Momentum`을 네 번째 전략으로 추가한 결과를 기록한다.

## 구현 내용

- `app/web/runtime/backtest.py`
  - `run_dual_momentum_backtest_from_db(...)` 추가
- `app/web/runtime/__init__.py`
  - public export 추가
- `app/web/pages/backtest.py`
  - 전략 선택기에 `Dual Momentum` 추가
  - Dual Momentum preset/manual 실행 form 추가
  - submit 시 DB-backed wrapper 실행 연결

## 입력 범위

first-pass UI는 기존 price-only 전략 패턴을 유지한다.

- universe mode
- preset 또는 manual tickers
- start / end
- advanced:
  - timeframe
  - option

다음 항목은 아직 공개하지 않았다.

- `top`
- `cash_ticker`
- lookback 관련 세부 파라미터

이 값들은 현재 sample/runtime 기준 기본값을 유지한다.

## 검증 결과

검증 입력:

- tickers: `QQQ, SPY, IWM, SOXX, BIL`
- start: `2016-01-01`
- end: `2026-03-20`

검증 결과:

- `strategy_name = Dual Momentum`
- `End Balance = 24600.7`

즉 현재 Backtest 탭의 공개 DB-backed price-only 전략은 아래 4개다.

- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`

## 의미

이 추가로 인해 Phase 4 first-pass 백테스트 UI는
기존 `finance/sample.py`의 대표 price-only 전략 4종을
모두 DB-backed runtime wrapper 기준으로 노출할 수 있게 되었다.
