# finance/data/fundamentals.py
from __future__ import annotations

import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Literal, Optional
from time import perf_counter

import pandas as pd
import yfinance as yf

from .db.mysql import MySQLClient
from .db.schema import FUNDAMENTAL_SCHEMAS, sync_table_schema

DB_FUND = "finance_fundamental"
Freq = Literal["annual", "quarterly"]


def _setup_logger(log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(exist_ok=True)
    logger = logging.getLogger("finance.fundamentals")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        Path(log_dir) / f"fundamentals_errors_{datetime.utcnow().strftime('%Y%m%d')}.log",
        encoding="utf-8",
    )
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def _safe_getattr(obj, names: list[str]):
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            if v is not None:
                return v
    return None


def _stmt_to_period_df(stmt: pd.DataFrame) -> pd.DataFrame:
    """
    yfinance statement:
      index = 항목명, columns = 기간
    -> rows = 기간(period_end)
    """
    if stmt is None or not isinstance(stmt, pd.DataFrame) or stmt.empty:
        return pd.DataFrame()

    d = stmt.copy()
    d.columns = pd.to_datetime(d.columns, errors="coerce")
    d = d.loc[:, d.columns.notna()]
    if d.empty:
        return pd.DataFrame()

    out = d.T
    out.index.name = "period_end"
    return out.reset_index()


def _pick(row: pd.Series, candidates: list[str]) -> Optional[float]:
    for c in candidates:
        if c in row.index:
            v = row.get(c)
            if pd.notna(v):
                try:
                    return float(v)
                except Exception:
                    return None
    return None


def _calc_shares_outstanding(row: pd.Series) -> Optional[float]:
    """
    period별 shares_outstanding 근사치 계산.
    우선순위:
      1) Share Issued - Treasury Shares Number
      2) Ordinary Shares Number
      3) (fallback) 평균주식수류
    """
    treasury_shares = _pick(row, ["Treasury Shares Number"])
    shares_issued = _pick(row, ["Share Issued"])
    ordinary_shares = _pick(row, ["Ordinary Shares Number"])

    shares_out = None

    # 1) best: issued - treasury
    if shares_issued is not None and treasury_shares is not None:
        try:
            calc = float(shares_issued) - float(treasury_shares)
            if calc > 0:
                shares_out = calc
        except Exception:
            shares_out = None

    # 2) fallback: ordinary shares
    if shares_out is None and ordinary_shares is not None:
        try:
            calc = float(ordinary_shares)
            if calc > 0:
                shares_out = calc
        except Exception:
            shares_out = None

    # 3) extra fallbacks (가끔 존재)
    # Q. 왜 Diluted/Basic “Average Shares”는 뒤로 가야 하나? (3순위 계산)
    # Diluted Average Shares, Basic Average Shares는 보통:
    # 기간 평균(가중평균) 주식수야 (EPS 계산용)
    # 즉, period_end 시점의 “스냅샷”이 아니라 기간 동안의 평균치
    # 그래서 이걸 period_end 가격과 곱하면,
    # 엄밀히는 “말 시점의 시총”이 아니라 기간 평균 주식수 기준의 시총이 돼서 살짝 어긋남.
    if shares_out is None:
        shares_out = _pick(row, [
            "Diluted Average Shares",
            "Basic Average Shares",
            "Average Shares",
            "Diluted Shares Outstanding",
            "Ordinary Shares",
        ])

    # 4) sanitize
    if shares_out is not None:
        try:
            shares_out = float(shares_out)
            if shares_out <= 0:
                return None
            if shares_out > 1e12:  # 비현실적 상한(원하면 조정)
                return None
            return shares_out
        except Exception:
            return None

    return None


