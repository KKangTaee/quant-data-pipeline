import pandas as pd
import json
from datetime import date
from pathlib import Path

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS, sync_table_schema

DB_NAME = "finance_meta"


def _snapshot_date_text(snapshot_date: str | None = None) -> str:
    return str(snapshot_date or date.today().isoformat())


def _upsert_symbol_lifecycle_rows(
    db: MySQLClient,
    *,
    kind: str,
    frame: pd.DataFrame,
    snapshot_date: str | None = None,
) -> int:
    """Record current NYSE listing rows as partial lifecycle evidence."""

    if kind not in {"stock", "etf"}:
        raise ValueError("kind는 'stock' 또는 'etf'만 가능합니다.")
    if frame.empty:
        return 0

    snapshot = _snapshot_date_text(snapshot_date)
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
                        "source_note": "current NYSE listing snapshot; not sufficient alone for historical survivorship PASS",
                    },
                    ensure_ascii=False,
                ),
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
            name, source_ref, evidence_json, collected_at, error_msg
        )
        VALUES (
            %(symbol)s, %(kind)s, %(listing_status)s, %(source)s, %(source_type)s, %(coverage_status)s,
            %(first_seen_date)s, %(last_seen_date)s, %(inactive_detected_at)s,
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
            name = VALUES(name),
            source_ref = VALUES(source_ref),
            evidence_json = VALUES(evidence_json),
            collected_at = VALUES(collected_at),
            error_msg = NULL
    """
    db.executemany(sql, rows)
    return len(rows)


def load_nyse_csv_to_mysql(
    kind: str,
    csv_dir: str = "csv",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    *,
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
    df = df[["symbol", "name", "url"]].astype(object)
    df = df.replace({pd.NA: None, float("nan"): None})
    
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        db.execute(NYSE_SCHEMAS[kind])

        sql = f"""
            INSERT INTO nyse_{kind} (symbol, name, url)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                url  = VALUES(url)
        """

        rows = df.values.tolist()

        db.executemany(
            sql,
            rows
        )

        if update_lifecycle:
            lifecycle_count = _upsert_symbol_lifecycle_rows(
                db,
                kind=kind,
                frame=df,
                snapshot_date=snapshot_date,
            )
            print(f"✅ nyse_symbol_lifecycle 갱신 완료 ({lifecycle_count:,} rows)")

        print(f"✅ nyse_{kind} 적재 완료 ({len(df):,} rows)")

    finally:
        db.close()
