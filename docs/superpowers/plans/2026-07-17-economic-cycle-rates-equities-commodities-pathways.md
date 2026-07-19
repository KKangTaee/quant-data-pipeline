# Economic Cycle Rates, Equities, and Commodities Pathways Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 경제사이클 화면의 3·4·5차를 완성해 채권·금리 구조, S&P 500, WTI·구리·금을 실제 저장 데이터와 측정 가능한 관측 경로로 설명한다.

**Architecture:** 기존 `macro_series_observation`, `futures_ohlcv`, `nyse_price_history`, `sp500_index_earnings`를 DB-only loader로 읽고, `finance/economic_cycle_asset_pathways.py`가 혼합 빈도의 관측 경로를 결정론적으로 조립한다. Overview service는 실패를 자산군별로 격리하고 React는 `현재 움직임 -> 함께 관찰된 경로 -> 현재 해석 -> 향후 확인 조건`만 렌더링한다.

**Tech Stack:** Python 3.12, pandas 3, MySQL 8, pytest, Streamlit custom component, React 18, TypeScript 5, Vite 6

## Global Constraints

- UI에서 provider, FRED, EIA, yfinance를 직접 호출하지 않는다.
- 3차는 `DGS2`, `DGS10`, derived `DGS10-DGS2`, `DFII10`, `T10YIE`만 사용하고 채권 가격·국채선물은 제외한다.
- 4차 주식 대표값은 S&P 500 하나이며 `^GSPC` 우선, `SPY` fallback이다.
- S&P 이익은 완료된 `quarterly + as_reported + actual` 8개 분기로 현재/전년 TTM을 만들 수 있을 때만 성장률을 계산한다.
- 5차는 `CL=F`, `HG=F`, 기존 `GC=F`만 사용하고 천연가스와 은은 제외한다.
- WTI 수급은 EIA 공식 `WCESTUS1`, `WCRFPUS2`, `WRPUPUS2` 주간 XLS만 사용한다.
- 가격은 5·21·63거래일 수익률, 금리·스프레드는 같은 horizon의 bp 변화, EIA는 최근 4주와 전년 동기 변화로 표시한다.
- 일별 시계열은 5 business day, 주간 EIA는 14 calendar day, 분기 EPS는 180 calendar day를 넘으면 stale이다.
- materiality는 기존 reference-date 이전 최근 5년 동일 horizon 절대변화 중앙값을 재사용한다.
- 누락·stale·짧은 history를 보간하거나 직전 값으로 채우지 않는다.
- 동행은 인과가 아니다. 원인·확률·가격예측·매수·매도 문장을 생성하지 않는다.
- 미래 영역은 가격 방향이 아니라 최대 3개의 `향후 1·2개월 확인 조건`이다.
- 금은 2차 `gold` context를 재사용하며 원자재에서 다시 계산하지 않는다.
- 경제사이클 확률 모델, publication gate, cycle map, 5년 ribbon을 변경하지 않는다.
- 카드에 좌측 장식선을 사용하지 않고 낮은 채도의 배경 블록만 사용한다.
- API key와 provider credential을 코드, 문서, payload, 로그에 저장하지 않는다.

---

### Task 1: Register T10YIE And Store Official EIA Weekly Series

**Files:**
- Create: `finance/data/eia_petroleum.py`
- Modify: `finance/data/macro.py:25-78,393-421`
- Modify: `app/jobs/ingestion_jobs.py:2795-2870`
- Modify: `tests/test_economic_cycle_asset_pathways.py`
- Create: `tests/test_eia_petroleum.py`

**Interfaces:**
- Produces: `EIA_WEEKLY_PETROLEUM_SERIES: dict[str, dict[str, str]]`
- Produces: `fetch_eia_weekly_petroleum_rows(series_ids, *, fetcher, collected_at) -> tuple[list[dict[str, object]], list[str], list[dict[str, str]]]`
- Produces: `collect_and_store_eia_weekly_petroleum(series_ids=None, *, fetcher=None, host="localhost", user="root", password="1234", port=3306) -> dict[str, object]`
- Produces: `store_macro_observation_rows(rows, *, host, user, password, port) -> int`
- Persists: existing `finance_meta.macro_series_observation`; no schema migration

