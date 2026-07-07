from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient
from finance.data.db.schema import PIT_UNIVERSE_SCHEMAS, sync_table_schema


PIT_UNIVERSE_METHOD_VERSION = "pit_universe_snapshot_v1"
PIT_UNIVERSE_SOURCE_BASIS = (
    "db_price_close * latest_known_statement_shares_outstanding"
)
DB_META = "finance_meta"


def normalize_pit_universe_code(target_size: int, *, frequency: str = "monthly") -> str:
    normalized_target = int(target_size)
    if normalized_target <= 0:
        raise ValueError("target_size must be positive.")
    normalized_frequency = str(frequency or "monthly").strip().upper()
    if normalized_frequency not in {"MONTHLY", "WEEKLY", "DAILY", "ADHOC"}:
        raise ValueError("frequency must be one of monthly, weekly, daily, adhoc.")
    return f"US_LARGE_{normalized_target}_MCAP_PIT_{normalized_frequency}"


def _normalize_symbol(value: object) -> str:
    return str(value or "").strip().upper()


def _normalize_symbols(values: Iterable[object] | None) -> list[str]:
    seen: dict[str, None] = {}
    for value in values or []:
        symbol = _normalize_symbol(value)
        if symbol:
            seen.setdefault(symbol, None)
    return list(seen.keys())


def _frame(value: pd.DataFrame | Sequence[dict[str, Any]] | None) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    if value is None:
        return pd.DataFrame()
    return pd.DataFrame(list(value))


def _latest_price_rows(price_rows: pd.DataFrame, as_of_ts: pd.Timestamp) -> pd.DataFrame:
    if price_rows.empty:
        return pd.DataFrame(columns=["symbol", "price_date", "close", "avg_dollar_volume_20d"])

    working = price_rows.copy()
    working["symbol"] = working["symbol"].map(_normalize_symbol)
    working["date"] = pd.to_datetime(working["date"], errors="coerce").dt.normalize()
    working["close"] = pd.to_numeric(working.get("close"), errors="coerce")
    if "volume" in working.columns:
        working["volume"] = pd.to_numeric(working["volume"], errors="coerce")
    else:
        working["volume"] = pd.NA

    working = working[
        working["symbol"].ne("")
        & working["date"].notna()
        & (working["date"] <= as_of_ts)
    ].copy()
    if working.empty:
        return pd.DataFrame(columns=["symbol", "price_date", "close", "avg_dollar_volume_20d"])

    adv_rows: list[dict[str, Any]] = []
    for symbol, group in working.sort_values("date").groupby("symbol", sort=True):
        tail = group.tail(20).copy()
        dollar_volume = pd.to_numeric(tail["close"], errors="coerce") * pd.to_numeric(
            tail["volume"], errors="coerce"
        )
        avg_dollar_volume_20d = dollar_volume.dropna().mean()
        latest = tail.iloc[-1]
        adv_rows.append(
            {
                "symbol": symbol,
                "price_date": latest["date"],
                "close": latest["close"],
                "avg_dollar_volume_20d": (
                    float(avg_dollar_volume_20d)
                    if pd.notna(avg_dollar_volume_20d)
                    else None
                ),
            }
        )
    return pd.DataFrame(adv_rows)


def _latest_statement_rows(statement_rows: pd.DataFrame, as_of_ts: pd.Timestamp) -> pd.DataFrame:
    if statement_rows.empty:
        return pd.DataFrame(columns=["symbol", "shares_outstanding", "shares_source"])

    working = statement_rows.copy()
    working["symbol"] = working["symbol"].map(_normalize_symbol)
    working["latest_available_at"] = pd.to_datetime(
        working["latest_available_at"], errors="coerce"
    ).dt.normalize()
    working["period_end"] = pd.to_datetime(working.get("period_end"), errors="coerce").dt.normalize()
    working["shares_outstanding"] = pd.to_numeric(
        working.get("shares_outstanding"), errors="coerce"
    )
    if "shares_outstanding_source" not in working.columns:
        working["shares_outstanding_source"] = None

    working = working[
        working["symbol"].ne("")
        & working["latest_available_at"].notna()
        & (working["latest_available_at"] <= as_of_ts)
        & working["shares_outstanding"].notna()
        & (working["shares_outstanding"] > 0)
    ].copy()
    if working.empty:
        return pd.DataFrame(columns=["symbol", "shares_outstanding", "shares_source"])

    working = working.sort_values(["symbol", "latest_available_at", "period_end"])
    latest = working.groupby("symbol", as_index=False).tail(1).copy()
    return latest.rename(columns={"shares_outstanding_source": "shares_source"})[
        ["symbol", "shares_outstanding", "shares_source"]
    ]


