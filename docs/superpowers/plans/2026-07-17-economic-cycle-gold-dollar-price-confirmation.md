# Economic Cycle Gold / Dollar Price Confirmation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 경제사이클 자산별 확인 포인트에서 금과 달러를 분리하고 저장된 실제 선물 가격으로 경제 배경과 가격의 일치·불일치를 표시한다.

**Architecture:** `finance/data/futures_market.py`가 달러인덱스 선물을 기존 futures ledger에 수집하고, 신규 `finance/loaders/economic_cycle_assets.py`가 DB-only 가격 행을 제공한다. `finance/economic_cycle_interpretation.py`는 거시 evidence와 5/21/63거래일 가격 흐름을 결합하고, Overview service와 React는 계산 결과만 표시한다.

**Tech Stack:** Python 3.12, MySQL 8, pytest, Streamlit custom component, React 18, TypeScript, Vite

## Global Constraints

- UI에서 provider를 직접 호출하지 않는다.
- 금은 `GC=F`, 달러는 `DX-Y.NYB`의 저장된 `1d` OHLCV만 사용한다.
- 1주/1개월/3개월은 5/21/63거래일 수익률이다.
- 1개월과 3개월이 모두 `+1%` 초과면 상승 확인, 모두 `-1%` 미만이면 하락 확인, 나머지는 방향 혼재다.
- 64개 미만이거나 최신 가격이 7일 이상 오래되면 가격 자료 부족이다.
- 결과는 가격 예측, 목표가격, 매수·매도 신호가 아니다.
- 경제사이클 모델 확률과 publication gate는 변경하지 않는다.

---

### Task 1: Dollar Index Instrument And DB-Only Price Loader

**Files:**
- Modify: `finance/data/futures_market.py`
- Create: `finance/loaders/economic_cycle_assets.py`
- Create: `tests/test_economic_cycle_asset_prices.py`

**Interfaces:**
- Produces: `load_economic_cycle_asset_prices(symbols: Sequence[str] = ("GC=F", "DX-Y.NYB"), lookback_rows: int = 80, query_fn: QueryFn | None = None) -> list[dict[str, object]]`
- Persists: existing `finance_price.futures_ohlcv` using existing idempotent unique key

- [ ] **Step 1: Write failing catalog and loader tests**

```python
def test_dollar_index_is_a_core_daily_futures_instrument():
    assert "DX-Y.NYB" in DEFAULT_CORE_FUTURES_SYMBOLS

def test_asset_price_loader_reads_only_stored_daily_rows():
    rows = load_economic_cycle_asset_prices(query_fn=fake_query)
    assert {row["provider_symbol"] for row in rows} == {"GC=F", "DX-Y.NYB"}
    assert "FROM futures_ohlcv" in captured_sql
```

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py -q`

Expected: FAIL because `DX-Y.NYB` and the loader do not exist.

- [ ] **Step 3: Add instrument and minimal loader**

```python
{"provider_symbol": "DX-Y.NYB", "display_name": "US Dollar Index", "futures_group": "FX Futures", "exchange": "ICE", "contract_hint": "US Dollar Index futures", "sort_order": 305}

def load_economic_cycle_asset_prices(...):
    # One bounded window query, daily rows only, no provider call.
    return _query("finance_price", sql, params, query_fn=query_fn)
```

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py -q`

Expected: PASS.

- [ ] **Step 5: Commit data unit**

```bash
git add finance/data/futures_market.py finance/loaders/economic_cycle_assets.py tests/test_economic_cycle_asset_prices.py
git commit -m "달러인덱스 가격 원천 추가"
```

### Task 2: Price Trend And Alignment Interpretation

**Files:**
- Modify: `finance/economic_cycle_interpretation.py`
- Modify: `tests/test_economic_cycle_asset_prices.py`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: stored price rows from Task 1
- Produces: five implication groups `rates`, `equities`, `gold`, `dollar`, `commodities`
- Produces per gold/dollar card: `price_context`, `alignment`, `alignment_label`

- [ ] **Step 1: Write failing return/status/alignment tests**

```python
assert gold["price_context"]["returns"] == {
    "one_week": -0.03,
    "one_month": -0.08,
    "three_months": -0.16,
}
assert gold["price_context"]["status"] == "FALLING"
assert gold["alignment"] == "DIVERGENCE"
assert [row["asset_group"] for row in result] == [
    "rates", "equities", "gold", "dollar", "commodities"
]
```

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -k 'price or implication' -q`

Expected: FAIL because combined `gold_dollar` has no price context.

- [ ] **Step 3: Implement price metrics and split orientations**

```python
def build_market_implications(horizons, evidence, price_rows=(), *, price_reference_date=None):
    # Macro assessment stays count-based; gold/dollar receive price context.
    ...