- [ ] **Step 1: Write failing catalog and XLS parsing tests**

```python
def test_rates_and_eia_series_catalogs_are_exact() -> None:
    assert "T10YIE" in DEFAULT_MACRO_SERIES
    assert FRED_SERIES_CONFIG["T10YIE"]["category"] == "inflation_expectation"
    assert set(EIA_WEEKLY_PETROLEUM_SERIES) == {"WCESTUS1", "WCRFPUS2", "WRPUPUS2"}


def test_eia_xls_parser_normalizes_weekly_rows() -> None:
    frame = pd.DataFrame({"Date": ["2026-06-26", "bad"], "value": [408359, "NA"]})
    rows = normalize_eia_weekly_frame("WCESTUS1", frame, collected_at="2026-07-17 00:00:00")
    assert rows == [{
        "series_id": "WCESTUS1", "observation_date": "2026-06-26",
        "source": "eia", "source_type": "official", "source_mode": "weekly_xls",
        "source_ref": "https://www.eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls",
        "series_name": "Weekly U.S. Ending Stocks excluding SPR of Crude Oil",
        "category": "petroleum_inventory", "frequency": "weekly",
        "units": "thousand_barrels", "value": 408359.0,
        "release_lag_days": None, "coverage_status": "actual",
        "missing_fields_json": "[]", "collected_at": "2026-07-17 00:00:00",
        "error_msg": None,
    }]
```

- [ ] **Step 2: Run RED tests**

Run: `PYTHONPATH=. uv run pytest tests/test_eia_petroleum.py tests/test_economic_cycle_asset_pathways.py::test_rates_and_eia_series_catalogs_are_exact -q`

Expected: FAIL because `T10YIE`, `eia_petroleum.py`, and the public store helper do not exist.

- [ ] **Step 3: Add exact catalogs and parser**

```python
EIA_WEEKLY_PETROLEUM_SERIES = {
    "WCESTUS1": {
        "series_name": "Weekly U.S. Ending Stocks excluding SPR of Crude Oil",
        "category": "petroleum_inventory",
        "units": "thousand_barrels",
        "url": "https://www.eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls",
    },
    "WCRFPUS2": {
        "series_name": "Weekly U.S. Field Production of Crude Oil",
        "category": "petroleum_production",
        "units": "thousand_barrels_per_day",
        "url": "https://www.eia.gov/dnav/pet/hist_xls/WCRFPUS2w.xls",
    },
    "WRPUPUS2": {
        "series_name": "Weekly U.S. Product Supplied of Petroleum Products",
        "category": "petroleum_product_supplied",
        "units": "thousand_barrels_per_day",
        "url": "https://www.eia.gov/dnav/pet/hist_xls/WRPUPUS2w.xls",
    },
}


def normalize_eia_weekly_frame(series_id: str, frame: pd.DataFrame, *, collected_at: str) -> list[dict[str, object]]:
    config = EIA_WEEKLY_PETROLEUM_SERIES[series_id]
    normalized = frame.iloc[:, :2].copy()
    normalized.columns = ["observation_date", "value"]
    normalized["observation_date"] = pd.to_datetime(normalized["observation_date"], errors="coerce")
    normalized["value"] = pd.to_numeric(normalized["value"], errors="coerce")
    normalized = normalized.dropna(subset=["observation_date", "value"])
    return [{
        "series_id": series_id,
        "observation_date": row.observation_date.strftime("%Y-%m-%d"),
        "source": "eia", "source_type": "official", "source_mode": "weekly_xls",
        "source_ref": config["url"], "series_name": config["series_name"],
        "category": config["category"], "frequency": "weekly", "units": config["units"],
        "value": float(row.value), "release_lag_days": None, "coverage_status": "actual",
        "missing_fields_json": "[]", "collected_at": collected_at, "error_msg": None,
    } for row in normalized.itertuples()]
```

The fetcher reads `sheet_name="Data 1", header=2, usecols=[0, 1]` with `pandas.read_excel`. Add `T10YIE` to `DEFAULT_MACRO_SERIES` and `FRED_SERIES_CONFIG` with daily percent metadata.

- [ ] **Step 4: Expose idempotent storage and job integration**

