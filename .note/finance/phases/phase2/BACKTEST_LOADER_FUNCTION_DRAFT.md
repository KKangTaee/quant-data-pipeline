# Backtest Loader Function Draft

## 목적
이 문서는 PHASE2의 백테스트 준비 단계에서,
DB 기반 전략 실행을 위해 필요한 loader 계층의 초안 함수 목록을 정의한다.

핵심 원칙:
- 전략 코드는 테이블명이나 SQL을 직접 알지 않는다
- loader는 DB 원천을 전략 입력 형태로 정리한다
- 웹 UI와 전략 엔진이 같은 loader 계층을 공유할 수 있어야 한다

---

## 설계 방향

loader는 크게 5개 축으로 나눈다.

1. universe loader
2. price loader
3. fundamentals loader
4. factor loader
5. detailed financial statement loader

이 계층은 최종적으로 예를 들면 아래 형태의 모듈로 모일 수 있다.

- `finance/loaders/universe.py`
- `finance/loaders/price.py`
- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `finance/loaders/financial_statements.py`

---

## 1. Universe Loader

### 역할
- 전략 실행 대상 심볼 집합을 결정
- stock / etf / filtered universe / custom list를 표준화

### 초안 함수

```python
load_universe(
    source: str,
    *,
    kind: str | None = None,
    sector: str | None = None,
    country: str | None = None,
    on_filter: bool = True,
    limit: int | None = None,
) -> list[str]
```

### 예상 source 예시
- `manual`
- `nyse_stocks`
- `nyse_etfs`
- `nyse_stocks_etfs`
- `profile_filtered_stocks`
- `profile_filtered_etfs`
- `profile_filtered_stocks_etfs`

### 내부 활용 후보
- `finance.data.asset_profile.load_symbols_from_asset_profile`
- `finance_meta.nyse_stock`
- `finance_meta.nyse_etf`

---

## 2. Price Loader

### 역할
- OHLCV를 전략 입력용 가격 DataFrame으로 반환
- 심볼 / 날짜 / timeframe 기준 로드

### 초안 함수

```python
load_price_history(
    symbols: list[str],
    *,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> pd.DataFrame
```

```python
load_price_matrix(
    symbols: list[str],
    *,
    field: str = "close",
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> pd.DataFrame
```

### 반환 형태
- `load_price_history`
  - long-form DataFrame
  - columns 예시:
    - `symbol`
    - `date`
    - `open`
    - `high`
    - `low`
    - `close`
    - `adj_close`
    - `volume`

- `load_price_matrix`
  - wide matrix
  - index = `date`
  - columns = `symbol`

### 내부 활용 후보
- `finance.data.data.load_ohlcv_many_mysql`

---

## 3. Fundamentals Loader

### 역할
- 정규화된 fundamentals를 전략 입력에 맞게 반환
- period_end 기준 재무 스냅샷 제공

### 초안 함수

```python
load_fundamentals(
    symbols: list[str] | None = None,
    *,
    freq: str = "annual",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame
```

```python
load_fundamental_snapshot(
    symbols: list[str],
    *,
    as_of_date: str,
    freq: str = "annual",
) -> pd.DataFrame
```

### 반환 형태
- long-form fundamentals DataFrame
- 필요시 `as_of_date` 기준 latest available snapshot

### 주요 컬럼 예시
- `symbol`
- `period_end`
- `freq`
- `total_revenue`
- `gross_profit`
- `operating_income`
- `net_income`
- `total_assets`
- `total_debt`
- `operating_cash_flow`
- `free_cash_flow`
- `shares_outstanding`

### 비고
- `load_fundamental_snapshot(...)`는 나중에 point-in-time 강화 시 중요

---

## 4. Factor Loader

### 역할
- 이미 계산된 factor 테이블을 전략 입력 형태로 반환

### 초안 함수

```python
load_factors(
    symbols: list[str] | None = None,
    *,
    freq: str = "annual",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame
```

