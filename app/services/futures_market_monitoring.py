from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import UTC, date, datetime
from typing import Any

import pandas as pd

from finance.data.futures_market import DEFAULT_FUTURES_INSTRUMENTS


QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

DEFAULT_INTERVAL = "1m"
DEFAULT_LOOKBACK_MINUTES = 360
FUTURES_REFRESH_DUE_MINUTES = 2
FUTURES_STALE_MINUTES = 10
CORE_GROUPS = ("Equity Index", "Rates", "Commodities", "FX Futures")

CANDLE_COLUMNS = ["Candle Time", "Symbol", "Open", "High", "Low", "Close", "Volume"]
SHOCK_COLUMNS = [
    "Group",
    "Symbol",
    "Name",
    "Latest",
    "Latest Candle UTC",
    "Age Min",
    "15m %",
    "60m %",
    "Range Spike",
    "Volume Spike",
    "State",
    "Source",
]


def _default_query(db_name: str, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    import pymysql

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        port=3306,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cur.execute(f"USE {db_name}")
            cur.execute(sql, params)
            return list(cur.fetchall())
    finally:
        conn.close()


def _preset_instruments() -> list[dict[str, Any]]:
    return [dict(row) for row in DEFAULT_FUTURES_INSTRUMENTS]


def _instrument_rows(query_fn: QueryFn) -> list[dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT provider_symbol, display_name, futures_group, exchange, contract_hint,
                   source, active, sort_order
            FROM futures_instrument
            WHERE active = 1
            ORDER BY sort_order, provider_symbol
            """,
            None,
        )
    except Exception:
        rows = []
    return rows or _preset_instruments()


def _symbols_for_group(instruments: Sequence[dict[str, Any]], group: str | None) -> list[str]:
    normalized_group = str(group or "").strip()
    symbols: list[str] = []
    for row in instruments:
        if normalized_group and normalized_group != "All" and str(row.get("futures_group") or "") != normalized_group:
            continue
        symbol = str(row.get("provider_symbol") or "").strip().upper()
        if symbol:
            symbols.append(symbol)
    return symbols


def _load_candle_rows(
    query_fn: QueryFn,
    *,
    symbols: Sequence[str],
    interval: str,
    lookback_minutes: int,
) -> list[dict[str, Any]]:
    if not symbols:
        return []
    placeholders = ", ".join(["%s"] * len(symbols))
    params: list[Any] = [interval, *symbols, max(1, int(lookback_minutes))]
    try:
        return query_fn(
            "finance_price",
            f"""
            SELECT provider_symbol, interval_code, candle_time_utc,
                   open, high, low, close, volume, source, provider_status
            FROM futures_ohlcv
            WHERE interval_code = %s
              AND provider_symbol IN ({placeholders})
              AND candle_time_utc >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL %s MINUTE)
            ORDER BY provider_symbol, candle_time_utc
            """,
            params,
        )
    except Exception:
        return []


def _load_latest_run(query_fn: QueryFn) -> dict[str, Any] | None:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT run_id, source, period_code, interval_code, cadence_mode, status,
                   started_at, finished_at, duration_sec,
                   symbols_requested, symbols_processed, rows_written,
                   latest_candle_time_utc, failed_symbols_json, message
            FROM futures_market_monitor_run
            ORDER BY COALESCE(finished_at, started_at) DESC
            LIMIT 1
            """,
            None,
        )
    except Exception:
        return None
    return dict(rows[0]) if rows else None


