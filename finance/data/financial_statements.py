from __future__ import annotations

import logging
import random
import time
from datetime import datetime, date
from pathlib import Path
from typing import Iterable, Literal, Optional, List, Dict, Any
import re
import math

import pandas as pd
from edgar import Company, set_identity

from .db.mysql import MySQLClient
from .db.schema import FUNDAMENTAL_SCHEMAS, sync_table_schema


DB_FUND = "finance_fundamental"
Freq = Literal["annual", "quarterly"]


# NOTE:
#  - test1.ipynb 에서 사용하던 financial_term_kor_map 을 모듈로 옮겨와
#    재무제표 라벨을 한글로 함께 저장할 수 있도록 함.
financial_term_kor_map: Dict[str, str] = {
    "Total Revenue": "총매출 (회사 전체의 매출액)",
    "Cost of Revenue": "매출원가 (제품/서비스 판매에 소요된 비용)",
    "Gross Profit": "매출총이익 (총매출 - 매출원가)",
    "Operating expenses:": "영업비용 (운영에 소요된 비용)",
    "Research and Development Expense": "연구개발비 (신제품/서비스 개발비용)",
    "Selling and Marketing Expense": "판매 및 마케팅 비용",
    "General and Administrative Expense": "일반관리비 (경영, 행정 비용)",
    "Operating Expenses": "영업비용 전체",
    "Selling, General and Administrative Expense": "판매 관리비 (SG&A)",
    "Operating Income (Loss)": "영업이익 (손실)",
    "Other Nonoperating Income (Expense)": "기타 영업외 수익(비용)",
    "Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest": "계속영업이익 (법인세 차감 전, 비지배 지분 전)",
    "Income Tax Expense (Benefit)": "법인세 비용(혜택)",
    "Net Income (Loss) Attributable to Parent": "순이익 (지배기업 귀속)",
    "Earnings Per Share, Basic": "주당 순이익 (기본)",
    "Earnings Per Share, Diluted": "주당 순이익 (희석)",
    "Other income (expense):": "기타수익(비용)",
    "Nonoperating Income (Expense)": "영업외 수익(비용)",
    "Additional Financial Items": "추가 재무 항목",
    "Amortization of Intangible Assets": "무형자산상각비",
    "Common Stock, Dividends, Per Share, Declared": "보통주 1주당 배당금",
    "Depreciation, Depletion and Amortization, Nonproduction": "감가상각비(비생산활동 관련)",
    "Goodwill, Impairment Loss": "영업권 손상차손",
    "Interest Expense": "이자 비용",
    "Interest Expense, Debt": "부채 이자 비용",
    "Reclassification from AOCI, Current Period, before Tax, Attributable to Parent": "기타포괄손익누계액의 재분류 (지배기업 귀속)",
    "Revenue, Net (Deprecated 2018-01-31)": "순매출(구버전, 더 이상 사용안함)",
    "Business Combination, Acquisition Related Costs": "사업결합, 인수 관련 비용",
    "Cost of Goods and Service, Excluding Depreciation, Depletion, and Amortization": "감가상각/고갈/무형자산상각 제외 상품 및 서비스 원가",
    "Cost of Goods Sold (Deprecated 2018-01-31)": "매출원가(구버전, 더 이상 사용안함)",
    "Current Income Tax Expense (Benefit)": "당기 법인세 비용(혜택)",
    "Equity Securities without Readily Determinable Fair Value, Impairment Loss, Annual Amount": "공정가치 산정 불가 지분증권 손상차손 (연간)",
    "Income (Loss) from Continuing Operations, Net of Tax, Attributable to Parent": "계속영업이익(세후, 지배기업 귀속)",
    "Income (Loss) from Continuing Operations before Income Taxes, Domestic": "국내 계속영업이익 (법인세 이전)",
    "Income (Loss) from Continuing Operations, Per Basic Share": "계속영업 주당 순이익(기본)",
    "Income (Loss) from Continuing Operations, Per Diluted Share": "계속영업 주당 순이익(희석)",
    "Income (Loss) from Discontinued Operations, Net of Tax, Attributable to Parent": "중단영업이익(손실, 세후, 지배기업 귀속)",
    "Income (Loss) from Equity Method Investments": "지분법 투자이익(손실)",
    "Interest Income (Expense), Net": "이자수익(비용) 순액",
    "Marketing and Advertising Expense": "마케팅 및 광고 비용",
    "Operating Lease, Expense": "운영리스 비용",
    "Restructuring and Related Cost, Incurred Cost": "구조조정 및 관련 비용, 확정된 비용",
    "Restructuring Costs": "구조조정 비용",
    "Sales Revenue, Goods, Net (Deprecated 2018-01-31)": "상품 순매출 (구버전, 더 이상 사용안함)",
    "Net Income (Loss) Attributable to Noncontrolling Interest": "순이익(비지배지분 귀속)",
    "Investment Income, Interest": "이자성 투자수익",
    "Foreign Currency Transaction Gain (Loss), before Tax": "외화거래이익(손실, 세전)",
    "Foreign Currency Transaction Gain (Loss), Realized": "외화거래이익(손실, 실현)",
    "Gain (Loss) on Investments": "투자이익(손실)",
    "Net Income (Loss) Available to Common Stockholders, Basic": "보통주주 귀속 순이익(손실, 기본)",
    "Expenses": "비용",
    "Policyholder Benefits and Claims Incurred, Net": "보험계약자 지급 및 발생손해, 순액",
    "Deferred Policy Acquisition Costs, Amortization Expense": "이연 보험계약 인수비용 상각",
    "Benefits, Losses and Expenses": "보험급여, 손실 및 비용",
    "Other Cost and Expense, Operating": "기타 운영비용",
    "Capitalized Computer Software, Amortization": "자본화된 소프트웨어 상각",
    "Equity Securities, FV-NI, Realized Gain (Loss)": "공정가치-당기손익 지분증권, 실현손익",
    "Investment Income, Net": "순투자수익",
    "Liability for Unpaid Claims and Claims Adjustment Expense, Incurred Claims": "미지급 보험금 및 청구조정비용 발생손해",
    "Other Expenses": "기타 비용",
    "Preferred Stock Dividends, Income Statement Impact": "우선주 배당금, 손익계산서 영향",
    "Accounts Payable, Current": "유동 매입채무",
    "Accounts Receivable": "매출채권",
    "Accounts Receivable, after Allowance for Credit Loss": "대손충당금 차감 후 매출채권",
    "Accounts Receivable, after Allowance for Credit Loss, Current": "유동 대손충당금 차감 후 매출채권",
    "Accretion Expense": "적립비용",
    "Accrued Liabilities, Current": "유동 미지급 부채",
    "Accrued capital expenditures": "미지급 자본적 지출",
    "Accumulated Other Comprehensive (Income) Loss, Defined Benefit Plan, after Tax": "기타포괄손익누계액(확정급여형 퇴직급여제도/세후)",
    "Accumulated Other Comprehensive Income (Loss), Net of Tax": "누적 기타포괄손익(순, 세후)",
    "Additional Paid in Capital": "자본잉여금",
    "Additional Paid in Capital, Common Stock": "자본잉여금(보통주)",
    "Amortization": "감가상각",
    "Amortization of Debt Issuance Costs": "부채발행비용 상각",
    "Amortization of Debt Issuance Costs and Discounts": "부채발행비용 및 할인의 상각",
    "Asset Retirement Obligation, Accretion Expense": "자산철거의무 적립비용",
    "Assets": "자산",
    "Assets, Current": "유동자산",
    "Bank Owned Life Insurance Income": "은행 소유 생명보험 수익",
    "Cash and Cash Equivalents, at Carrying Value": "현금및현금성자산(장부가액)",
    "Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents": "현금·현금성자산·제한적 현금 및 현금성자산",
    "Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Period Increase (Decrease), Including Exchange Rate Effect": "기준기간 중 현금 등 증감(환율효과 포함)",
    "Cash, Cash Equivalents, and Short-term Investments": "현금∙현금성자산 및 단기투자자산",
    "Common Stock, Value, Issued": "발행 보통주 자본금",
    "Cost of Goods and Services Sold": "매출원가",
    "Cost of Property Repairs and Maintenance": "자산 수리 및 유지보수비",
    "Cost, Depreciation and Amortization": "원가, 감가상각 및 상각비",
    "Costs and Expenses": "비용 및 경비",
    "Debt Securities, Available-for-sale, Realized Gain (Loss)": "매도가능증권 실현이익(손실)",
    "Debt Securities, Realized Gain (Loss)": "채무증권 실현이익(손실)",
    "Debt and Equity Securities, Gain (Loss)": "채권 및 주식증권 이익(손실)",
    "Deferred Compensation Equity": "이연보상자본",
    "Deferred Income Tax Expense (Benefit)": "이연법인세 비용(혜택)",
    "Deferred Income Tax Liabilities, Net": "순이연법인세부채",
    "Deferred Revenue, Current": "유동이연수익",
    "Deferred Revenue, Noncurrent": "비유동이연수익",
    "Defined Benefit Plan, Net Periodic Benefit Cost (Credit), Gain (Loss) Due to Settlement": "확정급여형 퇴직연금정산 순주기적급여비용(수익), 정산에 의한 이익(손실)",
    "Defined Benefit Plan, Net Periodic Benefit Cost (Credit), Gain (Loss) Due to Settlement and Curtailment": "확정급여형 퇴직연금정산·감축에 의한 이익(손실)",
    "Depreciation": "감가상각",
    "Depreciation and amortization": "감가상각 및 상각",
    "Depreciation, Amortization and Accretion, Net": "감가상각 및 적립(순)",
    "Depreciation, Depletion and Amortization": "감가상각, 고갈 및 상각",
    "Depreciation, Nonproduction": "비생산 감가상각",
    "Derivative, Gain (Loss) on Derivative, Net": "파생상품 순이익(손실)",
    "Discontinued Operation, Gain (Loss) on Disposal of Discontinued Operation, Net of Tax": "중단사업 처분이익(손실)(세후)",
    "Discontinued Operation, Income (Loss) from Discontinued Operation During Phase-out Period, Net of Tax": "중단사업 폐지 기간 중 손익(세후)",
    "Disposal Group, Not Discontinued Operation, Gain (Loss) on Disposal": "비중단 매각집단 처분이익(손실)",
    "Dividends Payable, Current": "유동미지급배당금",
    "Dividends paid": "지급배당금",
    "Effect of Exchange Rate on Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents": "환율변동이 현금등에 미치는 영향",
    "Environmental Remediation Expense": "환경정화비용",
    "Equity Method Investment, Other than Temporary Impairment": "지분법적용투자 일시적이외의 손상",
    "Equity Securities, FV-NI, Gain (Loss)": "공정가치-순이익지정주식 이익(손실)",
    "Equity Securities, FV-NI, Unrealized Gain (Loss)": "공정가치-순이익지정주식 미실현이익(손실)",
    "Fair Value, Option, Changes in Fair Value, Gain (Loss)": "공정가치 옵션 평가손익",
    "Financing Receivable, Credit Loss, Expense (Reversal)": "금융채권 신용손실비용(환입)",
    "Foreign Currency Transaction Gain (Loss), Unrealized": "외화거래 미실현이익(손실)",
    "Fuel Costs": "연료비",
    "Gain (Loss) Related to Litigation Settlement": "소송합의 관련 이익(손실)",
    "Gain (Loss) on Derivative Instruments, Net, Pretax": "파생상품 순이익(손실)(법인세차감전)",
    "Gain (Loss) on Disposition of Assets": "자산처분이익(손실)",
    "Gain (Loss) on Disposition of Business": "사업처분이익(손실)",
    "Gain (Loss) on Disposition of Other Assets": "기타자산 처분이익(손실)",
    "Gain (Loss) on Disposition of Property Plant Equipment": "유형자산 처분이익(손실)",
    "Gain (Loss) on Disposition of Property Plant Equipment, Excluding Oil and Gas Property and Timber Property": "유형자산 처분이익(손실, 유전·임야제외)",
    "Gain (Loss) on Extinguishment of Debt": "부채소멸이익(손실)",
    "Gain (Loss) on Sale of Assets and Asset Impairment Charges": "자산매각이익(손실) 및 자산손상차손",
    "Gain (Loss) on Sale of Derivatives": "파생상품 매각이익(손실)",
    "Gain (Loss) on Sale of Investments": "투자자산 매각이익(손실)",
    "Gain (Loss) on Sale of Mortgage Loans": "모기지대출 매각이익(손실)",
    "Gain (Loss) on Sale of Properties": "재산 매각이익(손실)",
    "Gain (Loss) on Sales of Loans, Net": "대출금 매각순이익(손실)",
    "Gain (Loss) on Termination of Lease": "리스종료 이익(손실)",
    "Gains (Losses) on Sales of Investment Real Estate": "투자부동산 매각이익(손실)",
    "Goodwill": "영업권",
    "Goodwill and Intangible Asset Impairment": "영업권 및 무형자산 손상",
    "Gross Profit (Calculated)": "매출총이익(계산)",
    "Impairment of Intangible Assets (Excluding Goodwill)": "무형자산손상(영업권제외)",
    "Impairment of Intangible Assets, Finite-lived": "내용연수유한 무형자산 손상",
    "Impairment of Intangible Assets, Indefinite-lived (Excluding Goodwill)": "내용연수무한 무형자산손상(영업권제외)",
    "Income (Loss) Attributable to Parent, before Tax": "모회사 귀속세전이익(손실)",
    "Income (Loss) from Continuing Operations, Net of Tax, Including Portion Attributable to Noncontrolling Interest": "지속영업 이익(손실)(비지배지분포함, 세후)",
    "Income (Loss) from Discontinued Operations, Net of Tax, Including Portion Attributable to Noncontrolling Interest": "중단사업 이익(손실)(비지배지분포함, 세후)",
    "Income (Loss) from Equity Method Investments, Net of Dividends or Distributions": "지분법투자이익(손실)(배당차감후)",
    "Income Taxes Paid, Net": "법인세납부(순)",
    "Increase (Decrease) in Accounts Payable": "매입채무증가(감소)",
    "Increase (Decrease) in Accounts Receivable": "매출채권증가(감소)",
    "Increase (Decrease) in Inventories": "재고자산증가(감소)",
    "Intangible Assets, Net (Excluding Goodwill)": "무형자산 순액(영업권제외)",
    "Interest Income (Expense), Nonoperating, Net": "영업외이자수익(비용,순)",
    "Interest Income, Operating": "영업이자수익",
    "Interest Income, Other": "기타이자수익",
    "Interest Paid, Excluding Capitalized Interest, Operating Activities": "영업현금흐름 내 이자지급액(자본화이자제외)",
    "Interest and Other Income": "이자 및 기타수익",
    "InterestExpenseNonoperating": "영업외이자비용",
    "InterestExpenseOperating": "영업이자비용",
    "Inventory Write-down": "재고자산감액",
    "Inventory, Net": "순재고자산",
    "Labor and Related Expense": "인건비 및 관련비용",
    "Liabilities": "부채",
    "Liabilities and Equity": "부채 및 자기자본",
    "Liabilities, Current": "유동부채",
    "Liabilities, Noncurrent": "비유동부채",
    "Long Term Debt": "장기부채",
    "Long-term Debt": "장기부채",
    "Long-term Debt, Current Maturities": "유동성장기부채",
    "Long-term Debt, Excluding Current Maturities": "비유동장기부채",
    "Management Fee Expense": "운용수수료비",
    "Marketable Securities, Realized Gain (Loss), Excluding Other-than-temporary Impairment Loss": "시장성유가증권실현이익(손실)(일시적손상제외)",
    "Marketable Securities, Unrealized Gain (Loss)": "시장성유가증권미실현이익(손실)",
    "Net Cash Provided by (Used in) Financing Activities": "재무활동 현금흐름",
    "Net Cash Provided by (Used in) Investing Activities": "투자활동 현금흐름",
    "Net Cash Provided by (Used in) Operating Activities": "영업활동 현금흐름",
    "Net Income (Loss) from Continuing Operations Available to Common Shareholders, Basic": "지속영업 보통주주귀속순이익(기본)",
    "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest": "순이익(손실)(비지배지분 포함)",
    "Net Investment Income": "순투자이익",
    "Net Periodic Defined Benefits Expense (Reversal of Expense), Excluding Service Cost Component": "확정급여 정기순비용(환입, 서비스비용제외)",
    "Noncash Merger Related Costs": "비현금합병관련비용",
    "Noncontrolling Interest in Net Income (Loss) Operating Partnerships, Redeemable": "상환가능운영파트너십 비지배지분순이익(손실)",
    "Operating Costs and Expenses": "영업비용 및 경비",
    "Operating Lease, Impairment Loss": "운용리스 손상차손",
    "Operating Lease, Lease Income": "운용리스 수익",
    "Operating Lease, Liability, Current": "운용리스 유동부채",
    "Operating Lease, Liability, Noncurrent": "운용리스 비유동부채",
    "Operating Lease, Right-of-Use Asset": "운용리스사용권자산",
    "Other Assets, Noncurrent": "기타비유동자산",
    "Other Cost of Operating Revenue": "기타영업비용",
    "Other Depreciation and Amortization": "기타감가상각",
    "Other General and Administrative Expense": "기타일반관리비",
    "Other Income": "기타수익",
    "Other Liabilities, Noncurrent": "기타비유동부채",
    "Other Operating Income (Expense), Net": "기타영업수익(비용,순)",
    "Parent Company": "모회사",
    "Partners' Capital": "파트너스자본",
    "Payment, Tax Withholding, Share-based Payment Arrangement": "세금원천징수, 주식보상지급",
    "Payments for (Proceeds from) Other Investing Activities": "기타투자활동으로 인한 현금유출(유입)",
    "Payments for Repurchase of Common Stock": "보통주 자사주매입지급",
    "Payments of Dividends": "배당금지급",
    "Payments of Financing Costs": "재무비용지급",
    "Payments of Ordinary Dividends, Common Stock": "보통주 일반배당금 지급",
    "Payments to Acquire Businesses, Net of Cash Acquired": "인수대금 순유출(취득현금차감후)",
    "Payments to Acquire Investments": "투자자산취득지급금",
    "Payments to Acquire Property, Plant, and Equipment": "유형자산 취득지급",
    "Preferred Stock Dividends and Other Adjustments": "우선주배당 및 기타조정",
    "Preferred Stock, Value, Issued": "발행우선주 자본금",
    "Prepaid Expense and Other Assets, Current": "선급비용 및 기타유동자산",
    "Proceeds from (Payments for) Other Financing Activities": "타재무활동현금유입(유출)",
    "Proceeds from Contributed Capital": "추가납입자본금유입",
    "Proceeds from Contributions from Affiliates": "계열회사납입금유입",
    "Proceeds from Issuance of Common Stock": "보통주발행대금유입",
    "Proceeds from Issuance of Long-term Debt": "장기부채발행대금유입",
    "Proceeds from Maturities, Prepayments and Calls of Debt Securities, Available-for-sale": "만기도래·상환·콜옵션 행사용 매도가능증권대금유입",
    "Proceeds from Noncontrolling Interests": "비지배지분 자금유입",
    "Proceeds from Stock Options Exercised": "스톡옵션 행사대금유입",
    "Property, Plant and Equipment, Net": "유형자산(순)",
    "Property, plant and equipment acquisitions funded by liabilities": "부채로 조달한 유형자산 취득",
    "Provision for Loan, Lease, and Other Losses": "대출·리스 등 손실충당금",
    "Purchases of property and equipment, accrued but unpaid": "미지급 유형자산 취득금액",
    "Real Estate Tax Expense": "부동산 세금비용",
    "Realized Investment Gains (Losses)": "실현투자이익(손실)",
    "Repayments of Long-term Debt": "장기부채 상환액",
    "Restricted Cash and Cash Equivalents": "제한성 현금및현금성자산",
    "Restricted Cash and Investments, Current": "제한성 유동현금 및 투자자산",
    "Restructuring Costs and Asset Impairment Charges": "구조조정비 및 자산손상차손",
    "Retained Earnings (Accumulated Deficit)": "이익잉여금(결손금)",
    "Revenue from Contract with Customer, Including Assessed Tax": "고객계약매출(세금포함)",
    "Share-based Payment Arrangement, Expense": "주식기반보상 비용",
    "Share-based Payment Arrangement, Noncash Expense": "주식기반보상 비현금비용",
    "Short-term Investments": "단기투자자산",
    "Stockholders' Equity Attributable to Noncontrolling Interest": "비지배지분",
    "Stockholders' Equity Attributable to Parent": "지배기업지분",
    "Total Assets": "총자산",
    "Total Liabilities": "총부채",
    "Total interest expense": "총이자비용",
    "Treasury Stock, Common, Value": "자기주식(보통주)",
    "Undistributed Earnings (Loss) Allocated to Participating Securities, Basic": "참여증권귀속미분배이익(손실,기본)",
    "Unrealized Gain (Loss) on Derivatives": "파생상품 미실현이익(손실)",
    "Unrealized Gain (Loss) on Investments": "투자자산 미실현이익(손실)",
}


