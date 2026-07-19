# Economic Cycle Multichannel Asset Interpretation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 미국 경제상태를 자산가격의 정답으로 두지 않고, 저장된 금리·실질금리·달러·위험회피 데이터와 금·달러 실제 가격을 다중 경로 카드로 설명한다.

**Architecture:** 기존 FRED ingestion과 MySQL 테이블을 확장하고, DB-only loader가 5년+63거래일 history를 제공한다. 신규 순수 계산 모듈이 물질성·신선도·경로 상태를 계산하며, 기존 interpretation/service는 경제상태와 deterministic narrative를 조립하고 React는 `economic_cycle_v2` read model만 표시한다.

**Tech Stack:** Python 3.12, pandas, MySQL 8, pytest, Streamlit custom component, React 18, TypeScript 5, Vite 6

## Global Constraints

- UI에서 provider를 직접 호출하지 않는다.
- 신규 FRED series는 `DGS2`, `DGS10`, `DFII10`이며 `finance_meta.macro_series_observation`에 저장한다.
- `5거래일`은 단기 맥락만 표시하고 `21·63거래일`이 같은 material 방향일 때만 경로 방향을 부여한다.
- 가격·지수 변화는 percentage point, 금리·실질금리·스프레드 변화는 basis point로 전달한다.
- materiality threshold는 reference date 이전 최근 5년 동일 horizon 절대변화의 중앙값이다.
- 63거래일 horizon change가 252개 미만이면 `INSUFFICIENT_HISTORY`다.
- 일별 시장자료는 reference date 기준 5 business day를 초과하면 `STALE_SERIES`다.
- 누락·오래됨·짧은 이력에서 방향을 생성하거나 값을 보간하지 않는다.
- 경제사이클 canonical factor는 관측된 경제상태이며 자산별 상승·하락 방향으로 직접 번역하지 않는다.
- 동행은 `함께 관측`으로 표현하고 원인·확률·가격예측·매매 표현을 만들지 않는다.
- 금 핵심 경로는 `DFII10`과 `DX-Y.NYB`이며, 달러는 해외 상대금리가 없으므로 최대 coverage가 `PARTIAL`이다.
- 금·달러 파일럿 동안 채권·주식·원자재의 기존 `FAVORABLE/BURDEN` 방향 결론은 UI에서 제거한다.
- 카드와 경로 블록은 흰색이며 왼쪽 컬러 강조선과 그룹 전체 배경색을 사용하지 않는다.
- 경제사이클 확률 모델, publication gate, cycle map, 5년 ribbon은 변경하지 않는다.
- API key는 환경변수로만 읽고 코드·문서·payload에 기록하지 않는다.

---

### Task 1: Register The Three FRED Pathway Series

**Files:**
- Modify: `finance/data/macro.py:25-53`
- Create: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Produces: `DEFAULT_MACRO_SERIES` containing `DGS2`, `DGS10`, `DFII10`, `VIXCLS`, `T10Y3M`, `BAA10Y`
- Produces: `FRED_SERIES_CONFIG` metadata with `frequency="daily"` and `units="percent"`
- Persists: existing `finance_meta.macro_series_observation`; no schema migration

- [ ] **Step 1: Write the failing catalog test**

```python
from finance.data.macro import DEFAULT_MACRO_SERIES, FRED_SERIES_CONFIG


def test_asset_pathway_fred_series_are_registered_for_default_collection() -> None:
    expected = {"DGS2", "DGS10", "DFII10"}
    assert expected.issubset(set(DEFAULT_MACRO_SERIES))
    assert FRED_SERIES_CONFIG["DGS2"] == {
        "series_name": "Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity",
        "category": "treasury_yield",
        "frequency": "daily",
        "units": "percent",
    }
    assert FRED_SERIES_CONFIG["DGS10"]["category"] == "treasury_yield"
    assert FRED_SERIES_CONFIG["DFII10"]["category"] == "real_yield"
```

- [ ] **Step 2: Run the test to verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_pathways.py::test_asset_pathway_fred_series_are_registered_for_default_collection -q`

Expected: FAIL because the three series are absent.

- [ ] **Step 3: Add the exact catalog entries**

```python
DEFAULT_MACRO_SERIES = (
    "VIXCLS", "T10Y3M", "BAA10Y", "DGS2", "DGS10", "DFII10",
)

FRED_SERIES_CONFIG.update({
    "DGS2": {
        "series_name": "Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity",
        "category": "treasury_yield",
        "frequency": "daily",
        "units": "percent",
    },
    "DGS10": {
        "series_name": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity",
        "category": "treasury_yield",
        "frequency": "daily",
        "units": "percent",
    },
    "DFII10": {
        "series_name": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Inflation-Indexed",
        "category": "real_yield",
        "frequency": "daily",
        "units": "percent",
    },
})
```

Place the entries directly in the existing dictionary rather than calling `update()` at import time; the snippet fixes the exact values.

- [ ] **Step 4: Run ingestion-focused tests**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_pathways.py -q`

Expected: PASS for the new catalog test.

- [ ] **Step 5: Commit the ingestion unit**

