import time
import random
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS

DB_NAME = "finance_meta"

def _chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

def _is_spac_heuristic(info: dict) -> int | None:
    # 확실한 정보 없으면 None
    name = (info.get("longName") or info.get("shortName") or "").lower()
    industry = (info.get("industry") or "").lower()

    if industry == "shell companies":
        return 1

    keywords = ["acquisition", "acq", "special purpose", "spac"]
    if any(k in name for k in keywords):
        return 1

    return 0 if name else None

def _detect_status(t: yf.Ticker, info: dict) -> tuple[str, str | None]:
    """
    active / delisted / not_found 추정
    """
    if not info:
        return "not_found", "empty info"

    # 가격 히스토리로 상폐/비거래 추정 (가장 간단하고 실전적)
    try:
        h = t.history(period="1mo", interval="1d")
        if h is None or h.empty:
            return "delisted", "empty 1mo history"
    except Exception as e:
        # history도 실패면 일단 error로 두고 재시도 여지
        return "error", f"history error: {e}"

    return "active", None

def _extract_profile(symbol: str, kind: str, t: yf.Ticker) -> dict:
    # info는 비용이 큰 편 → 예외처리 필수
    info = {}
    try:
        info = t.get_info()
    except Exception:
        # yfinance 버전에 따라 get_info가 없으면 t.info로 fallback
        info = getattr(t, "info", {}) or {}

    status, msg = _detect_status(t, info)

    quote_type = info.get("quoteType")
    exchange = info.get("exchange")
    # exchange_name = info.get("exchangeName")

    # fast_info 우선
    market_cap = None
    try:
        fi = getattr(t, "fast_info", None)
        if fi:
            market_cap = fi.get("marketCap")
    except Exception:
        pass
    if market_cap is None:
        market_cap = info.get("marketCap")

    row = {
        "symbol": symbol,
        "kind": kind,

        "quote_type": quote_type,
        "exchange": exchange,
        # "exchange_name": exchange_name,

        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),

        "market_cap": market_cap,
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),

        # 지수 편입은 별도 소스가 필요 → 일단 None로 두고 나중에 enrichment 추천
        # "in_sp500": None,
        # "in_nasdaq100": None,
        # "in_russell2000": None,

        "is_spac": _is_spac_heuristic(info),

        "status": status,
        "error_msg": msg,
        "last_collected_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "delisted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if status == "delisted" else None,
    }

    # ETF는 정보 부족할 수 있음 → “pass” 규칙: 핵심이 너무 비면 status=active라도 저장 최소화
    # (그래도 status 추적은 남기는 게 운영에 좋음)
    return row

def _upsert_profiles(db: MySQLClient, rows: list[dict]):
    if not rows:
        return

    sql = """
    INSERT INTO nyse_asset_profile (
      symbol, kind,
      quote_type, exchange,
      sector, industry, country,
      market_cap, dividend_yield, payout_ratio,
      is_spac,
      status, last_collected_at, delisted_at, error_msg
    ) VALUES (
      %(symbol)s, %(kind)s,
      %(quote_type)s, %(exchange)s,
      %(sector)s, %(industry)s, %(country)s,
      %(market_cap)s, %(dividend_yield)s, %(payout_ratio)s,
      %(is_spac)s,
      %(status)s, %(last_collected_at)s, %(delisted_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      quote_type = VALUES(quote_type),
      exchange = VALUES(exchange),
      sector = VALUES(sector),
      industry = VALUES(industry),
      country = VALUES(country),
      market_cap = VALUES(market_cap),
      dividend_yield = VALUES(dividend_yield),
      payout_ratio = VALUES(payout_ratio),
      is_spac = VALUES(is_spac),
      status = VALUES(status),
      last_collected_at = VALUES(last_collected_at),
      delisted_at = VALUES(delisted_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)

def collect_and_store_asset_profiles(
    kinds: tuple[str, ...] = ("stock", "etf"),
    chunk_size: int = 50,
    sleep: float = 0.4,
    max_retry: int = 3,
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    save_fail_csv: bool = True,
    csv_dir: str = "csv",
):
    db = MySQLClient(host, user, password, port)
    out_fail = []

    try:
        db.use_db(DB_NAME)
        db.execute(NYSE_SCHEMAS["asset_profile"])

        for kind in kinds:
            symbols = db.query(f"SELECT symbol FROM nyse_{kind}")
            symbols = [r["symbol"] for r in symbols if r.get("symbol")]

            for batch in _chunked(symbols, chunk_size):
                tickers = yf.Tickers(" ".join(batch)).tickers

                rows = []
                for sym in batch:
                    t = tickers.get(sym) or yf.Ticker(sym)

                    # 재시도(지수 백오프)
                    last_err = None
                    for k in range(max_retry):
                        try:
                            row = _extract_profile(sym, kind, t)
                            rows.append(row)

                            if row["status"] in ("not_found", "delisted", "error"):
                                out_fail.append({
                                    "symbol": sym,
                                    "kind": kind,
                                    "status": row["status"],
                                    "error_msg": row.get("error_msg"),
                                    "collected_at": row["last_collected_at"],
                                })
                            break
                        except Exception as e:
                            last_err = str(e)
                            # 백오프
                            time.sleep((2 ** k) + random.random() * 0.2)

                    else:
                        # retry 모두 실패
                        out_fail.append({
                            "symbol": sym,
                            "kind": kind,
                            "status": "error",
                            "error_msg": f"retry_failed: {last_err}",
                            "collected_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        })

                _upsert_profiles(db, rows)

                # 배치 sleep(+지터)
                time.sleep(sleep + random.random() * 0.2)

    finally:
        db.close()

    if save_fail_csv and out_fail:
        Path(csv_dir).mkdir(exist_ok=True)
        p = Path(csv_dir) / f"nyse_profile_failures_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        pd.DataFrame(out_fail).to_csv(p, index=False, encoding="utf-8-sig")

    return out_fail