def _setup_logger(log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(exist_ok=True)
    logger = logging.getLogger("finance.financial_statements")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        Path(log_dir) / f"financial_statements_errors_{datetime.utcnow().strftime('%Y%m%d')}.log",
        encoding="utf-8",
    )
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def _chunked(lst: List[str], size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def get_fundamental(symbol: str, periods: int = 4, period: str = "annual") -> pd.DataFrame:
    """
    SEC EDGAR 기반 재무제표(손익/재무상태/현금흐름)를 하나의 DataFrame으로 반환.

    반환 DF 컬럼 예시:
      symbol, statement_type, label, label_kr, (confidence?), FY 2025, FY 2024, ...
    또는 분기:
      symbol, statement_type, label, label_kr, Q4 2025, Q3 2025, ...
    """
    c = Company(symbol)
    dfs: List[pd.DataFrame] = []

    def _prepare(df: Optional[pd.DataFrame], statement_type: str):
        if df is None:
            return

        d = df.reset_index()
        d = d.drop(
            columns=["concept", "depth", "is_abstract", "is_total", "section"],
            errors="ignore",
        )

        # period 컬럼 탐지
        if period == "quarterly":
            # 'Q4 2025' / 'Q1 2024' 등
            period_cols = d.filter(regex=r"^Q[1-4]\s?\d{4}$").columns
        else:
            # 'FY2024' / 'FY 2023' / 'FY 2025' 등
            period_cols = d.filter(regex=r"^FY\s?\d{4}$|^FY\d{4}$|^FY").columns

        if len(period_cols) > 0:
            d = d.dropna(subset=period_cols, how="all")

        if "label" not in d.columns:
            print(f"[WARN] {symbol} - {statement_type} 에 'label' 컬럼 없음. 스킵.")
            return

        d["label_kr"] = d["label"].map(financial_term_kor_map)
        d["symbol"] = symbol
        d["statement_type"] = statement_type

        # 컬럼 순서 정리
        col_symbol = d.pop("symbol")
        d.insert(0, "symbol", col_symbol)
        col_statement_type = d.pop("statement_type")
        d.insert(1, "statement_type", col_statement_type)
        col_label_kr = d.pop("label_kr")
        i = d.columns.get_loc("label") + 1
        d.insert(i, "label_kr", col_label_kr)

        dfs.append(d)

    _prepare(c.income_statement(periods=periods, period=period, as_dataframe=True), "income_statement")
    _prepare(c.balance_sheet(periods=periods, period=period, as_dataframe=True), "balance_sheet")
    _prepare(c.cashflow_statement(periods=periods, period=period, as_dataframe=True), "cashflow")

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)