def _calc_gross_profit(row: pd.Series) -> Optional[float]:
    """
    gross_profit 우선순위:
      1) Gross Profit 컬럼이 있으면 그대로 사용
      2) Total Revenue - Cost Of Revenue
      3) Total Revenue - Cost Of Goods Sold (COGS)
      4) Total Revenue - Total Cost Of Revenue (가끔 이런 이름)
    실패하면 None 반환
    """
    # 1) direct
    gp = _pick(row, ["Gross Profit"])
    if gp is not None:
        return gp

    revenue = _pick(row, ["Total Revenue", "Operating Revenue"])
    if revenue is None:
        return None

    # 2~4) derived
    cost = _pick(row, [
        "Cost Of Revenue",
        "Cost of Revenue",
        "Cost Of Goods Sold",
        "Cost of Goods Sold",
        "Total Cost Of Revenue",
        "Total cost of revenue",
        "Cost Of Sales",
        "Cost of Sales",
    ])

    if cost is None:
        return None

    try:
        rev = float(revenue)
        cst = float(cost)
        # sanity
        if pd.isna(rev) or pd.isna(cst):
            return None
        return rev - cst
    except Exception:
        return None


def _calc_operating_income(row: pd.Series) -> Optional[float]:
    """
    operating_income 우선순위:
      1) Operating Income (직접 제공)
      2) Operating Income As Reported / Total Operating Income As Reported
      3) EBIT (Operating Income이 비어있는 케이스에서 대체로 유용)
      4) Gross Profit - Operating Expense(또는 Total Operating Expenses)
         (단, 둘 다 있을 때만; 없으면 None)

    주의:
      - EBIT는 D&A 포함/비포함 등 차이가 날 수 있어 완벽히 동일하진 않지만,
        Operating Income이 없는 경우 백테스트용 근사치로는 흔히 사용.
    """
    # 1~2) direct candidates
    op = _pick(row, [
        "Operating Income",
        "Operating Income As Reported",
        "Total Operating Income As Reported",
    ])
    if op is not None:
        return op

    # EBTI가 대체 가능하다고는 하지만 여기서는 이렇게 처리하지 않는다.
    # 3) fallback to EBIT
    # ebit = _pick(row, ["EBIT"])
    # if ebit is not None:
    #     return ebit

    # 4) derived: Gross Profit - Operating Expenses
    # gross profit도 계산 가능하게: _calc_gross_profit 사용
    gp = _calc_gross_profit(row)
    if gp is None:
        return None

    opex = _pick(row, [
        "Operating Expense",
        "Operating Expenses",
        "Total Operating Expenses",
        "Total Operating Expense",
    ])
    if opex is None:
        return None

    try:
        gp = float(gp)
        opex = float(opex)
        if pd.isna(gp) or pd.isna(opex):
            return None
        return gp - opex
    except Exception:
        return None


def _calc_ebit(row: pd.Series) -> Optional[float]:
    """
    ebit 우선순위(안전한 범위):
      1) EBIT (직접 제공)
      2) Operating Income (운영이익이 사실상 EBIT로 쓰이는 데이터가 많음)
      3) Pretax Income + Interest Expense (가능할 때만)
         - yfinance에서 Interest Expense가 없으면 계산 불가

    주의:
      - Pretax Income의 라벨이 다양함
      - Interest Expense는 보통 음수로 제공되는 경우가 있어 부호 처리 필요
        (대부분 'Interest Expense'가 비용(음수)로 들어오면 EBIT = Pretax - InterestExpense(=Pretax + abs))
    """
    # 1) direct
    ebit = _pick(row, ["EBIT"])
    if ebit is not None:
        return ebit

    # 2) fallback to operating income
    op = _calc_operating_income(row)
    if op is not None:
        return op

    # 3) derived: Pretax Income + Interest Expense
    pretax = _pick(row, [
        "Pretax Income",
        "Pre Tax Income",
        "Income Before Tax",
        "Earnings Before Tax",
        "Income Before Tax (EBT)",
    ])
    if pretax is None:
        return None

    interest = _pick(row, [
        "Interest Expense",
        "Interest Expense Non Operating",
        "Interest Expense, Net",
        "Net Interest Expense",
    ])
    if interest is None:
        return None

    try:
        p = float(pretax)
        i = float(interest)
        if pd.isna(p) or pd.isna(i):
            return None

        # interest가 비용으로 음수인 경우가 많음:
        # EBIT = EBT - InterestExpense
        # 예) EBT=100, InterestExpense=-10 -> EBIT=110
        return p - i
    except Exception:
        return None