```bash
git add finance/data/macro.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 시장 경로 FRED 계열 추가"
```

### Task 2: Add Bounded Historical DB Loaders

**Files:**
- Modify: `finance/loaders/economic_cycle_assets.py:1-73`
- Modify: `tests/test_economic_cycle_asset_prices.py:23-57`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Produces: `load_economic_cycle_market_series(*, series_ids: Sequence[str] = DEFAULT_PATHWAY_SERIES, start_date: object, end_date: object, macro_loader: Callable = load_macro_series_observations) -> list[dict[str, object]]`
- Produces: `load_economic_cycle_asset_prices(*, symbols: Sequence[str] = DEFAULT_ASSET_SYMBOLS, lookback_rows: int = 1500, end_date: object = None, query_fn: QueryFn | None = None) -> list[dict[str, object]]`
- Guarantees: observations after `end_date` are excluded before ranking

- [ ] **Step 1: Write failing macro-wrapper and historical-price tests**

```python
def test_market_series_loader_requests_only_the_pathway_window() -> None:
    captured: dict[str, object] = {}

    def fake_macro_loader(series_ids, *, start, end):
        captured.update(series_ids=tuple(series_ids), start=start, end=end)
        return pd.DataFrame([
            {"series_id": "DGS2", "observation_date": "2026-07-16", "value": 4.2}
        ])

    rows = load_economic_cycle_market_series(
        start_date="2021-03-01",
        end_date="2026-07-17",
        macro_loader=fake_macro_loader,
    )
    assert captured == {
        "series_ids": ("DGS2", "DGS10", "DFII10", "VIXCLS", "BAA10Y"),
        "start": "2021-03-01",
        "end": "2026-07-17",
    }
    assert rows[0]["series_id"] == "DGS2"


def test_asset_price_loader_applies_reference_date_before_row_rank() -> None:
    captured: dict[str, object] = {}

    def fake_query(database, sql, params):
        captured.update(database=database, sql=sql, params=params)
        return []

    load_economic_cycle_asset_prices(
        lookback_rows=1500,
        end_date="2026-07-17",
        query_fn=fake_query,
    )
    assert "candle_time_utc < DATE_ADD(%s, INTERVAL 1 DAY)" in captured["sql"]
    assert captured["params"][-2:] == ("2026-07-17", 1500)
```

- [ ] **Step 2: Run loader tests to verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_asset_pathways.py -k 'loader' -q`

Expected: FAIL because the wrapper and `end_date` boundary do not exist.

- [ ] **Step 3: Implement the two DB-only boundaries**

```python
from collections.abc import Callable, Sequence
from finance.loaders.macro import load_macro_series_observations

DEFAULT_PATHWAY_SERIES = ("DGS2", "DGS10", "DFII10", "VIXCLS", "BAA10Y")


def load_economic_cycle_market_series(
    *,
    series_ids: Sequence[str] = DEFAULT_PATHWAY_SERIES,
    start_date: object,
    end_date: object,
    macro_loader: Callable[..., object] = load_macro_series_observations,
) -> list[dict[str, object]]:
    frame = macro_loader(
        series_ids=series_ids,
        start=str(start_date)[:10],
        end=str(end_date)[:10],
    )
    if hasattr(frame, "to_dict"):
        return list(frame.to_dict("records"))
    return [dict(row) for row in frame]
```

Update the price query construction with this exact parameter contract:

```python
bounded_rows = max(315, min(int(lookback_rows), 2000))
end_clause = ""
params: tuple[object, ...] = normalized
if end_date is not None:
    end_clause = "AND candle_time_utc < DATE_ADD(%s, INTERVAL 1 DAY)"
    params = (*params, str(end_date)[:10])
sql = f"""
WITH ranked_rows AS (
  SELECT provider_symbol, candle_time_utc, close, source, provider_status,
         ROW_NUMBER() OVER (
           PARTITION BY provider_symbol ORDER BY candle_time_utc DESC
         ) AS row_rank
  FROM futures_ohlcv
  WHERE interval_code = '1d'
    AND provider_symbol IN ({placeholders})
    AND close IS NOT NULL
    AND provider_status = 'ok'
    {end_clause}
)
SELECT provider_symbol, candle_time_utc, close, source, provider_status
FROM ranked_rows
WHERE row_rank <= %s
ORDER BY provider_symbol ASC, candle_time_utc ASC
"""
rows = _query(DB_PRICE, sql, (*params, bounded_rows), query_fn=query_fn)
```

- [ ] **Step 4: Run loader tests to verify GREEN**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_asset_pathways.py -k 'loader' -q`

Expected: PASS; SQL remains DB-only and historical reads cannot see later rows.

- [ ] **Step 5: Commit the loader unit**

```bash
git add finance/loaders/economic_cycle_assets.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 시장 경로 이력 로더 추가"
```

### Task 3: Build The Pure Series Evaluator

**Files:**
- Create: `finance/economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_pathways.py`

**Interfaces:**
- Produces: `evaluate_series(points, *, series_id, reference_date, change_mode) -> dict[str, object]`
- `change_mode`: `PERCENT_RETURN` or `BASIS_POINT`
- Output fields: `series_id`, `as_of_date`, `unit`, `freshness`, `reason_code`, `changes`, `thresholds`, `directions`