def _infer_as_of_from_df(df: pd.DataFrame) -> date:
    meta_cols = {"symbol", "statement_type", "label", "label_kr", "confidence"}
    dates: List[date] = []
    for c in df.columns:
        if c in meta_cols:
            continue
        d = _parse_period_end(c)
        if d is not None:
            dates.append(d)
    return max(dates) if dates else date.today()


def _infer_latest_period_meta(df: pd.DataFrame) -> Dict[str, Any]:
    meta_cols = {"symbol", "statement_type", "label", "label_kr", "confidence"}
    metas: List[Dict[str, Any]] = []

    for c in df.columns:
        if c in meta_cols:
            continue
        m = _parse_period_meta(c)
        if m["period_end"] is not None:
            metas.append(m)

    if not metas:
        today = date.today()
        return {
            "period_end": today,
            "period_label": today.isoformat(),
            "period_type": "DATE",
            "fiscal_year": today.year,
            "fiscal_quarter": None,
        }

    # 가장 최신 period_end를 기준으로 대표 메타 선택
    metas.sort(key=lambda x: x["period_end"])
    return metas[-1]


_FY_RE = re.compile(r"^FY\s*(\d{4})$", re.IGNORECASE)
_Q_RE  = re.compile(r"^Q([1-4])\s*(\d{4})$", re.IGNORECASE)

