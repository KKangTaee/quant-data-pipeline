# Market Movers Read-Model Hardening V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended when the user explicitly requests sub-agents) or `superpowers:executing-plans` to execute this plan task by task.

**Goal:** 승인된 `A안: 결정형 워크벤치`의 React UI를 만들기 전에, sector filter, 수집 상태, sector/industry 흐름, 시총 Top 3, 선택 종목 재무 factor가 같은 의미를 공유하는 JSON-safe read model을 완성한다.

**Architecture:** 기존 `app/services/overview/market_movers.py`와 `app/services/overview/why_it_moved.py`는 공개 façade로 유지한다. 새 pure-Python 모듈이 taxonomy, readiness, group flow, financial factor를 소유하고, façade는 DB row를 새 모델로 변환한다. `app/web/overview/market_movers_payloads.py`가 4차 React shell이 사용할 안정된 payload를 조립하되, 이번 3차에서는 현재 UI 렌더링 구조를 바꾸지 않는다.

**Tech Stack:** Python 3.11+, pandas, MySQL-backed loaders, pytest, Streamlit/React JSON payload boundary.

**Global Constraints:**

- 이번 계획은 전체 5차 roadmap 중 **3차 데이터·읽기 모델 강화만** 다룬다.
- 4차 React one-shell UI와 5차 sector conditional outlook은 구현하지 않는다.
- `Ingestion -> DB -> Loader -> UI` 경계를 유지하고 UI에서 provider를 직접 호출하지 않는다.
- missing return, volume, market cap을 0으로 대체하지 않는다.
- 기존 public 함수명은 유지하고 새 계약은 additive key 또는 명시적 schema version 상승으로 노출한다.
- raw job/row/status 진단 panel을 새로 만들지 않는다.
- 현재가를 과거 EPS에 적용한 historical PER를 제거한다.
- registry, saved JSONL, run history, 기존 QA 이미지는 수정하거나 stage하지 않는다.

## Approved Source Of Truth

- 승인 설계: `.aiworkspace/note/finance/researches/active/2026-06-market-movers-redesign-v2-benchmark/RECOMMENDATION.md`
- 현행 감사: `.aiworkspace/note/finance/researches/active/2026-06-market-movers-redesign-v2-benchmark/CURRENT_PROJECT_AUDIT.md`
- 기존 서비스 façade: `app/services/overview/market_movers.py`
- 기존 선택 종목 조사 façade: `app/services/overview/why_it_moved.py`
- 기존 web façade: `app/web/overview/market_movers_helpers.py`

## Exact File Map

### Create

- `app/services/overview/market_movers_read_model.py`
  - canonical 11-sector taxonomy와 sector filter를 소유한다.
- `app/services/overview/market_movers_readiness.py`
  - Complete / Partial / Blocked와 user-facing gap taxonomy를 소유한다.
- `app/services/overview/market_movers_group_flow.py`
  - industry display key, current-flow state, market-cap bellwether Top 3를 소유한다.
- `app/services/overview/market_mover_research.py`
  - 보고 주기와 재무 factor를 분리한 factor series, filing-ledger 기반 current TTM valuation을 소유한다.
- `app/web/overview/market_movers_payloads.py`
  - 4차 React shell용 JSON-safe decision payload 조립을 소유한다.
- `tests/test_overview_market_movers_read_models.py`
  - taxonomy, readiness, group flow, payload 단위 계약을 검증한다.
- `tests/test_overview_market_mover_research.py`
  - financial factor와 PER 시점 계약을 검증한다.

### Modify

- `app/services/overview/market_movers.py`
  - 새 taxonomy/readiness/group-flow 모듈을 호출한다.
  - universe SQL 결과에 `p.kind AS asset_kind`, `p.quote_type`을 포함한다.
  - 기존 `ticker_leader_rows`와 새 `market_cap_bellwether_rows`를 구분한다.
- `app/services/overview/why_it_moved.py`
  - 재무 trend에서 historical PER 생성을 제거한다.
  - 새 financial factor/current valuation 모델을 façade 결과에 연결한다.
  - schema를 `market_mover_research_snapshot_v2`로 올린다.
- `app/web/overview/market_movers_helpers.py`
  - 기존 Streamlit/React bridge가 새 payload builder를 호출할 수 있는 얇은 façade를 추가한다.
  - 현재 화면 구조와 CSS는 바꾸지 않는다.
- `tests/test_service_contracts.py`
  - 기존 market mover regression에서 historical PER 기대를 제거하고 v2 additive keys를 검증한다.
- `.aiworkspace/note/finance/tasks/active/market-movers-read-model-hardening-v1-20260720/{STATUS,NOTES,RUNS,RISKS}.md`
  - task 진행과 검증 근거를 갱신한다.
- `.aiworkspace/note/finance/WORK_PROGRESS.md`
  - 3차 완료 후 milestone과 4차 handoff만 3~5줄로 기록한다.
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
  - 3차 결정과 남은 data gap만 짧게 기록한다.

