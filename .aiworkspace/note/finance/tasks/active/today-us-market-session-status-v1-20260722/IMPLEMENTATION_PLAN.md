# Today U.S. Market Session Status V1 Implementation Plan

**Execution Result:** Complete on 2026-07-22. Detailed verification evidence is recorded in `RUNS.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a DST-safe U.S. regular-market status strip to Today showing open state, New York and Korea clocks, both session-hour representations, and the countdown to the next open or close.

**Architecture:** A new pure Python session module converts DB-backed official holiday and early-close rows into a bounded UTC schedule. `today_page.py` performs only narrow DB reads, `app/services/today.py` composes the schedule into `today_home_v3`, and the existing React component resolves the live phase and countdown locally without Streamlit reruns.

**Tech Stack:** Python 3.12, `datetime`/`zoneinfo`, Streamlit, existing `market_event_calendar`, React 18, TypeScript 5.7, Vite 6, Vitest 4, pytest/unittest.

## Global Constraints

- Display regular market only: 09:30–16:00 ET. Do not add pre-market or after-hours.
- Use `America/New_York` and `Asia/Seoul`; never use fixed UTC offsets.
- Preserve `Ingestion -> DB -> Loader -> UI`; Today render must not fetch a provider or run ingestion.
- Read official `MARKET_HOLIDAY` and `EARLY_CLOSE` rows separately from the existing FOMC next-event snapshot.
- Do not add market-session state to Today evidence counts, risk labels, market direction, or trading signals.
- React consumes UTC boundaries supplied by Python and does not implement holiday rules.
- Keep existing Today portfolio, evidence, actions, fallback, and URL behavior unchanged.
- Do not stage registries, saved setups, run history, `.superpowers/`, or generated QA images.

---

## File Structure

- Create `app/services/today_market_session.py`: normalize calendar rows and build a deterministic multi-day UTC session schedule.
- Modify `app/services/today.py`: compose `market_session` into `today_home_v3` without affecting market readiness.
- Modify `app/web/today_page.py`: load official holiday and early-close yearly snapshots separately and pass them to Today.
- Modify `app/web/streamlit_components/today_workbench/src/types.ts`: define the session schedule and resolved-phase types.
- Modify `app/web/streamlit_components/today_workbench/src/presentation.ts`: resolve phase, next boundary, clocks, hours, and countdown.
- Modify `app/web/streamlit_components/today_workbench/src/presentation.test.ts`: cover phase boundaries and formatting.
- Modify `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`: render the live status strip and own the one-second timer.
- Modify `app/web/streamlit_components/today_workbench/src/style.css`: add compact responsive session-strip styling.
- Modify `tests/test_today_home.py`: Python service, page-loader, payload, and React source contracts.
- Rebuild `app/web/streamlit_components/today_workbench/component_static/`: update canonical deployable assets.
- Update task docs and durable finance handoff docs only after verification.

---

## 1/3차 — Time And Calendar Contract

### Task 1: Deterministic U.S. Regular-Session Schedule

**Files:**
- Create: `app/services/today_market_session.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: `build_us_market_session_model(*, generated_at: datetime, holiday_rows: Any, early_close_rows: Any, horizon_days: int = 15) -> dict[str, Any]`.
- Produces: `market_session_v1` with `calendar_quality`, `timezones`, and ordered `schedule` rows containing `trade_date`, `day_kind`, `holiday_label`, `open_at_utc`, `close_at_utc`, and `is_early_close`.

- [ ] **Step 1: Write failing weekday and exact-boundary tests**

Add `TodayMarketSessionTests` to `tests/test_today_home.py` and import timezone-aware helpers:

