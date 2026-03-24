# Phase 4 Statement-Driven Quality Prototype First Pass

## 목적
이 문서는 sample-universe 기준의 `statement-driven quality prototype` first-pass 구현을 기록한다.

이 경로의 목적은:
- 현재 public `Quality Snapshot`의 broad-research factor path와 별개로
- `nyse_financial_statement_values` strict snapshot만으로
- quality ranking backtest가 실제로 돌아갈 수 있는지 확인하는 것이다.

현재 성격:
- `prototype`
- `sample-universe only`
- `strict annual statement snapshot`
- 아직 public UI 전략으로 노출하지 않음

---

## 구현 범위

추가/변경된 코드:
- `finance/data/fundamentals.py`
  - `build_fundamentals_from_statement_snapshot(...)`
- `finance/data/factors.py`
  - `calculate_quality_factors_from_fundamentals(...)`
  - `build_quality_factor_snapshot_from_statement_snapshot(...)`
- `finance/sample.py`
  - `get_statement_quality_snapshot_from_db(...)`
- `app/web/runtime/backtest.py`
  - `run_statement_quality_prototype_backtest_from_db(...)`
- `app/web/runtime/__init__.py`
  - prototype runtime wrapper export

핵심 구조:
1. DB price history 로드
2. rebalance date별 strict statement snapshot 조회
3. statement row를 normalized fundamentals로 변환
4. fundamentals에서 quality factor snapshot 생성
5. 기존 `quality_snapshot_equal_weight(...)` 재사용

즉 전략 시뮬레이션은 새로 쓰지 않고,
`strict statement -> fundamentals -> factors` preprocessing만 새로 붙인 형태다.

---

## 현재 factor 구성

first-pass에서 사용하는 quality factor:
- `roe`
- `gross_margin`
- `operating_margin`
- `debt_ratio`

계산 기준:
- `roe = net_income / shareholders_equity`
- `gross_margin = gross_profit / revenue`
- `operating_margin = operating_income / revenue`
- `debt_ratio = total_debt / equity`

fallback:
- `gross_profit` direct row가 없으면 `revenue - cost_of_revenue`
- `total_debt`가 직접 완성되지 않으면
  - `LongTermDebt`
  - `LongTermDebtCurrent`
  - `ShortTermBorrowings`
  - `ShortTermDebt`
  합으로 계산
- debt component가 전부 없으면 `liabilities / equity` fallback

주의:
- `debt_ratio` fallback은 broad factor path와 완전히 같은 의미라고 보긴 어렵다
- 이 경로는 아직 statement-driven feasibility prototype으로 해석해야 한다

---

## 검증 결과

검증 입력:
- `tickers = ['AAPL', 'MSFT', 'GOOG']`
- `start = '2023-01-01'`
- `end = '2026-03-20'`
- `statement_freq = 'annual'`
- `top_n = 2`
- `rebalance_interval = 1`

결과:
- first active date: `2023-01-31`
- total rows: `39`
- final `End Balance = 23645.4`
- `CAGR = 0.316218`
- `Sharpe Ratio = 1.587924`
- `Maximum Drawdown = -0.143915`

현재 동작 해석:
- `2023-01-31`에는 `AAPL`만 investable
- 이후 `GOOG`, `MSFT` coverage가 늘어나며 sample-universe quality ranking이 동작

---

## 현재 한계

이 prototype은 아직 아래 한계를 가진다.

1. `2016` 시작 backtest용 public path는 아님
- sample-universe targeted backfill 후에도 strict annual statement coverage가 충분히 길지 않다

2. `MSFT` coverage가 늦다
- sample-universe strict statement usable history가 균등하지 않다

3. annual-only prototype
- quarterly strict statement quality path는 아직 범위 밖

4. public UI 미노출
- 현재는 backend/runtime/sample validation 용도다

---

## 결론

이번 first-pass로 확인된 점:
- statement-driven quality path는 실제로 구현 가능하다
- strict statement snapshot만으로 sample-universe quality prototype을 돌릴 수 있다
- 다만 현재 coverage 깊이로는 아직 public long-history quality strategy를 대체하기엔 이르다

즉 다음 결정은:
- 이 prototype을 더 다듬어 public 후보로 키울지
- 아니면 statement coverage/backfill을 더 늘릴지
중 하나다.
