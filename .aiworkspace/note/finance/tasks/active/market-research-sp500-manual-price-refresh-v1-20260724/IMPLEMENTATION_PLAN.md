# Market Research S&P 500 Manual Price Refresh V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `Market Research > 지수 가치평가 > S&P 500` 진입 시 저장된 SPX 가격일을 최신 완료 NYSE 거래일과 비교하고, 뒤처졌을 때만 사용자가 `^GSPC`와 `SPY` EOD를 수동 수집한 뒤 최신 가격 기준으로 가치평가를 다시 계산할 수 있게 한다.

**Architecture:** 브라우저 진입은 기존처럼 DB read-only로 유지하고, S&P 500 valuation payload에 별도의 가격 freshness 계약을 붙인다. React의 명시적 action은 Streamlit event handler와 overview action facade를 거쳐 기존 OHLCV ingestion job을 실행하며, 수집 성공 여부가 아니라 수집 후 DB의 SPX 가격일을 postcondition으로 검증한다.

**Tech Stack:** Python 3, `unittest`, Streamlit, React 18, TypeScript 5, Vite 6, 기존 NYSE calendar service, 기존 OHLCV ingestion job과 MySQL persistence.

## Global Constraints

- 백그라운드 `launchd`, cron, heartbeat, 브라우저 자동 수집을 추가하지 않는다.
- 화면 진입 시 provider를 호출하지 않는다. `Ingestion -> DB -> Loader -> UI` 경계를 유지한다.
- 수동 action은 `^GSPC`와 `SPY` 일봉만 `period="1mo"`, `interval="1d"`, `execution_profile="managed_safe"`로 수집한다.
- Shiller, SEP, 공식 S&P EPS와 valuation 산식은 변경하지 않는다.
- 성공 판정은 `latest ^GSPC date >= latest completed NYSE session`이라는 DB postcondition을 사용한다.
- SPX는 index valuation의 필수 기준이고 SPY는 conversion 보조 자료다.
- raw job, row count, provider log 중심의 진단 패널을 추가하지 않는다.
- 기존 개별주식 freshness action과 선택·검색 event 계약을 깨지 않는다.
- registry, saved setup, run history, QA image 등 사용자·generated artifact를 구현 커밋에 포함하지 않는다.
- 각 코드 task는 실패 테스트 작성 → 실패 확인 → 최소 구현 → 통과 확인 → 독립 커밋 순서로 진행한다.

---

## File Map

| Path | Responsibility |
|---|---|
| `app/services/overview/sp500_valuation_freshness.py` | SPX/SPY 가격일과 최신 완료 NYSE 거래일을 비교하는 순수 freshness 계약 |
| `app/services/overview/market_context_valuation.py` | S&P valuation payload에 freshness를 붙이고 valuation 실패와 freshness 실패를 격리 |
| `app/jobs/overview_actions.py` | 명시적 SPX/SPY OHLCV 수집과 DB postcondition 판정 |
| `app/web/overview/market_context_helpers.py` | S&P event nonce, 실행, 결과 기록, 두 valuation cache clear, fallback action |
| `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx` | S&P stale 안내와 수동 action event |
| `app/web/streamlit_components/market_context_valuation/src/style.css` | compact index freshness surface와 420px 반응형 스타일 |
| `tests/test_sp500_price_freshness.py` | freshness와 action facade의 결정적 unit tests |
| `tests/test_market_context_valuation.py` | combined payload, event/cache, React source contract 회귀 테스트 |
| `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` | 운영자가 이해할 수동 최신화 경계와 검증 절차 |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | 신규 service/action 소유 경계 |
| active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md` | 구현 상태, 결정, 실제 실행과 남은 검증 |
| root `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md` | 3~5줄 수준의 완료·handoff 지도 |

---

### Task 1: S&P 500 가격 Freshness 계약

**Files:**

- Create: `app/services/overview/sp500_valuation_freshness.py`
- Create: `tests/test_sp500_price_freshness.py`

**Interfaces:**

- Consumes: `latest_completed_nyse_session(now: datetime | None = None) -> date`
- Produces: `build_sp500_price_freshness(model: Mapping[str, Any], *, now: datetime | None = None) -> dict[str, Any]`
- Payload fields: `status`, `expected_price_date`, `price_basis_date`, `spy_price_basis_date`, `gap_sessions`, `message`, `warnings`, optional `action`

- [ ] **Step 1: Write failing service tests**

Add the following cases to `tests/test_sp500_price_freshness.py`. Patch the calendar boundary so the tests do not depend on the machine clock.

```python
from __future__ import annotations

import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo


class Sp500PriceFreshnessTests(unittest.TestCase):
    def test_ready_when_spx_reaches_latest_completed_session(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        model = {
            "basis": {
                "spx": {"date": "2026-07-23"},
                "spy": {"date": "2026-07-23"},
            }
        }
        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness(model)

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["gap_sessions"], 0)
        self.assertNotIn("action", result)

    def test_stale_spx_exposes_one_manual_action_and_session_gap(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        model = {
            "basis": {
                "spx": {"date": "2026-07-16"},
                "spy": {"date": "2026-07-22"},
            }
        }
        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness(model)

        self.assertEqual(result["status"], "REFRESH_AVAILABLE")
        self.assertEqual(result["gap_sessions"], 5)
        self.assertEqual(result["price_basis_date"], "2026-07-16")
        self.assertEqual(result["spy_price_basis_date"], "2026-07-22")
        self.assertEqual(
            result["action"],
            {
                "id": "refresh_sp500_price_data",
                "label": "최신 데이터로 다시 계산",
                "enabled": True,
            },
        )

    def test_missing_spx_is_actionable(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness({"basis": {}})

        self.assertEqual(result["status"], "MISSING")
        self.assertIsNone(result["price_basis_date"])
        self.assertEqual(result["action"]["id"], "refresh_sp500_price_data")

    def test_future_dated_spx_keeps_warning_evidence(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        model = {"basis": {"spx": {"date": "2026-07-24"}}}
        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness(model)

        self.assertEqual(result["status"], "READY")
        self.assertIn("SPX_PRICE_DATE_AFTER_COMPLETED_SESSION", result["warnings"])

    def test_calendar_error_preserves_retry_action(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            side_effect=RuntimeError("calendar unavailable"),
        ):
            result = build_sp500_price_freshness(
                {"basis": {"spx": {"date": "2026-07-16"}}}
            )

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["action"]["id"], "refresh_sp500_price_data")
        self.assertIn("최신 완료 장", result["message"])

    def test_market_open_uses_previous_completed_session(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        result = build_sp500_price_freshness(
            {"basis": {"spx": {"date": "2026-07-23"}}},
            now=datetime(
                2026,
                7,
                24,
                10,
                0,
                tzinfo=ZoneInfo("America/New_York"),
            ),
        )

        self.assertEqual(result["expected_price_date"], "2026-07-23")
        self.assertEqual(result["status"], "READY")

    def test_weekend_uses_friday_completed_session(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        result = build_sp500_price_freshness(
            {"basis": {"spx": {"date": "2026-07-24"}}},
            now=datetime(
                2026,
                7,
                25,
                12,
                0,
                tzinfo=ZoneInfo("America/New_York"),
            ),
        )

        self.assertEqual(result["expected_price_date"], "2026-07-24")
        self.assertEqual(result["status"], "READY")
```

- [ ] **Step 2: Run the focused tests and confirm the expected import failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_sp500_price_freshness -v
```

Expected: `ModuleNotFoundError: app.services.overview.sp500_valuation_freshness`.

- [ ] **Step 3: Implement the minimal freshness service**

Create `app/services/overview/sp500_valuation_freshness.py` with these concrete helpers and result rules:

```python
from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from typing import Any

from app.services.nyse_calendar import (
    latest_completed_nyse_session,
    previous_nyse_trading_day,
)


ACTION = {
    "id": "refresh_sp500_price_data",
    "label": "최신 데이터로 다시 계산",
    "enabled": True,
}


def _as_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _basis_date(model: Mapping[str, Any], symbol_key: str) -> date | None:
    basis = dict(model.get("basis") or {})
    row = dict(basis.get(symbol_key) or {})
    return _as_date(row.get("date") or row.get("price_basis_date"))


def _nyse_session_gap(start_exclusive: date, end_inclusive: date) -> int:
    current = start_exclusive + timedelta(days=1)
    count = 0
    while current <= end_inclusive:
        if previous_nyse_trading_day(current) == current:
            count += 1
        current += timedelta(days=1)
    return count


def build_sp500_price_freshness(
    model: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compare persisted SPX/SPY price dates with the last completed NYSE session."""
    spx_date: date | None = None
    spy_date: date | None = None
    try:
        spx_date = _basis_date(model, "spx")
        spy_date = _basis_date(model, "spy")
        expected = latest_completed_nyse_session(now)
        warnings: list[str] = []
        if spx_date and spx_date > expected:
            warnings.append("SPX_PRICE_DATE_AFTER_COMPLETED_SESSION")
        if spy_date and spy_date > expected:
            warnings.append("SPY_PRICE_DATE_AFTER_COMPLETED_SESSION")
        if spx_date is None:
            status = "MISSING"
            gap_sessions = None
            message = (
                f"SPX 가격 기준일이 없습니다. 최신 완료 장 {expected.isoformat()} "
                "자료를 수동으로 확인할 수 있습니다."
            )
        elif spx_date < expected:
            status = "REFRESH_AVAILABLE"
            gap_sessions = _nyse_session_gap(spx_date, expected)
            message = (
                f"가격 기준일 {spx_date.isoformat()} · "
                f"최신 완료 장 {expected.isoformat()}"
            )
        else:
            status = "READY"
            gap_sessions = 0
            message = f"최신 완료 장 {expected.isoformat()} 가격을 사용합니다."
        result: dict[str, Any] = {
            "status": status,
            "expected_price_date": expected.isoformat(),
            "price_basis_date": spx_date.isoformat() if spx_date else None,
            "spy_price_basis_date": spy_date.isoformat() if spy_date else None,
            "gap_sessions": gap_sessions,
            "message": message,
            "warnings": warnings,
        }
        if status != "READY":
            result["action"] = dict(ACTION)
        return result
    except Exception as exc:
        return {
            "status": "ERROR",
            "expected_price_date": None,
            "price_basis_date": spx_date.isoformat() if spx_date else None,
            "spy_price_basis_date": spy_date.isoformat() if spy_date else None,
            "gap_sessions": None,
            "message": f"최신 완료 장을 확인하지 못했습니다: {type(exc).__name__}",
            "warnings": ["FRESHNESS_CALCULATION_FAILED"],
            "action": dict(ACTION),
        }
```

- [ ] **Step 4: Run focused freshness tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_sp500_price_freshness -v
```

Expected: 7 tests pass.

- [ ] **Step 5: Commit the freshness contract**

```bash
git add app/services/overview/sp500_valuation_freshness.py tests/test_sp500_price_freshness.py
git commit -m "기능: S&P 500 가격 최신성 판정 추가"
```

---

### Task 2: S&P Valuation Read Model에 Freshness 연결

**Files:**

- Modify: `app/services/overview/market_context_valuation.py`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**

- Consumes: `build_sp500_price_freshness(model, *, now=None)`
- Produces: `model["instruments"]["sp500"]["data_freshness"]`
- Isolation rule: valuation payload를 먼저 만들고 freshness 계산 실패는 `ERROR` freshness로만 표현한다.

- [ ] **Step 1: Add a failing combined-model test**

Append a test that patches both builders and confirms the original S&P fields remain intact:

```python
    def test_combined_model_attaches_sp500_price_freshness_without_changing_valuation(self) -> None:
        from app.services.overview.market_context_valuation import (
            build_market_context_valuation_read_model,
        )

        sp500 = {
            "status": "READY",
            "basis": {
                "spx": {"date": "2026-07-16"},
                "spy": {"date": "2026-07-22"},
            },
            "marker": "preserved",
        }
        freshness = {
            "status": "REFRESH_AVAILABLE",
            "expected_price_date": "2026-07-23",
            "price_basis_date": "2026-07-16",
            "spy_price_basis_date": "2026-07-22",
            "action": {"id": "refresh_sp500_price_data", "enabled": True},
        }
        with patch(
            "app.services.overview.market_context_valuation.build_sp500_valuation_read_model",
            return_value=sp500,
        ), patch(
            "app.services.overview.market_context_valuation.build_sp500_price_freshness",
            return_value=freshness,
        ) as freshness_builder:
            model = build_market_context_valuation_read_model(
                default_instrument="sp500",
                show_instrument_selector=False,
            )

        actual = model["instruments"]["sp500"]
        self.assertEqual(actual["marker"], "preserved")
        self.assertEqual(actual["data_freshness"], freshness)
        freshness_builder.assert_called_once()
        self.assertEqual(freshness_builder.call_args.args[0]["marker"], "preserved")
```

In the existing
`test_combined_model_keeps_sp500_payload_and_isolates_stock_failure`, replace
the whole-dict equality assertion with:

```python
self.assertEqual(model["instruments"]["sp500"]["marker"], "unchanged")
self.assertIn("data_freshness", model["instruments"]["sp500"])
```

- [ ] **Step 2: Run the single test and confirm failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation.MarketContextValuationTests.test_combined_model_attaches_sp500_price_freshness_without_changing_valuation -v
```

Expected: FAIL because `build_sp500_price_freshness` is not imported or called.

- [ ] **Step 3: Attach freshness after isolated valuation construction**

Modify the S&P branch in `app/services/overview/market_context_valuation.py`:

```python
from app.services.overview.sp500_valuation_freshness import (
    build_sp500_price_freshness,
)

# ...
if "sp500" in selected_ids:
    sp500 = _isolated(build_sp500_valuation_read_model, SP500_INSTRUMENT)
    sp500["data_freshness"] = build_sp500_price_freshness(sp500)
    instruments["sp500"] = sp500
```

Do not call a loader or provider from this branch. Keep
`schema_version="market_context_valuation_v5"` because this is an additive
field.

- [ ] **Step 4: Run combined-model regression tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation -v
```

Expected: all tests pass, including existing S&P isolation and individual-stock freshness tests.

- [ ] **Step 5: Commit the read-model integration**

```bash
git add app/services/overview/market_context_valuation.py tests/test_market_context_valuation.py
git commit -m "기능: S&P 500 가치평가에 가격 최신성 연결"
```

---

### Task 3: 수동 SPX/SPY 수집 Action과 DB Postcondition

**Files:**

- Modify: `app/jobs/overview_actions.py`
- Modify: `tests/test_sp500_price_freshness.py`

**Interfaces:**

- Produces:

```python
def run_overview_sp500_price_refresh(
    *,
    model_builder: Callable[..., dict[str, Any]] = build_market_context_valuation_read_model,
    collection_runner: Callable[..., JobResult] = run_collect_ohlcv,
) -> JobResult:
    ...
```

- `model_builder(default_instrument="sp500", show_instrument_selector=False)`를 수집 전후에 호출한다.
- `collection_runner(["^GSPC", "SPY"], period="1mo", interval="1d", execution_profile="managed_safe")`를 정확히 한 번 호출한다.
- 결과 `details`는 `before`, `after`, `collection`만 보존하고 UI에는 compact reflection만 전달한다.

- [ ] **Step 1: Write failing action tests**

Add model factories and the four postcondition cases:

```python
def _sp500_model(
    status: str,
    spx: str | None,
    spy: str | None,
    expected: str = "2026-07-23",
) -> dict:
    action = (
        {
            "id": "refresh_sp500_price_data",
            "label": "최신 데이터로 다시 계산",
            "enabled": True,
        }
        if status != "READY"
        else None
    )
    freshness = {
        "status": status,
        "expected_price_date": expected,
        "price_basis_date": spx,
        "spy_price_basis_date": spy,
    }
    if action:
        freshness["action"] = action
    return {"instruments": {"sp500": {"data_freshness": freshness}}}


class Sp500PriceRefreshActionTests(unittest.TestCase):
    def test_collects_only_spx_and_spy_and_verifies_both_dates(self) -> None:
        from app.jobs.overview_actions import run_overview_sp500_price_refresh

        model_builder = Mock(
            side_effect=[
                _sp500_model("REFRESH_AVAILABLE", "2026-07-16", "2026-07-22"),
                _sp500_model("READY", "2026-07-23", "2026-07-23"),
            ]
        )
        collector = Mock(
            return_value={"status": "success", "rows_written": 2}
        )

        result = run_overview_sp500_price_refresh(
            model_builder=model_builder,
            collection_runner=collector,
        )

        self.assertEqual(result["status"], "success")
        collector.assert_called_once_with(
            ["^GSPC", "SPY"],
            period="1mo",
            interval="1d",
            execution_profile="managed_safe",
        )
        self.assertEqual(result["details"]["after"]["price_basis_date"], "2026-07-23")

    def test_collector_success_is_incomplete_when_spx_remains_stale(self) -> None:
        from app.jobs.overview_actions import run_overview_sp500_price_refresh

        stale = _sp500_model("REFRESH_AVAILABLE", "2026-07-16", "2026-07-23")
        result = run_overview_sp500_price_refresh(
            model_builder=Mock(side_effect=[stale, stale]),
            collection_runner=Mock(
                return_value={"status": "success", "rows_written": 1}
            ),
        )

        self.assertEqual(result["status"], "incomplete")
        self.assertIn("기존", result["message"])

    def test_spx_current_and_spy_stale_is_partial_success(self) -> None:
        from app.jobs.overview_actions import run_overview_sp500_price_refresh

        result = run_overview_sp500_price_refresh(
            model_builder=Mock(
                side_effect=[
                    _sp500_model("REFRESH_AVAILABLE", "2026-07-16", "2026-07-22"),
                    _sp500_model("READY", "2026-07-23", "2026-07-22"),
                ]
            ),
            collection_runner=Mock(
                return_value={"status": "partial_success", "rows_written": 1}
            ),
        )

        self.assertEqual(result["status"], "partial_success")
        self.assertIn("SPY", result["message"])

    def test_provider_exception_returns_failed_with_old_basis(self) -> None:
        from app.jobs.overview_actions import run_overview_sp500_price_refresh

        before = _sp500_model("REFRESH_AVAILABLE", "2026-07-16", "2026-07-22")
        result = run_overview_sp500_price_refresh(
            model_builder=Mock(return_value=before),
            collection_runner=Mock(
                side_effect=RuntimeError("provider unavailable")
            ),
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["details"]["before"]["price_basis_date"], "2026-07-16")

    def test_preflight_db_exception_returns_failed_without_calling_provider(self) -> None:
        from app.jobs.overview_actions import run_overview_sp500_price_refresh

        collector = Mock()
        result = run_overview_sp500_price_refresh(
            model_builder=Mock(side_effect=RuntimeError("db unavailable")),
            collection_runner=collector,
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["details"]["before"], {})
        collector.assert_not_called()
```

- [ ] **Step 2: Run only the action tests and confirm import failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_sp500_price_freshness.Sp500PriceRefreshActionTests -v
```

Expected: `ImportError` for `run_overview_sp500_price_refresh`.

- [ ] **Step 3: Implement the action facade and result helper**

Add a private extractor and result builder next to the existing selected-stock refresh action:

```python
def _sp500_freshness_from_market_context(model: dict[str, Any]) -> dict[str, Any]:
    instruments = dict(model.get("instruments") or {})
    sp500 = dict(instruments.get("sp500") or {})
    return dict(sp500.get("data_freshness") or {})


def _sp500_price_refresh_result(
    *,
    started_at: datetime,
    status: str,
    message: str,
    before: dict[str, Any],
    after: dict[str, Any],
    collection: dict[str, Any] | None,
) -> JobResult:
    finished_at = datetime.now()
    collected = dict(collection or {})
    return {
        "job_name": "overview_sp500_price_refresh",
        "status": status,
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": round((finished_at - started_at).total_seconds(), 3),
        "rows_written": int(collected.get("rows_written") or 0),
        "symbols_requested": 2,
        "symbols_processed": 2 if status in {"success", "partial_success"} else 0,
        "failed_symbols": list(collected.get("failed_symbols") or []),
        "message": message,
        "details": {
            "before": before,
            "after": after,
            "collection": collected,
        },
    }
```

Implement the public facade with the exact branch order:

```python
def run_overview_sp500_price_refresh(
    *,
    model_builder: Callable[..., dict[str, Any]] = build_market_context_valuation_read_model,
    collection_runner: Callable[..., JobResult] = run_collect_ohlcv,
) -> JobResult:
    """Collect bounded SPX/SPY EOD data and verify the persisted SPX postcondition."""
    started_at = datetime.now()
    try:
        before = _sp500_freshness_from_market_context(
            dict(
                model_builder(
                    default_instrument="sp500",
                    show_instrument_selector=False,
                )
            )
        )
    except Exception as exc:
        return _sp500_price_refresh_result(
            started_at=started_at,
            status="failed",
            message="저장된 S&P 500 가격 상태를 확인하지 못했습니다.",
            before={},
            after={},
            collection={"status": "failed", "message": f"{type(exc).__name__}: {exc}"},
        )
    if before.get("status") == "READY":
        return _sp500_price_refresh_result(
            started_at=started_at,
            status="success",
            message="S&P 500 가격 자료가 이미 최신 상태입니다.",
            before=before,
            after=before,
            collection=None,
        )
    action = dict(before.get("action") or {})
    if action.get("id") != "refresh_sp500_price_data" or not action.get("enabled"):
        return _sp500_price_refresh_result(
            started_at=started_at,
            status="failed",
            message="S&P 500 가격 갱신 조건을 확인할 수 없습니다.",
            before=before,
            after=before,
            collection=None,
        )
    try:
        collection = dict(
            collection_runner(
                ["^GSPC", "SPY"],
                period="1mo",
                interval="1d",
                execution_profile="managed_safe",
            )
        )
        after = _sp500_freshness_from_market_context(
            dict(
                model_builder(
                    default_instrument="sp500",
                    show_instrument_selector=False,
                )
            )
        )
    except Exception as exc:
        return _sp500_price_refresh_result(
            started_at=started_at,
            status="failed",
            message=(
                "최신 가격 자료를 확인하지 못했습니다. "
                f"기존 {before.get('price_basis_date') or '-'} 결과를 유지합니다."
            ),
            before=before,
            after=before,
            collection={"status": "failed", "message": f"{type(exc).__name__}: {exc}"},
        )
    expected = str(after.get("expected_price_date") or "")
    spx_date = str(after.get("price_basis_date") or "")
    spy_date = str(after.get("spy_price_basis_date") or "")
    if expected and spx_date >= expected and spy_date >= expected:
        status = "success"
        message = f"최신 완료 장 {expected} 가격으로 다시 계산했습니다."
    elif expected and spx_date >= expected:
        status = "partial_success"
        message = (
            f"SPX는 {expected}까지 반영했습니다. "
            f"SPY는 {spy_date or '자료 없음'}까지 확인됐습니다."
        )
    else:
        status = "incomplete"
        message = (
            "최신 완료 장까지 확인하지 못했습니다. "
            f"기존 {before.get('price_basis_date') or '-'} 결과를 유지합니다."
        )
    return _sp500_price_refresh_result(
        started_at=started_at,
        status=status,
        message=message,
        before=before,
        after=after,
        collection=collection,
    )
```

String comparison is safe here only because both sides are normalized `YYYY-MM-DD`; if the freshness contract later changes types, convert both with `_as_date` rather than keeping mixed types.

- [ ] **Step 4: Run action and existing overview action tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sp500_price_freshness.Sp500PriceRefreshActionTests \
  tests.test_us_stock_freshness -v
```

Expected: all selected tests pass. Existing overview action regressions are in
`tests.test_us_stock_freshness`.

- [ ] **Step 5: Commit the manual action**

```bash
git add app/jobs/overview_actions.py tests/test_sp500_price_freshness.py
git commit -m "기능: S&P 500 수동 가격 수집 액션 추가"
```

---

### Task 4: Streamlit Event, Cache, Result Reflection, Fallback

**Files:**

- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**

- New event id: `refresh_sp500_price_data`
- New session keys:
  - `SP500_COLLECTION_RESULT_KEY = "overview_sp500_price_refresh_result"`
  - `SP500_EVENT_KEY = "overview_sp500_price_refresh_last_event"`
- New UI runner: `_run_sp500_price_refresh_for_ui() -> dict[str, Any]`
- New cache helper: `_clear_sp500_valuation_caches() -> None`
- Run history is written exactly once by `_store_overview_job_result`.

- [ ] **Step 1: Write failing event/cache tests**

Add these tests to `tests/test_market_context_valuation.py`, using dependency injection so no real provider, DB, or Streamlit rerun is invoked:

```python
    def test_sp500_refresh_event_runs_once_and_clears_both_caches(self) -> None:
        from app.web.overview.market_context_helpers import (
            SP500_COLLECTION_RESULT_KEY,
            _handle_market_context_valuation_event,
        )

        state = {}
        run_action = Mock(return_value={"status": "success", "message": "반영 완료"})
        store_result = Mock()
        clear_cache = Mock()
        rerun = Mock()
        event = {"id": "refresh_sp500_price_data", "nonce": "spx-1"}

        first = _handle_market_context_valuation_event(
            event,
            state=state,
            run_sp500_action=run_action,
            store_sp500_result=store_result,
            clear_sp500_cache=clear_cache,
            rerun=rerun,
        )
        second = _handle_market_context_valuation_event(
            event,
            state=state,
            run_sp500_action=run_action,
            store_sp500_result=store_result,
            clear_sp500_cache=clear_cache,
            rerun=rerun,
        )

        self.assertTrue(first)
        self.assertFalse(second)
        run_action.assert_called_once_with()
        store_result.assert_called_once_with(run_action.return_value)
        clear_cache.assert_called_once_with()
        rerun.assert_called_once_with()
        self.assertEqual(
            SP500_COLLECTION_RESULT_KEY,
            "overview_sp500_price_refresh_result",
        )

    def test_sp500_failed_refresh_keeps_cache_and_reruns_with_retry_result(self) -> None:
        from app.web.overview.market_context_helpers import (
            _handle_market_context_valuation_event,
        )

        clear_cache = Mock()
        rerun = Mock()
        result = {"status": "failed", "message": "기존 결과 유지"}
        handled = _handle_market_context_valuation_event(
            {"id": "refresh_sp500_price_data", "nonce": "spx-2"},
            state={},
            run_sp500_action=Mock(return_value=result),
            store_sp500_result=Mock(),
            clear_sp500_cache=clear_cache,
            rerun=rerun,
        )

        self.assertTrue(handled)
        clear_cache.assert_not_called()
        rerun.assert_called_once_with()
```

- [ ] **Step 2: Run the two tests and confirm signature/constant failures**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_market_context_valuation.MarketContextValuationTests.test_sp500_refresh_event_runs_once_and_clears_both_caches \
  tests.test_market_context_valuation.MarketContextValuationTests.test_sp500_failed_refresh_keeps_cache_and_reruns_with_retry_result -v
```

Expected: FAIL because the S&P constants and handler parameters do not exist.

- [ ] **Step 3: Add S&P event handling without changing stock semantics**

Import `run_overview_sp500_price_refresh`, add the two constants, and use one accepted-id set:

```python
SP500_COLLECTION_RESULT_KEY = "overview_sp500_price_refresh_result"
SP500_EVENT_KEY = "overview_sp500_price_refresh_last_event"
MARKET_CONTEXT_EVENT_IDS = US_STOCK_EVENT_IDS | {"refresh_sp500_price_data"}
```

Update `_consume_market_context_valuation_event` to select the nonce key by action:

```python
event_key = (
    SP500_EVENT_KEY
    if action_id == "refresh_sp500_price_data"
    else US_STOCK_EVENT_KEY
)
if state.get(event_key) == event_token:
    return False
state[event_key] = event_token
```

Extend the handler signature:

```python
def _handle_market_context_valuation_event(
    event: dict[str, Any] | None,
    *,
    state: Any = None,
    run_action: Callable[[str], dict[str, Any]] | None = None,
    run_sp500_action: Callable[[], dict[str, Any]] | None = None,
    store_result: Callable[[dict[str, Any]], None] | None = None,
    store_sp500_result: Callable[[dict[str, Any]], None] | None = None,
    clear_cache: Callable[[], None] | None = None,
    clear_sp500_cache: Callable[[], None] | None = None,
    rerun: Callable[[], None] | None = None,
) -> bool:
```

Place the S&P branch after nonce consumption and before the stock search/select branches:

```python
if action_id == "refresh_sp500_price_data":
    result = (run_sp500_action or _run_sp500_price_refresh_for_ui)()
    if store_sp500_result is not None:
        store_sp500_result(result)
    else:
        _store_overview_job_result(SP500_COLLECTION_RESULT_KEY, result)
    if str(result.get("status") or "").lower() in {"success", "partial_success"}:
        (clear_sp500_cache or _clear_sp500_valuation_caches)()
    (rerun or st.rerun)()
    return True
```

Use these exact helpers:

```python
def _clear_sp500_valuation_caches() -> None:
    load_sp500_valuation_model.clear()
    load_market_context_valuation_model.clear()


def _run_sp500_price_refresh_for_ui() -> dict[str, Any]:
    with st.status("최신 장 마감 데이터를 수집하는 중입니다.", expanded=True) as status:
        result = run_overview_sp500_price_refresh()
        result_status = str(result.get("status") or "failed").lower()
        state = "complete" if result_status in {"success", "partial_success"} else "error"
        status.update(label=str(result.get("message") or "가격 자료 확인을 마쳤습니다."), state=state)
    return result
```

Do not clear caches for `incomplete` or `failed`. The old valuation remains visible and the next payload retains an actionable freshness state.

- [ ] **Step 4: Attach one-shot reflection and add the non-React fallback**

In `render_market_context_valuation`, pop `SP500_COLLECTION_RESULT_KEY` exactly once and attach:

```python
sp500_result = st.session_state.pop(SP500_COLLECTION_RESULT_KEY, None)
if isinstance(sp500_result, dict):
    instruments = dict(payload.get("instruments") or {})
    sp500 = dict(instruments.get("sp500") or {})
    sp500["collection_result"] = _sp500_collection_reflection(sp500_result)
    instruments["sp500"] = sp500
    payload["instruments"] = instruments
```

The reflection function returns only:

```python
{
    "status": str(result.get("status") or "failed"),
    "message": str(result.get("message") or ""),
}
```

In `_render_market_context_valuation_fallback`, before valuation metrics, render a warning and button only when the selected instrument is S&P and `data_freshness.status != "READY"`:

```python
freshness = dict(payload.get("data_freshness") or {})
action = dict(freshness.get("action") or {})
if action.get("id") == "refresh_sp500_price_data" and action.get("enabled"):
    st.warning(str(freshness.get("message") or "가격 자료 최신화가 필요합니다."))
    if st.button(
        str(action.get("label") or "최신 데이터로 다시 계산"),
        key="fallback_refresh_sp500_price_data",
    ):
        result = _run_sp500_price_refresh_for_ui()
        _store_overview_job_result(SP500_COLLECTION_RESULT_KEY, result)
        if str(result.get("status") or "").lower() in {"success", "partial_success"}:
            _clear_sp500_valuation_caches()
        st.rerun()
```

Keep the existing fallback metrics and disclaimers unchanged.

- [ ] **Step 5: Run event, fallback-source, and combined-model regressions**

Run:

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation -v
```

Expected: all tests pass; existing stock refresh still validates the selected symbol and consumes each nonce once.

- [ ] **Step 6: Commit the Streamlit event flow**

```bash
git add app/web/overview/market_context_helpers.py tests/test_market_context_valuation.py
git commit -m "기능: S&P 500 수동 최신화 이벤트 연결"
```

---

### Task 5: React S&P Freshness Surface와 Production Build

**Files:**

- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Modify: `app/web/streamlit_components/market_context_valuation/component_static/index.html`
- Replace generated hashed assets under: `app/web/streamlit_components/market_context_valuation/component_static/assets/`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**

- `DataFreshness.action.id` union: `"refresh_us_stock_data" | "refresh_sp500_price_data"`
- S&P event payload: `{id: "refresh_sp500_price_data", nonce: ...}` with no stock symbol.
- UI copy:
  - header: `가격 기준일`
  - title: `가격 자료 최신화 필요`
  - button: `최신 데이터로 다시 계산`
  - collecting: `갱신 중`

- [ ] **Step 1: Add failing React source-contract tests**

Add:

```python
    def test_react_sp500_stale_surface_has_price_basis_and_manual_action(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        for token in (
            "refresh_sp500_price_data",
            "function IndexFreshnessBar",
            "가격 자료 최신화 필요",
            "최신 완료 장",
            "emitEvent(action.id)",
        ):
            self.assertIn(token, component)
        self.assertIn(
            'isStock ? showTurnaround ? "재무 기준일" : "가격 기준일" : "가격 기준일"',
            component,
        )
        self.assertEqual(component.count("<IndexFreshnessBar"), 1)
```

Extend the existing individual-stock test so it still requires:

```python
self.assertIn('emitEvent(action.id, { symbol: action.symbol })', component)
```

- [ ] **Step 2: Run the React source-contract tests and confirm failure**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_market_context_valuation.MarketContextValuationTests.test_react_sp500_stale_surface_has_price_basis_and_manual_action \
  tests.test_market_context_valuation.MarketContextValuationTests.test_selected_stock_renders_one_header_refresh_action_before_analysis_selector -v
```

Expected: the new S&P test fails; the existing stock test passes.

- [ ] **Step 3: Generalize the type only as far as the two actions require**

Change `DataFreshness`:

```tsx
type DataFreshness = {
  status?: "READY" | "REFRESH_AVAILABLE" | "MISSING" | "ERROR" | "PARTIAL" | "BLOCKED" | string;
  expected_price_date?: string | null;
  price_basis_date?: string | null;
  spy_price_basis_date?: string | null;
  gap_sessions?: number | null;
  message?: string;
  warnings?: string[];
  profile_basis_date?: string | null;
  statement_period_end?: string | null;
  statement_available_at?: string | null;
  gaps?: { scope: string; reason_code: string; repairable: boolean }[];
  action?: {
    id: "refresh_us_stock_data" | "refresh_sp500_price_data";
    label: string;
    detail?: string;
    symbol?: string;
    scopes?: string[];
    enabled: boolean;
  };
};
```

Do not introduce a generic job/result table type.

- [ ] **Step 4: Add a dedicated compact index freshness component**

Place it beside `FreshnessBar`:

```tsx
function IndexFreshnessBar({
  freshness,
  collecting,
  result,
  onRefresh,
}: {
  freshness?: DataFreshness;
  collecting: boolean;
  result?: CollectionResult;
  onRefresh: () => void;
}) {
  const action = freshness?.action;
  if (freshness?.status === "READY" && !result) return null;
  return <section
    className={`index-freshness index-freshness-${(freshness?.status || "error").toLowerCase()}`}
    aria-label="S&P 500 가격 자료 최신화"
  >
    <div>
      <strong>{freshness?.status === "READY" ? "가격 자료 최신화 완료" : "가격 자료 최신화 필요"}</strong>
      <span>{result?.message || freshness?.message || "저장된 가격 자료를 확인합니다."}</span>
      <small>가격 기준일 {freshness?.price_basis_date || "-"} · 최신 완료 장 {freshness?.expected_price_date || "-"}</small>
    </div>
    {action?.enabled ? <button type="button" disabled={collecting} onClick={onRefresh}>
      {collecting ? "갱신 중" : action.label || "최신 데이터로 다시 계산"}
    </button> : null}
  </section>;
}
```

Change the header expression to:

```tsx
const basisLabel = isStock
  ? showTurnaround ? "재무 기준일" : "가격 기준일"
  : "가격 기준일";
```

Split the event method while preserving the existing stock payload:

```tsx
const refresh = () => {
  const action = payload.data_freshness?.action;
  if (!action?.enabled) return;
  if (isStock && action.id === "refresh_us_stock_data" && action.symbol) {
    setCollecting(true);
    emitEvent(action.id, { symbol: action.symbol });
    return;
  }
  if (!isStock && action.id === "refresh_sp500_price_data") {
    setCollecting(true);
    emitEvent(action.id);
  }
};
```

Render it once after the header and before valuation sections:

```tsx
{!isStock ? (
  <IndexFreshnessBar
    freshness={payload.data_freshness}
    collecting={collecting}
    result={payload.collection_result}
    onRefresh={refresh}
  />
) : null}
```

Retain the existing `FreshnessBar` render for selected stock.

- [ ] **Step 5: Add compact responsive CSS**

Add explicit styles without altering chart sizing:

```css
.index-freshness {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid rgba(217, 119, 6, 0.28);
  border-radius: 14px;
  background: rgba(255, 251, 235, 0.82);
}

.index-freshness > div {
  display: grid;
  gap: 3px;
}

.index-freshness span,
.index-freshness small {
  color: var(--muted);
}

.index-freshness button {
  flex: 0 0 auto;
}

@media (max-width: 640px) {
  .index-freshness {
    align-items: stretch;
    flex-direction: column;
  }

  .index-freshness button {
    width: 100%;
  }
}
```

Retain the class names and responsive layout above. Where the file already
defines a shared button rule, add `.index-freshness button` to that selector
instead of duplicating the same declarations.

- [ ] **Step 6: Run Python source-contract tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_market_context_valuation -v
```

Expected: all tests pass, including exactly one S&P action and exactly one stock action.

- [ ] **Step 7: Type-check through a production build**

Run:

```bash
npm run build
```

Working directory:

```text
app/web/streamlit_components/market_context_valuation
```

Expected: Vite exits 0 and rewrites `component_static/index.html` plus hashed JS/CSS assets. Confirm the old unreferenced hashed assets are removed by the build rather than staging both old and new copies.

- [ ] **Step 8: Commit source and compiled component together**

```bash
git add \
  app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx \
  app/web/streamlit_components/market_context_valuation/src/style.css \
  app/web/streamlit_components/market_context_valuation/component_static \
  tests/test_market_context_valuation.py
git commit -m "기능: S&P 500 가격 최신화 버튼 표시"
```

---

### Task 6: 실제 수집, Browser QA, Durable Documentation

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generated only, do not commit: one S&P refresh QA screenshot

**Interfaces:**

- Actual smoke invokes the same browser action the user will use.
- Expected date comes from `latest_completed_nyse_session()` at QA time; do not hardcode `2026-07-23`.
- Documentation must distinguish price freshness from Shiller/SEP/EPS cadence.

- [ ] **Step 1: Run focused and regression test suites**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sp500_price_freshness \
  tests.test_market_context_valuation \
  tests.test_sp500_valuation \
  tests.test_service_contracts -v
```

Expected: all selected tests pass.

- [ ] **Step 2: Run static verification**

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/overview/sp500_valuation_freshness.py \
  app/services/overview/market_context_valuation.py \
  app/jobs/overview_actions.py \
  app/web/overview/market_context_helpers.py
git diff --check
```

Expected: both commands exit 0 with no syntax or whitespace errors.

- [ ] **Step 3: Start or reuse the local Streamlit app and capture the stale state**

Open `Market Research > 지수 가치평가 > S&P 500`. Before clicking:

- confirm the header says `가격 기준일`;
- confirm the screen compares the stored SPX date with the dynamically calculated latest completed NYSE session;
- confirm `최신 데이터로 다시 계산` appears only if SPX is stale or missing;
- confirm no provider call occurs merely by entering the page.

Capture a generated screenshot outside staged paths when the stale state is available.

- [ ] **Step 4: Click the action once and verify the real DB postcondition**

Click `최신 데이터로 다시 계산` once. Confirm:

- the button changes to `갱신 중`;
- only `^GSPC` and `SPY` OHLCV collection runs;
- the event nonce prevents a duplicate execution across rerun;
- the screen rerenders with a current `가격 기준일`;
- the persistent action disappears when SPX is current;
- a compact one-shot confirmation may appear, but no raw rows/job panel appears.

Then verify through the existing loader:

```bash
.venv/bin/python - <<'PY'
from app.services.nyse_calendar import latest_completed_nyse_session
from finance.loaders.price import load_latest_prices

expected = latest_completed_nyse_session()
rows = load_latest_prices(["^GSPC", "SPY"])
by_symbol = {
    str(row.symbol): row.latest_date.date().isoformat()
    for row in rows.itertuples(index=False)
}
print({"expected": expected.isoformat(), "actual": by_symbol})
assert by_symbol["^GSPC"] >= expected.isoformat()
PY
```

Expected: assertion passes. Record whether SPY reached the same date; if it did not, record the action as `partial_success`, not a full failure.

- [ ] **Step 5: Perform desktop and 420px Browser QA**

Desktop:

- freshness surface sits between the header and valuation content;
- the stale/current dates and next action are readable without opening details;
- existing valuation graphs and evidence remain visible.

420px:

- copy does not overflow;
- action button spans the available width;
- chart and instrument navigation remain usable.

Keep one representative QA screenshot as a generated artifact and do not stage it.

- [ ] **Step 6: Synchronize durable and task documentation**

Update `PROJECT_MAP.md` with the new service/action ownership. Update `OVERVIEW_MARKET_INTELLIGENCE.md` with this operational contract:

```text
화면 진입: DB read-only freshness 판정
수동 버튼: ^GSPC / SPY 1개월 일봉 수집
성공 조건: DB ^GSPC latest_date >= latest completed NYSE session
제외 범위: Shiller / SEP / 공식 EPS
백그라운드 scheduler: 없음
```

Update task documents:

- `STATUS.md`: mark 1차, 2차, 3차 completion separately.
- `NOTES.md`: record the actual before/after SPX and SPY dates and the postcondition result.
- `RUNS.md`: record exact test/build/Browser QA commands and exit results.
- `RISKS.md`: keep only unresolved provider/calendar/DB risks; do not mark `NOT_RUN` as pass.

Update root logs with only the request, interpreted goal, completed outcome, and next handoff path.

- [ ] **Step 7: Inspect the final diff and exclude unrelated files**

Run:

```bash
git status --short
git diff --check
git diff --stat
git diff -- \
  .aiworkspace/note/finance/registries \
  .aiworkspace/note/finance/saved
```

Expected: no implementation change under `registries/` or `saved/`; existing unrelated dirty files remain unstaged.

- [ ] **Step 8: Commit documentation closeout**

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md \
  .aiworkspace/note/finance/tasks/active/market-research-sp500-manual-price-refresh-v1-20260724 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: S&P 500 수동 가격 최신화 흐름 정리"
```

- [ ] **Step 9: Run final verification against committed state**

Run:

```bash
git status --short
git log -6 --oneline
.venv/bin/python -m unittest \
  tests.test_sp500_price_freshness \
  tests.test_market_context_valuation \
  tests.test_sp500_valuation \
  tests.test_service_contracts -v
```

Expected:

- all selected tests pass;
- the task’s commits are present;
- only pre-existing unrelated registry/run-history/QA artifacts remain dirty;
- no launchd or cron files were created.

## Completion Handoff

Final response must state:

- 전체 roadmap 3차 중 3차까지 완료했는지;
- 실제 갱신 전후 SPX/SPY 가격일과 latest completed NYSE session;
- test/build/Browser QA evidence;
- screenshot path;
- remaining risks, especially provider or DB availability;
- no background scheduler was added;
- next continuation point: active task directory and `OVERVIEW_MARKET_INTELLIGENCE.md`.