```python
load_factor_matrix(
    factor_name: str,
    symbols: list[str] | None = None,
    *,
    freq: str = "annual",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame
```

```python
load_factor_snapshot(
    factor_names: list[str],
    symbols: list[str],
    *,
    as_of_date: str,
    freq: str = "annual",
) -> pd.DataFrame
```

### 반환 형태
- `load_factors`
  - long-form factor table
- `load_factor_matrix`
  - index = `period_end`
  - columns = `symbol`
- `load_factor_snapshot`
  - 한 시점의 cross-sectional factor table

### 주요 컬럼 예시
- `per`
- `pbr`
- `psr`
- `ev_ebit`
- `roe`
- `roa`
- `gpa`
- `current_ratio`
- `debt_ratio`
- `asset_growth`
- `shares_growth`

---

## 5. Detailed Financial Statement Loader

### 역할
- 장기 이력과 계정 수준 데이터를 읽는다
- 커스텀 팩터 계산과 과거 회계 항목 추적을 지원한다
- `values`가 raw ledger의 실제 source of truth이고,
  `labels`는 operator-facing summary 계층으로 취급한다

### 초안 함수

```python
load_statement_labels(
    symbols: list[str] | None = None,
    *,
    statement_type: str | None = None,
) -> pd.DataFrame
```

```python
load_statement_values(
    symbols: list[str] | None = None,
    *,
    freq: str | None = None,
    start: str | None = None,
    end: str | None = None,
    statement_type: str | None = None,
) -> pd.DataFrame
```

```python
load_statement_pivot(
    symbols: list[str],
    *,
    labels: list[str],
    freq: str | None = None,
    start: str | None = None,
    end: str | None = None,
    statement_type: str | None = None,
) -> pd.DataFrame
```

```python
load_statement_snapshot(
    symbols: list[str],
    *,
    labels: list[str],
    as_of_date: str,
    freq: str | None = None,
) -> pd.DataFrame
```

### 비고
- 이 loader는 `nyse_fundamentals` 대체가 아니라 보완/확장 목적
- 특히 4년보다 긴 재무 시계열 확보와 커스텀 팩터 재계산에 중요
- 핵심 loader는 `load_statement_values(...)` / `load_statement_snapshot(...)`
- `load_statement_labels(...)`는 UI/해석 보조용 성격이 더 강하다
- semantic identity는 가능한 한
  `accession_no`, `concept`, `period_end`, `statement_type`, `unit`
  조합을 기준으로 해석한다

---

## 6. 공통 보조 함수 초안

### 역할
- loader 입력을 공통 규격으로 정리
- universe source와 manual symbol list를 일관되게 해석

### 초안 함수

```python
resolve_loader_symbols(
    *,
    symbols: list[str] | None = None,
    universe_source: str | None = None,
) -> list[str]
```

```python
normalize_date_range(
    *,
    start: str | None = None,
    end: str | None = None,
) -> tuple[str | None, str | None]
```

---

## 1차 구현 우선순위

### 우선 구현
1. `load_universe(...)`
2. `load_price_history(...)`
3. `load_fundamentals(...)`
4. `load_factors(...)`

### 그 다음 구현
5. `load_factor_snapshot(...)`
6. `load_fundamental_snapshot(...)`

### 후속 구현
7. `load_statement_values(...)`
8. `load_statement_pivot(...)`
9. `load_statement_snapshot(...)`

---

## 다음 단계 연결

다음 TODO는 아래와 연결된다.

- `D-3 price / fundamentals / factors / detailed statements / universe loader 입력 계약 정리`
- `D-4 point-in-time 주의사항을 loader 설계 항목으로 분리`

즉 이번 문서는 “무슨 함수가 필요한가”를 정의한 초안이고,
다음 문서/작업은 “그 함수들의 입력 계약과 시점 규칙을 어떻게 고정할 것인가”에 초점을 맞춘다.
