# Phase 4 Strict Annual Quality Factor Set Refresh First Pass

## 목적

- `Quality Snapshot (Strict Annual)`의 기본 factor set을
  coverage-first 방향으로 다시 고정한다.
- factor set을 바꾼 뒤
  `US Statement Coverage 100 / 300`
  기준으로 public default 동작을 다시 검증한다.

## 변경 내용

이전 strict annual default:
- `roe`
- `gross_margin`
- `operating_margin`
- `debt_ratio`

현재 strict annual default:
- `roe`
- `roa`
- `net_margin`
- `asset_turnover`
- `current_ratio`

의미:
- 기존 default는 strict annual wider-universe 기준에서
  `gross_margin`, `debt_ratio` coverage가 약했다.
- 따라서 현재 public strict annual quality는
  profitability / efficiency / balance-sheet strength를 더 안정적으로 얻을 수 있는
  coverage-first factor set으로 재정렬되었다.

## 코드 반영 위치

- `finance/sample.py`
  - `QUALITY_STRICT_DEFAULT_FACTORS`
  - strict annual sample / shadow sample 기본값 갱신
- `app/web/runtime/backtest.py`
  - strict annual runtime default factor 갱신
- `app/web/pages/backtest.py`
  - single strategy strict annual form 기본값 갱신
  - compare mode strict annual form 기본값 갱신
  - history prefill fallback 기본값 갱신

## 검증

조건:
- `start = 2016-01-01`
- `end = 2026-03-20`
- `option = month_end`
- `top_n = 2`

### 1. US Statement Coverage 100

- elapsed: `3.319s`
- first active date: `2016-01-29`
- active rows: `124`
- `End Balance = 107324.3`
- `CAGR = 0.263759`
- `Sharpe Ratio = 0.904147`
- `Maximum Drawdown = -0.351943`

### 2. US Statement Coverage 300

- elapsed: `9.359s`
- first active date: `2016-01-29`
- active rows: `124`
- `End Balance = 366404.7`
- `CAGR = 0.426472`
- `Sharpe Ratio = 1.398554`
- `Maximum Drawdown = -0.239303`

## 현재 의미

- `Quality Snapshot (Strict Annual)`은 이제
  단순히 strict annual candidate인 수준을 넘어서,
  wider-universe strict annual public default까지
  한 단계 더 정리된 상태다.
- 다음 universe 확대를 논의할 때도
  기존 legacy 4-factor set보다
  현재 coverage-first default를 기준으로 보는 편이 맞다.

## 다음 단계

- `Coverage 300 -> wider universe` 확장 전,
  이 factor set으로 `Coverage 100 / 300` 추가 해석을 먼저 보는 것이 자연스럽다.
- 그 다음 annual coverage를 더 넓히고,
  이후 `NYSE 전체` strict annual feasibility를 다시 판단한다.