def _parse_period_meta(col_name: str) -> Dict[str, Any]:
    """
    컬럼명에서 period 메타를 추출.
    예:
      - FY 2025 -> period_end=2025-12-31, period_label='FY 2025', period_type='FY'
      - Q4 2025 -> period_end=2025-12-31, period_label='Q4 2025', period_type='Q'
    """
    s = str(col_name).strip()

    m = _FY_RE.match(s)
    if m:
        y = int(m.group(1))
        return {
            "period_end": date(y, 12, 31),
            "period_label": f"FY {y}",
            "period_type": "FY",
            "fiscal_year": y,
            "fiscal_quarter": None,
        }

    m = _Q_RE.match(s)
    if m:
        q = int(m.group(1))
        y = int(m.group(2))
        q_end = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}[q]
        return {
            "period_end": date(y, q_end[0], q_end[1]),
            "period_label": f"Q{q} {y}",
            "period_type": "Q",
            "fiscal_year": y,
            "fiscal_quarter": q,
        }

    dt = pd.to_datetime(s, errors="coerce")
    if pd.notna(dt):
        d = dt.date()
        return {
            "period_end": d,
            "period_label": d.isoformat(),
            "period_type": "DATE",
            "fiscal_year": d.year,
            "fiscal_quarter": None,
        }

    return {
        "period_end": None,
        "period_label": None,
        "period_type": None,
        "fiscal_year": None,
        "fiscal_quarter": None,
    }