```python
from datetime import datetime, timezone


class TodayMarketSessionTests(unittest.TestCase):
    def _builder(self):
        module = importlib.import_module("app.services.today_market_session")
        return module.build_us_market_session_model

    def test_regular_day_uses_new_york_wall_clock_and_utc_boundaries(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
            holiday_rows=[{"Date": "2026-07-03", "Title": "Independence Day"}],
            early_close_rows=[{"Date": "2026-11-27", "Event Time": "Early close 13:00 ET"}],
        )
        today = next(row for row in model["schedule"] if row["trade_date"] == "2026-07-22")
        self.assertEqual(today["day_kind"], "TRADING_DAY")
        self.assertEqual(today["open_at_utc"], "2026-07-22T13:30:00+00:00")
        self.assertEqual(today["close_at_utc"], "2026-07-22T20:00:00+00:00")
        self.assertFalse(today["is_early_close"])
        self.assertEqual(model["timezones"], {"market": "America/New_York", "viewer": "Asia/Seoul"})

    def test_winter_and_summer_keep_0930_et_but_shift_korea_boundary(self) -> None:
        summer = self._builder()(
            generated_at=datetime(2026, 7, 22, 0, 0, tzinfo=timezone.utc),
            holiday_rows=[{"Date": "2026-07-03", "Title": "Independence Day"}],
            early_close_rows=[],
        )["schedule"][0]
        winter = self._builder()(
            generated_at=datetime(2026, 12, 2, 0, 0, tzinfo=timezone.utc),
            holiday_rows=[{"Date": "2026-12-25", "Title": "Christmas Day"}],
            early_close_rows=[],
        )["schedule"][0]
        self.assertEqual(summer["open_at_utc"][11:16], "13:30")
        self.assertEqual(winter["open_at_utc"][11:16], "14:30")
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'TodayMarketSession' -q
```

Expected: FAIL because `app.services.today_market_session` does not exist.

- [ ] **Step 3: Implement row normalization and a regular-day schedule**

Create `app/services/today_market_session.py` with these public and internal contracts:

```python
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import re
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

MARKET_TIMEZONE = ZoneInfo("America/New_York")
VIEWER_TIMEZONE = ZoneInfo("Asia/Seoul")
REGULAR_OPEN = time(9, 30)
REGULAR_CLOSE = time(16, 0)


def _records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if hasattr(value, "to_dict"):
        rows = value.to_dict(orient="records")
        return [dict(row) for row in rows]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [dict(row) for row in value if isinstance(row, Mapping)]
    return []


def _iso_date(value: Any) -> str | None:
    text = str(value or "").strip()[:10]
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def _utc_iso(local_date: date, local_time: time) -> str:
    return datetime.combine(local_date, local_time, MARKET_TIMEZONE).astimezone(timezone.utc).isoformat(timespec="seconds")


def build_us_market_session_model(
    *,
    generated_at: datetime,
    holiday_rows: Any = None,
    early_close_rows: Any = None,
    horizon_days: int = 15,
) -> dict[str, Any]:
    now_utc = generated_at.replace(tzinfo=timezone.utc) if generated_at.tzinfo is None else generated_at.astimezone(timezone.utc)
    start_date = now_utc.astimezone(MARKET_TIMEZONE).date()
    holidays = {
        on_date: str(row.get("Title") or "미국 증시 휴장")
        for row in _records(holiday_rows)
        if (on_date := _iso_date(row.get("Date")))
    }
    early_closes = {
        on_date: row
        for row in _records(early_close_rows)
        if (on_date := _iso_date(row.get("Date")))
    }
    schedule: list[dict[str, Any]] = []
    for offset in range(max(8, min(int(horizon_days), 31))):
        local_date = start_date + timedelta(days=offset)
        trade_date = local_date.isoformat()
        if local_date.weekday() >= 5:
            schedule.append({
                "trade_date": trade_date, "day_kind": "WEEKEND", "holiday_label": "주말",
                "open_at_utc": None, "close_at_utc": None, "is_early_close": False,
            })
            continue
        if trade_date in holidays:
            schedule.append({
                "trade_date": trade_date, "day_kind": "HOLIDAY", "holiday_label": holidays[trade_date],
                "open_at_utc": None, "close_at_utc": None, "is_early_close": False,
            })
            continue
        schedule.append({
            "trade_date": trade_date,
            "day_kind": "TRADING_DAY",
            "holiday_label": None,
            "open_at_utc": _utc_iso(local_date, REGULAR_OPEN),
            "close_at_utc": _utc_iso(local_date, REGULAR_CLOSE),
            "is_early_close": trade_date in early_closes,
        })
    covered_years = sorted({int(day[:4]) for day in holidays})
    required_years = sorted({int(row["trade_date"][:4]) for row in schedule})
    return {
        "schema_version": "market_session_v1",
        "generated_at_utc": now_utc.isoformat(timespec="seconds"),
        "timezones": {"market": "America/New_York", "viewer": "Asia/Seoul"},
        "calendar_quality": "CONFIRMED" if set(required_years).issubset(covered_years) else "LIMITED",
        "schedule": schedule,
    }
```