def _asset_profile_map(asset_profile_rows: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if asset_profile_rows.empty:
        return {}
    working = asset_profile_rows.copy()
    working["symbol"] = working["symbol"].map(_normalize_symbol)
    if "delisted_at" in working.columns:
        working["delisted_at"] = pd.to_datetime(working["delisted_at"], errors="coerce").dt.normalize()
    return {
        row["symbol"]: row
        for row in working[working["symbol"].ne("")].to_dict(orient="records")
    }


def _profile_exclusion_reason(profile: dict[str, Any], as_of_ts: pd.Timestamp) -> str | None:
    kind = str(profile.get("kind") or "stock").strip().lower()
    if kind and kind != "stock":
        return "non_stock"
    country = str(profile.get("country") or "United States").strip().lower()
    if country and country not in {"united states", "us", "usa"}:
        return "non_us"
    is_spac = profile.get("is_spac")
    if str(is_spac).strip().lower() in {"1", "true", "yes"}:
        return "spac"
    status = str(profile.get("status") or "active").strip().lower()
    delisted_at = pd.to_datetime(profile.get("delisted_at"), errors="coerce")
    if status in {"dilist", "delist", "delisted"} and (pd.isna(delisted_at) or delisted_at <= as_of_ts):
        return "profile_delisted"
    return None


def _json_safe(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def build_equity_universe_snapshot_payload(
    *,
    as_of_date: str,
    target_size: int,
    price_rows: pd.DataFrame | Sequence[dict[str, Any]],
    statement_rows: pd.DataFrame | Sequence[dict[str, Any]],
    asset_profile_rows: pd.DataFrame | Sequence[dict[str, Any]] | None = None,
    candidate_symbols: Sequence[str] | None = None,
    universe_code: str | None = None,
    method_version: str = PIT_UNIVERSE_METHOD_VERSION,
    min_avg_dollar_volume_20d: float = 0.0,
) -> dict[str, Any]:
    """Build a deterministic PIT universe snapshot payload from already-loaded DB rows."""
    target = int(target_size)
    if target <= 0:
        raise ValueError("target_size must be positive.")

    as_of_ts = pd.Timestamp(as_of_date).normalize()
    code = universe_code or normalize_pit_universe_code(target)
    price_df = _frame(price_rows)
    statement_df = _frame(statement_rows)
    profile_df = _frame(asset_profile_rows)

    symbol_candidates = _normalize_symbols(candidate_symbols)
    if not symbol_candidates:
        symbol_candidates = _normalize_symbols(
            [
                *price_df.get("symbol", pd.Series(dtype=object)).tolist(),
                *statement_df.get("symbol", pd.Series(dtype=object)).tolist(),
                *profile_df.get("symbol", pd.Series(dtype=object)).tolist(),
            ]
        )

    latest_price = _latest_price_rows(price_df, as_of_ts).set_index("symbol", drop=False)
    latest_statement = _latest_statement_rows(statement_df, as_of_ts).set_index("symbol", drop=False)
    profiles = _asset_profile_map(profile_df)

    rows: list[dict[str, Any]] = []
    for symbol in sorted(symbol_candidates):
        profile = profiles.get(symbol, {})
        price = latest_price.loc[symbol].to_dict() if symbol in latest_price.index else {}
        statement = latest_statement.loc[symbol].to_dict() if symbol in latest_statement.index else {}

        close = pd.to_numeric(price.get("close"), errors="coerce")
        shares = pd.to_numeric(statement.get("shares_outstanding"), errors="coerce")
        avg_dollar_volume = pd.to_numeric(price.get("avg_dollar_volume_20d"), errors="coerce")
        excluded_reason = _profile_exclusion_reason(profile, as_of_ts)
        if excluded_reason is None and (pd.isna(close) or close <= 0):
            excluded_reason = "missing_price"
        if excluded_reason is None and (pd.isna(shares) or shares <= 0):
            excluded_reason = "missing_statement_shares"
        if (
            excluded_reason is None
            and min_avg_dollar_volume_20d > 0.0
            and (pd.isna(avg_dollar_volume) or float(avg_dollar_volume) < float(min_avg_dollar_volume_20d))
        ):
            excluded_reason = "liquidity_below_threshold"

        approx_market_cap = (
            float(close) * float(shares)
            if excluded_reason is None and pd.notna(close) and pd.notna(shares)
            else None
        )
        rows.append(
            {
                "universe_code": code,
                "as_of_date": as_of_ts.strftime("%Y-%m-%d"),
                "symbol": symbol,
                "rank_no": None,
                "eligible": excluded_reason is None,
                "included": False,
                "excluded_reason": excluded_reason,
                "price_date": (
                    pd.Timestamp(price["price_date"]).strftime("%Y-%m-%d")
                    if price.get("price_date") is not None and pd.notna(price.get("price_date"))
                    else None
                ),
                "close": float(close) if pd.notna(close) else None,
                "shares_outstanding": int(shares) if pd.notna(shares) else None,
                "shares_source": statement.get("shares_source"),
                "approx_market_cap": approx_market_cap,
                "avg_dollar_volume_20d": float(avg_dollar_volume) if pd.notna(avg_dollar_volume) else None,
                "listing_status": profile.get("status"),
                "lifecycle_source": None,
                "method_version": method_version,
                "evidence_json": _json_safe(
                    {
                        "source_basis": PIT_UNIVERSE_SOURCE_BASIS,
                        "profile_status": profile.get("status"),
                    }
                ),
            }
        )

    eligible_rows = [
        row for row in rows if row["eligible"] and row["approx_market_cap"] is not None
    ]
    eligible_rows.sort(key=lambda row: (-float(row["approx_market_cap"]), row["symbol"]))
    for rank_index, row in enumerate(eligible_rows, start=1):
        row["rank_no"] = rank_index
        if rank_index <= target:
            row["included"] = True
            row["excluded_reason"] = None
        else:
            row["excluded_reason"] = "below_rank_cutoff"

    included_count = sum(1 for row in rows if row["included"])
    eligible_count = sum(1 for row in rows if row["eligible"])
    status = "ok" if included_count >= target else "partial" if included_count else "empty"
    snapshot = {
        "universe_code": code,
        "as_of_date": as_of_ts.strftime("%Y-%m-%d"),
        "frequency": "monthly",
        "target_size": target,
        "method_version": method_version,
        "source_basis": PIT_UNIVERSE_SOURCE_BASIS,
        "candidate_count": len(rows),
        "eligible_count": eligible_count,
        "member_count": included_count,
        "excluded_count": len(rows) - included_count,
        "max_rank": max([int(row["rank_no"]) for row in rows if row["rank_no"] is not None], default=None),
        "status": status,
        "warning_json": _json_safe(
            {
                "approximation": "Uses DB close and latest-known statement shares; not official float-adjusted membership.",
                "target_filled": included_count >= target,
            }
        ),
    }
    return {"snapshot": snapshot, "members": rows}


def _month_end_price_dates(
    price_rows: pd.DataFrame,
    *,
    start: str,
    end: str,
) -> list[pd.Timestamp]:
    if price_rows.empty:
        return []
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    working = price_rows.copy()
    working["date"] = pd.to_datetime(working["date"], errors="coerce").dt.normalize()
    working = working[
        working["date"].notna()
        & (working["date"] >= start_ts)
        & (working["date"] <= end_ts)
    ].copy()
    if working.empty:
        return []
    working["month"] = working["date"].dt.to_period("M")
    return [
        pd.Timestamp(value).normalize()
        for value in working.groupby("month", sort=True)["date"].max().tolist()
    ]


def build_monthly_equity_universe_snapshot_payloads(
    *,
    start: str,
    end: str,
    target_size: int,
    price_rows: pd.DataFrame | Sequence[dict[str, Any]],
    statement_rows: pd.DataFrame | Sequence[dict[str, Any]],
    asset_profile_rows: pd.DataFrame | Sequence[dict[str, Any]] | None = None,
    candidate_symbols: Sequence[str] | None = None,
    universe_code: str | None = None,
    method_version: str = PIT_UNIVERSE_METHOD_VERSION,
    min_avg_dollar_volume_20d: float = 0.0,
) -> list[dict[str, Any]]:
    """Build one PIT universe payload per observed month-end trading date."""
    price_df = _frame(price_rows)
    statement_df = _frame(statement_rows)
    profile_df = _frame(asset_profile_rows)
    payloads: list[dict[str, Any]] = []
    for as_of_ts in _month_end_price_dates(price_df, start=start, end=end):
        payloads.append(
            build_equity_universe_snapshot_payload(
                as_of_date=as_of_ts.strftime("%Y-%m-%d"),
                target_size=target_size,
                price_rows=price_df,
                statement_rows=statement_df,
                asset_profile_rows=profile_df,
                candidate_symbols=candidate_symbols,
                universe_code=universe_code,
                method_version=method_version,
                min_avg_dollar_volume_20d=min_avg_dollar_volume_20d,
            )
        )
    return payloads


def ensure_pit_universe_schema(db: Any) -> None:
    db.use_db(DB_META)
    for table_name, create_sql in PIT_UNIVERSE_SCHEMAS.items():
        sync_table_schema(db, table_name, create_sql, DB_META)


def _db_bool(value: object) -> int:
    return 1 if bool(value) else 0


def _snapshot_db_params(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "universe_code": snapshot.get("universe_code"),
        "as_of_date": snapshot.get("as_of_date"),
        "frequency": snapshot.get("frequency") or "monthly",
        "target_size": int(snapshot.get("target_size") or 0),
        "method_version": snapshot.get("method_version") or PIT_UNIVERSE_METHOD_VERSION,
        "source_basis": snapshot.get("source_basis") or PIT_UNIVERSE_SOURCE_BASIS,
        "candidate_count": int(snapshot.get("candidate_count") or 0),
        "eligible_count": int(snapshot.get("eligible_count") or 0),
        "member_count": int(snapshot.get("member_count") or 0),
        "excluded_count": int(snapshot.get("excluded_count") or 0),
        "max_rank": snapshot.get("max_rank"),
        "status": snapshot.get("status") or "empty",
        "warning_json": snapshot.get("warning_json"),
    }


def _member_db_params(member: dict[str, Any]) -> dict[str, Any]:
    return {
        "universe_code": member.get("universe_code"),
        "as_of_date": member.get("as_of_date"),
        "symbol": member.get("symbol"),
        "rank_no": member.get("rank_no"),
        "eligible": _db_bool(member.get("eligible")),
        "included": _db_bool(member.get("included")),
        "excluded_reason": member.get("excluded_reason"),
        "price_date": member.get("price_date"),
        "close": member.get("close"),
        "shares_outstanding": member.get("shares_outstanding"),
        "shares_source": member.get("shares_source"),
        "approx_market_cap": member.get("approx_market_cap"),
        "avg_dollar_volume_20d": member.get("avg_dollar_volume_20d"),
        "listing_status": member.get("listing_status"),
        "lifecycle_source": member.get("lifecycle_source"),
        "method_version": member.get("method_version") or PIT_UNIVERSE_METHOD_VERSION,
        "evidence_json": member.get("evidence_json"),
    }


def upsert_equity_universe_snapshot_payload(
    payload: dict[str, Any],
    *,
    db: Any | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Persist one PIT universe snapshot payload idempotently."""
    owns_db = db is None
    active_db = db or MySQLClient(host, user, password, port)
    try:
        ensure_pit_universe_schema(active_db)
        snapshot = _snapshot_db_params(dict(payload.get("snapshot") or {}))
        members = [_member_db_params(dict(row)) for row in payload.get("members") or []]

        active_db.execute(
            """
            INSERT INTO equity_universe_snapshot (
              universe_code, as_of_date, frequency, target_size, method_version, source_basis,
              candidate_count, eligible_count, member_count, excluded_count, max_rank, status, warning_json
            ) VALUES (
              %(universe_code)s, %(as_of_date)s, %(frequency)s, %(target_size)s, %(method_version)s, %(source_basis)s,
              %(candidate_count)s, %(eligible_count)s, %(member_count)s, %(excluded_count)s, %(max_rank)s, %(status)s, %(warning_json)s
            )
            ON DUPLICATE KEY UPDATE
              frequency = VALUES(frequency),
              target_size = VALUES(target_size),
              source_basis = VALUES(source_basis),
              candidate_count = VALUES(candidate_count),
              eligible_count = VALUES(eligible_count),
              member_count = VALUES(member_count),
              excluded_count = VALUES(excluded_count),
              max_rank = VALUES(max_rank),
              status = VALUES(status),
              warning_json = VALUES(warning_json)
            """,
            snapshot,
        )
        if members:
            active_db.executemany(
                """
                INSERT INTO equity_universe_member (
                  universe_code, as_of_date, symbol, rank_no, eligible, included, excluded_reason,
                  price_date, close, shares_outstanding, shares_source, approx_market_cap,
                  avg_dollar_volume_20d, listing_status, lifecycle_source, method_version, evidence_json
                ) VALUES (
                  %(universe_code)s, %(as_of_date)s, %(symbol)s, %(rank_no)s, %(eligible)s, %(included)s, %(excluded_reason)s,
                  %(price_date)s, %(close)s, %(shares_outstanding)s, %(shares_source)s, %(approx_market_cap)s,
                  %(avg_dollar_volume_20d)s, %(listing_status)s, %(lifecycle_source)s, %(method_version)s, %(evidence_json)s
                )
                ON DUPLICATE KEY UPDATE
                  rank_no = VALUES(rank_no),
                  eligible = VALUES(eligible),
                  included = VALUES(included),
                  excluded_reason = VALUES(excluded_reason),
                  price_date = VALUES(price_date),
                  close = VALUES(close),
                  shares_outstanding = VALUES(shares_outstanding),
                  shares_source = VALUES(shares_source),
                  approx_market_cap = VALUES(approx_market_cap),
                  avg_dollar_volume_20d = VALUES(avg_dollar_volume_20d),
                  listing_status = VALUES(listing_status),
                  lifecycle_source = VALUES(lifecycle_source),
                  evidence_json = VALUES(evidence_json)
                """,
                members,
            )
        return {
            "universe_code": snapshot["universe_code"],
            "as_of_date": snapshot["as_of_date"],
            "snapshot_rows": 1,
            "member_rows": len(members),
        }
    finally:
        if owns_db:
            active_db.close()


def build_and_store_monthly_equity_universe_snapshots(
    *,
    candidate_symbols: Sequence[str],
    start: str,
    end: str,
    target_size: int,
    universe_code: str | None = None,
    method_version: str = PIT_UNIVERSE_METHOD_VERSION,
    statement_freq: str = "annual",
    min_avg_dollar_volume_20d: float = 0.0,
    db: Any | None = None,
) -> dict[str, Any]:
    """
    Read existing DB source rows, build monthly PIT universe payloads, and persist them.

    This orchestration intentionally does not collect external data. Operators must
    refresh prices, statement shadow rows, and lifecycle/profile data through the
    ingestion flow before running it.
    """
    symbols = _normalize_symbols(candidate_symbols)
    if not symbols:
        raise ValueError("candidate_symbols must not be empty.")

    from finance.loaders import (  # local import avoids loader -> data circular import
        load_asset_profile_status_summary,
        load_price_history,
        load_statement_fundamentals_shadow,
    )

    price_rows = load_price_history(
        symbols=symbols,
        start=start,
        end=end,
        timeframe="1d",
    )
    statement_rows = load_statement_fundamentals_shadow(
        symbols=symbols,
        freq=statement_freq,
        end=end,
    )
    asset_profile_rows = load_asset_profile_status_summary(symbols)
    payloads = build_monthly_equity_universe_snapshot_payloads(
        start=start,
        end=end,
        target_size=target_size,
        price_rows=price_rows,
        statement_rows=statement_rows,
        asset_profile_rows=asset_profile_rows,
        candidate_symbols=symbols,
        universe_code=universe_code,
        method_version=method_version,
        min_avg_dollar_volume_20d=min_avg_dollar_volume_20d,
    )

    total_member_rows = 0
    persisted: list[dict[str, Any]] = []
    for payload in payloads:
        write_result = upsert_equity_universe_snapshot_payload(payload, db=db)
        persisted.append(write_result)
        total_member_rows += int(write_result.get("member_rows") or 0)

    resolved_code = universe_code or normalize_pit_universe_code(target_size)
    return {
        "universe_code": resolved_code,
        "method_version": method_version,
        "candidate_count": len(symbols),
        "snapshots_built": len(payloads),
        "snapshots_persisted": len(persisted),
        "member_rows": total_member_rows,
        "first_as_of_date": payloads[0]["snapshot"]["as_of_date"] if payloads else None,
        "last_as_of_date": payloads[-1]["snapshot"]["as_of_date"] if payloads else None,
    }
