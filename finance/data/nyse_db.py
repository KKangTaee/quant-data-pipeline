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
    port=3306
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

        db.executemany(
            sql,
            rows
        )

        print(f"✅ nyse_{kind} 적재 완료 ({len(df):,} rows)")

    finally:
        db.close()