price_context = {
    "symbol": symbol,
    "as_of_date": latest_date,
    "status": "RISING" | "FALLING" | "MIXED" | "UNAVAILABLE",
    "status_label": "상승 확인" | "하락 확인" | "방향 혼재" | "자료 부족",
    "returns": {"one_week": ..., "one_month": ..., "three_months": ...},
    "source_basis": "stored continuous futures daily OHLCV",
}
```

- [ ] **Step 4: Verify GREEN and edge cases**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -q`

Expected: PASS including stale, insufficient, threshold boundary, and divergence cases.

- [ ] **Step 5: Commit interpretation unit**

```bash
git add finance/economic_cycle_interpretation.py tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py
git commit -m "금·달러 가격 확인 판정 추가"
```

### Task 3: Overview Service Integration

**Files:**
- Modify: `app/services/overview/economic_cycle.py`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: `load_economic_cycle_asset_prices`
- Produces: existing `economic_cycle_v1` payload with extended implication rows

- [ ] **Step 1: Write failing DB-only injection and failure-isolation tests**

```python
model = build_economic_cycle_read_model(
    snapshot_loader=fake_snapshot,
    history_loader=fake_history,
    asset_price_loader=lambda: price_rows,
    price_reference_date="2026-07-17",
)
assert model["market_implications"][2]["price_context"]["status"] == "FALLING"

model = build_economic_cycle_read_model(asset_price_loader=broken_loader, ...)
assert model["status"] in {"READY", "LIMITED"}
assert model["market_implications"][2]["price_context"]["status"] == "UNAVAILABLE"
```

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_service.py -k asset_price -q`

Expected: FAIL because the service has no price loader boundary.

- [ ] **Step 3: Inject loader and isolate price read errors**

```python
load_prices = asset_price_loader or load_economic_cycle_asset_prices
try:
    price_rows = load_prices()
except Exception:
    price_rows = []
```

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_service.py -q`

Expected: PASS; price failure does not replace the economic model with `READ_ERROR`.

- [ ] **Step 5: Commit service unit**

```bash
git add app/services/overview/economic_cycle.py tests/test_economic_cycle_service.py
git commit -m "경제 사이클 가격 확인 연결"
```

### Task 4: React Five-Card Reading Flow

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `tests/test_market_context_economic_cycle.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: implication `assessment`, optional `price_context`, optional `alignment`
- Produces: 2-column responsive five-card surface

- [ ] **Step 1: Write failing source contract**

```python
for token in (
    "경제 국면:", "경제 배경", "가격 확인", "종합 판단",
    "1주", "1개월", "3개월", "배경과 가격 불일치",
):
    assert token in source
```

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_market_context_economic_cycle.py -k full_reading_flow -q`

Expected: FAIL on the new labels.

- [ ] **Step 3: Implement card and responsive layout**

```tsx
<strong>경제 국면: {item.phase_context}</strong>
{item.price_context ? <PriceConfirmation item={item} /> : null}
```

```css
.implication-card:last-child:nth-child(odd) { grid-column: 1 / -1; }
@media (max-width: 760px) { .implication-card:last-child:nth-child(odd) { grid-column: auto; } }
```

- [ ] **Step 4: Build and verify**

Run: `npm run build`

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_market_context_economic_cycle.py -q`

Expected: build and tests PASS.

- [ ] **Step 5: Commit UI unit**

```bash
git add app/web/streamlit_components/economic_cycle_workbench tests/test_market_context_economic_cycle.py
git commit -m "금·달러 가격 확인 화면 추가"
```

### Task 5: Actual Backfill, QA, And Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-gold-dollar-price-confirmation-v1-20260717/*`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Persists: initial `DX-Y.NYB` 5y/1d rows through the existing idempotent collector
- Verifies: local DB read model and running Streamlit surface

- [ ] **Step 1: Backfill the dollar index**

Run:

```bash
PYTHONPATH=. .venv/bin/python - <<'PY'
from finance.data.futures_market import collect_and_store_futures_ohlcv
print(collect_and_store_futures_ohlcv(
    symbols=["DX-Y.NYB"], period="5y", interval="1d",
    cadence_mode="economic_cycle_asset_price_backfill",
))
PY
```

Expected: success and stored daily rows for `DX-Y.NYB`.

- [ ] **Step 2: Run full focused verification**

Run: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py -q`

Run: `.venv/bin/python -m py_compile finance/loaders/economic_cycle_assets.py finance/economic_cycle_interpretation.py app/services/overview/economic_cycle.py`

Run: `git diff --check`

Expected: all PASS.

- [ ] **Step 3: Verify actual read model**

```python
model = build_economic_cycle_read_model()
assert [row["asset_group"] for row in model["market_implications"]] == [
    "rates", "equities", "gold", "dollar", "commodities"
]
```

- [ ] **Step 4: Browser QA**

Check desktop and 420px: five cards, no horizontal overflow, separate economic/price dates, visible gold/dollar returns, no console/page errors. Capture one screenshot when browser runtime is available.

- [ ] **Step 5: Sync docs and commit closeout**

```bash
git add .aiworkspace/note/finance
git commit -m "금·달러 가격 확인 개선 완료"
```