The first GREEN implementation may still use 16:00 for early-close rows; the next RED/GREEN step replaces it with parsed official time.

- [ ] **Step 4: Run weekday tests and verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'regular_day or winter_and_summer' -q
```

Expected: 2 selected tests PASS.

- [ ] **Step 5: Write failing holiday, weekend, early-close, and malformed-time tests**

Add:

```python
    def test_holiday_and_weekend_rows_have_no_session_boundaries(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc),
            holiday_rows=[{"Date": "2026-07-03", "Title": "US Market Holiday: Independence Day"}],
            early_close_rows=[],
        )
        holiday, weekend = model["schedule"][:2]
        self.assertEqual((holiday["day_kind"], holiday["open_at_utc"]), ("HOLIDAY", None))
        self.assertIn("Independence Day", holiday["holiday_label"])
        self.assertEqual((weekend["day_kind"], weekend["open_at_utc"]), ("WEEKEND", None))

    def test_official_early_close_uses_1300_et_and_malformed_time_is_limited(self) -> None:
        valid = self._builder()(
            generated_at=datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc),
            holiday_rows=[{"Date": "2026-11-26", "Title": "Thanksgiving Day"}],
            early_close_rows=[{"Date": "2026-11-27", "Event Time": "Early close 13:00 ET"}],
        )
        self.assertEqual(valid["schedule"][0]["close_at_utc"], "2026-11-27T18:00:00+00:00")
        self.assertTrue(valid["schedule"][0]["is_early_close"])
        malformed = self._builder()(
            generated_at=datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc),
            holiday_rows=[{"Date": "2026-11-26", "Title": "Thanksgiving Day"}],
            early_close_rows=[{"Date": "2026-11-27", "Event Time": "Early close"}],
        )
        self.assertEqual(malformed["schedule"][0]["close_at_utc"], "2026-11-27T21:00:00+00:00")
        self.assertEqual(malformed["calendar_quality"], "LIMITED")
        self.assertIn("2026-11-27", malformed["warnings"][0])
```

- [ ] **Step 6: Run edge tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'holiday_and_weekend or official_early_close' -q
```

Expected: holiday/weekend may pass; early-close assertions FAIL because the first implementation still closes at 16:00 ET and has no warning.

- [ ] **Step 7: Parse stored early-close time without guessing**

Add and use:

```python
def _early_close_time(row: Mapping[str, Any]) -> time | None:
    label = str(row.get("Event Time") or row.get("event_time_label") or "").strip()
    match = re.search(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", label)
    if match is None:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return time(hour, minute)
```

Before the schedule loop, build `early_close_times` and `warnings`. For a valid row, use the parsed time and set `is_early_close=True`. For an invalid row, use `REGULAR_CLOSE`, set `is_early_close=False`, append `조기폐장 시간 확인 필요: YYYY-MM-DD`, and force `calendar_quality="LIMITED"`. Return `warnings` in the model.