## Public Contracts To Preserve

- `build_market_movers_snapshot`
- `build_group_leadership_snapshot`
- `load_market_mover_sector_options`
- `build_market_mover_research_snapshot`

기존 호출자는 함수명을 변경하지 않는다. DataFrame 기반 legacy key도 4차 UI 전환 전까지 유지한다.

---

## Task 1: Canonical Sector Taxonomy And Filter

**Files:**

- Create: `app/services/overview/market_movers_read_model.py`
- Create: `tests/test_overview_market_movers_read_models.py`
- Modify: `app/services/overview/market_movers.py`
- Modify: `tests/test_service_contracts.py`

### Step 1: Write the failing taxonomy tests

`tests/test_overview_market_movers_read_models.py`에 아래 계약을 먼저 작성한다.

```python
from app.services.overview.market_movers_read_model import (
    CANONICAL_SECTORS,
    canonical_sector,
    canonical_sector_options,
    filter_rows_by_canonical_sector,
)


def test_canonical_sector_collapses_provider_aliases() -> None:
    assert canonical_sector("Financial Services") == "Financials"
    assert canonical_sector("Information Technology") == "Technology"
    assert canonical_sector("Consumer Cyclical") == "Consumer Discretionary"
    assert canonical_sector("Consumer Defensive") == "Consumer Staples"
    assert canonical_sector("Healthcare") == "Health Care"
    assert canonical_sector("Basic Materials") == "Materials"


def test_sector_options_expose_only_canonical_values() -> None:
    rows = [
        {"sector": "Financial Services"},
        {"sector": "Financials"},
        {"sector": "Technology"},
        {"sector": None},
    ]
    assert canonical_sector_options(rows) == ["All", "Financials", "Technology", "Unknown"]
    assert len(CANONICAL_SECTORS) == 11


def test_filter_uses_same_canonical_value_as_options() -> None:
    rows = [
        {"symbol": "A", "sector": "Financial Services"},
        {"symbol": "B", "sector": "Financials"},
        {"symbol": "C", "sector": "Technology"},
    ]
    filtered = filter_rows_by_canonical_sector(rows, "Financials")
    assert [row["symbol"] for row in filtered] == ["A", "B"]
    assert {row["sector"] for row in filtered} == {"Financials"}
```

### Step 2: Run the focused test and confirm failure

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q
```

Expected: import error for `app.services.overview.market_movers_read_model`.

### Step 3: Implement the minimal taxonomy module

`app/services/overview/market_movers_read_model.py`에 다음 public surface를 구현한다.

```python
CANONICAL_SECTORS: tuple[str, ...] = (
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Health Care",
    "Industrials",
    "Materials",
    "Real Estate",
    "Technology",
    "Utilities",
)

SECTOR_ALIASES: dict[str, str] = {
    "basic materials": "Materials",
    "communication services": "Communication Services",
    "consumer cyclical": "Consumer Discretionary",
    "consumer defensive": "Consumer Staples",
    "consumer discretionary": "Consumer Discretionary",
    "consumer staples": "Consumer Staples",
    "energy": "Energy",
    "financial services": "Financials",
    "financials": "Financials",
    "health care": "Health Care",
    "healthcare": "Health Care",
    "industrials": "Industrials",
    "information technology": "Technology",
    "materials": "Materials",
    "real estate": "Real Estate",
    "technology": "Technology",
    "utilities": "Utilities",
}

```

- `canonical_sector(value: object) -> str`
- `canonicalize_market_mover_row(row: Mapping[str, Any]) -> dict[str, Any]`
- `canonical_sector_options(rows: Sequence[Mapping[str, Any]]) -> list[str]`
- `filter_rows_by_canonical_sector(rows: Sequence[Mapping[str, Any]], sector: str | None) -> list[dict[str, Any]]`

구현 규칙:

- trim + casefold 후 alias lookup한다.
- 빈 값과 미등록 값은 `Unknown`으로 반환한다. 미등록 raw label은 조용히 새 sector option으로 노출하지 않는다.
- 반환 row는 copy이며 원본 dict를 mutate하지 않는다.
- `All` filter는 canonicalized 전체 row를 반환한다.

### Step 4: Integrate the façade

`app/services/overview/market_movers.py`에서:

- `_filter_sector`가 `filter_rows_by_canonical_sector`를 호출하게 바꾼다.
- `load_market_mover_sector_options`가 raw distinct label이 아니라 canonical options를 반환하게 바꾼다.
- ranking/grouping으로 넘어가는 universe row의 `sector`가 canonical value인지 보장한다.
- `Unknown`은 제거하지 않고 별도 group으로 유지한다.

`tests/test_service_contracts.py`의 sector option/filter 테스트에는 `Financial Services`와 `Financials`가 하나의 option/filter 결과로 합쳐지는 regression case를 추가한다.

### Step 5: Run tests and confirm pass

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "market_mover and sector"
```

Expected: all selected tests pass; option 목록에 raw alias 중복이 없다.