def _parse_period_end(col_name: str) -> date | None:
    """
    'FY 2025', 'FY2025', 'Q4 2025' 같은 컬럼명을 period_end(date)로 변환.
    """
    return _parse_period_meta(col_name)["period_end"]


def _coerce_date(v) -> date | None:
    if v is None:
        return None
    try:
        dt = pd.to_datetime(v, errors="coerce")
    except Exception:
        return None
    if pd.isna(dt):
        return None
    return dt.date()


def _coerce_datetime(v):
    if v is None:
        return None
    try:
        dt = pd.to_datetime(v, errors="coerce")
    except Exception:
        return None
    if pd.isna(dt):
        return None
    return dt.to_pydatetime()


def _extract_pit_fields(row: pd.Series) -> Dict[str, Any]:
    """
    EDGAR/원천 DF에 filing/acceptance 시점 정보가 있는 경우 추출.
    없으면 None으로 저장.
    """
    filing_date = None
    accepted_at = None

    filing_candidates = ["filed", "filing_date", "filed_at", "report_date"]
    accepted_candidates = ["accepted", "accepted_at", "accepted_datetime", "acceptance_datetime"]

    for k in filing_candidates:
        if k in row.index:
            filing_date = _coerce_date(row.get(k))
            if filing_date is not None:
                break

    for k in accepted_candidates:
        if k in row.index:
            accepted_at = _coerce_datetime(row.get(k))
            if accepted_at is not None:
                break

    return {
        "filing_date": filing_date,
        "accepted_at": accepted_at,
    }