- [ ] **Step 8: Run all session-model tests and commit 1/3차 core**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'TodayMarketSession' -q
.venv/bin/python -m py_compile app/services/today_market_session.py
git diff --check
```

Expected: all selected tests PASS; compile and diff check exit 0.

Commit:

```bash
git add app/services/today_market_session.py tests/test_today_home.py
git commit -m "기능: 미국 정규장 일정 판정 추가"
```

### Task 2: DB-Only Calendar Loader And Today V3 Payload

**Files:**
- Modify: `app/web/today_page.py`
- Modify: `app/services/today.py`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- Consumes: `build_market_events_snapshot(...)`, `build_us_market_session_model(...)`.
- Produces: `load_today_market_calendar(generated_at: datetime) -> dict[str, Any]` and `today_home_v3.market_session`.

- [ ] **Step 1: Write failing page-loader and payload-isolation tests**

Add:

```python
    def test_today_market_calendar_loads_holidays_and_early_closes_separately(self) -> None:
        page = importlib.import_module("app.web.today_page")
        fake = MagicMock(side_effect=[{"status": "OK", "rows": []}, {"status": "OK", "rows": []}])
        generated_at = datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc)
        with patch.object(page, "build_market_events_snapshot", fake):
            result = page.load_today_market_calendar(generated_at=generated_at)
        self.assertEqual(set(result), {"holiday_rows", "early_close_rows", "statuses"})
        self.assertEqual([call.kwargs["event_type"] for call in fake.call_args_list], ["MARKET_HOLIDAY", "EARLY_CLOSE"])
        self.assertEqual(fake.call_args_list[0].kwargs["start_date"], "2026-01-01")
        self.assertEqual(fake.call_args_list[0].kwargs["end_date"], "2027-12-31")

    def test_market_session_does_not_change_evidence_readiness(self) -> None:
        inputs = self._complete_inputs()
        model = self._builder()(
            **inputs,
            market_calendar={"holiday_rows": [], "early_close_rows": []},
            generated_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(model["schema_version"], "today_home_v3")
        self.assertEqual(model["header"]["source_count"], 5)
        self.assertEqual(model["header"]["source_ready_count"], 5)
        self.assertEqual(model["market_session"]["schema_version"], "market_session_v1")
        self.assertFalse(model["boundaries"]["provider_fetch"])
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'market_calendar_loads or market_session_does_not' -q
```

Expected: FAIL because the page loader, `market_calendar` argument, and V3 payload do not exist.

- [ ] **Step 3: Implement the narrow yearly DB snapshots**

In `app/web/today_page.py`, import `timezone`, `ZoneInfo`, and `build_market_events_snapshot`, then add:

```python
def load_today_market_calendar(*, generated_at: datetime) -> dict[str, Any]:
    now_utc = generated_at.astimezone(timezone.utc)
    market_date = now_utc.astimezone(ZoneInfo("America/New_York")).date()
    start_date = f"{market_date.year}-01-01"
    end_date = f"{market_date.year + 1}-12-31"
    snapshots = {
        "holiday": build_market_events_snapshot(
            start_date=start_date, end_date=end_date, event_type="MARKET_HOLIDAY",
            recent_days=0, limit=100, today=market_date,
        ),
        "early_close": build_market_events_snapshot(
            start_date=start_date, end_date=end_date, event_type="EARLY_CLOSE",
            recent_days=0, limit=100, today=market_date,
        ),
    }
    return {
        "holiday_rows": snapshots["holiday"].get("rows"),
        "early_close_rows": snapshots["early_close"].get("rows"),
        "statuses": {
            "holiday": snapshots["holiday"].get("status"),
            "early_close": snapshots["early_close"].get("status"),
        },
    }
```

In `load_today_read_model()`, create one `generated_at = datetime.now(timezone.utc)`, pass it to both `load_today_market_calendar` and `build_today_read_model`, and wrap the calendar loader in `_safe_load` so Today remains available on DB errors.

- [ ] **Step 4: Compose the V3 payload without changing readiness counts**

In `app/services/today.py`:

```python
from app.services.today_market_session import build_us_market_session_model

TODAY_SCHEMA_VERSION = "today_home_v3"

def build_today_read_model(
    *,
    economic_cycle: Any,
    sp500: Any,
    futures_macro: Any,
    sentiment: Any,
    events: Any,
    portfolio: Any,
    market_calendar: Any = None,
    generated_at: datetime | None = None,
) -> dict[str, object]:
```

Keep all existing evidence/portfolio calculations. Before returning, normalize `calendar = _as_mapping(market_calendar)` and build:

```python
market_session = build_us_market_session_model(
    generated_at=timestamp,
    holiday_rows=calendar.get("holiday_rows"),
    early_close_rows=calendar.get("early_close_rows"),
)
```

Add `"market_session": market_session` only as a top-level sibling of `header`, `market`, and `portfolio`. Do not change `ready_count`, `available_count`, `source_count`, headline, or watch items.

- [ ] **Step 5: Update exact V2 test fixtures to V3 and verify 1/3차**

Replace Today schema assertions and mock payloads in `tests/test_today_home.py` from `today_home_v2` to `today_home_v3`. Do not change the internal `market_session_v1` schema.

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
.venv/bin/python -m py_compile app/services/today.py app/services/today_market_session.py app/web/today_page.py
git diff --check
```

Expected: all Today tests PASS; compile and diff check exit 0.

Commit:

```bash
git add app/services/today.py app/web/today_page.py tests/test_today_home.py
git commit -m "기능: Today 정규장 일정 계약 연결"
```

---

## 2/3차 — Live React Presentation

### Task 3: Pure React Phase And Time Presentation

**Files:**
- Modify: `app/web/streamlit_components/today_workbench/src/types.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/presentation.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/presentation.test.ts`

**Interfaces:**
- Consumes: `MarketSessionPayload.schedule` UTC timestamps.
- Produces: `resolveMarketSession(payload, nowMs)`, `formatCountdown(ms)`, `formatZonedClock(nowMs, timeZone)`, and `formatSessionHours(row, timeZone)`.

- [ ] **Step 1: Add failing phase-boundary tests**

Define a fixture with a Friday early close, weekend, and Monday trading day. Assert exact boundaries:

```typescript
const sessionPayload = {
  schema_version: "market_session_v1" as const,
  generated_at_utc: "2026-11-27T12:00:00+00:00",
  timezones: { market: "America/New_York" as const, viewer: "Asia/Seoul" as const },
  calendar_quality: "CONFIRMED" as const,
  warnings: [],
  schedule: [
    { trade_date: "2026-11-27", day_kind: "TRADING_DAY" as const, holiday_label: null, open_at_utc: "2026-11-27T14:30:00+00:00", close_at_utc: "2026-11-27T18:00:00+00:00", is_early_close: true },
    { trade_date: "2026-11-28", day_kind: "WEEKEND" as const, holiday_label: "주말", open_at_utc: null, close_at_utc: null, is_early_close: false },
    { trade_date: "2026-11-29", day_kind: "WEEKEND" as const, holiday_label: "주말", open_at_utc: null, close_at_utc: null, is_early_close: false },
    { trade_date: "2026-11-30", day_kind: "TRADING_DAY" as const, holiday_label: null, open_at_utc: "2026-11-30T14:30:00+00:00", close_at_utc: "2026-11-30T21:00:00+00:00", is_early_close: false },
  ],
};

expect(resolveMarketSession(sessionPayload, Date.parse("2026-11-27T14:29:59Z")).phase).toBe("PRE_OPEN");
expect(resolveMarketSession(sessionPayload, Date.parse("2026-11-27T14:30:00Z")).phase).toBe("OPEN");
expect(resolveMarketSession(sessionPayload, Date.parse("2026-11-27T18:00:00Z")).phase).toBe("CLOSED");
expect(resolveMarketSession(sessionPayload, Date.parse("2026-11-28T12:00:00Z")).phase).toBe("WEEKEND");
expect(resolveMarketSession(sessionPayload, Date.parse("2026-11-28T12:00:00Z")).targetAtMs).toBe(Date.parse("2026-11-30T14:30:00Z"));
```

- [ ] **Step 2: Run Vitest and verify RED**

Run:

```bash
cd app/web/streamlit_components/today_workbench && npm test -- --run
```

Expected: FAIL because session types and presentation functions do not exist.

- [ ] **Step 3: Define exact TypeScript session types**

Add to `types.ts`:

```typescript
export type MarketSessionDay = {
  trade_date: string;
  day_kind: "TRADING_DAY" | "HOLIDAY" | "WEEKEND";
  holiday_label: string | null;
  open_at_utc: string | null;
  close_at_utc: string | null;
  is_early_close: boolean;
};

export type MarketSessionPayload = {
  schema_version: "market_session_v1";
  generated_at_utc: string;
  timezones: { market: "America/New_York"; viewer: "Asia/Seoul" };
  calendar_quality: "CONFIRMED" | "LIMITED";
  warnings: string[];
  schedule: MarketSessionDay[];
};

export type MarketSessionPhase = "PRE_OPEN" | "OPEN" | "CLOSED" | "HOLIDAY" | "WEEKEND" | "STALE";
```

Add `market_session: MarketSessionPayload` to `TodayPayload` and change its schema literal to `today_home_v3`.

- [ ] **Step 4: Implement deterministic phase selection**

Add to `presentation.ts`:

```typescript
import type { MarketSessionDay, MarketSessionPayload, MarketSessionPhase } from "./types";

function marketDateKey(nowMs: number) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit",
  }).formatToParts(new Date(nowMs));
  const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${byType.year}-${byType.month}-${byType.day}`;
}