### Step 6: Commit

```bash
git add app/services/overview/market_movers_read_model.py app/services/overview/market_movers.py tests/test_overview_market_movers_read_models.py tests/test_service_contracts.py
git commit -m "변동 종목 섹터 분류 계약을 통합"
```

---

## Task 2: Typed Collection Readiness And Honest Denominators

**Files:**

- Create: `app/services/overview/market_movers_readiness.py`
- Modify: `tests/test_overview_market_movers_read_models.py`
- Modify: `app/services/overview/market_movers.py`
- Modify: `tests/test_service_contracts.py`

### Step 1: Write the failing readiness tests

추가할 핵심 test:

```python
from app.services.overview.market_movers_readiness import build_collection_readiness


def test_partial_readiness_keeps_metric_denominators_explicit() -> None:
    readiness = build_collection_readiness(
        universe_count=4,
        returnable_count=3,
        volume_count=2,
        market_cap_count=2,
        missing_rows=[
            {"symbol": "D", "reason": "missing end price", "gap_code": "MISSING_QUOTE"}
        ],
        basis="EOD",
        effective_end_date="2026-07-17",
        stale_days=0,
    )
    assert readiness["state"] == "PARTIAL"
    assert readiness["metrics"]["return"]["valid"] == 3
    assert readiness["metrics"]["volume"]["valid"] == 2
    assert readiness["metrics"]["market_cap"]["excluded"] == 2
    assert readiness["gap_summary"] == [{"code": "MISSING_QUOTE", "count": 1}]


def test_blocked_readiness_does_not_publish_a_false_empty_ranking() -> None:
    readiness = build_collection_readiness(
        universe_count=0,
        returnable_count=0,
        volume_count=0,
        market_cap_count=0,
        missing_rows=[],
        basis=None,
        effective_end_date=None,
        stale_days=None,
    )
    assert readiness["state"] == "BLOCKED"
    assert readiness["primary_action"] == "UNIVERSE_SETUP"
    assert readiness["publish_results"] is False
```

### Step 2: Run and confirm failure

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q -k readiness
```

Expected: import/function failure.

### Step 3: Implement readiness contract

`app/services/overview/market_movers_readiness.py` public surface:

```python
READINESS_STATES = ("COMPLETE", "PARTIAL", "BLOCKED")
GAP_CODES = (
    "STALE_SNAPSHOT",
    "MISSING_QUOTE",
    "LIMITED_HISTORY",
    "SYMBOL_REVIEW",
    "PROVIDER_GAP",
    "NO_UNIVERSE",
)

```

- `classify_missing_row(row: Mapping[str, Any]) -> str`
- `build_collection_readiness(*, universe_count: int, returnable_count: int, volume_count: int, market_cap_count: int, missing_rows: Sequence[Mapping[str, Any]], basis: str | None, effective_end_date: str | None, stale_days: int | None) -> dict[str, Any]`

반환 schema는 `market_movers_collection_readiness_v1`이며 다음 key를 가진다.

```python
{
    "schema_version": "market_movers_collection_readiness_v1",
    "state": "COMPLETE | PARTIAL | BLOCKED",
    "publish_results": bool,
    "basis": "INTRADAY | EOD | None",
    "effective_end_date": "YYYY-MM-DD | None",
    "freshness": {"state": "FRESH | STALE | UNKNOWN", "stale_days": int | None},
    "metrics": {
        "return": {"valid": int, "total": int, "excluded": int},
        "volume": {"valid": int, "total": int, "excluded": int},
        "market_cap": {"valid": int, "total": int, "excluded": int},
    },
    "gap_summary": [{"code": str, "count": int}],
    "primary_action": "REFRESH_MISSING | PREPARE_HISTORY | REVIEW_SYMBOLS | UNIVERSE_SETUP | None",
}
```

상태 규칙:

- universe 0이면 `BLOCKED / UNIVERSE_SETUP`.
- universe > 0이지만 returnable 0 또는 basis 없음이면 `BLOCKED / PREPARE_HISTORY`.
- stale 또는 어떤 metric이라도 excluded가 있으면 `PARTIAL`.
- 모든 metric valid가 universe count와 같고 fresh면 `COMPLETE`.
- gap summary는 count 내림차순, code 오름차순으로 결정적으로 정렬한다.

### Step 4: Integrate with market snapshot

`build_market_movers_snapshot` 결과에 `collection_readiness`를 additive key로 넣는다.

- return count는 실제 계산 가능한 return row만 센다.
- volume count는 실제 volume이 존재하는 return row만 센다.
- market-cap count는 positive market cap이 존재하는 return row만 센다.
- 기존 `coverage`는 호환을 위해 유지하되 4차 UI는 `collection_readiness`를 사용한다.
- `publish_results=False`이면 ranking/group 결과를 현재 결과처럼 내보내지 않고 빈 result + blocked reason을 반환한다.

### Step 5: Run tests

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "market_mover and (coverage or missing or snapshot)"
```

