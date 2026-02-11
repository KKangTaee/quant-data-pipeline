# finance/data/factors.py
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Literal, Iterable, Optional

import pandas as pd
import numpy as np

from .db.mysql import MySQLClient
from .db.schema import FUNDAMENTAL_SCHEMAS, sync_table_schema
from .data import load_ohlcv_many_mysql

DB_FUND = "finance_fundamental"
DB_PRICE = "finance_price"  # load_ohlcv_many_mysql 내부에서 사용
Freq = Literal["annual", "quarterly"]


def _setup_logger(log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(exist_ok=True)
    logger = logging.getLogger("finance.factors")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        Path(log_dir) / f"factors_errors_{datetime.utcnow().strftime('%Y%m%d')}.log",
        encoding="utf-8",
    )
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def _safe_div(a, b):
    if a is None or b is None:
        return None
    try:
        if pd.isna(a) or pd.isna(b) or b == 0:
            return None
        return float(a) / float(b)
    except Exception:
        return None


def _attach_price_asof(fund: pd.DataFrame, price: pd.DataFrame) -> pd.DataFrame:
    """
    period_end 기준으로 직전 거래일 종가(close)를 매칭.
    pandas merge_asof(by=...)에서 'left keys must be sorted'가 재발하는 케이스를 피하기 위해
    symbol별로 merge_asof를 수행한다.
    """
    if fund.empty:
        return fund

    f = fund.copy()
    f["symbol"] = f["symbol"].astype(str).str.strip()
    f["period_end"] = pd.to_datetime(f["period_end"], errors="coerce")
    f = f[f["period_end"].notna()].copy()

    if price is None or price.empty:
        f["price"] = None
        return f

    p = price.copy()
    p["symbol"] = p["symbol"].astype(str).str.strip()
    p["date"] = pd.to_datetime(p["date"], errors="coerce")
    p = p[p["date"].notna()].copy()
    # price를 symbol별 dict로 캐싱
    price_map = {
        sym: g.sort_values("date").reset_index(drop=True)
        for sym, g in p.groupby("symbol", sort=False)
    }

    out_parts = []
    for sym, g in f.groupby("symbol", sort=False):
        gg = g.sort_values("period_end").reset_index(drop=True)
        pg = price_map.get(sym)

        if pg is None or pg.empty:
            gg["price"] = None
            out_parts.append(gg)
            continue

        merged = pd.merge_asof(
            gg,
            pg[["date", "close"]],
            left_on="period_end",
            right_on="date",
            direction="backward",
            allow_exact_matches=True,
        )
        merged = merged.drop(columns=["date"], errors="ignore").rename(columns={"close": "price"})
        out_parts.append(merged)

    return pd.concat(out_parts, ignore_index=True)



def add_market_cap(df: pd.DataFrame) -> pd.DataFrame:
    """
    market_cap = price * shares_outstanding (period_end asof price)
    """
    out = df.copy()
    if "price" not in out.columns or "shares_outstanding" not in out.columns:
        out["market_cap"] = None
        return out

    # 벡터화: apply보다 빠름
    price = pd.to_numeric(out["price"], errors="coerce")
    shares = pd.to_numeric(out["shares_outstanding"], errors="coerce")

    mc = price * shares
    mc = mc.where((price.notna()) & (shares.notna()) & (shares > 0), pd.NA)

    out["market_cap"] = mc
    return out


def add_enterprise_value(df: pd.DataFrame) -> pd.DataFrame:
    """
    EV(근사) = market_cap + total_debt - cash_and_equivalents
    - cash_and_equivalents 컬럼이 없으면 EV는 전부 NULL
    """
    out = df.copy()

    mc = pd.to_numeric(out.get("market_cap"), errors="coerce")
    debt = pd.to_numeric(out.get("total_debt"), errors="coerce")
    cash = pd.to_numeric(out.get("cash_and_equivalents"), errors="coerce")

    ev = mc + debt - cash
    ev = ev.where(mc.notna() & debt.notna() & cash.notna(), pd.NA)

    out["enterprise_value"] = ev
    return out

