# Phase 4 Statement Shadow Shares Enhancement First Pass

## 목적
이 문서는 `nyse_fundamentals_statement` / `nyse_factors_statement`
shadow path에서 `shares_outstanding` 부재로 valuation 계열이 비던 문제를
first-pass 수준으로 보강한 기록이다.

---

## 문제

초기 shadow backfill 상태:
- accounting quality 계열
  - `gross_margin`
  - `operating_margin`
  - `roe`
  - `debt_ratio`
  는 잘 채워졌음
- 하지만 statement ledger에 sample-universe 기준
  `shares_outstanding` concept row가 거의 없어
  - `shares_outstanding`
  - `market_cap`
  - `per`
  - `pbr`
  같은 valuation 계열이 비어 있었다

실제 확인:
- `AAPL/MSFT/GOOG`에서
  `dei:EntityCommonStockSharesOutstanding`,
  `us-gaap:CommonStockSharesOutstanding`,
  `us-gaap:CommonSharesOutstanding`
  row는 current local statement ledger에서 발견되지 않았다

---

## 적용한 보강

추가된 보강:
- statement-derived `shares_outstanding`이 없을 때
- broad summary table `nyse_fundamentals`의
  nearest-period row에서 `shares_outstanding`을 fallback으로 가져오도록 함

구현 위치:
- `finance/data/fundamentals.py`

현재 fallback 규칙:
- 동일 `symbol`
- 동일 `freq`
- nearest `period_end`
- tolerance: `15 days`

source 표시는:
- `fallback:ordinary_shares_number`
- `fallback:share_issued_minus_treasury`
처럼 broad row의 기존 source를 그대로 prefix하여 남긴다

즉 이 값은:
- statement ledger direct 값이 아니라
- broad summary fallback 값이라는 점이 metadata에 드러난다

---

## sample-universe 결과

대상:
- `AAPL`
- `MSFT`
- `GOOG`
- `annual`

결과:
- `shares_outstanding`이 채워진 shadow fundamentals row:
  - `10 / 12`
- `market_cap`이 채워진 shadow factor row:
  - `10 / 12`

남는 빈 row:
- `AAPL 2021-09-25`
- `GOOG 2021-12-31`

이 둘은 broad fallback도 같은 period 근처 row가 충분하지 않아
현재 first-pass에서는 계속 `NULL`로 남는다.

---

## 의미

이번 보강으로:
- shadow path가 quality/accounting 검증 전용에서
- 부분적으로 valuation factor까지 읽을 수 있는 상태로 올라왔다

하지만 현재 해석은 분명히 해야 한다.

- quality/accounting 계열:
  - statement-driven 의미가 강함
- shares / market_cap / valuation 계열:
  - 현재는 broad summary fallback이 섞인 hybrid 상태

즉 strict statement-derived valuation history라고 부르기에는 아직 이르다.

---

## 결론

현재 shadow path는:
- accounting quality factor 검증에는 충분히 유용하고
- valuation 계열도 상당 부분 채워지지만
- 완전한 statement-only valuation history는 아니다

다음 판단 포인트:
- fallback 허용 범위를 더 넓힐지
- shares source를 다른 strict path로 더 보강할지
- 아니면 현재 수준을 prototype/public-candidate 전 단계로 유지할지