Expected: focused tests pass; missing metric이 0으로 채워지지 않는다.

### Step 6: Commit

```bash
git add app/services/overview/market_movers_readiness.py app/services/overview/market_movers.py tests/test_overview_market_movers_read_models.py tests/test_service_contracts.py
git commit -m "변동 종목 수집 준비도 계약을 추가"
```

---

## Task 3: Sector/Industry Current Flow And Market-Cap Bellwethers

**Files:**

- Create: `app/services/overview/market_movers_group_flow.py`
- Modify: `tests/test_overview_market_movers_read_models.py`
- Modify: `app/services/overview/market_movers.py`
- Modify: `tests/test_service_contracts.py`

### Step 1: Write failing group-flow tests

```python
from app.services.overview.market_movers_group_flow import (
    build_group_flow_state,
    build_market_cap_bellwethers,
    normalize_industry,
)


def test_market_cap_bellwethers_are_not_return_leaders() -> None:
    rows = [
        {"symbol": "BIG", "sector": "Technology", "return_pct": 1.0, "market_cap": 900, "asset_kind": "stock"},
        {"symbol": "MID", "sector": "Technology", "return_pct": 2.0, "market_cap": 500, "asset_kind": "stock"},
        {"symbol": "SMALL", "sector": "Technology", "return_pct": 12.0, "market_cap": 100, "asset_kind": "stock"},
        {"symbol": "ETF", "sector": "Technology", "return_pct": 3.0, "market_cap": 2000, "asset_kind": "etf"},
    ]
    result = build_market_cap_bellwethers(rows, group_by="sector", top_n=3)
    assert [row["symbol"] for row in result["Technology"]["rows"]] == ["BIG", "MID", "SMALL"]
    assert result["Technology"]["rows"][0]["rank"] == 1


def test_group_flow_labels_narrow_cap_led_rally() -> None:
    current = [{
        "group": "Technology",
        "symbols": 20,
        "positive_symbol_share": 35.0,
        "equal_weight_return": -0.2,
        "market_cap_weighted_return": 1.1,
    }]
    previous = [{
        "Group": "Technology",
        "Positive Symbol Share %": 45.0,
        "Equal Weight Return %": 0.1,
        "Market Cap Weighted Return %": 0.4,
    }]
    flow = build_group_flow_state(
        current_rows=current,
        previous_rows=previous,
        market_return_pct=0.5,
        group_by="sector",
    )
    assert flow[0]["state"] == "NARROW_CAP_LED"
    assert flow[0]["relative_strength_pp"] == 0.6
    assert flow[0]["breadth_change_pp"] == -10.0
```

industry normalization test에는 trim, repeated whitespace, case-insensitive explicit alias, `Unknown` 격리를 포함한다.

### Step 2: Run and confirm failure

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q -k "bellwether or group_flow or industry"
```

Expected: missing module/function failure.

### Step 3: Implement the group-flow module

`app/services/overview/market_movers_group_flow.py` public surface:

```python
INDUSTRY_ALIASES: dict[str, str] = {
    "software - infrastructure": "Software—Infrastructure",
    "software— infrastructure": "Software—Infrastructure",
    "semiconductors": "Semiconductors",
}

```

- `normalize_industry(value: object) -> str`
- `build_market_cap_bellwethers(rows: Sequence[Mapping[str, Any]], *, group_by: Literal["sector", "industry"], top_n: int = 3) -> dict[str, dict[str, Any]]`
- `build_group_flow_state(*, current_rows: Sequence[Mapping[str, Any]], previous_rows: Sequence[Mapping[str, Any]], market_return_pct: float | None, group_by: Literal["sector", "industry"]) -> list[dict[str, Any]]`

bellwether 규칙:

- `asset_kind == "stock"`만 포함한다. 누락된 `asset_kind`는 legacy compatibility를 위해 stock으로 간주하되 `kind_assumed_count`에 센다.
- `market_cap is None` 또는 `market_cap <= 0`은 rank에서 제외한다.
- market cap 내림차순, symbol 오름차순으로 정렬한다.
- 반환 group마다 `eligible_count`, `market_cap_valid_count`, `market_cap_excluded_count`, `kind_assumed_count`, `rows`를 포함한다.
- return leader는 기존 `ticker_leader_rows`에 남기고 bellwether와 합치지 않는다.

flow state 결정 순서:

1. symbols < 5이면 `SPARSE`.
2. breadth >= 50, breadth change > 0, relative strength > 0이면 `BROADENING_STRENGTH`.
3. cap-weight > 0, equal-weight <= 0, breadth < 50이면 `NARROW_CAP_LED`.
4. breadth change < 0이고 relative strength <= 0이면 `WEAKENING`.
5. current cap/equal 방향이 previous와 반대면 `REVERSAL_WATCH`.
6. 나머지는 `MIXED`.

이는 forecast가 아니라 현재 evidence state다. `next_observation`에는 다음 기간에 breadth/relative strength가 어떤 방향이어야 상태가 확인되는지만 넣는다.

### Step 4: Add issuer type and integrate the group snapshot

`app/services/overview/market_movers.py`의 세 universe SQL SELECT에 다음을 추가한다.

```sql
p.kind AS asset_kind,
p.quote_type
```

return row builder가 `asset_kind`, `quote_type`을 보존하게 한다.

`build_group_leadership_snapshot`에 additive keys를 추가한다.

```python
{
    "group_flow_schema_version": "market_movers_group_flow_v1",
    "group_flow": "list[dict[str, Any]]",
    "market_cap_bellwether_rows": "list[dict[str, Any]]",
}
```

flat `market_cap_bellwether_rows`의 각 row는 `Group`, `Group Type`, `Rank`, `Symbol`, `Name`, `Market Cap`, `Return %`, `Relative To Group pp`를 가진다.

- sector는 canonical 11-sector + Unknown을 사용한다.
- industry는 normalized stable display key를 사용한다.
- industry minimum group size 기본값 5를 유지한다.
- 현재 1D/5D/21D evidence는 이미 계산된 daily/weekly/monthly snapshot을 payload 조립 단계에서 결합한다. 이번 task에서는 존재하지 않는 기간 값을 추정하지 않는다.

### Step 5: Run tests

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "market_mover and (group or industry or leader)"
```