- [ ] **Step 1: Write failing unit and direction tests**

```python
def test_evaluate_series_uses_percent_and_basis_point_units() -> None:
    price = _daily_points(start="2021-03-01", count=1400, start_value=100.0, step=0.05)
    rates = _daily_points(start="2021-03-01", count=1400, start_value=3.0, step=0.001)
    reference = price[-1]["date"]

    price_result = evaluate_series(
        price, series_id="DX-Y.NYB", reference_date=reference,
        change_mode="PERCENT_RETURN",
    )
    rate_result = evaluate_series(
        rates, series_id="DFII10", reference_date=reference,
        change_mode="BASIS_POINT",
    )

    assert price_result["unit"] == "percent"
    assert rate_result["unit"] == "bp"
    assert rate_result["changes"]["21d"] == pytest.approx(2.1)
    assert price_result["directions"]["21d"] == "UP"
    assert price_result["directions"]["63d"] == "UP"


def test_evaluate_series_reports_neutral_conflict_and_unavailable_reasons() -> None:
    assert _direction(0.4, threshold=0.5) == "NEUTRAL"
    assert _direction(0.6, threshold=0.5) == "UP"
    assert evaluate_series([], series_id="DGS2", reference_date="2026-07-17", change_mode="BASIS_POINT")["reason_code"] == "MISSING_SERIES"
```

Add this exact fixture above the tests:

```python
def _daily_points(
    *, start: str, count: int, start_value: float, step: float,
) -> list[dict[str, object]]:
    dates = pd.bdate_range(start=start, periods=count)
    return [
        {"date": timestamp.date(), "value": start_value + step * index}
        for index, timestamp in enumerate(dates)
    ]
```

- [ ] **Step 2: Run evaluator tests to verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_pathways.py -k 'evaluate_series' -q`

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement the evaluator and stable reason codes**

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from statistics import median
from typing import Literal

import pandas as pd

HORIZONS = (5, 21, 63)
MIN_HISTORICAL_CHANGES = 252
MAX_STALENESS_BUSINESS_DAYS = 5
ChangeMode = Literal["PERCENT_RETURN", "BASIS_POINT"]


def _as_date(value: object) -> date:
    return pd.Timestamp(value).date()


def _change(current: float, previous: float, mode: ChangeMode) -> float:
    if mode == "BASIS_POINT":
        return (current - previous) * 100.0
    if previous <= 0:
        raise ValueError("PERCENT_RETURN requires a positive lagged value")
    return (current / previous - 1.0) * 100.0


def _direction(value: float, *, threshold: float) -> str:
    if abs(value) < threshold:
        return "NEUTRAL"
    return "UP" if value > 0 else "DOWN"


def _unavailable(series_id: str, reason_code: str, *, as_of_date: date | None = None) -> dict[str, object]:
    return {
        "series_id": series_id,
        "as_of_date": as_of_date.isoformat() if as_of_date else None,
        "unit": None,
        "freshness": "UNAVAILABLE",
        "reason_code": reason_code,
        "changes": {"5d": None, "21d": None, "63d": None},
        "thresholds": {"21d": None, "63d": None},
        "directions": {"21d": "UNAVAILABLE", "63d": "UNAVAILABLE"},
    }


def evaluate_series(
    points: Sequence[Mapping[str, object]],
    *,
    series_id: str,
    reference_date: object,
    change_mode: ChangeMode,
) -> dict[str, object]:
    reference = _as_date(reference_date)
    by_date: dict[date, float] = {}
    for row in points:
        try:
            row_date = _as_date(row["date"])
            value = float(row["value"])
        except (KeyError, TypeError, ValueError):
            continue
        if row_date <= reference and (change_mode == "BASIS_POINT" or value > 0):
            by_date[row_date] = value
    ordered = sorted(by_date.items())
    if not ordered:
        return _unavailable(series_id, "MISSING_SERIES")
    latest_date = ordered[-1][0]
    business_age = len(pd.bdate_range(latest_date, reference, inclusive="right"))
    if business_age > MAX_STALENESS_BUSINESS_DAYS:
        return _unavailable(series_id, "STALE_SERIES", as_of_date=latest_date)
    if len(ordered) - 63 < MIN_HISTORICAL_CHANGES:
        return _unavailable(series_id, "INSUFFICIENT_HISTORY", as_of_date=latest_date)

    values = [value for _, value in ordered]
    changes = {
        f"{horizon}d": _change(values[-1], values[-1 - horizon], change_mode)
        for horizon in HORIZONS
    }
    five_year_start = pd.Timestamp(reference) - pd.DateOffset(years=5)
    thresholds: dict[str, float] = {}
    for horizon in (21, 63):
        history = [
            abs(_change(values[index], values[index - horizon], change_mode))
            for index in range(horizon, len(values) - 1)
            if pd.Timestamp(ordered[index][0]) >= five_year_start
        ]
        if len(history) < MIN_HISTORICAL_CHANGES:
            return _unavailable(series_id, "INSUFFICIENT_HISTORY", as_of_date=latest_date)
        thresholds[f"{horizon}d"] = median(history)
    unit = "bp" if change_mode == "BASIS_POINT" else "percent"
    return {
        "series_id": series_id,
        "as_of_date": latest_date.isoformat(),
        "unit": unit,
        "freshness": "CURRENT",
        "reason_code": None,
        "changes": changes,
        "thresholds": thresholds,
        "directions": {
            key: _direction(changes[key], threshold=thresholds[key])
            for key in ("21d", "63d")
        },
    }
```

