from IPython.core import display
import pandas as pd
from pathlib import Path

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS

DB_NAME = "finance_meta"


def load_nyse_csv_to_mysql(
    kind: str,
    csv_dir: str = "csv",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    canonical_replace: bool = True,
):
    """
        nyse_etf 또는 nyse_stock csv 파일의 데이터를 db에 올림
    """

    if kind not in NYSE_SCHEMAS:
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
        if canonical_replace:
            latest_symbols = {str(row[0]).strip() for row in rows if row and str(row[0]).strip()}
            existing_rows = db.query(f"SELECT symbol FROM nyse_{kind}")
            stale_symbols = sorted(
                str(row["symbol"]).strip()
                for row in existing_rows
                if row.get("symbol") and str(row["symbol"]).strip() not in latest_symbols
            )
            for i in range(0, len(stale_symbols), 500):
                batch = stale_symbols[i:i + 500]
                placeholders = ", ".join(["%s"] * len(batch))
                db.execute(f"DELETE FROM nyse_{kind} WHERE symbol IN ({placeholders})", batch)
            if stale_symbols:
                print(f"🧹 nyse_{kind} stale rows 제거 ({len(stale_symbols):,} rows)")

        db.executemany(
            sql,
            rows
        )

        print(f"✅ nyse_{kind} 적재 완료 ({len(df):,} rows)")

    finally:
        db.close()