def _to_timestamp(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize(UTC)
    else:
        ts = ts.tz_convert(UTC)
    return ts


def _now_timestamp(now: datetime | None = None) -> pd.Timestamp:
    ts = pd.Timestamp(now or datetime.now(UTC))
    if ts.tzinfo is None:
        ts = ts.tz_localize(UTC)
    else:
        ts = ts.tz_convert(UTC)
    return ts


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _pct_change(latest: float | None, previous: float | None) -> float | None:
    if latest is None or previous in (None, 0):
        return None
    return ((latest / float(previous)) - 1.0) * 100.0


def _window_close(frame: pd.DataFrame, *, latest_ts: pd.Timestamp, minutes: int) -> float | None:
    if frame.empty:
        return None
    threshold = latest_ts - pd.Timedelta(minutes=minutes)
    older = frame[frame["ts"] <= threshold]
    if older.empty:
        return None
    return _safe_float(older.iloc[-1].get("close"))


def _range_spike(frame: pd.DataFrame) -> float | None:
    if frame.empty:
        return None
    recent = frame.tail(15)
    baseline = frame.tail(120)
    if recent.empty or baseline.empty:
        return None
    recent_high = _safe_float(recent["high"].max())
    recent_low = _safe_float(recent["low"].min())
    ranges = (baseline["high"].astype(float) - baseline["low"].astype(float)).dropna()
    median_range = _safe_float(ranges.median()) if not ranges.empty else None
    if recent_high is None or recent_low is None or not median_range:
        return None
    return (recent_high - recent_low) / median_range


def _volume_spike(frame: pd.DataFrame) -> float | None:
    if frame.empty or "volume" not in frame:
        return None
    latest_volume = _safe_float(frame.iloc[-1].get("volume"))
    volumes = frame.tail(120)["volume"].dropna().astype(float)
    median_volume = _safe_float(volumes.median()) if not volumes.empty else None
    if latest_volume is None or not median_volume:
        return None
    return latest_volume / median_volume


def _state_for_row(
    *,
    age_minutes: int | None,
    move_15m: float | None,
    move_60m: float | None,
    range_spike: float | None,
) -> str:
    if age_minutes is None:
        return "Missing"
    if age_minutes >= FUTURES_STALE_MINUTES:
        return "Stale"
    abs_15 = abs(move_15m or 0.0)
    abs_60 = abs(move_60m or 0.0)
    if abs_15 >= 1.0 or abs_60 >= 2.0 or (range_spike or 0.0) >= 2.5:
        return "Sharp"
    if abs_15 >= 0.4 or abs_60 >= 1.0 or (range_spike or 0.0) >= 1.5:
        return "Moving"
    return "Calm"


def _round(value: float | None, digits: int = 2) -> float | None:
    return round(float(value), digits) if value is not None else None


def _metric_rows(
    candles: pd.DataFrame,
    *,
    instruments: Sequence[dict[str, Any]],
    selected_symbols: Sequence[str],
    now: datetime | None,
) -> list[dict[str, Any]]:
    now_ts = _now_timestamp(now)
    by_symbol = {
        str(row.get("provider_symbol") or "").upper(): row
        for row in instruments
    }
    rows: list[dict[str, Any]] = []
    for symbol in selected_symbols:
        info = by_symbol.get(symbol, {"provider_symbol": symbol, "display_name": symbol, "futures_group": "Other"})
        frame = candles[candles["provider_symbol"] == symbol].sort_values("ts") if not candles.empty else pd.DataFrame()
        if frame.empty:
            rows.append(
                {
                    "Group": info.get("futures_group") or "Other",
                    "Symbol": symbol,
                    "Name": info.get("display_name") or symbol,
                    "Latest": None,
                    "Latest Candle UTC": None,
                    "Age Min": None,
                    "15m %": None,
                    "60m %": None,
                    "Range Spike": None,
                    "Volume Spike": None,
                    "State": "Missing",
                    "Source": info.get("source") or "yfinance",
                }
            )
            continue
        latest = frame.iloc[-1]
        latest_ts = latest["ts"]
        latest_close = _safe_float(latest.get("close"))
        age_minutes = max(0, int((now_ts - latest_ts).total_seconds() // 60))
        move_15 = _pct_change(latest_close, _window_close(frame, latest_ts=latest_ts, minutes=15))
        move_60 = _pct_change(latest_close, _window_close(frame, latest_ts=latest_ts, minutes=60))
        range_value = _range_spike(frame)
        volume_value = _volume_spike(frame)
        rows.append(
            {
                "Group": info.get("futures_group") or "Other",
                "Symbol": symbol,
                "Name": info.get("display_name") or symbol,
                "Latest": _round(latest_close, 4),
                "Latest Candle UTC": latest_ts.strftime("%Y-%m-%d %H:%M"),
                "Age Min": age_minutes,
                "15m %": _round(move_15, 2),
                "60m %": _round(move_60, 2),
                "Range Spike": _round(range_value, 2),
                "Volume Spike": _round(volume_value, 2),
                "State": _state_for_row(
                    age_minutes=age_minutes,
                    move_15m=move_15,
                    move_60m=move_60,
                    range_spike=range_value,
                ),
                "Source": latest.get("source") or info.get("source") or "yfinance",
            }
        )
    return rows


def _candle_frame(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=[*CANDLE_COLUMNS, "provider_symbol", "ts"])
    records: list[dict[str, Any]] = []
    for row in rows:
        ts = _to_timestamp(row.get("candle_time_utc"))
        if ts is None:
            continue
        records.append(
            {
                "Candle Time": ts.to_pydatetime(),
                "Symbol": row.get("provider_symbol"),
                "Open": _safe_float(row.get("open")),
                "High": _safe_float(row.get("high")),
                "Low": _safe_float(row.get("low")),
                "Close": _safe_float(row.get("close")),
                "Volume": _safe_float(row.get("volume")),
                "provider_symbol": str(row.get("provider_symbol") or "").upper(),
                "interval_code": row.get("interval_code"),
                "source": row.get("source") or "yfinance",
                "provider_status": row.get("provider_status") or "ok",
                "ts": ts,
                "open": _safe_float(row.get("open")),
                "high": _safe_float(row.get("high")),
                "low": _safe_float(row.get("low")),
                "close": _safe_float(row.get("close")),
                "volume": _safe_float(row.get("volume")),
            }
        )
    if not records:
        return pd.DataFrame(columns=[*CANDLE_COLUMNS, "provider_symbol", "ts"])
    return pd.DataFrame(records).sort_values(["provider_symbol", "ts"])


def _coverage_from_metrics(metrics: list[dict[str, Any]], latest_run: dict[str, Any] | None) -> dict[str, Any]:
    total = len(metrics)
    missing = sum(1 for row in metrics if row.get("State") == "Missing")
    stale = sum(1 for row in metrics if row.get("State") == "Stale")
    sharp = sum(1 for row in metrics if row.get("State") == "Sharp")
    moving = sum(1 for row in metrics if row.get("State") == "Moving")
    latest_ages = [int(row["Age Min"]) for row in metrics if row.get("Age Min") is not None]
    return {
        "symbol_count": total,
        "returnable_count": max(0, total - missing),
        "missing_count": missing,
        "stale_count": stale,
        "sharp_count": sharp,
        "moving_count": moving,
        "latest_age_minutes": min(latest_ages) if latest_ages else None,
        "oldest_age_minutes": max(latest_ages) if latest_ages else None,
        "latest_run_status": (latest_run or {}).get("status"),
        "latest_run_finished_at": (latest_run or {}).get("finished_at"),
        "latest_run_rows_written": (latest_run or {}).get("rows_written"),
    }


def _warnings(coverage: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if coverage.get("missing_count"):
        out.append(f"{coverage['missing_count']} futures symbols have no stored OHLCV rows.")
    if coverage.get("stale_count"):
        out.append(f"{coverage['stale_count']} futures symbols are stale; refresh before relying on pre-open context.")
    if coverage.get("latest_run_status") in {"failed", "partial_success"}:
        out.append("Latest futures provider collection had failed or partial symbols.")
    return out


def _status(coverage: dict[str, Any]) -> str:
    if int(coverage.get("returnable_count") or 0) <= 0:
        return "MISSING"
    if coverage.get("missing_count") or coverage.get("stale_count") or coverage.get("latest_run_status") in {"failed", "partial_success"}:
        return "REVIEW"
    return "OK"


def _top_move(metrics: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        row
        for row in metrics
        if row.get("15m %") is not None or row.get("60m %") is not None
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: max(abs(float(row.get("15m %") or 0.0)), abs(float(row.get("60m %") or 0.0))))


def build_futures_monitor_snapshot(
    *,
    group: str | None = "Equity Index",
    symbols: Sequence[str] | None = None,
    selected_symbol: str | None = None,
    interval: str = DEFAULT_INTERVAL,
    lookback_minutes: int = DEFAULT_LOOKBACK_MINUTES,
    now: datetime | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    query = query_fn or _default_query
    instruments = _instrument_rows(query)
    groups = ["All"] + sorted({str(row.get("futures_group") or "Other") for row in instruments})
    if symbols is None:
        selected_symbols = _symbols_for_group(instruments, group)
    else:
        selected_symbols = [str(symbol).strip().upper() for symbol in symbols if str(symbol).strip()]
    if not selected_symbols:
        selected_symbols = _symbols_for_group(instruments, "Equity Index")

    candle_rows = _load_candle_rows(
        query,
        symbols=selected_symbols,
        interval=interval,
        lookback_minutes=lookback_minutes,
    )
    candles = _candle_frame(candle_rows)
    metrics = _metric_rows(candles, instruments=instruments, selected_symbols=selected_symbols, now=now)
    latest_run = _load_latest_run(query)
    coverage = _coverage_from_metrics(metrics, latest_run)
    status = _status(coverage)
    active_selected = str(selected_symbol or selected_symbols[0]).strip().upper() if selected_symbols else None
    if active_selected not in selected_symbols and selected_symbols:
        active_selected = selected_symbols[0]
    selected_candles = (
        candles[candles["provider_symbol"] == active_selected][CANDLE_COLUMNS]
        if active_selected and not candles.empty
        else pd.DataFrame(columns=CANDLE_COLUMNS)
    )
    all_candles = candles[CANDLE_COLUMNS] if not candles.empty else pd.DataFrame(columns=CANDLE_COLUMNS)
    return {
        "status": status,
        "group": group,
        "groups": groups,
        "symbols": selected_symbols,
        "selected_symbol": active_selected,
        "interval": interval,
        "lookback_minutes": lookback_minutes,
        "coverage": coverage,
        "warnings": _warnings(coverage),
        "top_move": _top_move(metrics),
        "rows": pd.DataFrame(metrics, columns=SHOCK_COLUMNS),
        "all_candles": all_candles,
        "candles": selected_candles,
        "latest_run": latest_run,
        "source_note": "yfinance pilot source; not exchange-grade realtime.",
        "as_of_date": date.today().isoformat(),
    }


def load_overview_futures_monitor_snapshot(**kwargs: Any) -> dict[str, Any]:
    return build_futures_monitor_snapshot(**kwargs)