```python
def store_macro_observation_rows(rows, *, host="localhost", user="root", password="1234", port=3306) -> int:
    normalized = [dict(row) for row in rows]
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["macro_series_observation"])
        sync_table_schema(db, MACRO_TABLE, PROVIDER_SCHEMAS["macro_series_observation"], DB_META)
        _upsert_macro_rows(db, normalized)
    finally:
        db.close()
    return len(normalized)
```

`run_collect_macro_market_context` calls FRED only for IDs in `FRED_SERIES_CONFIG` and calls `collect_and_store_eia_weekly_petroleum` only for IDs in `EIA_WEEKLY_PETROLEUM_SERIES`; combine stored/missing/failed counts without exposing a new run-result UI.

- [ ] **Step 5: Run GREEN tests and commit**

Run: `PYTHONPATH=. uv run pytest tests/test_eia_petroleum.py tests/test_economic_cycle_asset_pathways.py -q`

Expected: PASS.

```bash
git add finance/data/eia_petroleum.py finance/data/macro.py app/jobs/ingestion_jobs.py tests/test_eia_petroleum.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 금리와 EIA 수급 계열 추가"
```

### Task 2: Expand DB-Only Asset, S&P Price, And Actual EPS Loaders

**Files:**
- Modify: `finance/loaders/economic_cycle_assets.py`
- Modify: `finance/loaders/sp500_valuation.py:61-123`
- Modify: `tests/test_economic_cycle_asset_prices.py`
- Modify: `tests/test_sp500_valuation.py`

**Interfaces:**
- `DEFAULT_ASSET_SYMBOLS = ("GC=F", "DX-Y.NYB", "CL=F", "HG=F")`
- `DEFAULT_EQUITY_SYMBOLS = ("^GSPC", "SPY")`
- `DEFAULT_PATHWAY_SERIES = ("DGS2", "DGS10", "DFII10", "T10YIE", "VIXCLS", "BAA10Y", "WCESTUS1", "WCRFPUS2", "WRPUPUS2")`
- Produces: `load_economic_cycle_asset_prices(*, symbols: Sequence[str] = DEFAULT_ASSET_SYMBOLS, equity_symbols: Sequence[str] = DEFAULT_EQUITY_SYMBOLS, lookback_rows: int = 1500, end_date: object = None, query_fn: QueryFn | None = None) -> list[dict[str, object]]` normalized to `provider_symbol`, `candle_time_utc`, `close`, `source`, `provider_status`, `source_basis`
- Produces: `load_sp500_actual_eps_history(quarter_count=8, *, end_date=None, query_fn=None) -> dict[str, object]`

- [ ] **Step 1: Write failing loader tests**

```python
def test_asset_loader_combines_futures_and_equity_rows_before_reference_date() -> None:
    calls = []
    def fake_query(database, sql, params):
        calls.append((database, sql, params))
        if "futures_ohlcv" in sql:
            return [{"provider_symbol": "CL=F", "candle_time_utc": "2026-07-16", "close": 70.0, "source": "yfinance", "provider_status": "ok"}]
        return [{"provider_symbol": "^GSPC", "candle_time_utc": "2026-07-16", "close": 6200.0, "source": "nyse_price_history", "provider_status": "ok"}]
    rows = load_economic_cycle_asset_prices(end_date="2026-07-17", query_fn=fake_query)
    assert {row["provider_symbol"] for row in rows} == {"CL=F", "^GSPC"}
    assert len(calls) == 2


def test_sp500_actual_eps_history_requires_eight_distinct_completed_quarters() -> None:
    result = load_sp500_actual_eps_history(query_fn=lambda _sql, _params: eight_actual_rows)
    assert result["status"] == "READY"
    assert result["current_ttm_eps"] == pytest.approx(sum(row["eps"] for row in eight_actual_rows[:4]))
    assert result["prior_ttm_eps"] == pytest.approx(sum(row["eps"] for row in eight_actual_rows[4:8]))
```

