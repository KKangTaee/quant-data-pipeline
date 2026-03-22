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


def _pick_with_source(row: pd.Series, candidates: list[str]) -> tuple[Optional[float], Optional[str]]:
    for c in candidates:
        if c in row.index:
            v = row.get(c)
            if pd.notna(v):
                try:
                    return float(v), c
                except Exception:
                    return None, None
    return None, None


def _calc_shares_outstanding(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
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
    source = None

    # 1) best: issued - treasury
    if shares_issued is not None and treasury_shares is not None:
        try:
            calc = float(shares_issued) - float(treasury_shares)
            if calc > 0:
                shares_out = calc
                source = "share_issued_minus_treasury"
        except Exception:
            shares_out = None

    # 2) fallback: ordinary shares
    if shares_out is None and ordinary_shares is not None:
        try:
            calc = float(ordinary_shares)
            if calc > 0:
                shares_out = calc
                source = "ordinary_shares_number"
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
        if shares_out is not None:
            source = "average_shares_fallback"

    # 4) sanitize
    if shares_out is not None:
        try:
            shares_out = float(shares_out)
            if shares_out <= 0:
                return None, None
            if shares_out > 1e12:  # 비현실적 상한(원하면 조정)
                return None, None
            return shares_out, source
        except Exception:
            return None, None

    return None, None


def _calc_gross_profit(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
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
        return gp, "gross_profit_direct"

    revenue = _pick(row, ["Total Revenue", "Operating Revenue"])
    if revenue is None:
        return None, None

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
        return None, None

    try:
        rev = float(revenue)
        cst = float(cost)
        # sanity
        if pd.isna(rev) or pd.isna(cst):
            return None, None
        return rev - cst, "revenue_minus_cost"
    except Exception:
        return None, None


def _calc_operating_income(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
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
        return op, "operating_income_direct"

    # EBTI가 대체 가능하다고는 하지만 여기서는 이렇게 처리하지 않는다.
    # 3) fallback to EBIT
    # ebit = _pick(row, ["EBIT"])
    # if ebit is not None:
    #     return ebit

    # 4) derived: Gross Profit - Operating Expenses
    # gross profit도 계산 가능하게: _calc_gross_profit 사용
    gp, gp_source = _calc_gross_profit(row)
    if gp is None:
        return None, None

    opex = _pick(row, [
        "Operating Expense",
        "Operating Expenses",
        "Total Operating Expenses",
        "Total Operating Expense",
    ])
    if opex is None:
        return None, None

    try:
        gp = float(gp)
        opex = float(opex)
        if pd.isna(gp) or pd.isna(opex):
            return None, None
        if gp_source:
            return gp - opex, f"{gp_source}_minus_opex"
        return gp - opex, "gross_profit_minus_opex"
    except Exception:
        return None, None


def _calc_ebit(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
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
        return ebit, "ebit_direct"

    # 2) fallback to operating income
    op, op_source = _calc_operating_income(row)
    if op is not None:
        return op, op_source or "operating_income_fallback"

    # 3) derived: Pretax Income + Interest Expense
    pretax = _pick(row, [
        "Pretax Income",
        "Pre Tax Income",
        "Income Before Tax",
        "Earnings Before Tax",
        "Income Before Tax (EBT)",
    ])
    if pretax is None:
        return None, None

    interest = _pick(row, [
        "Interest Expense",
        "Interest Expense Non Operating",
        "Interest Expense, Net",
        "Net Interest Expense",
    ])
    if interest is None:
        return None, None

    try:
        p = float(pretax)
        i = float(interest)
        if pd.isna(p) or pd.isna(i):
            return None, None

        # interest가 비용으로 음수인 경우가 많음:
        # EBIT = EBT - InterestExpense
        # 예) EBT=100, InterestExpense=-10 -> EBIT=110
        return p - i, "pretax_minus_interest"
    except Exception:
        return None, None


def _calc_free_cash_flow(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
    free_cf = _pick(row, ["Free Cash Flow"])
    if free_cf is not None:
        return free_cf, "free_cash_flow_direct"

    operating_cf = _pick(row, ["Operating Cash Flow"])
    capex = _pick(row, ["Capital Expenditure"])
    if operating_cf is None or capex is None:
        return None, None

    try:
        return float(operating_cf) - float(capex), "operating_cf_minus_capex"
    except Exception:
        return None, None


def _calc_total_debt(row: pd.Series) -> tuple[Optional[float], Optional[str], Optional[float], Optional[float]]:
    total_debt = _pick(row, ["Total Debt"])
    if total_debt is not None:
        short_term = _pick(row, ["Long Term Debt Current", "Current Debt", "Short Long Term Debt", "Short Term Debt"])
        long_term = _pick(row, ["Long Term Debt Noncurrent", "Long Term Debt", "Long-term Debt"])
        return total_debt, "total_debt_direct", short_term, long_term

    short_term = _pick(row, ["Long Term Debt Current", "Current Debt", "Short Long Term Debt", "Short Term Debt"])
    long_term = _pick(row, ["Long Term Debt Noncurrent", "Long Term Debt", "Long-term Debt"])
    if short_term is None and long_term is None:
        return None, None, None, None

    total = 0.0
    if short_term is not None:
        total += float(short_term)
    if long_term is not None:
        total += float(long_term)
    return total, "current_plus_long_term_debt", short_term, long_term


def _calc_shareholders_equity(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
    eq = _pick(row, ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"])
    if eq is not None:
        return eq, "shareholders_equity_direct"

    total_assets = _pick(row, ["Total Assets"])
    total_liabilities = _pick(row, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
    if total_assets is None or total_liabilities is None:
        return None, None

    try:
        return float(total_assets) - float(total_liabilities), "assets_minus_liabilities"
    except Exception:
        return None, None


def _has_meaningful_fundamental_payload(row: dict) -> bool:
    core_fields = [
        "total_revenue",
        "gross_profit",
        "operating_income",
        "ebit",
        "net_income",
        "total_assets",
        "current_assets",
        "total_liabilities",
        "current_liabilities",
        "total_debt",
        "shareholders_equity",
        "operating_cash_flow",
        "free_cash_flow",
        "cash_and_equivalents",
        "shares_outstanding",
    ]
    return any(row.get(field) is not None for field in core_fields)


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
        gross_profit, gross_profit_source = _calc_gross_profit(r)
        operating_income, operating_income_source = _calc_operating_income(r)
        ebit, ebit_source = _calc_ebit(r)
        pretax_income = _pick(r, [
            "Pretax Income",
            "Pre Tax Income",
            "Income Before Tax",
            "Earnings Before Tax",
            "Income Before Tax (EBT)",
        ])
        interest_expense = _pick(r, [
            "Interest Expense",
            "Interest Expense Non Operating",
            "Interest Expense, Net",
            "Net Interest Expense",
        ])
        net_income = _pick(r, ["Net Income", "Net Income Common Stockholders"])

        # Balance
        total_assets = _pick(r, ["Total Assets"])
        current_assets = _pick(r, ["Current Assets"])
        inventory = _pick(r, ["Inventory", "Inventory Net", "Inventory, Net"])
        total_liabilities = _pick(r, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
        current_liabilities = _pick(r, ["Current Liabilities"])
        total_debt, total_debt_source, short_term_debt, long_term_debt = _calc_total_debt(r)
        shareholders_equity, shareholders_equity_source = _calc_shareholders_equity(r)
        net_assets = shareholders_equity

        # Cashflow
        operating_cf = _pick(r, ["Operating Cash Flow"])
        free_cf, free_cash_flow_source = _calc_free_cash_flow(r)
        capex = _pick(r, ["Capital Expenditure"])

        dividends_paid = _pick(r, ["Cash Dividends Paid", "Common Stock Dividend Paid"])
        shares_out, shares_out_source = _calc_shares_outstanding(r)
        cash_and_equivalents = _pick(r, ["Cash And Cash Equivalents", "Cash And Cash Equivalents And Short Term Investments","Cash Cash Equivalents And Short Term Investments", "Cash And Short Term Investments", "Cash Financial"])

        row_data = {
            "symbol": symbol,
            "freq": freq,
            "period_end": pe.date(),
            "currency": currency,

            "total_revenue": total_revenue,
            "gross_profit": gross_profit,
            "operating_income": operating_income,
            "ebit": ebit,
            "pretax_income": pretax_income,
            "interest_expense": interest_expense,
            "net_income": net_income,

            "total_assets": total_assets,
            "current_assets": current_assets,
            "inventory": inventory,
            "total_liabilities": total_liabilities,
            "current_liabilities": current_liabilities,
            "short_term_debt": short_term_debt,
            "long_term_debt": long_term_debt,
            "total_debt": total_debt,
            "shareholders_equity": shareholders_equity,
            "net_assets": net_assets,

            "operating_cash_flow": operating_cf,
            "free_cash_flow": free_cf,
            "capital_expenditure": capex,
            "cash_and_equivalents": cash_and_equivalents,

            "dividends_paid": dividends_paid,
            "shares_outstanding": int(shares_out) if shares_out is not None else None,

            "source_mode": "provider_summary",
            "timing_basis": "period_end",
            "gross_profit_source": gross_profit_source,
            "operating_income_source": operating_income_source,
            "ebit_source": ebit_source,
            "free_cash_flow_source": free_cash_flow_source,
            "shares_outstanding_source": shares_out_source,
            "total_debt_source": total_debt_source,
            "shareholders_equity_source": shareholders_equity_source,

            "source": "yfinance",
            "last_collected_at": now,
            "error_msg": None,
        }

        if _has_meaningful_fundamental_payload(row_data):
            rows.append(row_data)

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
    replace_symbol_history: bool = True,
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
          total_revenue, gross_profit, operating_income, ebit, pretax_income, interest_expense, net_income,
          total_assets, current_assets, inventory, total_liabilities, current_liabilities,
          short_term_debt, long_term_debt, total_debt, shareholders_equity, net_assets,
          operating_cash_flow, free_cash_flow, capital_expenditure,
          cash_and_equivalents,
          dividends_paid, shares_outstanding,
          source_mode, timing_basis,
          gross_profit_source, operating_income_source, ebit_source,
          free_cash_flow_source, shares_outstanding_source, total_debt_source, shareholders_equity_source,
          source, last_collected_at, error_msg
        ) VALUES (
          %(symbol)s, %(freq)s, %(period_end)s,
          %(currency)s,
          %(total_revenue)s, %(gross_profit)s, %(operating_income)s, %(ebit)s, %(pretax_income)s, %(interest_expense)s, %(net_income)s,
          %(total_assets)s, %(current_assets)s, %(inventory)s, %(total_liabilities)s, %(current_liabilities)s,
          %(short_term_debt)s, %(long_term_debt)s, %(total_debt)s, %(shareholders_equity)s, %(net_assets)s,
          %(operating_cash_flow)s, %(free_cash_flow)s, %(capital_expenditure)s,
          %(cash_and_equivalents)s,
          %(dividends_paid)s, %(shares_outstanding)s,
          %(source_mode)s, %(timing_basis)s,
          %(gross_profit_source)s, %(operating_income_source)s, %(ebit_source)s,
          %(free_cash_flow_source)s, %(shares_outstanding_source)s, %(total_debt_source)s, %(shareholders_equity_source)s,
          %(source)s, %(last_collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          currency = VALUES(currency),
          total_revenue = VALUES(total_revenue),
          gross_profit = VALUES(gross_profit),
          operating_income = VALUES(operating_income),
          ebit = VALUES(ebit),
          pretax_income = VALUES(pretax_income),
          interest_expense = VALUES(interest_expense),
          net_income = VALUES(net_income),
          total_assets = VALUES(total_assets),
          current_assets = VALUES(current_assets),
          inventory = VALUES(inventory),
          total_liabilities = VALUES(total_liabilities),
          current_liabilities = VALUES(current_liabilities),
          short_term_debt = VALUES(short_term_debt),
          long_term_debt = VALUES(long_term_debt),
          total_debt = VALUES(total_debt),
          shareholders_equity = VALUES(shareholders_equity),
          net_assets = VALUES(net_assets),
          operating_cash_flow = VALUES(operating_cash_flow),
          free_cash_flow = VALUES(free_cash_flow),
          capital_expenditure = VALUES(capital_expenditure),
          cash_and_equivalents = VALUES(cash_and_equivalents),
          dividends_paid = VALUES(dividends_paid),
          shares_outstanding = VALUES(shares_outstanding),
          source_mode = VALUES(source_mode),
          timing_basis = VALUES(timing_basis),
          gross_profit_source = VALUES(gross_profit_source),
          operating_income_source = VALUES(operating_income_source),
          ebit_source = VALUES(ebit_source),
          free_cash_flow_source = VALUES(free_cash_flow_source),
          shares_outstanding_source = VALUES(shares_outstanding_source),
          total_debt_source = VALUES(total_debt_source),
          shareholders_equity_source = VALUES(shareholders_equity_source),
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
                if replace_symbol_history:
                    placeholders = ",".join(["%s"] * len(batch))
                    delete_sql = f"DELETE FROM nyse_fundamentals WHERE freq=%s AND symbol IN ({placeholders})"
                    db.execute(delete_sql, [freq, *batch])

                normalized_rows = []
                for row in all_rows:
                    clean = {}
                    for key, value in row.items():
                        try:
                            clean[key] = None if pd.isna(value) else value
                        except Exception:
                            clean[key] = value
                    normalized_rows.append(clean)

                db.executemany(upsert_sql, normalized_rows)
                inserted += len(normalized_rows)

            processed += len(batch)

            # ✅ 배치 1개 종료 로그
            elapsed = perf_counter() - t0
            pct = (processed / total) * 100 if total else 100
            logger.info(
                f"batch done | {processed}/{total} ({pct:.1f}%) | batch_symbols={len(batch)} | upsert_rows={len(normalized_rows) if all_rows else 0} | elapsed={elapsed/60:.1f}m"
            )

            time.sleep(sleep + random.random() * 0.3)

    finally:
        db.close()

    return inserted