def _extract_required_fields(symbol: str, freq: Freq, t: yf.Ticker) -> list[dict]:
    # statements
    if freq == "annual":
        income_raw = _safe_getattr(t, ["income_stmt", "financials"])
        bal_raw = _safe_getattr(t, ["balance_sheet"])
        cf_raw = _safe_getattr(t, ["cash_flow", "cashflow"])
    else:
        income_raw = _safe_getattr(t, ["quarterly_income_stmt", "quarterly_financials"])
        bal_raw = _safe_getattr(t, ["quarterly_balance_sheet"])
        cf_raw = _safe_getattr(t, ["quarterly_cash_flow", "quarterly_cashflow"])

    income = _stmt_to_period_df(income_raw)
    bal = _stmt_to_period_df(bal_raw)
    cf = _stmt_to_period_df(cf_raw)

    base = None
    for df in [income, bal, cf]:
        if df is None or df.empty:
            continue
        base = df if base is None else pd.merge(base, df, on="period_end", how="outer")

    if base is None or base.empty:
        return []

    # info / fast_info
    info = {}
    try:
        info = t.get_info()
    except Exception:
        info = getattr(t, "info", {}) or {}

    # market_cap = None
    # try:
    #     fi = getattr(t, "fast_info", None)
    #     if fi:
    #         market_cap = fi.get("marketCap")
    # except Exception:
    #     pass
    # if market_cap is None:
    #     market_cap = info.get("marketCap")

    # enterprise_value = info.get("enterpriseValue")
    # total_debt_info = info.get("totalDebt")
    # shares_out = info.get("sharesOutstanding")
    currency = info.get("financialCurrency") or info.get("currency")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    rows: list[dict] = []
    for _, r in base.iterrows():
        pe = pd.to_datetime(r["period_end"], errors="coerce")
        if pd.isna(pe):
            continue

        # Income
        total_revenue = _pick(r, ["Total Revenue", "Operating Revenue"])
        gross_profit = _calc_gross_profit(r)
        operating_income = _calc_operating_income(r)
        ebit = _calc_ebit(r)
        net_income = _pick(r, ["Net Income", "Net Income Common Stockholders"])

        # Balance
        total_assets = _pick(r, ["Total Assets"])
        current_assets = _pick(r, ["Current Assets"])
        total_liabilities = _pick(r, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
        current_liabilities = _pick(r, ["Current Liabilities"])
        total_debt = _pick(r, ["Total Debt"])
        net_assets = _pick(r, ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"])

        # Cashflow
        operating_cf = _pick(r, ["Operating Cash Flow"])
        free_cf = _pick(r, ["Free Cash Flow"])
        capex = _pick(r, ["Capital Expenditure"])
        if free_cf is None and operating_cf is not None and capex is not None:
            # yfinance capex는 보통 음수로 나오므로, OCF - (capex)면 “더 커질” 수 있음.
            # 일단 원형 유지: free_cf가 없는 경우에만 계산.
            free_cf = operating_cf - capex

        dividends_paid = _pick(r, ["Cash Dividends Paid", "Common Stock Dividend Paid"])
        shares_out = _calc_shares_outstanding(r)
        cash_and_equivalents = _pick(r, ["Cash And Cash Equivalents", "Cash And Cash Equivalents And Short Term Investments","Cash Cash Equivalents And Short Term Investments", "Cash And Short Term Investments", "Cash Financial"])

        rows.append({
            "symbol": symbol,
            "freq": freq,
            "period_end": pe.date(),
            "currency": currency,

            "total_revenue": total_revenue,
            "gross_profit": gross_profit,
            "operating_income": operating_income,
            "ebit": ebit,
            "net_income": net_income,

            "total_assets": total_assets,
            "current_assets": current_assets,
            "total_liabilities": total_liabilities,
            "current_liabilities": current_liabilities,
            "total_debt": total_debt,
            "net_assets": net_assets,

            "operating_cash_flow": operating_cf,
            "free_cash_flow": free_cf,
            "capital_expenditure": capex,
            "cash_and_equivalents": cash_and_equivalents,

            "dividends_paid": dividends_paid,
            "shares_outstanding": int(shares_out) if shares_out is not None else None,

            "source": "yfinance",
            "last_collected_at": now,
            "error_msg": None,
        })

    return rows


def upsert_fundamentals(
    symbols: Iterable[str],
    freq: Freq = "annual",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    chunk_size: int = 25,
    sleep: float = 0.6,
    max_retry: int = 3,
    log_dir: str = "logs",
) -> int:
    """
    symbols의 연간/분기 재무 스냅샷(필수항목)을 수집해서 nyse_fundamentals에 저장.
    """
    logger = _setup_logger(log_dir)

    symbols = [s for s in symbols if s and str(s).strip()]
    if not symbols:
        return 0

    total = len(symbols)
    processed = 0
    t0 = perf_counter()

    logger.info(f"start fundamentals | freq={freq} | total_symbols={total} | chunk_size={chunk_size}")


    db = MySQLClient(host, user, password, port)
    inserted = 0

    try:
        db.use_db(DB_FUND)
        db.execute(FUNDAMENTAL_SCHEMAS["fundamentals"])
        sync_table_schema(db, "nyse_fundamentals", FUNDAMENTAL_SCHEMAS["fundamentals"], DB_FUND)

        upsert_sql = """
        INSERT INTO nyse_fundamentals (
          symbol, freq, period_end,
          currency,
          total_revenue, gross_profit, operating_income, ebit, net_income,
          total_assets, current_assets, total_liabilities, current_liabilities,
          total_debt, net_assets,
          operating_cash_flow, free_cash_flow, capital_expenditure,
          cash_and_equivalents,
          dividends_paid, shares_outstanding,
          source, last_collected_at, error_msg
        ) VALUES (
          %(symbol)s, %(freq)s, %(period_end)s,
          %(currency)s,
          %(total_revenue)s, %(gross_profit)s, %(operating_income)s, %(ebit)s, %(net_income)s,
          %(total_assets)s, %(current_assets)s, %(total_liabilities)s, %(current_liabilities)s,
          %(total_debt)s, %(net_assets)s,
          %(operating_cash_flow)s, %(free_cash_flow)s, %(capital_expenditure)s,
          %(cash_and_equivalents)s,
          %(dividends_paid)s, %(shares_outstanding)s,
          %(source)s, %(last_collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          currency = VALUES(currency),
          total_revenue = VALUES(total_revenue),
          gross_profit = VALUES(gross_profit),
          operating_income = VALUES(operating_income),
          ebit = VALUES(ebit),
          net_income = VALUES(net_income),
          total_assets = VALUES(total_assets),
          current_assets = VALUES(current_assets),
          total_liabilities = VALUES(total_liabilities),
          current_liabilities = VALUES(current_liabilities),
          total_debt = VALUES(total_debt),
          net_assets = VALUES(net_assets),
          operating_cash_flow = VALUES(operating_cash_flow),
          free_cash_flow = VALUES(free_cash_flow),
          capital_expenditure = VALUES(capital_expenditure),
          cash_and_equivalents = VALUES(cash_and_equivalents),
          dividends_paid = VALUES(dividends_paid),
          shares_outstanding = VALUES(shares_outstanding),
          last_collected_at = VALUES(last_collected_at),
          error_msg = VALUES(error_msg)
        """

        def chunked(lst, size):
            for i in range(0, len(lst), size):
                yield lst[i:i + size]

        for batch in chunked(symbols, chunk_size):
            tickers = yf.Tickers(" ".join(batch)).tickers

            all_rows: list[dict] = []
            for sym in batch:
                t = tickers.get(sym) or yf.Ticker(sym)

                last_err = None
                for k in range(max_retry):
                    try:
                        rows = _extract_required_fields(sym, freq, t)
                        if not rows:
                            logger.warning(f"{sym} | {freq} | empty statements")
                        all_rows.extend(rows)
                        break
                    except Exception as e:
                        last_err = str(e)
                        time.sleep((2 ** k) + random.random() * 0.3)

                if last_err:
                    logger.error(f"{sym} | {freq} | {last_err}")

            if all_rows:
                db.executemany(upsert_sql, all_rows)
                inserted += len(all_rows)

            processed += len(batch)

            # ✅ 배치 1개 종료 로그
            elapsed = perf_counter() - t0
            pct = (processed / total) * 100 if total else 100
            logger.info(
                f"batch done | {processed}/{total} ({pct:.1f}%) | batch_symbols={len(batch)} | upsert_rows={len(all_rows)} | elapsed={elapsed/60:.1f}m"
            )

            time.sleep(sleep + random.random() * 0.3)

    finally:
        db.close()

    return inserted