function nextOpen(schedule: MarketSessionDay[], afterMs: number) {
  return schedule.find((row) => row.open_at_utc != null && Date.parse(row.open_at_utc) > afterMs) ?? null;
}

export function resolveMarketSession(payload: MarketSessionPayload, nowMs: number): {
  phase: MarketSessionPhase;
  today: MarketSessionDay | null;
  targetAtMs: number | null;
  nextTradingDay: MarketSessionDay | null;
} {
  const today = payload.schedule.find((row) => row.trade_date === marketDateKey(nowMs)) ?? null;
  if (today == null) return { phase: "STALE", today: null, targetAtMs: null, nextTradingDay: null };
  const upcoming = nextOpen(payload.schedule, nowMs);
  if (today.day_kind !== "TRADING_DAY") {
    return { phase: today.day_kind, today, targetAtMs: upcoming?.open_at_utc ? Date.parse(upcoming.open_at_utc) : null, nextTradingDay: upcoming };
  }
  const openMs = Date.parse(today.open_at_utc ?? "");
  const closeMs = Date.parse(today.close_at_utc ?? "");
  if (!Number.isFinite(openMs) || !Number.isFinite(closeMs)) {
    return { phase: "STALE", today, targetAtMs: null, nextTradingDay: upcoming };
  }
  if (nowMs < openMs) return { phase: "PRE_OPEN", today, targetAtMs: openMs, nextTradingDay: today };
  if (nowMs < closeMs) return { phase: "OPEN", today, targetAtMs: closeMs, nextTradingDay: today };
  return { phase: "CLOSED", today, targetAtMs: upcoming?.open_at_utc ? Date.parse(upcoming.open_at_utc) : null, nextTradingDay: upcoming };
}
```

- [ ] **Step 5: Add failing clock, countdown, and date-crossing tests**

Add exact assertions:

```typescript
expect(formatCountdown(5 * 60 * 60 * 1000 + 18 * 60 * 1000 + 9 * 1000)).toBe("5시간 18분 09초");
expect(formatCountdown(-1)).toBe("전환 중");
expect(formatZonedClock(Date.parse("2026-07-22T13:00:00Z"), "America/New_York")).toBe("09:00");
expect(formatZonedClock(Date.parse("2026-07-22T13:00:00Z"), "Asia/Seoul")).toBe("22:00");
expect(formatSessionHours({
  trade_date: "2026-07-22", day_kind: "TRADING_DAY", holiday_label: null,
  open_at_utc: "2026-07-22T13:30:00Z", close_at_utc: "2026-07-22T20:00:00Z", is_early_close: false,
}, "Asia/Seoul")).toBe("07.22 22:30–07.23 05:00");
```

- [ ] **Step 6: Implement stable Korean-readable formatting**

Use `Intl.DateTimeFormat` with `hourCycle: "h23"`. `formatCountdown` clamps non-positive values to `전환 중`, includes seconds, and omits a zero-hour prefix. `formatSessionHours` returns `일정 자료 부족` when either boundary is null; otherwise it formats both dates and times so KST cross-date behavior is explicit.

- [ ] **Step 7: Run frontend pure tests and commit**

Run:

```bash
cd app/web/streamlit_components/today_workbench && npm test -- --run && npm run typecheck
```

Expected: all Vitest tests PASS and TypeScript exits 0.

Commit:

```bash
git add app/web/streamlit_components/today_workbench/src/types.ts app/web/streamlit_components/today_workbench/src/presentation.ts app/web/streamlit_components/today_workbench/src/presentation.test.ts
git commit -m "기능: Today 정규장 시간 표시 계산 추가"
```

### Task 4: Live Status Strip And Canonical Build

**Files:**
- Modify: `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/style.css`
- Modify: `tests/test_today_home.py`
- Rebuild: `app/web/streamlit_components/today_workbench/component_static/`

**Interfaces:**
- Consumes: Task 3 presentation functions and `payload.market_session`.
- Produces: a responsive live strip under the Today hero; no new Streamlit event.

- [ ] **Step 1: Write failing source-contract tests**

Extend `TodayHomePageContractTests`:

```python
    def test_today_react_renders_regular_market_status_without_extended_hours(self) -> None:
        root = Path("app/web/streamlit_components/today_workbench/src")
        source = (root / "TodayWorkbench.tsx").read_text(encoding="utf-8")
        styles = (root / "style.css").read_text(encoding="utf-8")
        self.assertIn("미국 정규장", source)
        self.assertIn("뉴욕", source)
        self.assertIn("한국", source)
        self.assertIn("resolveMarketSession", source)
        self.assertIn("setInterval", source)
        self.assertIn(".today-market-session", styles)
        self.assertNotIn("프리마켓", source)
        self.assertNotIn("애프터마켓", source)
