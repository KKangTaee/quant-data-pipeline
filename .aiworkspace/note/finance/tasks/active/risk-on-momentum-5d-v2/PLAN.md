# Risk-On Momentum 5D V2 Plan

Status: Active

## Goal

`Backtest Analysis > Single Strategy > Risk-On Momentum 5D`를 Daily Swing 연구 lane 안에서 고도화한다.

## 이걸 하는 이유?

V1은 `close_based + fixed_pct` 중심의 1차 연구용 백테스트였다. V2는 실전 승인이나 자동 거래가 아니라, ATR 청산, macro ranking penalty, 보유기간 / 비용 / 민감도 / 안정성 비교를 같은 Backtest Analysis 화면에서 확인해 전략 후보의 과거 데이터 검증 품질을 높인다.

## Scope

- `finance/swing.py`와 분리 helper에서 ATR 기반 청산과 macro ranking penalty를 구현한다.
- `finance/swing_analysis.py`에서 exit / macro / holding comparison, sensitivity, stability, trade-cause, quality warning 결과를 만든다.
- Single Strategy form, runtime adapter, history replay, compare default runner, Swing Detail UI에 V2 설정과 결과를 연결한다.
- Practical Validation / Final Review / Selected Dashboard Daily Signal lane은 설계 후보로만 남기고 구현하지 않는다.

## Stop Condition

- Manual small universe로 fixed_pct와 atr_based가 실행된다.
- ranking_penalty가 hard_filter와 별도 mode로 실행되고 history replay에 보존된다.
- Swing Detail에 V2 comparison / sensitivity / stability / quality warning surface가 표시된다.
- Focused tests, compile, diff check, hygiene check, Browser QA를 수행하고 남은 gap을 기록한다.