Expected: Top 3는 market cap 순서이며 ETF가 제외되고, return leader 계약은 그대로 통과한다.

### Step 6: Commit

```bash
git add app/services/overview/market_movers_group_flow.py app/services/overview/market_movers.py tests/test_overview_market_movers_read_models.py tests/test_service_contracts.py
git commit -m "변동 종목 그룹 흐름과 대장주 계약을 추가"
```

---

## Task 4: Financial Factor Series And Point-In-Time PER Correction

**Files:**

- Create: `app/services/overview/market_mover_research.py`
- Create: `tests/test_overview_market_mover_research.py`
- Modify: `app/services/overview/why_it_moved.py`
- Modify: `tests/test_service_contracts.py`

### Step 1: Write failing factor-series tests

```python
from app.services.overview.market_mover_research import (
    build_current_ttm_valuation,
    build_financial_factor_series,
)


def test_financial_factor_series_separates_period_and_factor() -> None:
    rows = [{
        "period_end": "2025-12-31",
        "total_revenue": 100.0,
        "operating_income": 15.0,
        "net_income": 10.0,
        "current_assets": 80.0,
        "current_liabilities": 40.0,
        "total_liabilities": 90.0,
        "shareholders_equity": 60.0,
    }]
    series = build_financial_factor_series(rows, freq="annual")
    point = series["factors"]["operating_margin"]["points"][0]
    assert series["freq"] == "annual"
    assert point["value"] == 15.0
    assert series["factors"]["current_ratio"]["points"][0]["value"] == 2.0
    assert series["factors"]["debt_ratio"]["points"][0]["value"] == 150.0


def test_current_ttm_per_requires_four_consecutive_reported_quarters() -> None:
    rows = [
        {"fiscal_year": 2025, "fiscal_quarter": 1, "period_end": "2025-03-31", "diluted_eps": 1.0, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
        {"fiscal_year": 2025, "fiscal_quarter": 2, "period_end": "2025-06-30", "diluted_eps": 1.2, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
        {"fiscal_year": 2025, "fiscal_quarter": 3, "period_end": "2025-09-30", "diluted_eps": 1.3, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
        {"fiscal_year": 2025, "fiscal_quarter": 4, "period_end": "2025-12-31", "diluted_eps": 1.5, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
    ]
    value = build_current_ttm_valuation(rows, latest_price=100.0, latest_price_date="2026-01-02")
    assert value["status"] == "OK"
    assert value["ttm_diluted_eps"] == 5.0
    assert value["current_per"] == 20.0


def test_current_ttm_per_is_unavailable_when_one_quarter_is_missing() -> None:
    rows = [
        {"fiscal_year": 2025, "fiscal_quarter": 1, "period_end": "2025-03-31", "diluted_eps": 1.0, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
        {"fiscal_year": 2025, "fiscal_quarter": 2, "period_end": "2025-06-30", "diluted_eps": None, "metric_provenance": {}},
        {"fiscal_year": 2025, "fiscal_quarter": 3, "period_end": "2025-09-30", "diluted_eps": 1.3, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
        {"fiscal_year": 2025, "fiscal_quarter": 4, "period_end": "2025-12-31", "diluted_eps": 1.5, "metric_provenance": {"diluted_eps": {"source_kind": "REPORTED"}}},
    ]
    value = build_current_ttm_valuation(rows, latest_price=100.0, latest_price_date="2026-01-02")
    assert value["status"] == "UNAVAILABLE"
    assert value["reason_code"] == "INCOMPLETE_REPORTED_DILUTED_EPS"
    assert value["current_per"] is None
```

historical trend regression test는 어떤 annual/quarterly point에도 `per` key가 없음을 검증한다.