```

- [ ] **Step 2: Run the source test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'regular_market_status' -q
```

Expected: FAIL because the strip and timer are absent.

- [ ] **Step 3: Add the one-second clock and phase labels**

In `TodayWorkbench.tsx`, change the React import to include `useState`, initialize `nowMs` with `Date.now()`, and add:

```typescript
useEffect(() => {
  const timer = window.setInterval(() => setNowMs(Date.now()), 1000);
  return () => window.clearInterval(timer);
}, []);

const resolvedSession = resolveMarketSession(payload.market_session, nowMs);
const phaseCopy = {
  PRE_OPEN: { label: "개장 전", countdown: "정규장 개장까지" },
  OPEN: { label: "장 진행 중", countdown: "정규장 마감까지" },
  CLOSED: { label: "정규장 마감", countdown: "다음 정규장 개장까지" },
  HOLIDAY: { label: "휴장", countdown: "다음 정규장 개장까지" },
  WEEKEND: { label: "휴장", countdown: "다음 정규장 개장까지" },
  STALE: { label: "일정 자료 부족", countdown: "새로고침 필요" },
}[resolvedSession.phase];
```

Render `<section className={`today-market-session phase-${resolvedSession.phase.toLowerCase()}`}>` immediately after the hero. Include:

- `미국 정규장 · {phaseCopy.label}`
- `뉴욕 {formatZonedClock(...)} · 한국 {formatZonedClock(...)}`
- ET hours from `resolvedSession.today` when it is a trading day, otherwise the next trading day
- KST hours from the same selected trading-day row
- `{phaseCopy.countdown} {formatCountdown((resolvedSession.targetAtMs ?? nowMs) - nowMs)}`
- holiday label, `조기폐장`, `일정 확인 필요`, or `새로고침 필요` only when applicable

