# Phase 4 Strict Annual Operator Automation First Pass

## 목적

- strict annual maintenance를 반복 가능한 operator flow로 만든다.

## 이번 추가

- 새 helper job:
  - `run_strict_annual_shadow_refresh(...)`

## 수행 흐름

1. `Extended Statement Refresh` (`annual`, configurable `periods`)
2. `nyse_fundamentals_statement` shadow rebuild
3. `nyse_factors_statement` shadow rebuild

## 의미

- strict annual family 운영 시
  operator가 매번 개별 단계를 수동으로 기억하지 않아도 되는 baseline helper가 생겼다.
- wider-universe annual coverage 실험과 shadow refresh를 같은 흐름으로 재사용할 수 있다.

## smoke check

- sample universe:
  - `AAPL`, `MSFT`, `GOOG`
  - `periods = 1`
- result:
  - `status = success`
  - `rows_written = 581`
  - steps:
    - `extended_statement_refresh`
    - `statement_fundamentals_shadow`
    - `statement_factors_shadow`

## operator 해석

- public UI default를 바로 바꾸는 기능은 아니다.
- 하지만 strict annual family를 반복 관리하는 기반으로는 충분한 first pass다.