- [ ] **Step 2: Run RED tests**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_prices.py tests/test_sp500_valuation.py -k 'economic_cycle or actual_eps_history' -q`

Expected: FAIL because equity rows, CL/HG defaults, and 8-quarter EPS loader are absent.

- [ ] **Step 3: Implement two-table price normalization**

Keep the existing futures ranked CTE. Add a second ranked query against `nyse_price_history` with `timeframe='1d'`, `symbol IN ({equity_placeholders})`, and ``date < DATE_ADD(%s, INTERVAL 1 DAY)`` before `ROW_NUMBER()`. Alias fields in SQL:

```sql
SELECT symbol AS provider_symbol,
       `date` AS candle_time_utc,
       COALESCE(adj_close, close) AS close,
       'nyse_price_history' AS source,
       'ok' AS provider_status,
       'stored index/ETF daily OHLCV' AS source_basis
```

Add `source_basis='stored continuous futures daily OHLCV'` to futures rows after query normalization.

- [ ] **Step 4: Implement strict actual EPS history**

```python
def load_sp500_actual_eps_history(*, quarter_count: int = 8, end_date: object = None, query_fn: QueryFn | None = None) -> dict[str, Any]:
    limit = max(8, int(quarter_count))
    end_clause = "AND period_end <= %s" if end_date is not None else "AND period_end <= CURRENT_DATE()"
    params = (str(end_date)[:10],) if end_date is not None else ()
    rows = _query_meta(f"""
        SELECT period_end, eps, source, source_ref, source_release_date, collected_at
        FROM sp500_index_earnings
        WHERE period_type = 'quarterly'
          AND earnings_basis = 'as_reported'
          AND value_status = 'actual'
          AND eps > 0
          {end_clause}
        ORDER BY period_end DESC, source_release_date DESC
    """, params, query_fn=query_fn)
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {"status": "INSUFFICIENT_HISTORY", "quarter_count": 0, "growth_pct": None, "quarters": []}
    frame["period_end"] = pd.to_datetime(frame["period_end"], errors="coerce")
    frame["source_release_date"] = pd.to_datetime(frame["source_release_date"], errors="coerce")
    frame["eps"] = pd.to_numeric(frame["eps"], errors="coerce")
    frame = frame.dropna(subset=["period_end", "eps"]).sort_values(["period_end", "source_release_date"], ascending=False).drop_duplicates("period_end").head(limit)
    quarters = [{"period_end": row.period_end.strftime("%Y-%m-%d"), "eps": float(row.eps), "source_release_date": row.source_release_date.strftime("%Y-%m-%d") if not pd.isna(row.source_release_date) else None} for row in frame.itertuples()]
    if len(quarters) < 8:
        return {"status": "INSUFFICIENT_HISTORY", "quarter_count": len(quarters), "growth_pct": None, "quarters": quarters}
    current_ttm = sum(row["eps"] for row in quarters[:4])
    prior_ttm = sum(row["eps"] for row in quarters[4:8])
    growth = (current_ttm / prior_ttm - 1.0) * 100.0 if prior_ttm > 0 else None
    return {"status": "READY" if growth is not None else "INSUFFICIENT_HISTORY", "quarter_count": len(quarters), "current_ttm_eps": current_ttm, "prior_ttm_eps": prior_ttm, "growth_pct": growth, "latest_period_end": quarters[0]["period_end"], "latest_release_date": quarters[0]["source_release_date"], "quarters": quarters, "source_basis": "S&P official actual as-reported EPS"}
```

Replace the body above with the same normalization pattern as `load_latest_sp500_ttm_actual_eps`; return exact keys `status`, `quarter_count`, `current_ttm_eps`, `prior_ttm_eps`, `growth_pct`, `latest_period_end`, `latest_release_date`, `quarters`, `source_basis="S&P official actual as-reported EPS"`. No Shiller fallback is allowed in this economic-cycle path.

- [ ] **Step 5: Run GREEN tests and commit**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_prices.py tests/test_sp500_valuation.py -q`

Expected: PASS.

```bash
git add finance/loaders/economic_cycle_assets.py finance/loaders/sp500_valuation.py tests/test_economic_cycle_asset_prices.py tests/test_sp500_valuation.py
git commit -m "경제사이클 자산 가격과 실제 EPS 로더 확장"
```