def _none_if_nan(v):
    """pandas/numpy NaN 포함 결측을 None으로 변환 (MySQL NULL 용)"""
    return None if pd.isna(v) else v


def _none_if_not_finite_number(x):
    """float 변환 후 nan/inf면 None 반환"""
    try:
        fx = float(x)
    except Exception:
        return None
    if not math.isfinite(fx):   # nan, inf, -inf 방지
        return None
    return fx


def _iter_value_rows(df: pd.DataFrame, freq: Freq) -> List[Dict[str, Any]]:
    """
    wide DF(FY/Q 컬럼 다수) -> values 테이블에 넣을 long rows로 변환
    """
    if df is None or df.empty:
        return []

    meta_cols = {"symbol", "statement_type", "label", "label_kr", "confidence"}
    value_cols = [c for c in df.columns if c not in meta_cols]

    rows: List[Dict[str, Any]] = []
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for _, r in df.iterrows():
        symbol = r.get("symbol")
        stype = r.get("statement_type")
        label = r.get("label")

        if not symbol or not stype or not label:
            continue

        for col in value_cols:
            v = r.get(col)
            if pd.isna(v):
                continue

            meta = _parse_period_meta(col)
            period_end = meta["period_end"]
            if period_end is None:
                continue

            fv = _none_if_not_finite_number(v)
            if fv is None:
                continue

            pit = _extract_pit_fields(r)

            rows.append({
                "symbol": symbol,
                "freq": freq,
                "period_end": period_end,
                "period_label": meta["period_label"],
                "period_type": meta["period_type"],
                "fiscal_year": meta["fiscal_year"],
                "fiscal_quarter": meta["fiscal_quarter"],
                "statement_type": stype,
                "label": label,
                "value": fv,
                "filing_date": pit["filing_date"],
                "accepted_at": pit["accepted_at"],
                "source": "edgar",
                "last_collected_at": now,
                "error_msg": None,
            })

    return rows


