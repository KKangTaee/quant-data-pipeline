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
        ocf = float(operating_cf)
        cap = float(capex)
        if pd.isna(ocf) or pd.isna(cap):
            return None, None
        if cap <= 0:
            return ocf + cap, "operating_cash_flow_plus_capex"
        return ocf - cap, "operating_cash_flow_minus_capex"
    except Exception:
        return None, None


def _pick_statement_value(row: pd.Series, candidates: list[str]) -> tuple[Optional[float], Optional[str]]:
    for concept in candidates:
        if concept not in row.index:
            continue
        value = row[concept]
        if pd.notna(value):
            try:
                return float(value), concept
            except Exception:
                return None, None
    return None, None


def _safe_div_scalar(a, b):
    if a is None or b is None:
        return None
    try:
        if pd.isna(a) or pd.isna(b) or float(b) == 0:
            return None
        return float(a) / float(b)
    except Exception:
        return None


def _sanitize_share_count(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    try:
        numeric = float(value)
    except Exception:
        return None
    if pd.isna(numeric) or numeric <= 0:
        return None
    if numeric > 1e13:
        return None
    return numeric


def _pick_statement_shares_outstanding(row: pd.Series) -> tuple[Optional[float], Optional[str]]:
    """
    statement ledger 기반 historical shares fallback.

    우선순위:
    1) point-in-time 성격이 더 강한 outstanding concepts
    2) 없으면 weighted-average shares fallback

    주의:
    - weighted-average shares는 period-end snapshot은 아니지만,
      strict annual valuation factor history를 너무 늦게 시작시키는 문제를
      줄이기 위한 fallback으로만 사용한다.
    """
    direct_candidates = [
        "dei:EntityCommonStockSharesOutstanding",
        "us-gaap:CommonStockSharesOutstanding",
        "us-gaap:CommonSharesOutstanding",
    ]
    weighted_average_candidates = [
        "us-gaap:WeightedAverageNumberOfSharesOutstandingBasic",
        "us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding",
    ]

    shares_outstanding, shares_source = _pick_statement_value(row, direct_candidates)
    shares_outstanding = _sanitize_share_count(shares_outstanding)
    if shares_outstanding is not None:
        return shares_outstanding, shares_source

    shares_outstanding, shares_source = _pick_statement_value(row, weighted_average_candidates)
    shares_outstanding = _sanitize_share_count(shares_outstanding)
    if shares_outstanding is not None and shares_source is not None:
        return shares_outstanding, f"fallback:{shares_source}"

    return None, None


def build_fundamentals_from_statement_snapshot(
    statement_snapshot: pd.DataFrame,
    *,
    as_of_date=None,
    freq: str = "annual",
) -> pd.DataFrame:
    """
    strict statement snapshot rows를 normalized fundamentals 단면으로 변환한다.

    용도:
    - statement-driven factor prototype
    - future statement-driven fundamentals/factors rebuild path

    현재는 sample/prototype 성격의 pure transform이며 DB write는 하지 않는다.
    """
    base_columns = [
        "symbol",
        "freq",
        "as_of_date",
        "statement_period_end",
        "total_revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "total_assets",
        "current_assets",
        "total_liabilities",
        "current_liabilities",
        "total_debt",
        "net_assets",
        "operating_cash_flow",
        "free_cash_flow",
        "capital_expenditure",
        "cash_and_equivalents",
        "interest_expense",
        "revenue_source",
        "gross_profit_source",
        "operating_income_source",
        "net_income_source",
        "net_assets_source",
        "total_debt_source",
        "operating_cash_flow_source",
        "free_cash_flow_source",
        "capital_expenditure_source",
        "cash_and_equivalents_source",
        "interest_expense_source",
    ]
    if statement_snapshot is None or statement_snapshot.empty:
        return pd.DataFrame(columns=base_columns)

    working = statement_snapshot.copy()
    working["symbol"] = working["symbol"].astype(str).str.strip().str.upper()
    if "unit" in working.columns and (working["unit"] == "USD").any():
        working = working[working["unit"] == "USD"].copy()
    if working.empty:
        return pd.DataFrame(columns=base_columns)

    pivot = working.pivot_table(
        index="symbol",
        columns="concept",
        values="value",
        aggfunc="last",
    )
    if pivot.empty:
        return pd.DataFrame(columns=base_columns)

    period_end_map = (
        working.groupby("symbol")["period_end"]
        .max()
        .to_dict()
    )
    normalized_as_of = pd.to_datetime(as_of_date).normalize() if as_of_date is not None else pd.NaT

    revenue_candidates = [
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:Revenues",
        "us-gaap:SalesRevenueNet",
    ]
    gross_profit_candidates = ["us-gaap:GrossProfit"]
    cost_candidates = [
        "us-gaap:CostOfRevenue",
        "us-gaap:CostOfGoodsSold",
        "us-gaap:CostOfSales",
    ]
    operating_income_candidates = ["us-gaap:OperatingIncomeLoss"]
    net_income_candidates = [
        "us-gaap:NetIncomeLoss",
        "us-gaap:ProfitLoss",
    ]
    assets_candidates = ["us-gaap:Assets"]
    current_assets_candidates = ["us-gaap:AssetsCurrent"]
    liabilities_candidates = ["us-gaap:Liabilities"]
    current_liabilities_candidates = ["us-gaap:LiabilitiesCurrent"]
    equity_candidates = [
        "us-gaap:StockholdersEquity",
        "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "us-gaap:StockholdersEquityIncludingPortionAttributableToRedeemableNoncontrollingInterest",
    ]
    cash_candidates = [
        "us-gaap:CashAndCashEquivalentsAtCarryingValue",
        "us-gaap:Cash",
        "us-gaap:CashCashEquivalentsAndShortTermInvestments",
    ]
    operating_cash_flow_candidates = ["us-gaap:NetCashProvidedByUsedInOperatingActivities"]
    capex_candidates = ["us-gaap:PaymentsToAcquirePropertyPlantAndEquipment"]
    interest_candidates = [
        "us-gaap:InterestExpense",
        "us-gaap:InterestExpenseAndOther",
        "us-gaap:InterestExpenseDebt",
    ]
    debt_component_candidates = [
        "us-gaap:LongTermDebt",
        "us-gaap:LongTermDebtCurrent",
        "us-gaap:ShortTermBorrowings",
        "us-gaap:ShortTermDebt",
    ]

    records: list[dict] = []
    for symbol, row in pivot.iterrows():
        total_revenue, revenue_source = _pick_statement_value(row, revenue_candidates)
        gross_profit, gross_profit_source = _pick_statement_value(row, gross_profit_candidates)
        cost_of_revenue, cost_source = _pick_statement_value(row, cost_candidates)
        operating_income, operating_income_source = _pick_statement_value(row, operating_income_candidates)
        net_income, net_income_source = _pick_statement_value(row, net_income_candidates)
        total_assets, total_assets_source = _pick_statement_value(row, assets_candidates)
        current_assets, current_assets_source = _pick_statement_value(row, current_assets_candidates)
        total_liabilities, total_liabilities_source = _pick_statement_value(row, liabilities_candidates)
        current_liabilities, current_liabilities_source = _pick_statement_value(row, current_liabilities_candidates)
        net_assets, net_assets_source = _pick_statement_value(row, equity_candidates)
        cash_and_equivalents, cash_source = _pick_statement_value(row, cash_candidates)
        operating_cash_flow, operating_cash_flow_source = _pick_statement_value(row, operating_cash_flow_candidates)
        capital_expenditure, capital_expenditure_source = _pick_statement_value(row, capex_candidates)
        interest_expense, interest_expense_source = _pick_statement_value(row, interest_candidates)

        debt_parts = []
        debt_sources = []
        for candidate in debt_component_candidates:
            debt_value, debt_source = _pick_statement_value(row, [candidate])
            if debt_value is None:
                continue
            debt_parts.append(debt_value)
            if debt_source is not None:
                debt_sources.append(debt_source)
        total_debt = float(sum(debt_parts)) if debt_parts else None

        if gross_profit is None and total_revenue is not None and cost_of_revenue is not None:
            gross_profit = float(total_revenue - cost_of_revenue)
            gross_profit_source = "derived:revenue_minus_cost_of_revenue"

        free_cash_flow = None
        free_cash_flow_source = None
        if operating_cash_flow is not None and capital_expenditure is not None:
            free_cash_flow = float(operating_cash_flow - capital_expenditure)
            free_cash_flow_source = "derived:operating_cash_flow_minus_capex"

        records.append(
            {
                "symbol": symbol,
                "freq": freq,
                "as_of_date": normalized_as_of,
                "statement_period_end": period_end_map.get(symbol),
                "total_revenue": total_revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "total_assets": total_assets,
                "current_assets": current_assets,
                "total_liabilities": total_liabilities,
                "current_liabilities": current_liabilities,
                "total_debt": total_debt,
                "net_assets": net_assets,
                "operating_cash_flow": operating_cash_flow,
                "free_cash_flow": free_cash_flow,
                "capital_expenditure": capital_expenditure,
                "cash_and_equivalents": cash_and_equivalents,
                "interest_expense": interest_expense,
                "revenue_source": revenue_source,
                "gross_profit_source": gross_profit_source or cost_source,
                "operating_income_source": operating_income_source,
                "net_income_source": net_income_source,
                "net_assets_source": net_assets_source,
                "total_assets_source": total_assets_source,
                "current_assets_source": current_assets_source,
                "total_liabilities_source": total_liabilities_source,
                "current_liabilities_source": current_liabilities_source,
                "total_debt_source": ",".join(debt_sources) if debt_sources else None,
                "operating_cash_flow_source": operating_cash_flow_source,
                "free_cash_flow_source": free_cash_flow_source,
                "capital_expenditure_source": capital_expenditure_source,
                "cash_and_equivalents_source": cash_source,
                "interest_expense_source": interest_expense_source,
            }
        )

    out = pd.DataFrame(records)
    if out.empty:
        return pd.DataFrame(columns=base_columns)

    # optional quality preview columns; downstream factor builder can reuse them directly
    out["gross_margin"] = [_safe_div_scalar(a, b) for a, b in zip(out["gross_profit"], out["total_revenue"])]
    out["operating_margin"] = [_safe_div_scalar(a, b) for a, b in zip(out["operating_income"], out["total_revenue"])]
    out["roe"] = [_safe_div_scalar(a, b) for a, b in zip(out["net_income"], out["net_assets"])]
    out["debt_ratio"] = [_safe_div_scalar(a, b) for a, b in zip(out["total_debt"], out["net_assets"])]
    return out.sort_values("symbol").reset_index(drop=True)


def _normalize_symbol_list(symbols: Iterable[str] | None) -> list[str]:
    if not symbols:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        value = str(symbol).strip().upper()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _load_statement_values_strict_history_mysql(
    symbols: Iterable[str] | None = None,
    *,
    freq: Freq = "annual",
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

        where = [
            "freq = %s",
            "accession_no IS NOT NULL",
            "accession_no <> ''",
            "unit IS NOT NULL",
            "unit <> ''",
            "available_at IS NOT NULL",
        ]
        params: list[object] = [freq]

        symbol_list = _normalize_symbol_list(symbols)
        if symbol_list:
            placeholders = ",".join(["%s"] * len(symbol_list))
            where.append(f"symbol IN ({placeholders})")
            params.extend(symbol_list)

        if start:
            where.append("period_end >= %s")
            params.append(pd.Timestamp(start).strftime("%Y-%m-%d"))
        if end:
            where.append("period_end <= %s")
            params.append(pd.Timestamp(end).strftime("%Y-%m-%d"))

        sql = f"""
        SELECT
          symbol,
          freq,
          period_end,
          report_date,
          statement_type,
          concept,
          value,
          unit,
          available_at,
          accession_no,
          form_type
        FROM nyse_financial_statement_values
        WHERE {" AND ".join(where)}
        ORDER BY
          symbol ASC,
          period_end ASC,
          statement_type ASC,
          concept ASC,
          unit ASC,
          available_at ASC,
          accession_no ASC
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()
    df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce")
    if "report_date" in df.columns:
        df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
    df["available_at"] = pd.to_datetime(df["available_at"], errors="coerce")
    df = df[df["period_end"].notna() & df["available_at"].notna()].copy()
    return df


def _load_broad_shares_fallback_mysql(
    symbols: Iterable[str] | None = None,
    *,
    freq: Freq = "annual",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
) -> pd.DataFrame:
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_FUND)
        where = ["freq = %s", "shares_outstanding IS NOT NULL"]
        params: list[object] = [freq]

        symbol_list = _normalize_symbol_list(symbols)
        if symbol_list:
            placeholders = ",".join(["%s"] * len(symbol_list))
            where.append(f"symbol IN ({placeholders})")
            params.extend(symbol_list)

        sql = f"""
        SELECT
          symbol,
          period_end,
          shares_outstanding,
          shares_outstanding_source
        FROM nyse_fundamentals
        WHERE {" AND ".join(where)}
        ORDER BY symbol ASC, period_end ASC
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()
    df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce")
    return df[df["period_end"].notna()].copy()


def build_fundamentals_history_from_statement_values(
    statement_values: pd.DataFrame,
    *,
    freq: Freq = "annual",
    broad_shares_fallback: pd.DataFrame | None = None,
    shares_tolerance_days: int = 15,
) -> pd.DataFrame:
    base_columns = [
        "symbol",
        "freq",
        "period_end",
        "currency",
        "total_revenue",
        "gross_profit",
        "operating_income",
        "ebit",
        "pretax_income",
        "interest_expense",
        "net_income",
        "total_assets",
        "current_assets",
        "inventory",
        "total_liabilities",
        "current_liabilities",
        "short_term_debt",
        "long_term_debt",
        "total_debt",
        "shareholders_equity",
        "net_assets",
        "operating_cash_flow",
        "free_cash_flow",
        "capital_expenditure",
        "cash_and_equivalents",
        "dividends_paid",
        "shares_outstanding",
        "latest_available_at",
        "latest_accession_no",
        "latest_form_type",
        "source_mode",
        "timing_basis",
        "gross_profit_source",
        "operating_income_source",
        "ebit_source",
        "free_cash_flow_source",
        "shares_outstanding_source",
        "total_debt_source",
        "shareholders_equity_source",
        "source",
        "last_collected_at",
        "error_msg",
    ]
    if statement_values is None or statement_values.empty:
        return pd.DataFrame(columns=base_columns)

    working = statement_values.copy()
    working["symbol"] = working["symbol"].astype(str).str.strip().str.upper()
    working["period_end"] = pd.to_datetime(working["period_end"], errors="coerce")
    working["available_at"] = pd.to_datetime(working["available_at"], errors="coerce")
    working = working[
        working["period_end"].notna()
        & working["available_at"].notna()
        & working["accession_no"].notna()
        & (working["accession_no"] != "")
        & working["unit"].notna()
        & (working["unit"] != "")
    ].copy()
    if working.empty:
        return pd.DataFrame(columns=base_columns)

    if "report_date" in working.columns:
        working["report_date"] = pd.to_datetime(working["report_date"], errors="coerce")
        report_anchor_map = (
            working[working["report_date"].notna()]
            .groupby("symbol", sort=False)["report_date"]
            .apply(lambda s: {pd.Timestamp(value).normalize() for value in s.dropna().tolist()})
            .to_dict()
        )
        if report_anchor_map:
            keep_mask = []
            for row in working.itertuples(index=False):
                anchors = report_anchor_map.get(getattr(row, "symbol"), set())
                period_end = getattr(row, "period_end")
                keep_mask.append(
                    not anchors or pd.Timestamp(period_end).normalize() in anchors
                )
            working = working[pd.Series(keep_mask, index=working.index)].copy()
            if working.empty:
                return pd.DataFrame(columns=base_columns)

    working = working.sort_values(
        ["symbol", "period_end", "statement_type", "concept", "unit", "available_at", "accession_no"],
        ascending=[True, True, True, True, True, True, True],
    )

    inventory_candidates = ["us-gaap:InventoryNet", "us-gaap:InventoryFinishedGoods", "us-gaap:InventoryGross"]
    pretax_income_candidates = ["us-gaap:IncomeBeforeTaxExpenseBenefit", "us-gaap:PretaxIncome"]
    short_term_debt_candidates = [
        "us-gaap:LongTermDebtCurrent",
        "us-gaap:ShortTermBorrowings",
        "us-gaap:ShortTermDebt",
    ]
    long_term_debt_candidates = ["us-gaap:LongTermDebt", "us-gaap:LongTermDebtNoncurrent"]
    dividends_paid_candidates = [
        "us-gaap:PaymentsOfDividends",
        "us-gaap:PaymentsOfOrdinaryDividends",
        "us-gaap:DividendsPaid",
    ]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    records: list[dict] = []

    for (symbol, period_end), group in working.groupby(["symbol", "period_end"], sort=False):
        ordered_group = group.sort_values(
            ["available_at", "accession_no", "statement_type", "concept", "unit"],
            ascending=[True, True, True, True, True],
        ).reset_index(drop=True)
        if ordered_group.empty:
            continue

        first_accession_no = ordered_group.iloc[0].get("accession_no")
        filing_snapshot = ordered_group[
            ordered_group["accession_no"] == first_accession_no
        ].copy()
        if filing_snapshot.empty:
            filing_snapshot = ordered_group.copy()

        fundamentals = build_fundamentals_from_statement_snapshot(
            filing_snapshot,
            as_of_date=filing_snapshot["available_at"].max(),
            freq=freq,
        )
        if fundamentals.empty:
            continue

        availability_point = filing_snapshot.sort_values(["available_at", "accession_no"]).iloc[-1]
        pivot = filing_snapshot.pivot_table(
            index="symbol",
            columns="concept",
            values="value",
            aggfunc="last",
        )
        pivot_row = pivot.iloc[0] if not pivot.empty else pd.Series(dtype="object")

        pretax_income, _ = _pick_statement_value(pivot_row, pretax_income_candidates)
        inventory, _ = _pick_statement_value(pivot_row, inventory_candidates)
        short_term_debt, _ = _pick_statement_value(pivot_row, short_term_debt_candidates)
        long_term_debt, _ = _pick_statement_value(pivot_row, long_term_debt_candidates)
        dividends_paid, _ = _pick_statement_value(pivot_row, dividends_paid_candidates)
        shares_outstanding, shares_source = _pick_statement_shares_outstanding(pivot_row)

        fund_row = fundamentals.iloc[0].to_dict()
        record = {
            "symbol": symbol,
            "freq": freq,
            "period_end": pd.Timestamp(period_end).date(),
            "currency": "USD",
            "total_revenue": fund_row.get("total_revenue"),
            "gross_profit": fund_row.get("gross_profit"),
            "operating_income": fund_row.get("operating_income"),
            "ebit": fund_row.get("operating_income"),
            "pretax_income": pretax_income,
            "interest_expense": fund_row.get("interest_expense"),
            "net_income": fund_row.get("net_income"),
            "total_assets": fund_row.get("total_assets"),
            "current_assets": fund_row.get("current_assets"),
            "inventory": inventory,
            "total_liabilities": fund_row.get("total_liabilities"),
            "current_liabilities": fund_row.get("current_liabilities"),
            "short_term_debt": short_term_debt,
            "long_term_debt": long_term_debt,
            "total_debt": fund_row.get("total_debt"),
            "shareholders_equity": fund_row.get("net_assets"),
            "net_assets": fund_row.get("net_assets"),
            "operating_cash_flow": fund_row.get("operating_cash_flow"),
            "free_cash_flow": fund_row.get("free_cash_flow"),
            "capital_expenditure": fund_row.get("capital_expenditure"),
            "cash_and_equivalents": fund_row.get("cash_and_equivalents"),
            "dividends_paid": dividends_paid,
            "shares_outstanding": int(shares_outstanding) if shares_outstanding is not None else None,
            "latest_available_at": availability_point.get("available_at"),
            "latest_accession_no": availability_point.get("accession_no"),
            "latest_form_type": availability_point.get("form_type"),
            "source_mode": "statement_shadow_first_available",
            "timing_basis": "first_available_for_period_end",
            "gross_profit_source": fund_row.get("gross_profit_source"),
            "operating_income_source": fund_row.get("operating_income_source"),
            "ebit_source": fund_row.get("operating_income_source"),
            "free_cash_flow_source": fund_row.get("free_cash_flow_source"),
            "shares_outstanding_source": shares_source,
            "total_debt_source": fund_row.get("total_debt_source"),
            "shareholders_equity_source": fund_row.get("net_assets_source"),
            "source": "statement_ledger",
            "last_collected_at": now,
            "error_msg": None,
        }
        if _has_meaningful_fundamental_payload(record):
            records.append(record)

    out = pd.DataFrame(records)
    if out.empty:
        return pd.DataFrame(columns=base_columns)

    if broad_shares_fallback is not None and not broad_shares_fallback.empty:
        fallback = broad_shares_fallback.copy()
        fallback["symbol"] = fallback["symbol"].astype(str).str.strip().str.upper()
        fallback["period_end"] = pd.to_datetime(fallback["period_end"], errors="coerce")
        fallback = fallback[
            fallback["period_end"].notna()
            & fallback["shares_outstanding"].notna()
        ].copy()
        if not fallback.empty:
            out["period_end"] = pd.to_datetime(out["period_end"], errors="coerce")
            for symbol, group in out.groupby("symbol", sort=False):
                fallback_group = fallback[fallback["symbol"] == symbol].copy()
                if fallback_group.empty:
                    continue
                fallback_group = fallback_group.sort_values("period_end")
                target_idx = group.index[group["shares_outstanding"].isna()]
                if len(target_idx) == 0:
                    continue

                left = out.loc[target_idx, ["period_end"]].sort_values("period_end")
                right = fallback_group[["period_end", "shares_outstanding", "shares_outstanding_source"]]
                merged = pd.merge_asof(
                    left,
                    right,
                    on="period_end",
                    direction="nearest",
                    tolerance=pd.Timedelta(days=shares_tolerance_days),
                )
                merged.index = left.index
                matched = merged["shares_outstanding"].notna()
                if matched.any():
                    matched_idx = merged.index[matched]
                    out.loc[matched_idx, "shares_outstanding"] = merged.loc[matched_idx, "shares_outstanding"]
                    out.loc[matched_idx, "shares_outstanding_source"] = merged.loc[matched_idx, "shares_outstanding_source"].apply(
                        lambda v: f"fallback:{v}" if pd.notna(v) else "fallback:broad_fundamentals_nearest_period_end"
                    )

    out["period_end"] = pd.to_datetime(out["period_end"], errors="coerce")
    out["latest_available_at"] = pd.to_datetime(out["latest_available_at"], errors="coerce")
    return out.sort_values(["symbol", "period_end"]).reset_index(drop=True)


def upsert_statement_fundamentals_shadow(
    symbols: Iterable[str] | None = None,
    *,
    freq: Freq = "annual",
    start: str | None = None,
    end: str | None = None,
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    log_dir: str = "logs",
    replace_symbol_history: bool = True,
) -> int:
    logger = _setup_logger(log_dir)
    symbol_list = _normalize_symbol_list(symbols)

    statement_values = _load_statement_values_strict_history_mysql(
        symbols=symbol_list,
        freq=freq,
        start=start,
        end=end,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    if statement_values.empty:
        logger.warning("statement fundamentals shadow | empty strict statement history")
        return 0

    broad_shares_fallback = _load_broad_shares_fallback_mysql(
        symbols=symbol_list or None,
        freq=freq,
        host=host,
        user=user,
        password=password,
        port=port,
    )

    fundamentals = build_fundamentals_history_from_statement_values(
        statement_values,
        freq=freq,
        broad_shares_fallback=broad_shares_fallback,
    )
    if fundamentals.empty:
        logger.warning("statement fundamentals shadow | no normalized rows built")
        return 0

    db = MySQLClient(host, user, password, port)
    inserted = 0
    try:
        db.use_db(DB_FUND)
        db.execute(FUNDAMENTAL_SCHEMAS["fundamentals_statement"])
        sync_table_schema(
            db,
            "nyse_fundamentals_statement",
            FUNDAMENTAL_SCHEMAS["fundamentals_statement"],
            DB_FUND,
        )

        upsert_sql = """
        INSERT INTO nyse_fundamentals_statement (
          symbol, freq, period_end,
          currency,
          total_revenue, gross_profit, operating_income, ebit, pretax_income, interest_expense, net_income,
          total_assets, current_assets, inventory, total_liabilities, current_liabilities,
          short_term_debt, long_term_debt, total_debt, shareholders_equity, net_assets,
          operating_cash_flow, free_cash_flow, capital_expenditure,
          cash_and_equivalents,
          dividends_paid, shares_outstanding,
          latest_available_at, latest_accession_no, latest_form_type,
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
          %(latest_available_at)s, %(latest_accession_no)s, %(latest_form_type)s,
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
          latest_available_at = VALUES(latest_available_at),
          latest_accession_no = VALUES(latest_accession_no),
          latest_form_type = VALUES(latest_form_type),
          source_mode = VALUES(source_mode),
          timing_basis = VALUES(timing_basis),
          gross_profit_source = VALUES(gross_profit_source),
          operating_income_source = VALUES(operating_income_source),
          ebit_source = VALUES(ebit_source),
          free_cash_flow_source = VALUES(free_cash_flow_source),
          shares_outstanding_source = VALUES(shares_outstanding_source),
          total_debt_source = VALUES(total_debt_source),
          shareholders_equity_source = VALUES(shareholders_equity_source),
          source = VALUES(source),
          last_collected_at = VALUES(last_collected_at),
          error_msg = VALUES(error_msg)
        """

        records = []
        for _, row in fundamentals.iterrows():
            rec = {}
            for key, value in row.to_dict().items():
                try:
                    rec[key] = None if pd.isna(value) else value
                except Exception:
                    rec[key] = value
            records.append(rec)

        if records:
            if replace_symbol_history:
                delete_symbols = sorted({record["symbol"] for record in records if record.get("symbol")})
                delete_params: list[object] = [freq]
                placeholders = ",".join(["%s"] * len(delete_symbols))
                delete_sql = f"DELETE FROM nyse_fundamentals_statement WHERE freq=%s AND symbol IN ({placeholders})"
                delete_params.extend(delete_symbols)
                db.execute(delete_sql, delete_params)

            db.executemany(upsert_sql, records)
            inserted = len(records)

        logger.info(
            "statement fundamentals shadow | freq=%s | symbols=%s | rows=%s",
            freq,
            ",".join(symbol_list) if symbol_list else "ALL",
            inserted,
        )
        return inserted
    finally:
        db.close()


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
