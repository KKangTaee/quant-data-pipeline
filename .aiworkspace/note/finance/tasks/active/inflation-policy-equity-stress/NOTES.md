# Inflation Policy Equity Stress Notes

## 2026-08-03 Intake

- current code는 `finance/inflation_policy_*.py` 평면 module 구조다.
- `sp500_monthly_valuation` Shiller history는 strict PIT forward-EPS source가 아니다.
- actual DB: official EPS 0 rows, Shiller monthly 1,867 rows, `^GSPC` price 2,524 rows,
  DGS10·DFII10·T10YIE vintage history는 존재한다.
- 실제 결과는 엔진 구현과 별개로 입력·검증 gate를 통과하기 전 `NOT_AVAILABLE`이다.