### Step 2: Run and confirm failure

```bash
.venv/bin/python -m pytest tests/test_overview_market_mover_research.py -q
```

Expected: missing module/function failure.

### Step 3: Implement the factor contract

`app/services/overview/market_mover_research.py` public surface:

```python
FINANCIAL_FACTOR_GROUPS = {
    "income": ("revenue", "operating_income", "net_income", "diluted_eps"),
    "profitability": ("operating_margin", "net_margin", "roe"),
    "stability": ("current_ratio", "debt_ratio"),
}

```

- `build_financial_factor_series(rows: Sequence[Mapping[str, Any]], *, freq: Literal["annual", "quarterly"]) -> dict[str, Any]`
- `build_current_ttm_valuation(quarterly_rows: Sequence[Mapping[str, Any]], *, latest_price: float | None, latest_price_date: str | None) -> dict[str, Any]`

factor 계산 규칙:

- revenue = `total_revenue`.
- operating margin = `operating_income / total_revenue * 100`.
- net margin = `net_income / total_revenue * 100`.
- ROE = `net_income / average(beginning shareholders_equity, ending shareholders_equity) * 100`; 이전 equity가 없으면 unavailable이며 ending equity 단독 fallback을 쓰지 않는다.
- current ratio = `current_assets / current_liabilities`.
- debt ratio = `total_liabilities / shareholders_equity * 100`.
- zero/negative denominator는 unavailable reason을 가진다.
- factor마다 `label`, `group`, `unit`, `points`, `available_count`, `excluded_count`를 가진다.
- points는 period_end 오름차순이고 서로 다른 단위의 factor를 한 series에 합치지 않는다.

TTM valuation 규칙:

- 입력은 existing PIT `nyse_financial_statement_values`를 이용하는 quarterly-series loader 결과다.
- latest 4개 연속 fiscal quarter의 `diluted_eps`가 모두 `metric_provenance.diluted_eps.source_kind == "REPORTED"`일 때만 합산한다.
- 분기 간격이 끊기거나 중복 quarter만 있거나 EPS가 하나라도 없으면 unavailable이다.
- TTM EPS <= 0이면 current PER를 제공하지 않고 `NON_POSITIVE_TTM_EPS`를 반환한다.
- current PER만 `latest_price / ttm_diluted_eps`로 계산하며 price date와 네 quarter period_end를 evidence로 반환한다.
- historical PER는 이 task에서 제공하지 않는다.

### Step 4: Connect existing PIT filing-ledger data

`app/services/overview/why_it_moved.py`는 provider 호출을 추가하지 않고 기존 DB-backed loader 경계를 사용한다.

- `finance.loaders.us_stock_turnaround.load_us_stock_turnaround_inputs`가 반환하는 `inputs["series"]["timeline"]`을 통해 reported diluted EPS timeline을 읽는다.
- `build_market_mover_research_snapshot`에 `quarterly_eps_loader: Callable[..., dict[str, Any]] | None = None`를 추가한다. 기본값은 `load_us_stock_turnaround_inputs`이고, test loader도 같은 dict shape를 반환한다.
- EPS loader failure는 전체 research snapshot을 실패시키지 않고 `current_valuation.status=UNAVAILABLE`로 격리한다.
- annual/quarterly statement shadow는 revenue/profitability/stability factor source로 계속 사용한다.

snapshot v2 additive keys:

```python
{
    "schema_version": "market_mover_research_snapshot_v2",
    "financial_factor_series": {
        "annual": "financial factor series object",
        "quarterly": "financial factor series object",
    },
    "current_valuation": "current valuation object",
}
```

기존 `annual_financials`, `quarterly_financials`, `financial_trends`는 호환을 위해 남기되:

- `_financial_snapshot_from_row`가 synthetic EPS와 PER를 만들지 않는다.
- trend point에서 `per`를 제거한다.
- 재무 데이터가 없다는 판정은 새 factor 목록 전체를 기준으로 한다.

### Step 5: Update regressions and run tests

`tests/test_service_contracts.py`에서:

- v1 schema 기대를 v2로 바꾼다.
- annual/quarterly trend에 latest-price historical PER가 존재한다는 기대를 제거한다.
- current valuation의 injected four-quarter EPS success와 missing-quarter unavailable을 추가한다.
- legacy statement snapshot의 net_income/shares 기반 EPS fallback을 기대하지 않는다.

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_market_mover_research.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "market_mover and (research or financial or per or eps)"
```

Expected: all selected tests pass; historical points에 `per`가 없고 current PER만 four-quarter gate를 통과한다.

### Step 6: Commit

```bash
git add app/services/overview/market_mover_research.py app/services/overview/why_it_moved.py tests/test_overview_market_mover_research.py tests/test_service_contracts.py
git commit -m "변동 종목 재무 팩터와 PER 시점 계약을 교정"
```

---

## Task 5: Stable Decision-Workbench Payload For Phase 4

**Files:**

- Create: `app/web/overview/market_movers_payloads.py`
- Modify: `tests/test_overview_market_movers_read_models.py`
- Modify: `app/web/overview/market_movers_helpers.py`
- Modify: `tests/test_service_contracts.py`

### Step 1: Write the failing payload test

```python
import json