- [ ] **Step 4: Add stale, insufficient-history, neutral, and historical-cutoff cases**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_pathways.py -k 'evaluate_series or materiality or stale' -q`

Expected: PASS for current, neutral, stale, missing, and insufficient-history outputs.

- [ ] **Step 5: Commit the pure evaluator**

```bash
git add finance/economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_pathways.py
git commit -m "경제사이클 시장 경로 판정기 추가"
```

### Task 4: Compose Gold And Dollar Pathways And Narratives

**Files:**
- Modify: `finance/economic_cycle_asset_pathways.py`
- Modify: `finance/economic_cycle_interpretation.py:37-145,251-580`
- Modify: `tests/test_economic_cycle_asset_pathways.py`
- Modify: `tests/test_economic_cycle_asset_prices.py`
- Modify: `tests/test_economic_cycle_service.py:252-380`

**Interfaces:**
- Produces: `build_asset_pathway_contexts(evidence, macro_rows, price_rows, *, economic_as_of_date, reference_date) -> dict[str, dict[str, object]]`
- Produces gold/dollar fields: `analysis_status`, `economic_state`, `pathways`, `price_context`, `coverage`, `coverage_label`, `narrative`, `unmeasured_pathways`
- Changes: `build_market_implications(horizons: Sequence[Mapping[str, object]], evidence: Sequence[Mapping[str, object]], price_rows: Sequence[Mapping[str, object]] = (), *, market_rows: Sequence[Mapping[str, object]] = (), economic_as_of_date: object = None, price_reference_date: object = None) -> list[dict[str, object]]` returns the new common contract for all five groups

- [ ] **Step 1: Write failing gold/dollar composition tests**

Add these exact raw-history fixtures in `tests/test_economic_cycle_asset_pathways.py`:

```python
def _economic_evidence() -> list[dict[str, object]]:
    return [
        {"factor": "activity_score", "value": -0.8, "source_date": "2026-06-30"},
        {"factor": "labor_income_score", "value": -0.5, "source_date": "2026-06-30"},
        {"factor": "financial_leading_score", "value": 0.2, "source_date": "2026-06-30"},
        {"factor": "inflation_policy_score", "value": 0.7, "source_date": "2026-06-30"},
    ]


def _macro_history(directions: dict[str, str]) -> list[dict[str, object]]:
    dates = pd.bdate_range(start="2021-03-01", periods=1400)
    rows: list[dict[str, object]] = []
    for series_id, direction in directions.items():
        start_value = 20.0 if series_id == "VIXCLS" else 5.0
        step = 0.001 if direction == "UP" else -0.001
        rows.extend(
            {
                "series_id": series_id,
                "observation_date": timestamp.date(),
                "value": start_value + step * index,
            }
            for index, timestamp in enumerate(dates)
        )
    return rows


def _price_history(directions: dict[str, str]) -> list[dict[str, object]]:
    dates = pd.bdate_range(start="2021-03-01", periods=1400)
    rows: list[dict[str, object]] = []
    for symbol, direction in directions.items():
        step = 0.02 if direction == "UP" else -0.02
        rows.extend(
            {
                "provider_symbol": symbol,
                "candle_time_utc": timestamp.date(),
                "close": 100.0 + step * index,
                "provider_status": "ok",
            }
            for index, timestamp in enumerate(dates)
        )
    return rows
```

```python
def test_gold_pathways_separate_real_yield_dollar_and_risk_directions() -> None:
    contexts = build_asset_pathway_contexts(
        _economic_evidence(),
        _macro_history({"DFII10": "UP", "DGS2": "UP", "VIXCLS": "DOWN", "BAA10Y": "DOWN"}),
        _price_history({"GC=F": "DOWN", "DX-Y.NYB": "UP"}),
        economic_as_of_date="2026-06-30",
        reference_date="2026-07-17",
    )
    gold = contexts["gold"]
    statuses = {row["pathway_id"]: row["status"] for row in gold["pathways"]}
    assert statuses == {
        "real_yield": "SUPPORTS_FALL",
        "dollar": "SUPPORTS_FALL",
        "short_rate": "SUPPORTS_FALL",
        "risk_aversion": "SUPPORTS_FALL",
    }
    assert gold["coverage"] == "SUFFICIENT"
    assert gold["price_context"]["status"] == "FALLING"
    assert "가격 원인을 확정" in gold["narrative"]