### Task 3: Add Mixed-Frequency Observation Evaluators

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Produces: `evaluate_spread(long_points, short_points, *, reference_date, series_id="DGS10-DGS2") -> dict[str, object]`
- Produces: `evaluate_weekly_series(points, *, series_id, reference_date) -> dict[str, object]`
- Produces: `build_observed_pathway(pathway_id, label, series, *, interpretation) -> dict[str, object]`
- Adds evaluation unit: `level`, `percent`, `bp`; weekly changes expose `4w` and `52w`

- [ ] **Step 1: Write failing evaluator tests**

```python
def test_spread_uses_same_horizon_long_minus_short_changes() -> None:
    spread = evaluate_spread(dgs10_points, dgs2_points, reference_date="2026-07-17")
    assert spread["changes"]["21d"] > 0
    assert spread["structure_status"] == "STEEPENING"


def test_weekly_evaluator_separates_four_week_and_year_over_year() -> None:
    result = evaluate_weekly_series(weekly_points, series_id="WCESTUS1", reference_date="2026-07-17")
    assert set(result["changes"]) == {"4w", "52w"}
    assert result["freshness"] == "CURRENT"
```

- [ ] **Step 2: Run RED tests**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py -k 'spread or weekly_evaluator' -q`

Expected: FAIL because mixed-frequency helpers do not exist.

- [ ] **Step 3: Implement spread and weekly contracts**

```python
def evaluate_spread(long_points, short_points, *, reference_date, series_id="DGS10-DGS2"):
    long_by_date = {_as_date(row["date"]): float(row["value"]) for row in long_points if _as_date(row["date"]) <= _as_date(reference_date)}
    short_by_date = {_as_date(row["date"]): float(row["value"]) for row in short_points if _as_date(row["date"]) <= _as_date(reference_date)}
    aligned = [{"date": row_date, "value": long_by_date[row_date] - short_by_date[row_date]} for row_date in sorted(set(long_by_date) & set(short_by_date))]
    result = evaluate_series(aligned, series_id=series_id, reference_date=reference_date, change_mode="BASIS_POINT")
    if result.get("reason_code"):
        result["structure_status"] = "UNAVAILABLE"
        return result
    directions = result["directions"]
    result["current_level_bp"] = aligned[-1]["value"] * 100.0
    result["structure_status"] = "STEEPENING" if directions["21d"] == directions["63d"] == "UP" else "FLATTENING" if directions["21d"] == directions["63d"] == "DOWN" else "MIXED"
    return result
```

`evaluate_weekly_series` deduplicates dates up to reference date, rejects latest observations older than 14 calendar days, requires 53 observations, and computes `(latest/lag4-1)*100` plus `(latest/lag52-1)*100` without daily interpolation.

- [ ] **Step 4: Keep gold/dollar regression green**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py -q`

Expected: all existing gold/dollar and new evaluator tests PASS.

- [ ] **Step 5: Commit**

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 혼합 빈도 경로 판정기 추가"
```

### Task 4: Build Stage 3 Rates Structure Context

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Produces: `build_rates_context(*, evaluations, economic_state) -> dict[str, object]`
- Context keys: `asset_group="rates"`, `coverage`, `economic_state`, `current_movement`, `observed_pathways`, `current_interpretation`, `next_check_conditions`, `provenance`, `limitations`, `narrative`

- [ ] **Step 1: Write failing rates-context test**

```python
def test_rates_context_explains_two_ten_spread_and_ten_year_components() -> None:
    contexts = build_asset_pathway_contexts(evidence=_economic_evidence(), market_rows=rows, price_rows=[], reference_date="2026-07-17")
    rates = contexts["rates"]
    assert rates["coverage"] == "SUFFICIENT"
    assert {row["metric_id"] for row in rates["current_movement"]} == {"DGS2", "DGS10", "DGS10-DGS2"}
    assert {row["pathway_id"] for row in rates["observed_pathways"]} == {"real_yield", "breakeven_inflation"}
    assert rates["next_check_conditions"]
    assert "원인" not in rates["narrative"]
```

- [ ] **Step 2: Run RED test**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py::test_rates_context_explains_two_ten_spread_and_ten_year_components -q`

Expected: FAIL because `rates` is absent.

- [ ] **Step 3: Implement rates builder and deterministic copy**

