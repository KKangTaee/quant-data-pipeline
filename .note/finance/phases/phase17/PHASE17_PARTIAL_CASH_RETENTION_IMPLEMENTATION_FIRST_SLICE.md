# Phase 17 Partial Cash Retention Implementation First Slice

## 목적
- strict annual family의 first structural downside lever로
  `partial cash retention`을 실제 코드에 연결한다.
- 목표는 새 전략 family를 여는 것이 아니라,
  기존 `Value / Quality / Quality + Value` strict annual 후보에서
  trend overlay partial rejection 시
  `survivor reweighting` 대신 `cash retention`을 실험할 수 있게 만드는 것이다.

## 이번 slice에서 구현된 것

- strict annual core strategy 로직인
  `finance.strategy.quality_snapshot_equal_weight(...)`
  가 `partial_cash_retention_enabled`를 받도록 확장됐다.
- 동작 범위는 현재 **Trend Filter의 부분 탈락**에 한정된다.
  - raw selected top-N 중 일부만 `Close < MA{window}`로 탈락하면
  - 옵션이 꺼져 있을 때:
    살아남은 종목들에 다시 100% 재배분한다.
  - 옵션이 켜져 있을 때:
    탈락한 슬롯 비중은 현금으로 남기고,
    살아남은 종목은 raw selected count 기준 비중만 보유한다.
- `market regime`와
  `underperformance / drawdown guardrail`의 전체 risk-off는
  여전히 기존대로 **전부 현금 처리**한다.

## 코드 경로

- strategy:
  - `finance/strategy.py`
- DB-backed strict annual sample/runtime bridge:
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
- Streamlit form / payload / prefill:
  - `app/web/pages/backtest.py`

## UI surface

- Single Strategy
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- Compare
  - 위 strict annual 3 family compare override

표시 이름은:
- `Retain Rejected Slots As Cash`

Glossary / help wording 기준 개념은:
- `Partial Cash Retention`

## 결과 surface에 남는 것

- input params:
  - `partial_cash_retention_enabled`
- row-level execution trace:
  - `Partial Cash Retention Enabled`
  - `Partial Cash Retention Active`
  - `Partial Cash Retention Base Count`
- selection interpretation:
  - partial cash retention이 실제로 적용된 리밸런싱이면
    "rejected slot(s) in cash"로 읽히고,
  - 꺼져 있으면
    "survivors reweighted"로 읽힌다.

## 검증

- `py_compile`
  - `finance/sample.py`
  - `finance/strategy.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
- synthetic smoke
  - 2종목 / Top N 2 / 1종목 trend 탈락 예제에서
  - off:
    - survivor 1종목에 `100%` 재배분
    - `Cash = 0`
  - on:
    - survivor 1종목에 `50%`
    - `Cash = 50%`
- DB-backed runtime wrapper smoke는
  code path 자체는 통과했지만,
  로컬 데이터 상태에서는
  strict statement shadow factor preflight가 먼저 막혀
  representative live rerun 숫자 검증은 아직 별도 데이터 준비가 필요하다.

## 현재 해석

- 이 slice는 same-gate lower-MDD practical candidate를
  **바로 보장하는 결과 문서가 아니라**
  그 질문을 실제 코드로 실험할 수 있게 만든
  first implementation slice다.
- 다음 단계는
  `Value`와 `Quality + Value` strongest/current anchor에
  이 contract를 넣어서 representative rerun을 다시 보는 것이다.

## 다음 작업

- `Value` strongest / lower-MDD near-miss에서
  partial cash retention representative rerun
- `Quality + Value` strongest practical point에서
  same-gate lower-MDD 여부 재검토
- 필요하면 다음 structural lever:
  - defensive sleeve risk-off
  - concentration-aware weighting
