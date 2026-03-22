# Phase 3 Loader / Runtime Validation Examples

## 목적
이 문서는 Phase 3 loader / runtime 경로를 실제로 검증할 때
바로 실행할 수 있는 최소 예시를 모아둔 reference다.

이 문서는
- 어떤 경로를 검증할지 정의한 smoke scenario 문서와 달리
- 실제 호출 예시와 확인 포인트를 빠르게 복붙할 수 있게 정리한다.

관련 문서:
- `.note/finance/phase3/PHASE3_REPEATABLE_DB_BACKED_SMOKE_SCENARIOS.md`

---

## 1. Price Loader -> Strategy Dict

목적:
- price loader와 runtime adapter가 DB row를
  전략 입력 형태 `{ticker: DataFrame}`로 바꾸는지 확인

```python
from finance.loaders import load_price_strategy_dfs

dfs = load_price_strategy_dfs(
    symbols=['AAPL', 'MSFT', 'GOOG'],
    start='2024-01-01',
    end='2024-12-31',
    timeframe='1d',
)

print(dfs.keys())
print(dfs['AAPL'].head())
```

확인 포인트:
- key가 symbol list와 맞는지
- 각 DataFrame에 `Date`, `Close`가 존재하는지

---

## 2. BacktestEngine DB Price Path

목적:
- engine 기준 DB-backed entrypoint가 살아 있는지 확인

```python
from finance.engine import BacktestEngine

engine = (
    BacktestEngine(['AAPL', 'MSFT', 'GOOG'], period='db', option='month_end')
    .load_ohlcv_from_db(start='2024-01-01', end='2024-12-31', timeframe='1d')
    .filter_by_period()
    .align_dates()
)

print(engine.dfs.keys())
print(engine.dfs['AAPL'].tail())
```

확인 포인트:
- `engine.dfs`가 비어 있지 않은지
- 월말 기준으로 정렬/정규화된 row가 생성되는지

---

## 3. DB-Backed Equal Weight Sample

목적:
- 가장 단순한 DB-backed sample 전략 실행 확인

```python
from finance.sample import get_equal_weight_from_db

df = get_equal_weight_from_db(
    tickers=['AAPL', 'MSFT', 'GOOG'],
    start='2024-01-01',
    end='2024-12-31',
    interval=21,
)

print(df.tail())
```

확인 포인트:
- 예외 없이 실행
- `Date`, `Total Balance`, `Total Return` 존재

---

## 4. Direct vs DB Portfolio Parity

목적:
- canonicalized DB path가 legacy direct path와 같은 결과를 재현하는지 확인

```python
from finance.sample import portfolio_sample, portfolio_sample_from_db

# reference path
portfolio_sample()

# DB-backed path
portfolio_sample_from_db(start='2016-01-01', end='2026-03-20', timeframe='1d')
```

확인 포인트:
- 각 전략의 시작일 동일
- 종료일 동일
- 성과 요약 지표 동일

비고:
- 현재 기준 핵심 회귀 검증 예시

---

## 5. Broad Fundamentals Loader

목적:
- broad fundamentals history / snapshot 조회 확인

```python
from finance.loaders import load_fundamentals, load_fundamental_snapshot

history = load_fundamentals(
    ['AAPL', 'MSFT'],
    freq='annual',
    start='2022-01-01',
    end='2025-12-31',
)

snapshot = load_fundamental_snapshot(
    ['AAPL', 'MSFT'],
    as_of_date='2025-12-31',
    freq='annual',
)

print(history.tail())
print(snapshot)
```

확인 포인트:
- history는 symbol-period 시계열
- snapshot은 symbol당 1행
- `pretax_income`, `shareholders_equity`, `gross_profit_source` 같은 새 컬럼이 존재하는지

---

## 6. Broad Factors Loader

목적:
- broad factors history / snapshot / matrix 조회 확인

```python
from finance.loaders import load_factors, load_factor_snapshot, load_factor_matrix

history = load_factors(
    ['AAPL', 'MSFT'],
    freq='annual',
    start='2022-01-01',
    end='2025-12-31',
)

snapshot = load_factor_snapshot(
    ['per', 'pbr', 'book_to_market', 'revenue_growth'],
    ['AAPL', 'MSFT'],
    as_of_date='2025-12-31',
    freq='annual',
)

matrix = load_factor_matrix(
    'book_to_market',
    ['AAPL', 'MSFT'],
    freq='annual',
    start='2022-01-01',
    end='2025-12-31',
)

print(history.tail())
print(snapshot)
print(matrix)
```

확인 포인트:
- history에 `price_date`, `pit_mode`, `sales_yield`, `gross_margin` 등이 있는지
- snapshot이 symbol당 1행인지
- matrix가 `index=period_end`, `columns=symbol`인지

---

## 7. Detailed Statement Broad / Strict

목적:
- statement loader의 broad read와 strict snapshot read를 모두 확인

```python
from finance.loaders import load_statement_values, load_statement_snapshot_strict

values = load_statement_values(
    ['AAPL', 'MSFT'],
    freq='annual',
    start='2024-01-01',
    end='2025-12-31',
)

snapshot = load_statement_snapshot_strict(
    ['AAPL', 'MSFT'],
    as_of_date='2025-12-31',
    freq='annual',
)

print(values.head())
print(snapshot.head())
```

확인 포인트:
- broad values는 long-form raw fact row인지
- strict snapshot은 `available_at <= as_of_date` 기준을 따르는지

---

## 8. Fundamentals / Factors Rebuild Sample

목적:
- 최근 hardening된 summary / derived layer 재수집 경로 확인

```python
from finance.data.fundamentals import upsert_fundamentals
from finance.data.factors import upsert_factors

symbols = ['AAPL', 'MSFT']

print(upsert_fundamentals(symbols, freq='annual', chunk_size=2, sleep=0.0, max_retry=2))
print(upsert_factors(symbols, freq='annual'))
```

확인 포인트:
- `nyse_fundamentals` blank row 제거가 유지되는지
- 새 source metadata가 들어가는지
- `nyse_factors`에 새 factor / price metadata가 들어가는지

---

## 9. 추천 사용 순서

### 일반 코드 변경 후

1. `Price Loader -> Strategy Dict`
2. `DB-Backed Equal Weight Sample`
3. `Direct vs DB Portfolio Parity`

### fundamentals / factors 변경 후

1. `Fundamentals / Factors Rebuild Sample`
2. `Broad Fundamentals Loader`
3. `Broad Factors Loader`

### statement loader 변경 후

1. `Detailed Statement Broad / Strict`

---

## 결론

이 문서의 예시들은 Phase 3 loader/runtime 레이어의
가장 짧은 재검증 경로를 제공한다.

즉 이후 수정 시:
- smoke scenario 문서로 “무엇을 볼지” 확인하고
- 이 문서에서 “어떻게 실행할지” 바로 따라가면 된다.