def round_numeric_columns(
    df: pd.DataFrame,
    decimals: int = 3,
    exclude: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    df에서 숫자 컬럼만 선택해서 round(decimals) 적용.
    exclude에 있는 컬럼은 제외(예: market_cap, shares_outstanding 등 정수성 유지 목적)

    반환: 원본을 복사한 DataFrame
    """
    out = df.copy()

    num_cols = out.select_dtypes(include=[np.number]).columns
    if exclude:
        excl = set(exclude)
        num_cols = [c for c in num_cols if c not in excl]

    if len(num_cols) > 0:
        out[num_cols] = out[num_cols].round(decimals)

    return out


def load_fundamentals_mysql(
    symbols: list[str] | None = None,
    freq: Freq | None = None,
    start: str | None = None,
    end: str | None = None,
    host="localhost",
    user="root",
    password="1234",
    port=3306,
) -> pd.DataFrame:
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_FUND)

        where = []
        params = []

        if symbols:
            placeholders = ",".join(["%s"] * len(symbols))
            where.append(f"symbol IN ({placeholders})")
            params.extend(symbols)

        if freq:
            where.append("freq=%s")
            params.append(freq)

        if start:
            where.append("period_end >= %s")
            params.append(start)
        if end:
            where.append("period_end <= %s")
            params.append(end)

        sql = f"""
        SELECT
          symbol, freq, period_end, currency,
          total_revenue, gross_profit, operating_income, ebit, net_income,
          total_assets, current_assets, total_liabilities, current_liabilities,
          total_debt, net_assets,
          operating_cash_flow, free_cash_flow, capital_expenditure,
          cash_and_equivalents,
          dividends_paid, shares_outstanding
        FROM nyse_fundamentals
        {("WHERE " + " AND ".join(where)) if where else ""}
        ORDER BY symbol ASC, freq ASC, period_end ASC
        """
        rows = db.query(sql, params)
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["period_end"] = pd.to_datetime(df["period_end"])
        return df
    finally:
        db.close()


def calculate_factors(fund: pd.DataFrame) -> pd.DataFrame:
    """
    fund(필수항목 스냅샷) -> 백테스트용 팩터 계산
    """
    if fund.empty:
        return fund

    df = fund.copy()
    # 표준 편의 변수
    mc = df["market_cap"]
    ev = df["enterprise_value"]
    rev = df["total_revenue"]
    gp = df["gross_profit"]
    op = df["operating_income"]
    ebit = df["ebit"]
    ni = df["net_income"]

    ta = df["total_assets"]
    ca = df["current_assets"]
    tl = df["total_liabilities"]
    cl = df["current_liabilities"]
    td = df["total_debt"]
    eq = df["net_assets"]

    ocf = df["operating_cash_flow"]
    fcf = df["free_cash_flow"]
    div_paid = df["dividends_paid"]
    sh = df["shares_outstanding"]

    # 팩터 계산
    df["psr"] = [ _safe_div(a, b) for a, b in zip(mc, rev) ]
    df["gpa"] = [ _safe_div(a, b) for a, b in zip(gp, ta) ]
    df["por"] = [ _safe_div(a, b) for a, b in zip(mc, op) ]          # POR=Price/OperatingIncome(=MC/OP)
    df["ev_ebit"] = [ _safe_div(a, b) for a, b in zip(ev, ebit) ]
    df["per"] = [ _safe_div(a, b) for a, b in zip(mc, ni) ]
    df["pbr"] = [ _safe_div(a, b) for a, b in zip(mc, eq) ]
    df["pcr"] = [ _safe_div(a, b) for a, b in zip(mc, ocf) ]
    df["pfcr"] = [ _safe_div(a, b) for a, b in zip(mc, fcf) ]
    df["current_ratio"] = [ _safe_div(a, b) for a, b in zip(ca, cl) ]
    df["debt_ratio"] = [ _safe_div(a, b) for a, b in zip(td, eq) ]   # (총차입금/자기자본)

    # 청산가치(보수적 근사): 유동자산 - 부채총계
    df["liquidation_value"] = df.apply(
        lambda r: None if pd.isna(r["current_assets"]) or pd.isna(r["total_liabilities"])
        else float(r["current_assets"]) - float(r["total_liabilities"]),
        axis=1
    )

    # ROE, ROA, 자산회전률
    df["roe"] = [ _safe_div(a, b) for a, b in zip(ni, eq) ]
    df["roa"] = [ _safe_div(a, b) for a, b in zip(ni, ta) ]
    df["asset_turnover"] = [ _safe_div(a, b) for a, b in zip(rev, ta) ]

    # 배당성향: abs(dividends_paid)/net_income (dividends_paid는 보통 음수)
    def _payout(d, n):
        if d is None or n is None:
            return None
        try:
            if pd.isna(d) or pd.isna(n) or n == 0:
                return None
            return abs(float(d)) / float(n)
        except Exception:
            return None

    df["dividend_payout"] = [_payout(d, n) for d, n in zip(div_paid, ni)]

    # 성장률(연간=1칸, 분기=4칸 shift)
    df = df.sort_values(["symbol", "freq", "period_end"])
    lag = df["freq"].map(lambda x: 1 if x == "annual" else 4)

    # 그룹별 shift를 “freq에 따라 다르게” 적용하기 위해 freq별로 나눠서 계산
    def _growth(group: pd.DataFrame, col: str, n: int) -> pd.Series:
        prev = group[col].shift(n)
        return (group[col] - prev) / prev.replace({0: pd.NA})

    df["op_income_growth"] = None
    df["asset_growth"] = None
    df["debt_growth"] = None
    df["shares_growth"] = None

    for fq, n in [("annual", 1), ("quarterly", 4)]:
        m = df["freq"] == fq
        g = df[m].groupby("symbol", group_keys=False)

        df.loc[m, "op_income_growth"] = g.apply(lambda x: _growth(x, "operating_income", n))
        df.loc[m, "asset_growth"] = g.apply(lambda x: _growth(x, "total_assets", n))
        df.loc[m, "debt_growth"] = g.apply(lambda x: _growth(x, "total_debt", n))
        df.loc[m, "shares_growth"] = g.apply(lambda x: _growth(x, "shares_outstanding", n))

    # 이걸 해줘야지 소스점 처리가 된다.
    for c in ["price", "op_income_growth", "asset_growth", "debt_growth", "shares_growth"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # interest_coverage는 interest_expense가 없어서 NULL(추후 컬럼/수집 추가 추천)
    df["interest_coverage"] = None

    return df


def upsert_factors(
    symbols: Iterable[str] | None = None,
    freq: Freq | None = None,
    start: str | None = None,
    end: str | None = None,
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    log_dir: str = "logs",
) -> int:
    """
    nyse_fundamentals를 읽고 nyse_factors에 UPSERT.
    """
    logger = _setup_logger(log_dir)

    symbols = list(symbols) if symbols else None

    # 1) load fundamentals
    fund = load_fundamentals_mysql(
        symbols=symbols, freq=freq, start=start, end=end,
        host=host, user=user, password=password, port=port
    )
    if fund.empty:
        return 0

    # 2) attach price (period_end asof)
    # price는 “충분히 넓게” 로딩 후 merge_asof
    min_d = (fund["period_end"].min() - pd.Timedelta(days=14)).strftime("%Y-%m-%d")
    max_d = fund["period_end"].max().strftime("%Y-%m-%d")
    price = load_ohlcv_many_mysql(
        symbols=fund["symbol"].unique().tolist(),
        start=min_d, end=max_d,
        timeframe="1d",
        host=host, user=user, password=password, port=port,
    )
    
    fund2 = _attach_price_asof(fund, price)

    fund2 = add_market_cap(fund2)
    fund2 = add_enterprise_value(fund2)

    # 3) calc factors
    fac = calculate_factors(fund2)

    # 소수점 제외 처리
    fac = round_numeric_columns(
        fac,
        decimals=4,
        exclude={"market_cap", "shares_outstanding"},
    )

    # 4) UPSERT
    db = MySQLClient(host, user, password, port)
    inserted = 0
    try:
        db.use_db(DB_FUND)
        db.execute(FUNDAMENTAL_SCHEMAS["factors"])
        sync_table_schema(db, "nyse_factors", FUNDAMENTAL_SCHEMAS["factors"], DB_FUND)

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        fac["last_calculated_at"] = now

        # error_msg 구성: “팩터 계산에 필요한 분모가 없어서 NULL 된 핵심값” 정도만 기록
        def build_err(r):
            missing = []
            # 예시: PER에 필요한 net_income
            if pd.isna(r.get("net_income")):
                missing.append("net_income")
            if pd.isna(r.get("total_revenue")):
                missing.append("total_revenue")
            if pd.isna(r.get("total_assets")):
                missing.append("total_assets")
            if pd.isna(r.get("net_assets")):
                missing.append("net_assets")
            if pd.isna(r.get("enterprise_value")) and pd.isna(r.get("ev")):
                missing.append("enterprise_value")
            return None if not missing else "missing:" + ",".join(missing)

        fac["error_msg"] = fac.apply(build_err, axis=1)

        upsert_sql = """
        INSERT INTO nyse_factors (
          symbol, freq, period_end,
          price, market_cap, enterprise_value,
          psr, gpa, por, ev_ebit, per,
          liquidation_value, current_ratio, pbr, debt_ratio,
          pcr, pfcr, dividend_payout,
          op_income_growth, roe, roa, asset_turnover, interest_coverage,
          asset_growth, debt_growth, shares_growth,
          last_calculated_at, error_msg
        ) VALUES (
          %(symbol)s, %(freq)s, %(period_end)s,
          %(price)s, %(market_cap)s, %(enterprise_value)s,
          %(psr)s, %(gpa)s, %(por)s, %(ev_ebit)s, %(per)s,
          %(liquidation_value)s, %(current_ratio)s, %(pbr)s, %(debt_ratio)s,
          %(pcr)s, %(pfcr)s, %(dividend_payout)s,
          %(op_income_growth)s, %(roe)s, %(roa)s, %(asset_turnover)s, %(interest_coverage)s,
          %(asset_growth)s, %(debt_growth)s, %(shares_growth)s,
          %(last_calculated_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          price = VALUES(price),
          market_cap = VALUES(market_cap),
          enterprise_value = VALUES(enterprise_value),

          psr = VALUES(psr),
          gpa = VALUES(gpa),
          por = VALUES(por),
          ev_ebit = VALUES(ev_ebit),
          per = VALUES(per),

          liquidation_value = VALUES(liquidation_value),
          current_ratio = VALUES(current_ratio),
          pbr = VALUES(pbr),
          debt_ratio = VALUES(debt_ratio),

          pcr = VALUES(pcr),
          pfcr = VALUES(pfcr),
          dividend_payout = VALUES(dividend_payout),

          op_income_growth = VALUES(op_income_growth),
          roe = VALUES(roe),
          roa = VALUES(roa),
          asset_turnover = VALUES(asset_turnover),
          interest_coverage = VALUES(interest_coverage),

          asset_growth = VALUES(asset_growth),
          debt_growth = VALUES(debt_growth),
          shares_growth = VALUES(shares_growth),

          last_calculated_at = VALUES(last_calculated_at),
          error_msg = VALUES(error_msg)
        """

        # MySQL insert용 NaN -> None
        def to_none(x):
            try:
                if pd.isna(x):
                    return None
            except Exception:
                pass
            return x

        records = []
        for _, r in fac.iterrows():
            rec = r.to_dict()
            for k, v in list(rec.items()):
                rec[k] = to_none(v)
            # enterprise_value fill
            if rec.get("enterprise_value") is None:
                rec["enterprise_value"] = rec.get("ev")
            records.append(rec)

        if records:
            db.executemany(upsert_sql, records)
            inserted = len(records)

        # 추가 로그
        bad = fac[fac["error_msg"].notna()]
        for _, r in bad.iterrows():
            logger.warning(f'{r["symbol"]} | {r["freq"]} | {str(r["period_end"])[:10]} | {r["error_msg"]}')

        return inserted

    finally:
        db.close()