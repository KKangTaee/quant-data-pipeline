# finance/data/db/mysql.py

import pymysql


class MySQLClient:
    def __init__(self, host, user, password, port=3306, charset="utf8mb4"):
        self.conn = pymysql.connect(
            host=host, user=user, password=password, port=port,
            charset=charset, autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,  # ✅ dict로 받기
        )

    def execute(self, sql: str, params=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, params)

    def executemany(self, sql: str, params: list):
        with self.conn.cursor() as cur:
            cur.executemany(sql, params)

    def query(self, sql: str, params=None) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())

    def use_db(self, db_name: str):
        self.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        self.execute(f"USE {db_name}")

    def close(self):
        self.conn.close()