def test_dollar_is_partial_until_relative_rates_are_collected() -> None:
    dollar = build_asset_pathway_contexts(
        _economic_evidence(),
        _macro_history({
            "DGS2": "UP", "DGS10": "UP", "DFII10": "UP",
            "VIXCLS": "UP", "BAA10Y": "UP",
        }),
        _price_history({"GC=F": "DOWN", "DX-Y.NYB": "UP"}),
        economic_as_of_date="2026-06-30", reference_date="2026-07-17",
    )["dollar"]
    assert dollar["coverage"] == "PARTIAL"
    relative = next(row for row in dollar["unmeasured_pathways"] if row["pathway_id"] == "relative_rates")
    assert relative["reason_code"] == "RELATIVE_RATE_NOT_COLLECTED"
    assert "해외 상대금리" in dollar["narrative"]
```

Add a regression test asserting that `rates`, `equities`, and `commodities` have `analysis_status == "PATHWAYS_NOT_CONNECTED"` and no `assessment`, `macro_signal_label`, `alignment`, or `relationship_label` keys.

- [ ] **Step 2: Run composition tests to verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -k 'pathway or relative_rates or pathways_not_connected' -q`

Expected: FAIL because the new contract is not implemented.

- [ ] **Step 3: Add asset specs and deterministic composition**

```python
PATHWAY_SPECS = {
    "gold": (
        {"pathway_id": "real_yield", "label": "실질금리 경로", "members": (("DFII10", "DOWN"),), "core": True},
        {"pathway_id": "dollar", "label": "달러 경로", "members": (("DX-Y.NYB", "DOWN"),), "core": True},
        {"pathway_id": "short_rate", "label": "단기금리 경로", "members": (("DGS2", "DOWN"),), "core": False},
        {"pathway_id": "risk_aversion", "label": "위험회피 경로", "members": (("VIXCLS", "UP"), ("BAA10Y", "UP")), "core": False},
    ),
    "dollar": (
        {"pathway_id": "us_nominal_yield", "label": "미국 명목금리 경로", "members": (("DGS2", "UP"), ("DGS10", "UP")), "core": True},
        {"pathway_id": "us_real_yield", "label": "미국 실질금리 경로", "members": (("DFII10", "UP"),), "core": True},
        {"pathway_id": "risk_aversion", "label": "위험회피 경로", "members": (("VIXCLS", "UP"), ("BAA10Y", "UP")), "core": False},
    ),
}

COMMON_UNMEASURED = (
    {
        "pathway_id": "official_flows",
        "label": "ETF·중앙은행 수요",
        "scope_label": "후속 후보",
        "reason_code": "SOURCE_NOT_APPROVED",
    },
    {
        "pathway_id": "external_events",
        "label": "뉴스·지정학",
        "scope_label": "현재 범위 제외",
        "reason_code": "OUT_OF_MEASURED_SCOPE",
    },
)


def _member_status(evaluation: Mapping[str, object], rise_when: str) -> str:
    if evaluation.get("reason_code"):
        return "UNAVAILABLE"
    directions = evaluation["directions"]
    mapped: list[str] = []
    for horizon in ("21d", "63d"):
        direction = directions[horizon]
        if direction == "NEUTRAL":
            mapped.append("NEUTRAL")
        elif direction == rise_when:
            mapped.append("SUPPORTS_RISE")
        else:
            mapped.append("SUPPORTS_FALL")
    if mapped[0] == mapped[1]:
        return mapped[0]
    if "NEUTRAL" in mapped:
        return "NEUTRAL"
    return "MIXED"


def _combine_members(statuses: Sequence[str]) -> str:
    if "UNAVAILABLE" in statuses:
        return "UNAVAILABLE"
    if "MIXED" in statuses:
        return "MIXED"
    if "NEUTRAL" in statuses:
        return "NEUTRAL"
    return statuses[0] if len(set(statuses)) == 1 else "MIXED"
```

Normalize macro rows into `{"date", "value"}` per series, normalize price rows the same way per symbol, call `evaluate_series`, then compose each spec with `_member_status` and `_combine_members`. Price status mapping is exact:

```python
PRICE_STATUS = {
    "SUPPORTS_RISE": "RISING",
    "SUPPORTS_FALL": "FALLING",
    "MIXED": "MIXED",
    "NEUTRAL": "NEUTRAL",
    "UNAVAILABLE": "UNAVAILABLE",
}
```

Gold coverage is `SUFFICIENT` only when price, `real_yield`, and `dollar` have current data; one current core pathway is `PARTIAL`; otherwise `INSUFFICIENT`. Dollar coverage is never promoted beyond `PARTIAL` while relative rates are unmeasured.

Populate gold `unmeasured_pathways` with `COMMON_UNMEASURED`. Populate dollar with `COMMON_UNMEASURED` plus this exact row:

```python
{
    "pathway_id": "relative_rates",
    "label": "해외 상대금리",
    "scope_label": "미측정 · 후속 데이터 후보",
    "reason_code": "RELATIVE_RATE_NOT_COLLECTED",
}
```

- [ ] **Step 4: Replace alignment copy with deterministic pathway narrative**

In `finance/economic_cycle_interpretation.py`, keep canonical factor normalization but replace gold/dollar `assessment/alignment` fields. Use these exact sentence rules:

```python
def _pathway_narrative(asset_group: str, context: Mapping[str, object]) -> str:
    economic = str(context.get("economic_state_summary") or "관측된 경제상태가 부족합니다.")
    rise = [row["label"] for row in context["pathways"] if row["status"] == "SUPPORTS_RISE"]
    fall = [row["label"] for row in context["pathways"] if row["status"] == "SUPPORTS_FALL"]
    clauses = [economic]
    if rise:
        clauses.append(f"{', '.join(rise)}는 {context['label']} 상승 지지 방향과 함께 관측됐습니다.")
    if fall:
        clauses.append(f"{', '.join(fall)}는 {context['label']} 하락 지지 방향과 함께 관측됐습니다.")
    if context["price_context"]["status"] in {"RISING", "FALLING"}:
        direction = "상승" if context["price_context"]["status"] == "RISING" else "하락"
        clauses.append(f"실제 {context['label']} 가격은 최근 1개월과 3개월 {direction}했습니다.")
    if asset_group == "dollar":
        clauses.append("해외 상대금리를 측정하지 않아 미국 금리만으로 가격 원인을 확정할 수 없습니다.")
    else:
        clauses.append("현재 데이터 범위만으로 가격 원인을 확정하지 않습니다.")
    return " ".join(clauses)
```

For `rates`, `equities`, and `commodities`, return this exact safe shape:

```python
{
    "asset_group": asset_group,
    "label": asset_label,
    "analysis_status": "PATHWAYS_NOT_CONNECTED",
    "economic_state": economic_state,
    "pathways": [],
    "price_context": None,
    "coverage": "INSUFFICIENT",
    "coverage_label": "시장 경로 미연결",
    "narrative": "현재 단계에서는 관측된 경제상태만 표시하며 자산 방향은 판단하지 않습니다.",
    "unmeasured_pathways": [],
    "is_directional_forecast": False,
}
```

- [ ] **Step 5: Verify contract and commit**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -q`

Expected: PASS; old alignment assertions are replaced, not retained alongside the new contract.

```bash
git add finance/economic_cycle_asset_pathways.py finance/economic_cycle_interpretation.py tests/test_economic_cycle_asset_pathways.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py
git commit -m "금·달러 다중 전달경로 해석 추가"
```

### Task 5: Wire The V2 Overview Read Model With Failure Isolation

**Files:**
- Modify: `app/services/overview/economic_cycle.py:1-120,251-355`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: `load_economic_cycle_market_series` and `load_economic_cycle_asset_prices`
- Adds injection: `market_series_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None`
- Keeps injection: `asset_price_loader`, but calls it with `lookback_rows=1500` and `end_date=market_reference_date`
- Produces: `schema_version="economic_cycle_v2"`

- [ ] **Step 1: Write failing service boundary tests**

```python
def test_service_uses_one_reference_date_for_market_pathway_reads() -> None:
    calls: dict[str, object] = {}

    def market_loader(**kwargs):
        calls["market"] = kwargs
        return []

    def price_loader(**kwargs):
        calls["price"] = kwargs
        return []

    model = build_economic_cycle_read_model(
        as_of_date="2026-06-30",
        snapshot_loader=lambda **kwargs: _ready_snapshot(),
        history_loader=lambda **kwargs: [],
        market_series_loader=market_loader,
        asset_price_loader=price_loader,
        price_reference_date="2026-06-30",
    )
    assert model["schema_version"] == "economic_cycle_v2"
    assert calls["market"]["end_date"] == "2026-06-30"
    assert calls["price"] == {"lookback_rows": 1500, "end_date": "2026-06-30"}


def test_market_loader_failure_limits_cards_without_hiding_cycle_model() -> None:
    def broken_market_loader(**kwargs):
        raise RuntimeError("macro table unavailable")

    model = build_economic_cycle_read_model(
        snapshot_loader=lambda **kwargs: _ready_snapshot(),
        history_loader=lambda **kwargs: [],
        market_series_loader=broken_market_loader,
        asset_price_loader=lambda **kwargs: [],
        price_reference_date="2026-07-17",
    )
    assert model["status"] == "READY"
    gold = next(row for row in model["market_implications"] if row["asset_group"] == "gold")
    assert gold["coverage"] in {"PARTIAL", "INSUFFICIENT"}
    assert "macro table unavailable" not in json.dumps(model, ensure_ascii=False)
```

- [ ] **Step 2: Run service tests to verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_service.py -k 'reference_date_for_market or market_loader_failure' -q`

Expected: FAIL because the service has no market-series boundary or v2 schema.

- [ ] **Step 3: Load both histories inside independent try blocks**

```python
SCHEMA_VERSION = "economic_cycle_v2"

market_reference = pd.Timestamp(
    price_reference_date or as_of_date or date.today()
).date()
market_start = (pd.Timestamp(market_reference) - pd.DateOffset(years=5, months=4)).date()

load_market = market_series_loader or load_economic_cycle_market_series
try:
    market_rows = list(load_market(start_date=market_start, end_date=market_reference))
except Exception:
    market_rows = []

load_prices = asset_price_loader or load_economic_cycle_asset_prices
try:
    asset_price_rows = list(load_prices(lookback_rows=1500, end_date=market_reference))
except Exception:
    asset_price_rows = []

market_implications = build_market_implications(
    horizons,
    evidence,
    asset_price_rows,
    market_rows=market_rows,
    economic_as_of_date=snapshot_date or None,
    price_reference_date=market_reference,
)
```