`current_movement` contains raw levels plus 5/21/63-day bp changes for DGS2/DGS10 and the derived spread. `observed_pathways` contains DFII10 and T10YIE separately. Generate at most four factual sentences: 2Y direction, 10Y direction, spread steepening/flattening, and component agreement/mix. `next_check_conditions` contains the 2Y, spread, and DFII10/T10YIE continuation checks.

- [ ] **Step 4: Run rates and regression tests**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py -q`

Expected: all pathway tests PASS; interpretation wiring remains owned by Task 7.

- [ ] **Step 5: Commit rates unit**

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 채권 금리구조 경로 추가"
```

### Task 5: Build Stage 4 S&P 500 Context

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Extends: `build_asset_pathway_contexts(*, evidence: Sequence[Mapping[str, object]], market_rows: Sequence[Mapping[str, object]], price_rows: Sequence[Mapping[str, object]], reference_date: object, sp500_earnings: Mapping[str, object] | None = None) -> dict[str, dict[str, object]]`
- Produces: `build_equities_context(*, evaluations, economic_state, sp500_earnings) -> dict[str, object]`

- [ ] **Step 1: Write failing S&P context tests**

```python
def test_equities_context_prefers_spx_and_keeps_paths_parallel() -> None:
    contexts = build_asset_pathway_contexts(evidence=_economic_evidence(), market_rows=rows, price_rows=price_rows, sp500_earnings=earnings, reference_date="2026-07-17")
    equities = contexts["equities"]
    assert equities["price_context"]["symbol"] == "^GSPC"
    assert {row["pathway_id"] for row in equities["observed_pathways"]} == {"real_yield", "credit_spread", "volatility", "actual_earnings"}
    assert "때문" not in equities["narrative"]


def test_equities_context_falls_back_to_spy_and_marks_provenance() -> None:
    assert context["price_context"]["symbol"] == "SPY"
    assert "S&P 500 ETF fallback" in context["provenance"]
```

- [ ] **Step 2: Run RED tests**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py -k 'equities or sp500' -q`

Expected: FAIL because S&P context and earnings injection are absent.

- [ ] **Step 3: Implement S&P builder**

Prefer evaluated `^GSPC`; use evaluated `SPY` only when `^GSPC` is unavailable. Keep DFII10, BAA10Y, VIXCLS, and actual EPS as four rows without adding statuses. Narrative lists the price return and each available measured change. EPS uses `growth_pct`, `latest_period_end`, and `latest_release_date`; stale or incomplete EPS affects only that row and coverage.

- [ ] **Step 4: Keep unavailable earnings local to the earnings row**

Pass `{"status": "UNAVAILABLE", "reason_code": "EARNINGS_READ_ERROR"}` into the builder test and assert that S&P price, real yield, credit spread, and VIX remain visible while only `actual_earnings` is unavailable.

- [ ] **Step 5: Run GREEN tests and commit**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py -q`

Expected: pathway tests PASS.

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 S&P500 관측 경로 추가"
```

### Task 6: Build Stage 5 WTI, Copper, And Gold Context

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Produces: `build_commodities_context(*, evaluations, economic_state, gold_context) -> dict[str, object]`
- Produces: `assets` with exact ordered IDs `wti`, `copper`, `gold`; every row contains `asset_id`, `label`, `coverage`, `price_context`, `observed_pathways`, `current_interpretation`, `next_check_conditions`, `provenance`, `limitations`, `narrative`
- Gold asset reuses the same `price_context`, pathways, narrative, and basis dates from `contexts["gold"]`

- [ ] **Step 1: Write failing commodity tests**

```python
def test_commodities_keep_wti_copper_and_gold_separate() -> None:
    assets = {row["asset_id"]: row for row in contexts["commodities"]["assets"]}
    assert set(assets) == {"wti", "copper", "gold"}
    assert {row["pathway_id"] for row in assets["wti"]["observed_pathways"]} == {"inventory", "production", "product_supplied", "dollar"}
    assert assets["copper"]["coverage"] == "PARTIAL"
    assert assets["gold"]["price_context"] == contexts["gold"]["price_context"]
    assert assets["gold"]["narrative"] == contexts["gold"]["narrative"]
```

- [ ] **Step 2: Run RED test**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py::test_commodities_keep_wti_copper_and_gold_separate -q`

Expected: FAIL because commodities context is absent.

