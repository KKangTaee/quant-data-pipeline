# Phase 14 Controlled Factor Expansion Shortlist First Pass

## 목적

- Phase 14 calibration review 이후,
  strict annual family에서 factor search space를 무작정 크게 넓히지 않고
  **small controlled set**만 먼저 열기 위한 shortlist를 정리한다.
- 현재 DB / loader에는 저장되지만 UI에 아직 노출되지 않은 factor 중,
  sign 해석과 operator 설명이 비교적 명확한 후보만 선별한다.

## 현재 strict annual UI factor surface

근거:

- `app/web/pages/backtest.py`
- `finance/sample.py`

현재 UI 기본 surface:

- Quality strict options
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
  - `cash_ratio`
  - `operating_margin`
  - `debt_to_assets`
  - `debt_ratio`
  - `gross_margin`
- Value strict options
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `fcf_yield`
  - `operating_income_yield`
  - `per`
  - `pbr`
  - `psr`
  - `pcr`
  - `pfcr`
  - `ev_ebit`
  - `por`

## DB / loader에는 있지만 UI에는 안 열려 있던 후보

근거:

- `finance/loaders/factors.py`
- `finance/data/factors.py`

대표 후보:

- quality / robustness
  - `interest_coverage`
  - `ocf_margin`
  - `fcf_margin`
  - `net_debt_to_equity`
- value / deep value / balance-sheet
  - `liquidation_value`
  - `dividend_payout`
- growth / behavior-heavy
  - `gross_profit_growth`
  - `op_income_growth`
  - `net_income_growth`
  - `asset_growth`
  - `debt_growth`
  - `fcf_growth`
  - `shares_growth`
- profitability / mixed semantics
  - `gpa`

## First-pass shortlist

이번 first pass에서 실제 UI에 여는 small-set은 아래다.

### Quality strict additions

- `interest_coverage`
  - 계열: quality / robustness
  - sign: higher is better
  - 이유:
    - 부채 상환 여력을 보여주고
    - operator 설명이 명확하며
    - lower-is-better 예외 처리가 필요 없다.

- `ocf_margin`
  - 계열: quality / cash efficiency
  - sign: higher is better
  - 이유:
    - 회계 이익 대신 현금창출력 마진을 보강하는 quality 후보다.

- `fcf_margin`
  - 계열: quality / cash efficiency
  - sign: higher is better
  - 이유:
    - free cash flow 기반 quality를 따로 볼 수 있다.

- `net_debt_to_equity`
  - 계열: quality / balance-sheet robustness
  - sign: lower is better
  - 이유:
    - 현재 runtime lower-is-better 처리에 이미 포함돼 있어 sign 리스크가 낮다.

### Value strict additions

- `liquidation_value`
  - 계열: deep value / balance-sheet
  - sign: higher is better
  - 이유:
    - 기존 value surface가 ratio 중심이라,
      balance-sheet 기반 deep-value 후보를 small-set으로 하나 여는 의미가 있다.

## 이번 first pass에서 보류한 후보

- `dividend_payout`
  - 높은 값이 항상 좋은지 해석이 애매하다.
- `gpa`
  - profitability 성격이 강해서 quality/value 경계가 애매하다.
- growth 계열
  - `gross_profit_growth`
  - `op_income_growth`
  - `net_income_growth`
  - `asset_growth`
  - `debt_growth`
  - `fcf_growth`
  - `shares_growth`
  - 이유:
    - sign 해석과 strategy-family 배치가 더 민감하고,
      calibration workstream과 섞이기 쉽다.

## 구현 원칙

- default factor는 유지한다.
- new option만 추가한다.
- lower-is-better 추가 처리가 이미 있는 후보만 우선 사용한다.
- operator-facing docs와 glossary는 새 option 노출과 같이 맞춘다.

## 이번 first-pass 해석

- factor expansion은 필요하지만,
  이번 phase에서는 **controlled search widening**으로 다루는 것이 맞다.
- 따라서
  - sign이 명확하고
  - 현재 코드에서 안전하게 다루며
  - operator가 설명하기 쉬운 factor만 먼저 연다.
