# Phase 4 Statement-Driven Fundamentals / Factors Backfill Plan First Pass

## 목적
이 문서는 `statement-driven fundamentals/factors backfill`을
실제로 시작하기 전에 필요한 구조 선택과 운영 순서를 정리한다.

이번 문서의 초점:
- 지금 스키마에서 무엇이 바로 가능한지
- 무엇이 아직 위험한지
- 어떤 순서로 backfill을 여는 게 가장 안전한지

---

## 현재 전제

현재 broad-research public path:

```text
yfinance summary
  -> nyse_fundamentals
  -> nyse_factors
```

현재 새로 열린 statement-driven path:

```text
nyse_financial_statement_values / filings
  -> strict statement snapshot
  -> normalized fundamentals
  -> quality factor snapshot
```

즉 statement-driven path의 계산 경로는 생겼지만,
**과거 전체 history를 다시 채우는 backfill 운영 경로는 아직 없다.**

---

## 지금 바로 드러나는 핵심 제약

### 1. 현재 `nyse_fundamentals` / `nyse_factors`는 broad row와 statement-driven row를 동시에 담기 어렵다

현재 key:
- `nyse_fundamentals`
  - `UNIQUE KEY uk_symbol_freq_period (symbol, freq, period_end)`
- `nyse_factors`
  - `UNIQUE KEY uk_symbol_freq_period (symbol, freq, period_end)`

의미:
- 같은 `symbol/freq/period_end`에 대해
  broad-research row와 statement-driven row를 동시에 저장할 수 없다
- 즉 지금 테이블에 바로 backfill을 넣으면
  **현재 public broad row를 덮어쓰는 선택**이 된다

이건 중요한 설계 결정이다.

---

## 현실적인 선택지

### Option A. 기존 `nyse_fundamentals` / `nyse_factors`를 직접 덮어쓴다

의미:
- statement-driven backfill 결과를 기존 테이블에 바로 넣는다

장점:
- 테이블 수가 늘지 않는다
- public loader를 바로 전환하기 쉽다

단점:
- 현재 broad public path를 바로 깨뜨릴 수 있다
- 비교/검증 기간이 짧아진다
- partial coverage 상태에서 테이블 의미가 더 혼란스러워질 수 있다

판단:
- 지금 시점에는 이르다

### Option B. statement-driven shadow table을 따로 만든다

예시:
- `nyse_fundamentals_statement`
- `nyse_factors_statement`

장점:
- broad public path를 보존할 수 있다
- coverage audit / diff 비교 / selective promotion이 쉽다
- 가장 안전하다

단점:
- 테이블이 늘어난다
- loader 분기가 하나 더 생긴다

판단:
- **현재 가장 추천되는 방향**

### Option C. 기존 테이블 key를 확장해서 row mode를 같이 저장한다

예시:
- unique key에 `source_mode` 또는 `pit_mode` 포함

장점:
- 테이블은 유지하면서 multiple mode를 함께 저장 가능

단점:
- 기존 schema / loader / public path를 더 넓게 건드려야 한다
- 지금 시점에는 리팩터링 파급이 크다

판단:
- 장기적으로는 가능하지만 지금은 무겁다

---

## 현재 추천 전략

현재는 아래 순서가 가장 안전하다.

1. `coverage audit`
   - 어떤 symbol/freq에서 strict statement usable history가 얼마나 있는지 요약
2. `sample-universe / targeted-universe shadow backfill`
   - broad path를 건드리지 않고 statement-driven rows를 별도 저장
3. `diff / validation`
   - broad vs statement-driven 비교
   - quality backtest usable start date 비교
4. `promotion decision`
   - 충분히 길고 안정적이면 public 후보로 승격

즉 지금 바로 기존 public tables를 덮어쓰는 것은 추천하지 않는다.

---

## 이번 first-pass에서 바로 추가한 준비물

### coverage audit helper

추가된 loader:
- `finance/loaders/financial_statements.py`
  - `load_statement_coverage_summary(...)`

역할:
- strict statement row 기준으로 symbol별 coverage를 빠르게 요약
- 확인 항목:
  - `strict_rows`
  - `distinct_accessions`
  - `distinct_period_ends`
  - `min_period_end`
  - `max_period_end`
  - `min_available_at`
  - `max_available_at`
  - `statement_types`

즉 backfill 전에
“이 심볼이 실제로 얼마나 usable한가”
를 먼저 볼 수 있다.

---

## 현재 권장 다음 단계

가장 자연스러운 다음 단계:

1. `shadow table 방향`을 사용자와 확정
2. 그 다음
   - statement-driven fundamentals shadow schema
   - statement-driven factors shadow schema
   - targeted backfill writer
   를 순서대로 구현

현재 상태 업데이트:
- 위 first-pass는 실제로 구현되었다
- sample-universe (`AAPL/MSFT/GOOG`, annual) 기준
  - `nyse_fundamentals_statement`
  - `nyse_factors_statement`
  write/read validation까지 완료되었다
- 따라서 다음 결정은 저장 전략 자체보다
  - coverage 확대
  - valuation 필드 보강
  - public 후보 승격 여부
  쪽으로 이동했다

---

## 결론

현재 `statement-driven backfill`은
바로 대규모 write를 시작하는 단계가 아니라,
**어떤 저장 전략으로 시작할지 먼저 고정해야 하는 단계**다.

현재 기준 추천:
- broad public path는 유지
- statement-driven path는 shadow table로 먼저 backfill
- 충분히 검증된 뒤 승격 여부 판단