- [ ] **Step 3: Implement WTI and copper factual paths**

WTI uses `CL=F`, the three EIA weekly evaluations, and DX-Y.NYB. Its text explicitly labels EIA data `최근 4주` and never aligns it to 21 trading days. Copper uses `HG=F`, DX-Y.NYB, and the canonical activity observation; it always adds limitation `연결된 산업활동 자료는 미국 중심` and therefore remains `PARTIAL`.

- [ ] **Step 4: Reuse gold by identity-safe copy**

Create gold subasset using `dict(gold_context)` and copied lists so React mutation cannot alter the top-level card. Assert equality in tests rather than recomputing evaluations.

- [ ] **Step 5: Run GREEN tests and commit**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py -q`

Expected: PASS.

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 원자재 다중 경로 추가"
```

### Task 7: Replace Stage 3-5 Placeholders And Preserve Failure Isolation

**Files:**
- Modify: `finance/economic_cycle_interpretation.py:458-532`
- Modify: `app/services/overview/economic_cycle.py:254-377`
- Modify: `tests/test_economic_cycle_service.py`
- Modify: `tests/test_economic_cycle_asset_prices.py`

**Interfaces:**
- `build_market_implications` receives complete contexts and preserves order `rates, equities, gold, dollar, commodities`
- `build_economic_cycle_read_model` injects `sp500_earnings_loader`, calls it with `end_date=market_reference`, and passes the result to `build_market_implications`
- Connected status mapping: `SUFFICIENT -> READY`, `PARTIAL -> PARTIAL`, `INSUFFICIENT -> LIMITED`
- No connected stage returns `PATHWAYS_NOT_CONNECTED`

- [ ] **Step 1: Replace placeholder assertions with failing connected-contract tests**

```python
def test_all_five_asset_groups_expose_connected_observation_contracts() -> None:
    rows = build_market_implications([], evidence, price_rows, market_rows=market_rows, sp500_earnings=earnings, price_reference_date="2026-07-17")
    assert [row["asset_group"] for row in rows] == ["rates", "equities", "gold", "dollar", "commodities"]
    assert all(row["analysis_status"] != "PATHWAYS_NOT_CONNECTED" for row in rows)
    assert all(row["is_directional_forecast"] is False for row in rows)
```

- [ ] **Step 2: Run RED service tests**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_service.py tests/test_economic_cycle_asset_prices.py -q`

Expected: FAIL while interpretation still creates placeholders.

- [ ] **Step 3: Normalize all contexts in one loop**

Remove the placeholder branch. Require every asset group in `contexts`; if a builder fails internally, create a limited context for that group only with `limitations=[translated reason]`, empty observed paths, and no directional claim.

In `build_economic_cycle_read_model`, call `load_sp500_actual_eps_history(end_date=market_reference)` in its own `try/except`. Failure supplies `{"status": "UNAVAILABLE", "reason_code": "EARNINGS_READ_ERROR"}` and does not clear market or price rows.

- [ ] **Step 4: Add forbidden-copy regression assertion**

```python
for item in implications:
    text = " ".join([str(item.get("narrative") or ""), *map(str, item.get("current_interpretation") or [])])
    assert not any(term in text for term in ("때문에", "원인입니다", "확률", "매수", "매도"))
```

- [ ] **Step 5: Run GREEN tests and commit**

Run: `PYTHONPATH=. uv run pytest tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -q`

Expected: PASS.

```bash
git add finance/economic_cycle_interpretation.py app/services/overview/economic_cycle.py tests/test_economic_cycle_service.py tests/test_economic_cycle_asset_prices.py
git commit -m "경제사이클 전체 자산 경로 연결"
```

### Task 8: Render The Common Observation UI

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `tests/test_market_context_economic_cycle.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- TypeScript adds `MovementMetric`, `ObservedPathway`, `CommodityAsset` and optional `current_movement`, `observed_pathways`, `current_interpretation`, `next_check_conditions`, `assets`, `provenance`, `limitations`
- Old gold/dollar `pathways` and `price_context` remain accepted during transition

- [ ] **Step 1: Write failing source-contract test**

