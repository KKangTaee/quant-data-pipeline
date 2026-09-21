"""Exact, completed-bar comparisons; no provider access or return forecasting."""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from math import isfinite
from zoneinfo import ZoneInfo

from app.services.futures_macro_intraday import active_futures_session_date
from app.services.today_market_session import build_us_market_session_model

UTC = timezone.utc
NY = ZoneInfo("America/New_York")
CURRENCIES = ("6E=F", "6J=F", "6B=F", "6A=F", "6C=F")
CORE = ("ES=F", "NQ=F", "ZN=F", *CURRENCIES)
SYMBOLS = (*CORE, "GC=F", "CL=F", "YM=F", "RTY=F", "HG=F", "ZB=F")


def utc(value):
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def positive_price(value):
    try:
        number = float(value)
        return number if isfinite(number) and number > 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def normalize_closed_bars(rows, *, evaluation_time):
    """Provider timestamps mark starts. Reject all versions of conflicting keys."""
    now = utc(evaluation_time)
    unique, conflicts = {}, set()
    for row in rows:
        try:
            end = utc(row["candle_time_utc"]) + timedelta(minutes=5)
        except (KeyError, ValueError, TypeError):
            continue
        if end > now:
            continue
        key = (row.get("provider_symbol"), end)
        normalized = dict(row, bar_end_utc=end, close=positive_price(row.get("close")))
        if key in unique and (unique[key]["close"], unique[key].get("source")) != (normalized["close"], normalized.get("source")):
            conflicts.add(key)
        unique[key] = normalized
    return [row for key, row in unique.items() if key not in conflicts]


def build_window_returns(rows, *, symbols, start_utc, end_utc):
    """Require two exact endpoints from one provider; never forward-fill prices."""
    indexed = {(r["provider_symbol"], r["bar_end_utc"]): r for r in rows}
    returns, endpoints = {}, {}
    for symbol in symbols:
        a, b = indexed.get((symbol, start_utc), {}), indexed.get((symbol, end_utc), {})
        p, q = positive_price(a.get("close")), positive_price(b.get("close"))
        value = 100 * (q / p - 1) if p and q and a.get("source") == b.get("source") else None
        returns[symbol] = value if value is not None and isfinite(value) else None
        endpoints[symbol] = {"start_price": p, "end_price": q, "source": b.get("source"),
                             "collected_at": str(b.get("collected_at") or "")}
    return {"returns_pct": returns, "endpoints": endpoints,
            "missing_symbols": [s for s, value in returns.items() if value is None]}


def build_cash_session_calendar(*, evaluation_time, holiday_rows, early_close_rows, calendar_statuses, covered_years):
    """Extend the existing DST-aware schedule backwards using explicit annual coverage."""
    now = utc(evaluation_time)
    result = build_us_market_session_model(generated_at=now-timedelta(days=15),
        holiday_rows=holiday_rows, early_close_rows=early_close_rows,
        calendar_statuses=calendar_statuses, horizon_days=17)
    needed = {int(row["trade_date"][:4]) for row in result["schedule"]}
    confirmed = needed.issubset(set(covered_years)) and not result["warnings"] and all(
        calendar_statuses.get(k) == "OK" for k in ("holiday", "early_close"))
    result["calendar_quality"] = "CONFIRMED" if confirmed else "LIMITED"
    return result


def previous_cash_close(instant, calendar):
    if calendar.get("calendar_quality") != "CONFIRMED":
        return None
    closes = [utc(r["close_at_utc"]) for r in calendar.get("schedule", []) if r.get("close_at_utc")]
    return max((t for t in closes if t <= utc(instant)), default=None)


def _freshness(now, end):
    """Ordinary weekly closure is healthy only with data near the actual closing time."""
    if (now-end).total_seconds() <= 30*60:
        return "AVAILABLE"
    if active_futures_session_date(now) is None:
        local = now.astimezone(NY)
        day = local.date()
        if local.weekday() >= 5:
            day -= timedelta(days=local.weekday()-4)
        close = datetime.combine(day, time(17), NY).astimezone(UTC)
        if abs((close-end).total_seconds()) <= 30*60:
            return "MARKET_CLOSED"
    return "STALE"


def build_futures_macro_window_snapshot(*, rows, evaluation_time, calendar):
    now = utc(evaluation_time)
    bars = normalize_closed_bars(rows, evaluation_time=now)
    times = {s: {r["bar_end_utc"] for r in bars if r["provider_symbol"] == s and r["close"] is not None} for s in CORE}
    # With absent members, retain available observations but withhold the combined reading.
    present = [times[s] for s in CORE if times[s]]
    common = set.intersection(*present) if present else set()
    end = max(common, default=None)
    windows = {}
    for name in ("since_close", "last_hour"):
        start = (previous_cash_close(end, calendar) if name == "since_close" else end-timedelta(hours=1)) if end else None
        data = build_window_returns(bars, symbols=SYMBOLS, start_utc=start, end_utc=end)
        missing = [s for s in CORE if s in data["missing_symbols"]]
        if name == "since_close" and end and start is None:
            missing = []  # Calendar uncertainty cannot be repaired by fetching prices.
        currency_values = [data["returns_pct"][s] for s in CURRENCIES]
        dollar = -sum(currency_values)/len(CURRENCIES) if all(v is not None for v in currency_values) else None
        status = _freshness(now, end) if end else "UNAVAILABLE"
        if start is None or start == end:
            status = "UNAVAILABLE"
        elif missing and status != "STALE":
            status = "PARTIAL"
        windows[name] = {**data, "missing_symbols": missing, "status": status,
                         "start_utc": start.isoformat() if start else None,
                         "end_utc": end.isoformat() if end else None, "dollar_proxy_pct": dollar}
    return {"schema_version": "futures_macro_windows_v1", "evaluated_at_utc": now.isoformat(),
            "calendar_quality": calendar.get("calendar_quality", "LIMITED"), "windows": windows}