Do not emit a component value and do not add an action button.

- [ ] **Step 4: Add compact responsive styling**

Add `.today-market-session` as a four-column desktop grid with the status as the strongest text, clocks and hours as secondary text, and countdown right-aligned. Use existing Today blue-gray tokens; `phase-open` may use the existing positive token, but all states must retain explicit text. At `max-width: 760px`, switch to two columns; at `max-width: 520px`, use one column and left-align countdown. Ensure `min-width: 0` and `overflow-wrap: anywhere` on textual cells.

- [ ] **Step 5: Run source, frontend, and Python regression tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
cd app/web/streamlit_components/today_workbench && npm test -- --run && npm run typecheck && npm run build
```

Expected: Today Python tests PASS; Vitest and typecheck PASS; Vite writes a new canonical `component_static/` bundle.

- [ ] **Step 6: Verify the deployable bundle and commit 2/3차**

Run:

```bash
test -f app/web/streamlit_components/today_workbench/component_static/index.html
rg -n "미국 정규장|장 진행 중|정규장 마감" app/web/streamlit_components/today_workbench/component_static/assets
git diff --check
```

Expected: index exists, built assets contain the session copy, diff check exits 0.

Commit:

```bash
git add app/web/streamlit_components/today_workbench/src app/web/streamlit_components/today_workbench/component_static tests/test_today_home.py
git commit -m "기능: Today 미국 정규장 상태 표시"
```

---

## 3/3차 — Verification And Closeout

### Task 5: Actual Browser QA And Finance Documentation Alignment

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/today-us-market-session-status-v1-20260722/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-us-market-session-status-v1-20260722/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-us-market-session-status-v1-20260722/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/today-us-market-session-status-v1-20260722/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not stage: `today-us-market-session-status-v1-qa.png`

**Interfaces:**
- Consumes: fully built `today_home_v3` component and actual DB-backed Today page.
- Produces: verification evidence, one QA screenshot, complete task status, and concise root handoff.

- [ ] **Step 1: Run complete automated verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'today or market_event' -q
.venv/bin/python -m py_compile app/services/today.py app/services/today_market_session.py app/web/today_page.py app/web/today_react_component.py
cd app/web/streamlit_components/today_workbench && npm test -- --run && npm run typecheck && npm run build
git diff --check
```