from app.web.overview.market_movers_payloads import build_market_movers_decision_payload


def test_decision_payload_is_json_safe_and_keeps_contracts_separate() -> None:
    payload = build_market_movers_decision_payload(
        market_snapshot={
            "collection_readiness": {"state": "PARTIAL", "publish_results": True},
            "rows": [{"Symbol": "AAPL", "Return %": 2.1}],
        },
        sector_snapshots={"daily": {"group_flow": [], "market_cap_bellwether_rows": []}},
        industry_snapshots={"daily": {"group_flow": [], "market_cap_bellwether_rows": []}},
        selected_research=None,
    )
    assert payload["schema_version"] == "market_movers_decision_payload_v1"
    assert payload["trust"]["state"] == "PARTIAL"
    assert payload["group_context"]["sector"]["daily"]["bellwethers"] == []
    assert payload["group_context"]["sector"]["daily"].get("conditional_outlook") is None
    json.dumps(payload)
```

### Step 2: Run and confirm failure

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q -k decision_payload
```

Expected: missing module/function failure.

### Step 3: Implement the payload adapter

`app/web/overview/market_movers_payloads.py`에 `build_market_movers_decision_payload(*, market_snapshot: Mapping[str, Any], sector_snapshots: Mapping[str, Mapping[str, Any]], industry_snapshots: Mapping[str, Mapping[str, Any]], selected_research: Mapping[str, Any] | None) -> dict[str, Any]`를 구현한다.

반환 top-level:

```python
{
    "schema_version": "market_movers_decision_payload_v1",
    "trust": "collection readiness object",
    "ranking": {"rows": "list[dict[str, Any]]", "period": "str", "ranking_mode": "str"},
    "group_context": {
        "sector": {"daily": "group object", "weekly": "group object", "monthly": "group object"},
        "industry": {"daily": "group object", "weekly": "group object", "monthly": "group object"},
    },
    "selected_research": dict | None,
}
```

규칙:

- pandas DataFrame/Series, Timestamp, numpy scalar를 JSON-native list/dict/number/string/null로 변환한다.
- sector/industry와 daily/weekly/monthly key를 항상 유지하되, 없는 snapshot은 `status=UNAVAILABLE`로 명시한다.
- `ticker_leaders`와 `bellwethers`를 별도 key로 둔다.
- `conditional_outlook`은 5차 전까지 넣지 않는다.
- selected research v2는 그대로 전달하되 source/debug object는 disclosure용 `evidence` 아래로 정리한다.

### Step 4: Add a thin web façade without changing the visible UI

`app/web/overview/market_movers_helpers.py`에 payload builder import와 wrapper만 추가한다. 기존 render 순서, component props, CSS, tab layout은 4차까지 유지한다.

기존 component가 새 payload를 아직 소비하지 않는다는 사실을 task `STATUS.md`에 명시한다.

### Step 5: Run tests

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "market_mover"
```

Expected: payload가 `json.dumps` 가능하고 Level 2 outlook을 위조하지 않는다.

### Step 6: Commit

```bash
git add app/web/overview/market_movers_payloads.py app/web/overview/market_movers_helpers.py tests/test_overview_market_movers_read_models.py tests/test_service_contracts.py
git commit -m "변동 종목 결정 워크벤치 페이로드를 고정"
```

---

## Task 6: Phase-3 Regression, Real-DB Smoke, Documentation Closeout

**Files:**

- Modify: `.aiworkspace/note/finance/tasks/active/market-movers-read-model-hardening-v1-20260720/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-movers-read-model-hardening-v1-20260720/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-movers-read-model-hardening-v1-20260720/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-movers-read-model-hardening-v1-20260720/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

### Step 1: Run syntax and focused tests

```bash
.venv/bin/python -m py_compile \
  app/services/overview/market_movers_read_model.py \
  app/services/overview/market_movers_readiness.py \
  app/services/overview/market_movers_group_flow.py \
  app/services/overview/market_mover_research.py \
  app/services/overview/market_movers.py \
  app/services/overview/why_it_moved.py \
  app/web/overview/market_movers_payloads.py \
  app/web/overview/market_movers_helpers.py
.venv/bin/python -m pytest tests/test_overview_market_movers_read_models.py tests/test_overview_market_mover_research.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "market_mover"
```

Expected: all commands exit 0.

### Step 2: Run real-DB read-only smoke

아래 smoke는 write API를 호출하지 않는다.