Apply the same empty-pathway contract in `_empty_model` so missing materialized snapshots still serialize without React errors.

- [ ] **Step 4: Run full service and historical boundary tests**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_service.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_asset_pathways.py -q`

Expected: PASS; explicit historical reads contain no market observations after their reference date.

- [ ] **Step 5: Commit the service unit**

```bash
git add app/services/overview/economic_cycle.py tests/test_economic_cycle_service.py
git commit -m "경제사이클 다중 경로 read model 연결"
```

### Task 6: Render The Approved White Pathway Cards

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:42-122,423-507,555-617`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css:192-260`
- Modify: `tests/test_market_context_economic_cycle.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: `economic_cycle_v2` and common pathway card contract
- Produces: desktop hover/focus detail and mobile `<details>` tap expansion
- Preserves: Probability Path, Cycle Map, Evidence, Regime Ribbon DOM and copy

- [ ] **Step 1: Write the failing React source contract**

```python
def test_multichannel_asset_cards_use_the_approved_reading_flow() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    style = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()
    for token in (
        "economic_cycle_v2", "관측된 경제 상태", "상승 요인이 될 수 있는 측정 경로",
        "하락 요인이 될 수 있는 측정 경로", "현재 데이터 범위 밖",
        "데이터 범위", "21거래일", "63거래일",
    ):
        assert token in source
    assert "border-left" not in _pathway_style_block(style)
    assert ".pathway-item" in style and "background: #fff" in style
```

Add this exact helper in the test module so the negative assertion is limited to the new CSS block:

```python
def _pathway_style_block(style: str) -> str:
    start = style.index(".pathway-group")
    end = style.index(".method-disclosure", start)
    return style[start:end]
```

- [ ] **Step 2: Run the source contract to verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_market_context_economic_cycle.py -k multichannel_asset_cards -q`

Expected: FAIL on v2 types and pathway labels.

- [ ] **Step 3: Replace the old alignment types and components**

Use these exact TypeScript types:

```tsx
type PathwayStatus = "SUPPORTS_RISE" | "SUPPORTS_FALL" | "MIXED" | "NEUTRAL" | "UNAVAILABLE";
type CoverageStatus = "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT";
type PriceStatus = "RISING" | "FALLING" | "MIXED" | "NEUTRAL" | "UNAVAILABLE";

type SeriesEvaluation = {
  series_id: string;
  as_of_date?: string | null;
  unit?: "percent" | "bp" | null;
  freshness: "CURRENT" | "UNAVAILABLE";
  reason_code?: string | null;
  changes: { "5d": number | null; "21d": number | null; "63d": number | null };
};

type AssetPathway = {
  pathway_id: string;
  label: string;
  status: PathwayStatus;
  status_label: string;
  reason_code?: string | null;
  series: SeriesEvaluation[];
};

type MarketImplication = {
  asset_group: "rates" | "equities" | "gold" | "dollar" | "commodities";
  label: string;
  analysis_status: "READY" | "PATHWAYS_NOT_CONNECTED";
  economic_state: { as_of_date?: string | null; summary: string; observations: Evidence[] };
  pathways: AssetPathway[];
  price_context?: {
    symbol: string;
    as_of_date?: string | null;
    status: PriceStatus;
    status_label: string;
    returns: { one_week: number | null; one_month: number | null; three_months: number | null };
  } | null;
  coverage: CoverageStatus;
  coverage_label: string;
  narrative: string;
  unmeasured_pathways: { pathway_id: string; label: string; scope_label: string; reason_code: string }[];
  is_directional_forecast: false;
};
```

Update `CyclePayload.schema_version` and the render guard to `economic_cycle_v2`. Because backend v2 returns percentage points, replace the old decimal-return formatter with unit-aware functions:

```tsx
const formatPricePercent = (value: number | null) => value == null
  ? "-"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
const formatPathChange = (value: number | null, unit?: "percent" | "bp" | null) => value == null
  ? "-"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}${unit === "bp" ? "bp" : "%"}`;
```

Render `PathwayGroup` three times using filtered statuses. The item itself remains white and contains default 21·63 values; `<details className="pathway-detail">` contains source date, 5d value, freshness, and reason label. For non-pilot assets render only `economic_state.summary` and `시장 경로 미연결 · 단계적 확장 예정`.

- [ ] **Step 4: Apply the approved no-accent visual contract**

```css
.pathway-group { display: grid; gap: 10px; padding-block: 16px; border-top: 1px solid #e3eaee; }
.pathway-group h5 { margin: 0; color: #365468; font-size: 12px; }
.pathway-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
.pathway-item { min-width: 0; padding: 12px; border: 1px solid #dfe7eb; border-radius: 12px; background: #fff; }
.pathway-values { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
.pathway-detail summary { cursor: pointer; color: #688092; font-size: 9px; }
.pathway-detail[open] > div { margin-top: 7px; color: #667985; font-size: 9px; line-height: 1.5; }
@media (max-width: 760px) { .pathway-list { grid-template-columns: 1fr; } }
```