Expected: all selected Python/React tests PASS, compile/typecheck/build succeed, and diff check exits 0.

- [ ] **Step 2: Start the existing Finance Streamlit app and perform desktop QA**

Use the repository's established Streamlit start command and open root `/`. Confirm:

- Today hero is followed by the new regular-market strip.
- phase text matches the actual current ET time.
- New York and Korea clocks advance without a Streamlit page rerun.
- ET and KST open/close hours correspond to the same UTC boundaries.
- countdown decrements each second and targets open or close appropriately.
- FOMC next-event, evidence cards, portfolio chart, contributor cards, and three actions are unchanged.
- browser console has no warning/error.

- [ ] **Step 3: Perform 420px mobile QA and capture one screenshot**

Confirm one-column layout, no clipped countdown, no horizontal overflow, readable KST cross-date label, and no collision with hero metadata. Save `today-us-market-session-status-v1-qa.png` at the repository root and leave it untracked.

- [ ] **Step 4: Record exact evidence and close risks**

Update task docs with exact test counts, Browser QA viewport, displayed phase/time example, console state, screenshot path, and any limitation observed. Mark calendar/DST/timer/layout risks closed only when directly verified; preserve emergency-halt limitation as an explicit V1 boundary.

- [ ] **Step 5: Synchronize durable docs and root handoff**

In `docs/INDEX.md`, add the completed Today task and `3/3차` status. In `WORK_PROGRESS.md`, record the completed capability and next location in 3–5 lines. In `QUESTION_AND_ANALYSIS_LOG.md`, record the user request, interpreted regular-session-only goal, implementation result, and no required follow-up.

- [ ] **Step 6: Review only the intended diff and commit 3/3차**

Run:

```bash
git status --short
git diff --check
git diff -- app/services/today_market_session.py app/services/today.py app/web/today_page.py app/web/streamlit_components/today_workbench tests/test_today_home.py .aiworkspace/note/finance/tasks/active/today-us-market-session-status-v1-20260722 .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
```

Do not stage registry JSONL, run history, `.superpowers/`, existing unrelated PNGs, or the new QA screenshot.

Commit:

```bash
git add .aiworkspace/note/finance/tasks/active/today-us-market-session-status-v1-20260722 .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Today 정규장 상태 검증 결과 정리"
```

## Completion Evidence

The task is complete only when all three stages are done: `1/3차` deterministic session and DB calendar contract, `2/3차` live React status strip and canonical build, and `3/3차` actual desktop/mobile Browser QA plus documentation alignment. A passing unit test without actual Today Browser QA is not completion.
