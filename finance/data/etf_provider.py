from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
DB_PRICE = "finance_price"
OPERABILITY_TABLE = "etf_operability_snapshot"
DEFAULT_LOOKBACK_DAYS = 60


def _normalize_symbols(symbols: str | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []
    raw_items = symbols.replace("\n", ",").split(",") if isinstance(symbols, str) else list(symbols)
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        symbol = str(item).strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return normalized


def _to_none(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.to_pydatetime()
    return value


def _date_string(value: Any) -> str | None:
    if value is None:
        return None
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return None
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _is_missing_table_error(exc: Exception, table_name: str) -> bool:
    message = str(exc).lower()
    return table_name.lower() in message and ("doesn't exist" in message or "unknown table" in message)


def ensure_etf_operability_snapshot_schema(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    """Create or sync the ETF operability snapshot table in finance_meta."""
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["etf_operability_snapshot"])
        sync_table_schema(
            db,
            OPERABILITY_TABLE,
            PROVIDER_SCHEMAS["etf_operability_snapshot"],
            DB_META,
        )
    finally:
        db.close()


def _load_asset_profile_rows(db: MySQLClient, symbols: list[str]) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    db.use_db(DB_META)
    try:
        rows = db.query(
            f"""
            SELECT
                symbol,
                kind,
                quote_type,
                fund_family,
                total_assets,
                bid,
                ask,
                status,
                last_collected_at,
                error_msg
            FROM nyse_asset_profile
            WHERE symbol IN ({placeholders})
            """,
            symbols,
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "nyse_asset_profile"):
            return {}
        raise
    return {str(row.get("symbol") or "").upper(): row for row in rows if row.get("symbol")}


def _load_latest_price_dates(
    db: MySQLClient,
    symbols: list[str],
    *,
    as_of_date: str | None,
    timeframe: str,
) -> dict[str, pd.Timestamp]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    where = [f"symbol IN ({placeholders})", "timeframe = %s"]
    params: list[Any] = list(symbols) + [timeframe]
    if as_of_date is not None:
        where.append("`date` <= %s")
        params.append(as_of_date)

    db.use_db(DB_PRICE)
    try:
        rows = db.query(
            f"""
            SELECT symbol, MAX(`date`) AS latest_date
            FROM nyse_price_history
            WHERE {" AND ".join(where)}
            GROUP BY symbol
            """,
            params,
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "nyse_price_history"):
            return {}
        raise
    out: dict[str, pd.Timestamp] = {}
    for row in rows:
        latest = pd.to_datetime(row.get("latest_date"), errors="coerce")
        if pd.isna(latest):
            continue
        out[str(row.get("symbol") or "").upper()] = pd.Timestamp(latest).normalize()
    return out


def _load_price_metric_rows(
    db: MySQLClient,
    symbols: list[str],
    *,
    latest_dates: dict[str, pd.Timestamp],
    lookback_days: int,
    timeframe: str,
) -> dict[str, dict[str, Any]]:
    if not symbols or not latest_dates:
        return {}

    latest_values = [value for value in latest_dates.values() if value is not None]
    if not latest_values:
        return {}

    query_start = min(latest_values) - pd.Timedelta(days=max(int(lookback_days) * 3, 90))
    query_end = max(latest_values)
    placeholders = ",".join(["%s"] * len(symbols))

    db.use_db(DB_PRICE)
    try:
        rows = db.query(
            f"""
            SELECT symbol, `date`, close, adj_close, volume
            FROM nyse_price_history
            WHERE symbol IN ({placeholders})
              AND timeframe = %s
              AND `date` >= %s
              AND `date` <= %s
            ORDER BY symbol ASC, `date` ASC
            """,
            list(symbols) + [timeframe, query_start.strftime("%Y-%m-%d"), query_end.strftime("%Y-%m-%d")],
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "nyse_price_history"):
            return {}
        raise
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {}

    frame["symbol"] = frame["symbol"].astype(str).str.upper()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["adj_close"] = pd.to_numeric(frame.get("adj_close"), errors="coerce")
    frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
    frame = frame.dropna(subset=["symbol", "date"]).sort_values(["symbol", "date"])

    out: dict[str, dict[str, Any]] = {}
    for symbol, group in frame.groupby("symbol", sort=False):
        latest_date = latest_dates.get(str(symbol).upper())
        if latest_date is None:
            continue
        symbol_frame = group[group["date"] <= latest_date].tail(max(int(lookback_days), 1)).copy()
        if symbol_frame.empty:
            continue
        close_series = symbol_frame["close"].dropna()
        latest_close = float(close_series.iloc[-1]) if not close_series.empty else None
        volume_series = symbol_frame["volume"].dropna()
        avg_volume = float(volume_series.mean()) if not volume_series.empty else None
        dollar_volume = (symbol_frame["close"] * symbol_frame["volume"]).dropna()
        avg_dollar_volume = float(dollar_volume.mean()) if not dollar_volume.empty else None
        out[str(symbol).upper()] = {
            "latest_date": latest_date.strftime("%Y-%m-%d"),
            "market_price": latest_close,
            "avg_daily_volume": avg_volume,
            "avg_daily_dollar_volume": avg_dollar_volume,
        }
    return out


def _bid_ask_spread_pct(bid: Any, ask: Any) -> float | None:
    bid_value = pd.to_numeric(pd.Series([bid]), errors="coerce").iloc[0]
    ask_value = pd.to_numeric(pd.Series([ask]), errors="coerce").iloc[0]
    if pd.isna(bid_value) or pd.isna(ask_value) or bid_value <= 0 or ask_value <= 0:
        return None
    mid = (float(bid_value) + float(ask_value)) / 2.0
    if mid <= 0:
        return None
    return abs(float(ask_value) - float(bid_value)) / mid


def _missing_fields(row: dict[str, Any]) -> list[str]:
    required_proxy_fields = [
        "market_price",
        "avg_daily_dollar_volume",
        "total_assets",
        "bid_ask_spread_pct",
    ]
    missing = [field for field in required_proxy_fields if row.get(field) is None]
    provider_only_fields = [
        "expense_ratio",
        "nav",
        "premium_discount_pct",
        "median_bid_ask_spread_pct",
        "official_leverage_inverse_metadata",
    ]
    missing.extend(provider_only_fields)
    return missing


def _coverage_status(row: dict[str, Any]) -> str:
    has_profile_bridge = any(row.get(field) is not None for field in ("total_assets", "bid", "ask", "bid_ask_spread_pct"))
    has_price_proxy = any(row.get(field) is not None for field in ("market_price", "avg_daily_volume", "avg_daily_dollar_volume"))
    if has_profile_bridge:
        return "bridge"
    if has_price_proxy:
        return "proxy"
    return "missing"


def _source_type_for_status(status: str) -> str:
    if status == "proxy":
        return "computed_proxy"
    return "database_bridge"


def _build_db_bridge_rows(
    symbols: list[str],
    *,
    as_of_date: str | None,
    lookback_days: int,
    profile_rows: dict[str, dict[str, Any]],
    price_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    collected_at = _utc_now_string()
    rows: list[dict[str, Any]] = []
    today = pd.Timestamp.utcnow().strftime("%Y-%m-%d")

    for symbol in symbols:
        profile = profile_rows.get(symbol) or {}
        price = price_rows.get(symbol) or {}
        bid = _to_none(profile.get("bid"))
        ask = _to_none(profile.get("ask"))
        row_as_of = as_of_date or price.get("latest_date") or _date_string(profile.get("last_collected_at")) or today
        source_refs: list[str] = []
        if price:
            source_refs.append("finance_price.nyse_price_history")
        if profile:
            source_refs.append("finance_meta.nyse_asset_profile")

        row = {
            "symbol": symbol,
            "as_of_date": row_as_of,
            "source": "db_bridge",
            "source_type": "database_bridge",
            "source_ref": "+".join(source_refs) if source_refs else None,
            "fund_family": _to_none(profile.get("fund_family")),
            "category": None,
            "expense_ratio": None,
            "turnover_ratio": None,
            "total_assets": _to_none(profile.get("total_assets")),
            "net_assets": None,
            "nav": None,
            "market_price": _to_none(price.get("market_price")),
            "premium_discount_pct": None,
            "bid": bid,
            "ask": ask,
            "bid_ask_spread_pct": _bid_ask_spread_pct(bid, ask),
            "median_bid_ask_spread_pct": None,
            "avg_daily_volume": _to_none(price.get("avg_daily_volume")),
            "avg_daily_dollar_volume": _to_none(price.get("avg_daily_dollar_volume")),
            "lookback_days": int(lookback_days),
            "inception_date": None,
            "leverage_factor": None,
            "is_inverse": None,
            "has_daily_objective": None,
            "coverage_status": "missing",
            "missing_fields_json": None,
            "collected_at": collected_at,
            "error_msg": None,
        }
        status = _coverage_status(row)
        row["coverage_status"] = status
        row["source_type"] = _source_type_for_status(status)
        row["missing_fields_json"] = json.dumps(_missing_fields(row), ensure_ascii=False)
        if status == "missing":
            row["error_msg"] = "no price/profile bridge data"
        rows.append(row)

    return rows


def _upsert_etf_operability_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    sql = f"""
    INSERT INTO {OPERABILITY_TABLE} (
      symbol, as_of_date, source, source_type, source_ref,
      fund_family, category,
      expense_ratio, turnover_ratio, total_assets, net_assets, nav, market_price, premium_discount_pct,
      bid, ask, bid_ask_spread_pct, median_bid_ask_spread_pct,
      avg_daily_volume, avg_daily_dollar_volume, lookback_days,
      inception_date, leverage_factor, is_inverse, has_daily_objective,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(symbol)s, %(as_of_date)s, %(source)s, %(source_type)s, %(source_ref)s,
      %(fund_family)s, %(category)s,
      %(expense_ratio)s, %(turnover_ratio)s, %(total_assets)s, %(net_assets)s, %(nav)s, %(market_price)s, %(premium_discount_pct)s,
      %(bid)s, %(ask)s, %(bid_ask_spread_pct)s, %(median_bid_ask_spread_pct)s,
      %(avg_daily_volume)s, %(avg_daily_dollar_volume)s, %(lookback_days)s,
      %(inception_date)s, %(leverage_factor)s, %(is_inverse)s, %(has_daily_objective)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_type = VALUES(source_type),
      source_ref = VALUES(source_ref),
      fund_family = VALUES(fund_family),
      category = VALUES(category),
      expense_ratio = VALUES(expense_ratio),
      turnover_ratio = VALUES(turnover_ratio),
      total_assets = VALUES(total_assets),
      net_assets = VALUES(net_assets),
      nav = VALUES(nav),
      market_price = VALUES(market_price),
      premium_discount_pct = VALUES(premium_discount_pct),
      bid = VALUES(bid),
      ask = VALUES(ask),
      bid_ask_spread_pct = VALUES(bid_ask_spread_pct),
      median_bid_ask_spread_pct = VALUES(median_bid_ask_spread_pct),
      avg_daily_volume = VALUES(avg_daily_volume),
      avg_daily_dollar_volume = VALUES(avg_daily_dollar_volume),
      lookback_days = VALUES(lookback_days),
      inception_date = VALUES(inception_date),
      leverage_factor = VALUES(leverage_factor),
      is_inverse = VALUES(is_inverse),
      has_daily_objective = VALUES(has_daily_objective),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


def collect_and_store_etf_operability(
    symbols: str | Iterable[str],
    *,
    as_of_date: str | None = None,
    provider: str = "db_bridge",
    refresh_mode: str = "upsert",
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    timeframe: str = "1d",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Build ETF operability bridge/proxy snapshots from local DB price/profile data."""
    normalized_symbols = _normalize_symbols(symbols)
    if not normalized_symbols:
        return {
            "requested": 0,
            "stored": 0,
            "missing": [],
            "failed": [],
            "coverage": {},
        }

    normalized_provider = str(provider or "db_bridge").strip().lower()
    if normalized_provider not in {"auto", "db_bridge"}:
        raise NotImplementedError("Only db_bridge ETF operability collection is implemented in P2-2A.")
    if str(refresh_mode or "upsert").strip().lower() != "upsert":
        raise NotImplementedError("Only upsert refresh_mode is supported for ETF operability bridge snapshots.")
    if int(lookback_days) <= 0:
        raise ValueError("lookback_days must be positive.")

    as_of = _date_string(as_of_date) if as_of_date is not None else None
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["etf_operability_snapshot"])
        sync_table_schema(
            db,
            OPERABILITY_TABLE,
            PROVIDER_SCHEMAS["etf_operability_snapshot"],
            DB_META,
        )
        profile_rows = _load_asset_profile_rows(db, normalized_symbols)
        latest_dates = _load_latest_price_dates(
            db,
            normalized_symbols,
            as_of_date=as_of,
            timeframe=timeframe,
        )
        price_rows = _load_price_metric_rows(
            db,
            normalized_symbols,
            latest_dates=latest_dates,
            lookback_days=int(lookback_days),
            timeframe=timeframe,
        )
        rows = _build_db_bridge_rows(
            normalized_symbols,
            as_of_date=as_of,
            lookback_days=int(lookback_days),
            profile_rows=profile_rows,
            price_rows=price_rows,
        )
        db.use_db(DB_META)
        _upsert_etf_operability_rows(db, rows)
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1
    missing = [row["symbol"] for row in rows if row.get("coverage_status") == "missing"]

    return {
        "requested": len(normalized_symbols),
        "stored": len(rows),
        "updated": None,
        "missing": missing,
        "failed": [],
        "coverage": coverage,
        "source": "db_bridge",
        "lookback_days": int(lookback_days),
    }