def _iter_label_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    labels 테이블(심볼별 label 메타)에 넣을 rows 생성
    - symbol 포함 (symbol마다 condition/priority 등이 달라질 수 있으므로)
    - condition/priority/enabled 같은 운영 컬럼은 여기서 세팅하지 않고 DB에 맡김
      (수집이 운영 설정을 덮어쓰지 않도록 upsert에서도 update 제외)
    """
    if df is None or df.empty:
        return []

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    as_of_meta = _infer_latest_period_meta(df)
    as_of = as_of_meta["period_end"]

    cols = [c for c in ["symbol", "label", "label_kr", "statement_type", "confidence"] if c in df.columns]
    x = df[cols].drop_duplicates(subset=["symbol", "label"]).copy()

    rows: List[Dict[str, Any]] = []
    for _, r in x.iterrows():
        symbol = r.get("symbol")
        label = r.get("label")
        if not symbol or not label:
            continue

        conf = None
        if "confidence" in x.columns:
            conf = _none_if_not_finite_number(r.get("confidence"))

        rows.append({
            "symbol": symbol,
            "label": label,
            "as_of": as_of,
            "as_of_label": as_of_meta["period_label"] or (as_of.isoformat() if isinstance(as_of, date) else None),
            "as_of_period_type": as_of_meta["period_type"],
            "as_of_fiscal_year": as_of_meta["fiscal_year"],
            "as_of_fiscal_quarter": as_of_meta["fiscal_quarter"],
            "label_kr": _none_if_nan(r.get("label_kr")),
            "statement_type": _none_if_nan(r.get("statement_type")),
            "confidence": conf,
            "last_updated_at": now,
        })
    return rows





def upsert_financial_statements(
    symbols: Iterable[str],
    freq: Freq = "annual",
    periods: int = 4,
    period: str = "annual",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    chunk_size: int = 20,
    sleep: float = 0.8,
    max_retry: int = 3,
    log_dir: str = "logs",
) -> Dict[str, Any]:
    """
    get_fundamental(symbol, periods, period)로 재무제표를 수집한 후,
    아래 2개 테이블에 업서트:

    1) nyse_financial_statement_labels  (symbol, label 기준)
    2) nyse_financial_statement_values  (symbol, freq, period_end, statement_type, label 기준)

    - symbols 를 chunk_size 로 나눠 배치 처리
    - 배치 간 sleep + 지터
    - 심볼 단위 max_retry + 지수 backoff
    - 실패 심볼은 로그 파일/반환값 failed_symbols 로 관리
    """
    logger = _setup_logger(log_dir)

    symbols = [s for s in symbols if s and str(s).strip()]
    if not symbols:
        return {"inserted_values": 0, "upserted_labels": 0, "failed_symbols": []}

    try:
        set_identity("honeypipeline@gmail.com")
    except Exception:
        pass

    db = MySQLClient(host, user, password, port)
    inserted_values = 0
    upserted_labels = 0
    failed: List[str] = []

    try:
        db.use_db(DB_FUND)

        # --- (1) labels 테이블 준비 ---
        db.execute(FUNDAMENTAL_SCHEMAS["financial_statement_labels"])
        sync_table_schema(
            db,
            "nyse_financial_statement_labels",
            FUNDAMENTAL_SCHEMAS["financial_statement_labels"],
            DB_FUND,
        )

        upsert_labels_sql = """
        INSERT INTO nyse_financial_statement_labels (
            symbol, label, as_of, as_of_label, as_of_period_type, as_of_fiscal_year, as_of_fiscal_quarter,
            label_kr, statement_type, confidence, last_updated_at
        ) VALUES (
        %(symbol)s, %(label)s, %(as_of)s, %(as_of_label)s, %(as_of_period_type)s, %(as_of_fiscal_year)s, %(as_of_fiscal_quarter)s,
        %(label_kr)s, %(statement_type)s, %(confidence)s, %(last_updated_at)s
        )
            ON DUPLICATE KEY UPDATE
            as_of_label = VALUES(as_of_label),
            as_of_period_type = VALUES(as_of_period_type),
            as_of_fiscal_year = VALUES(as_of_fiscal_year),
            as_of_fiscal_quarter = VALUES(as_of_fiscal_quarter),
            label_kr = VALUES(label_kr),
            statement_type = VALUES(statement_type),
            confidence = VALUES(confidence),
            last_updated_at = VALUES(last_updated_at)
        """

        # --- (2) values 테이블 준비 ---
        db.execute(FUNDAMENTAL_SCHEMAS["financial_statement_values"])
        sync_table_schema(
            db,
            "nyse_financial_statement_values",
            FUNDAMENTAL_SCHEMAS["financial_statement_values"],
            DB_FUND,
        )

        upsert_values_sql = """
        INSERT INTO nyse_financial_statement_values (
          symbol, freq, period_end,
          period_label, period_type, fiscal_year, fiscal_quarter,
          statement_type, label,
          value,
          filing_date, accepted_at,
          source, last_collected_at, error_msg
        ) VALUES (
          %(symbol)s, %(freq)s, %(period_end)s,
          %(period_label)s, %(period_type)s, %(fiscal_year)s, %(fiscal_quarter)s,
          %(statement_type)s, %(label)s,
          %(value)s,
          %(filing_date)s, %(accepted_at)s,
          %(source)s, %(last_collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          period_label = VALUES(period_label),
          period_type = VALUES(period_type),
          fiscal_year = VALUES(fiscal_year),
          fiscal_quarter = VALUES(fiscal_quarter),
          value = VALUES(value),
          filing_date = VALUES(filing_date),
          accepted_at = VALUES(accepted_at),
          last_collected_at = VALUES(last_collected_at),
          error_msg = VALUES(error_msg)
        """

        for batch in _chunked(symbols, chunk_size):
            all_value_rows: List[Dict[str, Any]] = []
            all_label_rows: List[Dict[str, Any]] = []

            for sym in batch:
                last_err: Optional[str] = None

                for k in range(max_retry):
                    try:
                        df = get_fundamental(sym, periods=periods, period=period)

                        # labels / values rows 생성
                        label_rows = _iter_label_rows(df)
                        value_rows = _iter_value_rows(df, freq)

                        if not value_rows:
                            logger.warning(f"{sym} | {freq} | empty financial statement values")
                        if not label_rows:
                            logger.warning(f"{sym} | {freq} | empty financial statement labels")

                        all_label_rows.extend(label_rows)
                        all_value_rows.extend(value_rows)
                        break
                    except Exception as e:
                        last_err = str(e)
                        time.sleep((2**k) + random.random() * 0.3)

                if last_err:
                    logger.error(f"{sym} | {freq} | {last_err}")
                    failed.append(sym)

            # labels 먼저 (선택: 중복이 많으면 dedup 후 넣어도 됨)
            if all_label_rows:
                db.executemany(upsert_labels_sql, all_label_rows)
                upserted_labels += len(all_label_rows)

            if all_value_rows:
                db.executemany(upsert_values_sql, all_value_rows)
                inserted_values += len(all_value_rows)

            time.sleep(sleep + random.random() * 0.3)

    finally:
        db.close()

    return {
        "inserted_values": inserted_values,
        "upserted_labels": upserted_labels,
        "failed_symbols": failed,
    }