```python
def test_economic_cycle_asset_ui_uses_observation_sections_without_left_rails() -> None:
    source = WORKBENCH_SOURCE.read_text()
    css = WORKBENCH_CSS.read_text()
    for label in ("현재 움직임", "함께 관찰된 경로", "현재 해석", "향후 1·2개월 확인 조건"):
        assert label in source
    assert "상승 요인이 될 수 있는 측정 경로" not in source
    assert "border-left" not in css[css.index(".observation-block"):css.index(".observation-block") + 600]
```

- [ ] **Step 2: Run RED UI contract test**

Run: `PYTHONPATH=. uv run pytest tests/test_market_context_economic_cycle.py -q`

Expected: FAIL because the new section names and styles are absent.

- [ ] **Step 3: Implement shared renderers**

Add `CurrentMovementBlock`, `ObservedPathwaysBlock`, `InterpretationBlock`, and `NextCheckBlock`. Rates uses one wide card. Equities uses one wide card. Commodities maps three `assets` cards. Gold/dollar adapt their existing pathway data into the same visible headings without changing backend results.

- [ ] **Step 4: Add low-chroma responsive styling**

`.observation-block` uses `border: 1px solid #dfe7ec`, `background: #f7fafb`, `border-radius: 12px`, and no left border override. Desktop uses two columns where content permits; at `max-width: 760px`, cards and metric grids become one column. Hover/focus shows dates and values only; mobile uses native details.

- [ ] **Step 5: Build and run UI tests**

Run: `cd app/web/streamlit_components/economic_cycle_workbench && npm run build`

Expected: TypeScript and Vite build complete successfully.

Run: `PYTHONPATH=. uv run pytest tests/test_market_context_economic_cycle.py tests/test_economic_cycle_service.py -q`

Expected: PASS.

- [ ] **Step 6: Commit UI unit**

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx app/web/streamlit_components/economic_cycle_workbench/src/style.css app/web/streamlit_components/economic_cycle_workbench/component_static tests/test_market_context_economic_cycle.py
git commit -m "경제사이클 자산 관측 UI 통합"
```

### Task 9: Actual Data Bootstrap, Browser QA, And Durable Documentation

**Files:**
- Create/update: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-pathways-stages3-5-v1-20260717/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Actual source flow: EIA/FRED/yfinance or existing price ingestion -> DB -> loader -> service -> React
- Browser QA target: `http://localhost:8501/`
- Screenshot: generated artifact only, not staged

- [ ] **Step 1: Collect approved series and prices**

Run the existing macro job for `T10YIE` plus the three EIA IDs, collect daily futures for `CL=F,HG=F,GC=F,DX-Y.NYB`, and use the existing price ingestion for `^GSPC,SPY`. Do not print environment keys.

Expected: stored rows for every source that the provider currently returns; unavailable sources remain explicit.

- [ ] **Step 2: Verify database basis dates**

Run bounded SQL counts and latest-date checks for the nine macro/EIA series, four futures, two S&P symbols, and eight actual EPS quarters.

Expected: dates do not exceed the requested reference date; any stale/missing item matches the UI limitation.

- [ ] **Step 3: Run full focused verification**

Run: `PYTHONPATH=. uv run pytest tests/test_eia_petroleum.py tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py tests/test_sp500_valuation.py -q`

Expected: PASS.

Run: `git diff --check`

Expected: no output.

- [ ] **Step 4: Perform desktop and mobile Browser QA**

Confirm rates, S&P 500, WTI, copper, and gold all render; no card says `PATHWAYS_NOT_CONNECTED`; 1주·1개월·3개월 versus 최근 4주 versus 완료 분기 labels are distinct; hover/focus works; mobile cards stack; no left rail is visible. Save one final desktop screenshot outside Git.

- [ ] **Step 5: Sync task and durable docs**

Record commands/results in `RUNS.md`, actual limitations in `RISKS.md`, completed roadmap `3차·4차·5차` in `STATUS.md`, and only durable table/source changes in `docs/data` and architecture docs. Root logs receive a 3-5 line handoff only.

- [ ] **Step 6: Final commit**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-pathways-stages3-5-v1-20260717 .aiworkspace/note/finance/docs .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "경제사이클 자산 경로 3~5차 문서 동기화"
```

Do not stage the benchmark research folder, `.superpowers/`, browser screenshots, run artifacts, or temp XLS files.