```bash
.venv/bin/python - <<'PY'
import json
from app.services.overview.market_movers import (
    build_group_leadership_snapshot,
    build_market_movers_snapshot,
    load_market_mover_sector_options,
)

for universe in ("SP500", "TOP1000", "TOP2000"):
    options = load_market_mover_sector_options(universe_code=universe)
    assert options[0] == "All"
    assert len([value for value in options if value != "Unknown"]) <= 12
    for period in ("daily", "weekly", "monthly"):
        movers = build_market_movers_snapshot(
            universe_code=universe,
            period=period,
        )
        readiness = movers["collection_readiness"]
        assert readiness["state"] in {"COMPLETE", "PARTIAL", "BLOCKED"}
        groups = build_group_leadership_snapshot(
            universe_code=universe,
            period=period,
            group_by="sector",
        )
        assert "market_cap_bellwether_rows" in groups
        json.dumps(readiness)
print("market movers phase-3 DB smoke: OK")
PY
```

Expected: `market movers phase-3 DB smoke: OK`. DB가 실행 중이지 않으면 실패 출력과 환경 이유를 `RUNS.md` 및 최종 응답에 남기며 테스트 성공으로 대체하지 않는다.

### Step 3: Run full service regression if runtime permits

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -q
```

Expected: exit 0. 60초 이상 걸리면 commentary update 후 계속 기다린다.

### Step 4: Run static repository checks

```bash
git diff --check
rg -n "NotImplementedError|pass$" \
  app/services/overview/market_movers_read_model.py \
  app/services/overview/market_movers_readiness.py \
  app/services/overview/market_movers_group_flow.py \
  app/services/overview/market_mover_research.py \
  app/web/overview/market_movers_payloads.py \
  tests/test_overview_market_movers_read_models.py \
  tests/test_overview_market_mover_research.py
git status --short
```

Expected: `git diff --check` exit 0, unfinished-stub scan no matches. `git status`에는 scoped changes와 기존 사용자 artifact가 구분되어 보인다.

### Step 5: Perform contract self-review

다음 항목을 코드와 test에서 일대일로 확인하고 `STATUS.md`에 체크한다.

- sector option과 filter가 같은 canonical mapping을 쓴다.
- Complete/Partial/Blocked가 결과 공개 여부와 일치한다.
- metric별 valid denominator가 분리된다.
- sector/industry group flow가 forecast 문구를 만들지 않는다.
- market-cap Top 3와 positive-return leader가 분리된다.
- ETF가 bellwether에서 제외된다.
- 보고 주기와 factor 선택이 payload에서 독립 축이다.
- historical PER가 제거됐다.
- current PER는 4개 연속 reported diluted EPS만 사용한다.
- industry conditional outlook이 없다.
- existing registry/saved/run-history/QA artifact가 stage되지 않았다.

### Step 6: Update durable handoff docs

`STATUS.md`에는 `3차 완료 / 4차 React shell 대기`를 기록한다. `NOTES.md`에는 새 schema와 façade ownership만 남긴다. `RUNS.md`에는 실제 명령과 결과를 남긴다. `RISKS.md`에는 다음 두 항목의 실측 결과를 갱신한다.

- PIT diluted EPS coverage가 낮을 경우 current PER unavailable 비율.
- provider industry label alias가 taxonomy version 없이 흔들릴 가능성.

root log에는 상세 구현을 복사하지 않고 task 경로와 4차 handoff만 3~5줄 추가한다.

### Step 7: Commit the closeout docs

```bash
git add \
  .aiworkspace/note/finance/tasks/active/market-movers-read-model-hardening-v1-20260720 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "변동 종목 읽기 모델 3차 검증을 정리"
```

---

## Definition Of Done

- canonical sector option과 filter mismatch가 재현되지 않는다.
- ranking, breadth, bellwether가 missing value를 0으로 해석하지 않는다.
- Complete/Partial/Blocked와 사용자 다음 action을 read model이 결정한다.
- sector/industry current flow와 market-cap Top 3가 JSON-safe contract로 제공된다.
- sector bellwether와 return leader가 별도 의미로 제공된다.
- financial report period와 factor가 독립 contract로 제공된다.
- current-price historical PER가 완전히 제거된다.
- current PER는 PIT reported diluted EPS 4개 연속분이 있을 때만 제공된다.
- 4차 React UI가 DB/DataFrame semantics를 다시 해석하지 않고 payload를 소비할 수 있다.
- focused test, relevant service regression, syntax check, diff check가 통과한다.
- 가능한 환경에서는 SP500/Top1000/Top2000 × 일/주/월 real-DB read-only smoke가 통과한다.

## Out Of Scope For This Plan

- React one-shell 레이아웃과 CSS 구현
- ranking row interaction과 selected-state 연결
- price/momentum 70/30 chart 구현
- financial factor segmented control 구현
- news/SEC tab visual polish
- sector historical episode, forward 5D/20D/60D conditional distribution
- industry PIT taxonomy와 industry outlook
- 새 provider ingestion 또는 raw operation dashboard

## Phase Handoff

이 계획 완료 후 4차는 `market_movers_decision_payload_v1`만 입력으로 받아 React shell을 구현한다. 4차 UI가 server-side DataFrame column, raw sector label, DB loader, provider semantics를 다시 판단하게 만들지 않는다.