Do not add `border-left`, support/pressure group background fills, or hover-only essential direction text.

- [ ] **Step 5: Build, run source tests, and commit**

Run: `npm run build`

Working directory: `app/web/streamlit_components/economic_cycle_workbench`

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_market_context_economic_cycle.py -q`

Expected: Vite build and tests PASS.

```bash
git add app/web/streamlit_components/economic_cycle_workbench tests/test_market_context_economic_cycle.py
git commit -m "경제사이클 다중 경로 카드 UI 적용"
```

### Task 7: Refresh Data, Run Browser QA, And Sync Durable Docs

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-multichannel-asset-interpretation-v1-20260717/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Persists: 5년+4개월 FRED history for `DGS2`, `DGS10`, `DFII10`, `VIXCLS`, `BAA10Y`
- Verifies: actual DB read model and localhost Economic Cycle surface
- Documents: stages 1-2 complete; stages 3-5 remaining

- [ ] **Step 1: Mark the pre-created active task as implementation in progress**

Update `STATUS.md` from `Plan ready` to `Implementation in progress`. Record the current branch and starting commit in `RUNS.md` before the first product-code change.

- [ ] **Step 2: Collect the required FRED window through the existing ingestion path**

Run:

```bash
PYTHONPATH=. .venv/bin/python - <<'PY'
from datetime import date
import pandas as pd
from finance.data.macro import collect_and_store_macro_series

end = date.today()
start = (pd.Timestamp(end) - pd.DateOffset(years=5, months=4)).date()
result = collect_and_store_macro_series(
    series_ids=["DGS2", "DGS10", "DFII10", "VIXCLS", "BAA10Y"],
    start=start.isoformat(),
    end=end.isoformat(),
    source_mode="auto",
)
print({key: result[key] for key in ("requested", "stored", "missing", "failed")})
assert not result["failed"]
assert not result["missing"]
PY
```

Expected: five requested series, non-zero stored rows, empty `missing` and `failed`. `auto` uses `FRED_API_KEY` when present and the existing official CSV fallback otherwise.

- [ ] **Step 3: Run focused verification and actual read-model smoke**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest \
  tests/test_economic_cycle_asset_pathways.py \
  tests/test_economic_cycle_asset_prices.py \
  tests/test_economic_cycle_service.py \
  tests/test_market_context_economic_cycle.py -q

.venv/bin/python -m py_compile \
  finance/data/macro.py \
  finance/loaders/economic_cycle_assets.py \
  finance/economic_cycle_asset_pathways.py \
  finance/economic_cycle_interpretation.py \
  app/services/overview/economic_cycle.py

PYTHONPATH=. .venv/bin/python - <<'PY'
from app.services.overview.economic_cycle import build_economic_cycle_read_model
model = build_economic_cycle_read_model()
assert model["schema_version"] == "economic_cycle_v2"
assert [row["asset_group"] for row in model["market_implications"]] == [
    "rates", "equities", "gold", "dollar", "commodities",
]
gold = model["market_implications"][2]
dollar = model["market_implications"][3]
assert gold["coverage"] in {"SUFFICIENT", "PARTIAL", "INSUFFICIENT"}
assert dollar["coverage"] in {"PARTIAL", "INSUFFICIENT"}
print(gold["coverage"], dollar["coverage"])
PY

git diff --check
```

Expected: all tests and compile checks PASS; actual read model serializes without provider calls.

- [ ] **Step 4: Perform Browser QA**

Use the browser-control skill against the running localhost app. Verify:

1. desktop two-column and 420px one-column layouts have no horizontal overflow;
2. gold/dollar cards show economic state, rise paths, fall paths, current-data-outside, 5/21/63 price, narrative, and coverage;
3. path blocks are white with no left accent line and no colored group background;
4. desktop keyboard focus/hover and mobile tap reveal source date, 5d value, freshness, and reason;
5. rates/equities/commodities do not show `우호`, `부담`, or an asset direction conclusion;
6. cycle map, evidence, 5-year ribbon, and current/+1M/+2M sections remain intact;
7. no page error or browser console error appears.

Capture one final desktop screenshot outside git-tracked paths.

- [ ] **Step 5: Sync documentation and commit closeout**

Invoke `finance-doc-sync` and record actual commands/results in the active task `RUNS.md`; record remaining stages 3-5 and any unavailable pathway in `RISKS.md`. Keep root logs to a 3-5 line handoff.

```bash
git add \
  .aiworkspace/note/finance/tasks/active/overview-economic-cycle-multichannel-asset-interpretation-v1-20260717 \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/data/README.md \
  .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "경제사이클 다중 경로 파일럿 완료"
```

## Final Verification Gate

Before claiming completion, invoke `superpowers:verification-before-completion` and rerun the Task 7 focused suite, React build, `git diff --check`, actual read-model smoke, and Browser QA. Report stages 1-2 as complete only if all required checks pass; stages 3-5 remain explicitly pending.
