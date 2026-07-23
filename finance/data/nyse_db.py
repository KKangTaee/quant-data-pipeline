import json
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS, sync_table_schema

DB_NAME = "finance_meta"
LISTING_KINDS = ("stock", "etf")


def _snapshot_date_text(snapshot_date: str | None = None) -> str:
    return str(snapshot_date or date.today().isoformat())


def _upsert_symbol_lifecycle_rows(
    db: MySQLClient,
    *,
    kind: str,
    frame: pd.DataFrame,
    snapshot_date: str | None = None,
    ensure_schema: bool = True,
) -> int:
    """Record current NYSE listing rows as partial lifecycle evidence."""

    if kind not in {"stock", "etf"}:
        raise ValueError("kind는 'stock' 또는 'etf'만 가능합니다.")
    if frame.empty:
        return 0

    snapshot = _snapshot_date_text(snapshot_date)
    if ensure_schema:
        sync_table_schema(db, "nyse_symbol_lifecycle", NYSE_SCHEMAS["symbol_lifecycle"], DB_NAME)
    rows = []
    for record in frame[["symbol", "name", "url"]].to_dict(orient="records"):
        symbol = str(record.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        rows.append(
            {
                "symbol": symbol,
                "kind": kind,
                "listing_status": "active",
                "source": "nyse_listings_directory",
                "source_type": "current_listing_snapshot",
                "coverage_status": "partial",
                "first_seen_date": snapshot,
                "last_seen_date": snapshot,
                "inactive_detected_at": None,
                "name": record.get("name"),
                "source_ref": record.get("url"),
                "evidence_json": json.dumps(
                    {
                        "snapshot_date": snapshot,
                        "event_type": "listing_observed",
                        "event_date": snapshot,
                        "source_note": "current NYSE listing snapshot; not sufficient alone for historical survivorship PASS",
                    },
                    ensure_ascii=False,
                ),
                "event_type": "listing_observed",
                "event_date": snapshot,
                "related_symbol": None,
                "related_cik": None,
                "collected_at": f"{snapshot} 00:00:00",
                "error_msg": None,
            }
        )
    if not rows:
        return 0

    sql = """
        INSERT INTO nyse_symbol_lifecycle (
            symbol, kind, listing_status, source, source_type, coverage_status,
            first_seen_date, last_seen_date, inactive_detected_at,
            event_type, event_date, related_symbol, related_cik,
            name, source_ref, evidence_json, collected_at, error_msg
        )
        VALUES (
            %(symbol)s, %(kind)s, %(listing_status)s, %(source)s, %(source_type)s, %(coverage_status)s,
            %(first_seen_date)s, %(last_seen_date)s, %(inactive_detected_at)s,
            %(event_type)s, %(event_date)s, %(related_symbol)s, %(related_cik)s,
            %(name)s, %(source_ref)s, %(evidence_json)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
            listing_status = VALUES(listing_status),
            source_type = VALUES(source_type),
            coverage_status = VALUES(coverage_status),
            first_seen_date = CASE
                WHEN first_seen_date IS NULL OR VALUES(first_seen_date) < first_seen_date
                    THEN VALUES(first_seen_date)
                ELSE first_seen_date
            END,
            last_seen_date = CASE
                WHEN last_seen_date IS NULL OR VALUES(last_seen_date) > last_seen_date
                    THEN VALUES(last_seen_date)
                ELSE last_seen_date
            END,
            inactive_detected_at = NULL,
            event_type = VALUES(event_type),
            event_date = VALUES(event_date),
            related_symbol = VALUES(related_symbol),
            related_cik = VALUES(related_cik),
            name = VALUES(name),
            source_ref = VALUES(source_ref),
            evidence_json = VALUES(evidence_json),
            collected_at = VALUES(collected_at),
            error_msg = NULL
    """
    db.executemany(sql, rows)
    return len(rows)


def _normalize_listing_frame(frame: pd.DataFrame, *, kind: str) -> pd.DataFrame:
    """Normalize current listing rows before retention checks and persistence."""

    if kind not in LISTING_KINDS:
        raise ValueError("kind는 'stock' 또는 'etf'만 가능합니다.")
    required_columns = {"symbol", "name", "url"}
    missing_columns = sorted(required_columns.difference(frame.columns))
    if missing_columns:
        raise ValueError(f"{kind} listing snapshot missing columns: {missing_columns}")

    normalized = frame[["symbol", "name", "url"]].copy()
    normalized = normalized.replace({pd.NA: None, float("nan"): None})
    for column in ("symbol", "name", "url"):
        normalized[column] = normalized[column].map(
            lambda value: str(value or "").strip()
        )
    normalized = normalized[
        (normalized["symbol"] != "") & (normalized["name"] != "")
    ].copy()
    normalized["_symbol_key"] = normalized["symbol"].str.upper()
    normalized = (
        normalized.drop_duplicates("_symbol_key", keep="first")
        .sort_values("_symbol_key")
        .drop(columns=["_symbol_key"])
        .reset_index(drop=True)
    )
    if normalized.empty:
        raise ValueError(f"{kind} listing snapshot has no usable rows.")
    return normalized


def _ensure_listing_schemas(db: MySQLClient) -> None:
    """Ensure all DDL is complete before the explicit refresh transaction."""

    for kind in LISTING_KINDS:
        db.execute(NYSE_SCHEMAS[kind])
    sync_table_schema(
        db,
        "nyse_symbol_lifecycle",
        NYSE_SCHEMAS["symbol_lifecycle"],
        DB_NAME,
    )


def _load_current_listing_symbols(
    db: MySQLClient,
    *,
    kind: str,
) -> dict[str, str]:
    rows = db.query(f"SELECT symbol FROM nyse_{kind}")
    return {
        str(row["symbol"]).strip().upper(): str(row["symbol"]).strip()
        for row in rows
        if row.get("symbol") and str(row["symbol"]).strip()
    }


def _validate_listing_retention(
    frames: Mapping[str, pd.DataFrame],
    existing: Mapping[str, Mapping[str, str]],
    minimum_retention_ratio: float,
) -> None:
    if not 0.0 <= float(minimum_retention_ratio) <= 1.0:
        raise ValueError("minimum_retention_ratio must be between 0 and 1.")

    for kind in LISTING_KINDS:
        existing_count = len(existing[kind])
        current_count = len(frames[kind])
        if existing_count <= 0:
            continue
        retention_ratio = current_count / existing_count
        if retention_ratio < float(minimum_retention_ratio):
            raise ValueError(
                f"{kind} listing retention {retention_ratio:.3f} is below "
                f"{float(minimum_retention_ratio):.3f}; existing masters were preserved."
            )


def _replace_listing_master(
    db: MySQLClient,
    *,
    kind: str,
    frame: pd.DataFrame,
    existing_symbols: Mapping[str, str],
    canonical_replace: bool = True,
) -> dict[str, Any]:
    current_by_key = {
        str(record["symbol"]).strip().upper(): str(record["symbol"]).strip()
        for record in frame[["symbol"]].to_dict(orient="records")
    }
    added_keys = sorted(set(current_by_key).difference(existing_symbols))
    removed_keys = sorted(set(existing_symbols).difference(current_by_key))

    rows = frame[["symbol", "name", "url"]].values.tolist()
    db.executemany(
        f"""
            INSERT INTO nyse_{kind} (symbol, name, url)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                url = VALUES(url)
        """,
        rows,
    )

    if canonical_replace:
        stale_symbols = [existing_symbols[key] for key in removed_keys]
        for index in range(0, len(stale_symbols), 500):
            batch = stale_symbols[index:index + 500]
            placeholders = ", ".join(["%s"] * len(batch))
            db.execute(
                f"DELETE FROM nyse_{kind} WHERE symbol IN ({placeholders})",
                batch,
            )

    return {
        "before_count": len(existing_symbols),
        "current_count": len(current_by_key),
        "added_count": len(added_keys),
        "removed_count": len(removed_keys) if canonical_replace else 0,
        "added_symbols": [current_by_key[key] for key in added_keys],
        "removed_symbols": (
            [existing_symbols[key] for key in removed_keys]
            if canonical_replace
            else []
        ),
    }


def refresh_nyse_listing_universe(
    frames: Mapping[str, pd.DataFrame],
    *,
    snapshot_date: str | None = None,
    minimum_retention_ratio: float = 0.8,
    db_factory: Callable[..., MySQLClient] = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Atomically replace the current stock and ETF listing masters."""

    missing_kinds = [kind for kind in LISTING_KINDS if kind not in frames]
    if missing_kinds:
        raise ValueError(f"listing snapshots missing kinds: {missing_kinds}")
    normalized = {
        kind: _normalize_listing_frame(frames[kind], kind=kind)
        for kind in LISTING_KINDS
    }
    snapshot = _snapshot_date_text(snapshot_date)

    db = db_factory(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        _ensure_listing_schemas(db)
        existing = {
            kind: _load_current_listing_symbols(db, kind=kind)
            for kind in LISTING_KINDS
        }
        _validate_listing_retention(
            normalized,
            existing,
            minimum_retention_ratio,
        )

        kind_summaries: dict[str, dict[str, Any]] = {}
        lifecycle_rows = 0
        db.begin()
        try:
            for kind in LISTING_KINDS:
                kind_summaries[kind] = _replace_listing_master(
                    db,
                    kind=kind,
                    frame=normalized[kind],
                    existing_symbols=existing[kind],
                )
                lifecycle_rows += _upsert_symbol_lifecycle_rows(
                    db,
                    kind=kind,
                    frame=normalized[kind],
                    snapshot_date=snapshot,
                    ensure_schema=False,
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

        master_rows = sum(
            int(summary["current_count"])
            for summary in kind_summaries.values()
        )
        return {
            "snapshot_date": snapshot,
            "rows_written": master_rows,
            "lifecycle_rows_written": lifecycle_rows,
            "kinds": kind_summaries,
            "target_tables": [
                "finance_meta.nyse_stock",
                "finance_meta.nyse_etf",
                "finance_meta.nyse_symbol_lifecycle",
            ],
        }
    finally:
        db.close()


def load_nyse_listing_universe_status(
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    *,
    db_factory: Callable[..., MySQLClient] = MySQLClient,
) -> dict[str, Any]:
    """Load the current master counts and common lifecycle snapshot basis."""

    db = db_factory(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        kinds: dict[str, dict[str, Any]] = {}
        for kind in LISTING_KINDS:
            count_rows = db.query(
                f"SELECT COUNT(*) AS row_count FROM nyse_{kind}"
            )
            kinds[kind] = {
                "row_count": int(
                    (count_rows[0] if count_rows else {}).get("row_count") or 0
                ),
                "last_seen_date": None,
                "collected_at": None,
            }

        lifecycle_rows = db.query(
            """
                SELECT
                    kind,
                    MAX(last_seen_date) AS last_seen_date,
                    MAX(collected_at) AS collected_at
                FROM nyse_symbol_lifecycle
                WHERE source = 'nyse_listings_directory'
                GROUP BY kind
            """
        )
        for row in lifecycle_rows:
            kind = str(row.get("kind") or "")
            if kind not in kinds:
                continue
            kinds[kind]["last_seen_date"] = (
                str(row["last_seen_date"]) if row.get("last_seen_date") else None
            )
            kinds[kind]["collected_at"] = (
                str(row["collected_at"]) if row.get("collected_at") else None
            )

        snapshot_dates = [
            str(kinds[kind]["last_seen_date"])
            for kind in LISTING_KINDS
            if kinds[kind].get("last_seen_date")
        ]
        latest_snapshot_date = min(snapshot_dates) if snapshot_dates else None
        return {
            "status": "ok",
            "latest_snapshot_date": latest_snapshot_date,
            "kinds": kinds,
            "message": (
                "NYSE stock and ETF listing master status loaded."
                if latest_snapshot_date
                else "NYSE listing snapshot date is unavailable."
            ),
        }
    finally:
        db.close()


def load_nyse_csv_to_mysql(
    kind: str,
    csv_dir: str = "csv",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    *,
    canonical_replace: bool = True,
    update_lifecycle: bool = True,
    snapshot_date: str | None = None,
):
    """
        nyse_etf 또는 nyse_stock csv 파일의 데이터를 db에 올림
    """

    if kind not in {"stock", "etf"}:
        raise ValueError("kind는 'stock' 또는 'etf'만 가능합니다.")

    csv_path = Path(csv_dir) / f"nyse_{kind}.csv"
    df = pd.read_csv(csv_path, keep_default_na=False) # NA를 nan으로 변환하는걸 막는다.

    print(df.columns.tolist())
    print(df[df["symbol"].isna()].head())
    print(df[df["symbol"].astype(str).str.strip() == ""].head())
 
    # ✅ MySQL용 NaN 처리 (중요)
    df = _normalize_listing_frame(df, kind=kind)
    
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        db.execute(NYSE_SCHEMAS[kind])
        if update_lifecycle:
            sync_table_schema(
                db,
                "nyse_symbol_lifecycle",
                NYSE_SCHEMAS["symbol_lifecycle"],
                DB_NAME,
            )
        existing = _load_current_listing_symbols(db, kind=kind)

        db.begin()
        try:
            summary = _replace_listing_master(
                db,
                kind=kind,
                frame=df,
                existing_symbols=existing,
                canonical_replace=canonical_replace,
            )
            lifecycle_count = 0
            if update_lifecycle:
                lifecycle_count = _upsert_symbol_lifecycle_rows(
                    db,
                    kind=kind,
                    frame=df,
                    snapshot_date=snapshot_date,
                    ensure_schema=False,
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

        if summary["removed_count"]:
            print(
                f"🧹 nyse_{kind} stale rows 제거 "
                f"({summary['removed_count']:,} rows)"
            )
        if update_lifecycle:
            print(f"✅ nyse_symbol_lifecycle 갱신 완료 ({lifecycle_count:,} rows)")

        print(f"✅ nyse_{kind} 적재 완료 ({len(df):,} rows)")

    finally:
        db.close()
