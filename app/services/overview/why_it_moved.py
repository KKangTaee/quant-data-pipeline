from __future__ import annotations

import json

import os

import re

import urllib.request

from collections.abc import Callable, Sequence

from datetime import date, datetime, timezone, timedelta

from html import unescape

from typing import Any

from urllib.parse import quote, quote_plus, urlencode, urlparse

from xml.etree import ElementTree

import pandas as pd

from app.services.overview.market_mover_research import (
    build_current_ttm_valuation,
    build_financial_factor_series,
)
from finance.loaders.financial_statements import load_statement_filings
from finance.loaders.fundamentals import load_fundamental_snapshot, load_statement_fundamentals_shadow
from finance.loaders.financial_source_contract import (
    LEGACY_BROAD_YFINANCE_SOURCE,
    SEC_EDGAR_STATEMENT_SHADOW_SOURCE,
)
from finance.loaders.price import load_price_history
from finance.loaders.us_stock_turnaround import load_us_stock_turnaround_inputs
from finance.loaders.sentiment import (
    CNN_COMPONENT_SERIES,
    CORE_SENTIMENT_SERIES,
    load_market_sentiment_history,
    load_market_sentiment_snapshot,
)

PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly", "yearly": "Yearly"}

FINANCIAL_TREND_ANNUAL_LIMIT = 8
FINANCIAL_TREND_QUARTERLY_LIMIT = 32

UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000 by 20D avg dollar volume",
    "TOP2000": "Top 2000 by 20D avg dollar volume",
    "NASDAQ": "Nasdaq-listed current snapshot",
}

CATALYST_LINK_COLUMNS = [
    "Source",
    "Symbol",
    "Name",
    "Period",
    "Coverage",
    "Rank Type",
    "Rank",
    "Search Query",
    "Purpose",
    "URL",
]

WHY_IT_MOVED_NEWS_COLUMNS = ["Title", "Source", "Published At", "URL"]

WHY_IT_MOVED_KOREAN_NEWS_COLUMNS = ["Title", "Source", "Published At", "Snippet", "URL"]

WHY_IT_MOVED_SEC_COLUMNS = ["Form", "Filing Date", "Title", "URL"]

WHY_IT_MOVED_METADATA_LANES = ("news", "korean_news", "sec_filings")

GOOGLE_NEWS_KR_RSS_SEARCH_URL = "https://news.google.com/rss/search"

WHY_IT_MOVED_STATUS_LABELS = {
    "NOT_REQUESTED": ("조회 전", "neutral"),
    "OK": ("완료", "success"),
    "PARTIAL": ("부분 완료", "warning"),
    "FAILED": ("실패", "error"),
    "NO_METADATA": ("메타데이터 없음", "warning"),
}

SEC_FILING_FORM_PRIORITY = {
    "8-K": 0,
    "10-Q": 1,
    "10-K": 2,
    "S-1": 3,
    "S-3": 4,
    "S-8": 5,
    "4": 6,
}

def _rows_frame(rows: list[dict[str, Any]], *, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)

def _market_mover_link_context(
    *,
    symbol: str,
    name: str,
    period: str,
    coverage: str,
    rank: int | str | None,
    rank_source: str,
) -> dict[str, str]:
    normalized_symbol = str(symbol or "").strip().upper()
    normalized_name = str(name or "").strip() or normalized_symbol
    normalized_period = str(period or "daily").strip().lower()
    period_label = PERIOD_LABELS.get(normalized_period, normalized_period.title())
    normalized_coverage = str(coverage or "").strip().upper()
    coverage_label = UNIVERSE_LABELS.get(normalized_coverage, str(coverage or "").strip() or "Selected coverage")
    rank_label = str(rank).strip() if rank not in (None, "") else "-"
    rank_source_label = str(rank_source or "Rank").strip() or "Rank"
    rank_context = f"{rank_source_label} {rank_label}" if rank_label != "-" else rank_source_label
    base_query = (
        f"{normalized_symbol} {normalized_name} {period_label} market mover "
        f"{coverage_label} {rank_context}"
    )
    return {
        "symbol": normalized_symbol,
        "name": normalized_name,
        "period_label": period_label,
        "coverage_label": coverage_label,
        "rank_label": rank_label,
        "rank_source_label": rank_source_label,
        "rank_context": rank_context,
        "base_query": base_query,
    }

def _google_news_url(query: str, *, hl: str = "en-US", gl: str = "US", ceid: str = "US:en") -> str:
    return "https://news.google.com/search?" + urlencode(
        {"q": query, "hl": hl, "gl": gl, "ceid": ceid}
    )

def _google_search_url(query: str) -> str:
    return "https://www.google.com/search?" + urlencode({"q": query})

def _naver_news_url(query: str) -> str:
    return "https://search.naver.com/search.naver?" + urlencode({"where": "news", "query": query})

def build_market_mover_catalyst_links(
    *,
    symbol: str,
    name: str | None,
    period: str,
    coverage: str,
    rank: int | str | None,
    rank_source: str = "Return Rank",
) -> pd.DataFrame:
    """Build outbound research-start links for a selected Market Movers row."""

    context = _market_mover_link_context(
        symbol=symbol,
        name=name or "",
        period=period,
        coverage=coverage,
        rank=rank,
        rank_source=rank_source,
    )
    normalized_symbol = context["symbol"]
    if not normalized_symbol:
        return _rows_frame([], columns=CATALYST_LINK_COLUMNS)

    yahoo_symbol = quote(normalized_symbol.replace(".", "-"), safe="")
    base_query = context["base_query"]
    news_query = f"{base_query} stock news catalyst earnings guidance"
    sec_query = f"{base_query} SEC filings 8-K 10-Q 10-K earnings"
    ir_query = f"{base_query} investor relations earnings results press release"
    korean_news_query = f"{normalized_symbol} {context['name']} 주가 뉴스 실적 공시 급등 급락"
    rows = [
        {
            "Source": "Yahoo Finance",
            "Symbol": normalized_symbol,
            "Name": context["name"],
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
            "Search Query": base_query,
            "Purpose": "Quote, chart, news, and analysis landing page.",
            "URL": f"https://finance.yahoo.com/quote/{yahoo_symbol}",
        },
        {
            "Source": "Google News",
            "Symbol": normalized_symbol,
            "Name": context["name"],
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
            "Search Query": news_query,
            "Purpose": "Recent headlines for manual catalyst review.",
            "URL": _google_news_url(news_query),
        },
        {
            "Source": "SEC Company Search",
            "Symbol": normalized_symbol,
            "Name": context["name"],
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
            "Search Query": sec_query,
            "Purpose": "Company filings search for 8-K, 10-Q, 10-K, and related disclosures.",
            "URL": f"https://www.sec.gov/edgar/search/#/q={quote_plus(sec_query)}",
        },
        {
            "Source": "Investor Relations / Earnings Search",
            "Symbol": normalized_symbol,
            "Name": context["name"],
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
            "Search Query": ir_query,
            "Purpose": "Company IR, earnings release, and presentation discovery.",
            "URL": _google_search_url(ir_query),
        },
        {
            "Source": "Google News KR",
            "Symbol": normalized_symbol,
            "Name": context["name"],
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
            "Search Query": korean_news_query,
            "Purpose": "Korean-language Google News search for manual catalyst review.",
            "URL": _google_news_url(korean_news_query, hl="ko", gl="KR", ceid="KR:ko"),
        },
        {
            "Source": "Naver News",
            "Symbol": normalized_symbol,
            "Name": context["name"],
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
            "Search Query": korean_news_query,
            "Purpose": "Naver News search for Korean-language manual catalyst review.",
            "URL": _naver_news_url(korean_news_query),
        },
    ]
    return _rows_frame(rows, columns=CATALYST_LINK_COLUMNS)

def _clean_optional_text(value: Any, *, uppercase: bool = False) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if not text:
        return None
    return text.upper() if uppercase else text

def _coerce_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text or text in {"-", "—"}:
            return None
        is_accounting_negative = text.startswith("(") and text.endswith(")")
        normalized = text.strip("()").replace(",", "").replace("$", "").strip()
        try:
            numeric = float(normalized)
        except ValueError:
            return None
        return -numeric if is_accounting_negative else numeric
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

def _coerce_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None

def _iso_date_label(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return pd.Timestamp(value).date().isoformat()
    except (TypeError, ValueError):
        text = str(value).strip()
        return text or None

def _research_as_of_date(value: Any | None) -> str:
    if value is None:
        return date.today().isoformat()
    resolved = _iso_date_label(value)
    return resolved or date.today().isoformat()

def _first_available_float(row: dict[str, Any], keys: Sequence[str]) -> float | None:
    for key in keys:
        value = _coerce_optional_float(row.get(key))
        if value is not None:
            return value
    return None

def _market_cap_change_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    change_pct = _first_available_float(
        row,
        (
            "Market Cap YoY Change %",
            "Market Cap 1Y Change %",
            "Market Cap Change YoY %",
            "Market Cap Change %",
        ),
    )
    if change_pct is None:
        return {
            "status": "UNAVAILABLE",
            "reason": "과거 시총 snapshot이 현재 Market Movers read model에 없습니다.",
        }
    return {
        "status": "OK",
        "change_pct": change_pct,
        "basis": "existing Market Movers read model field",
    }

def _market_mover_ytd_snapshot(
    symbol: str,
    *,
    as_of_date: str,
    price_history_loader: Callable[..., pd.DataFrame],
) -> dict[str, Any]:
    year_start = f"{pd.Timestamp(as_of_date).year}-01-01"
    try:
        frame = price_history_loader(symbols=symbol, start=year_start, end=as_of_date, timeframe="1d")
    except Exception as exc:
        return {"status": "UNAVAILABLE", "reason": f"가격 이력 조회 실패: {exc}", "start_date": year_start}
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return {"status": "UNAVAILABLE", "reason": "올해 가격 이력 row가 없습니다.", "start_date": year_start}

    date_column = "date" if "date" in frame.columns else "Date" if "Date" in frame.columns else None
    price_column = "adj_close" if "adj_close" in frame.columns else "close" if "close" in frame.columns else None
    if date_column is None or price_column is None:
        return {
            "status": "UNAVAILABLE",
            "reason": "가격 이력에 date/close 계열 필드가 없습니다.",
            "start_date": year_start,
        }

    work = frame[[date_column, price_column]].copy()
    work[date_column] = pd.to_datetime(work[date_column], errors="coerce")
    work[price_column] = pd.to_numeric(work[price_column], errors="coerce")
    work = work.dropna(subset=[date_column, price_column]).sort_values(date_column)
    work = work[work[price_column] > 0]
    if len(work.index) < 2:
        return {
            "status": "UNAVAILABLE",
            "reason": "YTD 계산에 필요한 시작/현재 가격이 부족합니다.",
            "start_date": year_start,
        }

    first = work.iloc[0]
    latest = work.iloc[-1]
    start_price = float(first[price_column])
    latest_price = float(latest[price_column])
    return {
        "status": "OK",
        "return_pct": ((latest_price / start_price) - 1.0) * 100.0,
        "start_date": _iso_date_label(first[date_column]),
        "end_date": _iso_date_label(latest[date_column]),
        "start_price": start_price,
        "latest_price": latest_price,
        "basis": "DB daily adjusted close",
    }

def _source_payload_from_financial_row(
    row: dict[str, Any],
    *,
    default_source: str,
    default_mode: str,
    default_table: str,
    default_detail: str | None = None,
) -> dict[str, Any]:
    financial_source = _clean_optional_text(row.get("financial_source")) or default_source
    financial_source_mode = _clean_optional_text(row.get("financial_source_mode")) or default_mode
    source_table = _clean_optional_text(row.get("source_table")) or default_table
    source_detail = _clean_optional_text(row.get("source_detail")) or default_detail
    available_at = _iso_date_label(row.get("available_at"))
    form_type = _clean_optional_text(row.get("form_type"), uppercase=True)
    accession_no = _clean_optional_text(row.get("accession_no"))
    return {
        "financial_source": financial_source,
        "financial_source_mode": financial_source_mode,
        "source_table": source_table,
        "source_detail": source_detail,
        "available_at": available_at,
        "form_type": form_type,
        "accession_no": accession_no,
    }


def _latest_financial_row(
    frame: pd.DataFrame,
    *,
    as_of_date: str,
) -> dict[str, Any] | None:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return None
    work = frame.copy()
    if "period_end" in work.columns:
        work["period_end"] = pd.to_datetime(work["period_end"], errors="coerce")
    if "available_at" in work.columns:
        work["available_at"] = pd.to_datetime(work["available_at"], errors="coerce")
        as_of_ts = pd.Timestamp(as_of_date)
        work = work[(work["available_at"].isna()) | (work["available_at"] <= as_of_ts)].copy()
    if work.empty:
        return None
    sort_columns = [column for column in ["period_end", "available_at", "accession_no"] if column in work.columns]
    if sort_columns:
        work = work.sort_values(sort_columns)
    return dict(work.iloc[-1])


def _financial_snapshot_from_row(
    row: dict[str, Any],
    *,
    freq: str,
    latest_price: float | None,
    source_payload: dict[str, Any],
    fallback_used: bool = False,
    fallback_reason: str | None = None,
) -> dict[str, Any]:
    net_income = _coerce_optional_float(row.get("net_income"))
    total_revenue = _coerce_optional_float(row.get("total_revenue"))
    operating_income = _coerce_optional_float(row.get("operating_income"))
    shares = _coerce_optional_float(row.get("shares_outstanding"))
    current_assets = _coerce_optional_float(row.get("current_assets"))
    current_liabilities = _coerce_optional_float(row.get("current_liabilities"))
    total_liabilities = _coerce_optional_float(row.get("total_liabilities"))
    shareholders_equity = _coerce_optional_float(row.get("shareholders_equity"))
    current_ratio = _coerce_optional_float(row.get("current_ratio"))
    if current_ratio is None and current_assets is not None and current_liabilities and current_liabilities > 0:
        current_ratio = current_assets / current_liabilities
    free_cash_flow = _coerce_optional_float(row.get("free_cash_flow"))
    if (
        net_income is None
        and total_revenue is None
        and operating_income is None
        and current_ratio is None
        and free_cash_flow is None
    ):
        return {
            "status": "UNAVAILABLE",
            "freq": freq,
            "period_end": _iso_date_label(row.get("period_end")),
            "reason": "revenue / income / balance-sheet / cash-flow factor 필드가 부족합니다.",
            "fallback_used": bool(fallback_used),
            "fallback_reason": fallback_reason,
            **source_payload,
        }
    return {
        "status": "OK",
        "freq": freq,
        "period_end": _iso_date_label(row.get("period_end")),
        "total_revenue": total_revenue,
        "operating_income": operating_income,
        "net_income": net_income,
        "shares_outstanding": shares,
        "current_assets": current_assets,
        "current_liabilities": current_liabilities,
        "total_liabilities": total_liabilities,
        "shareholders_equity": shareholders_equity,
        "current_ratio": current_ratio,
        "free_cash_flow": free_cash_flow,
        "basis": f"latest {freq} DB fundamental snapshot",
        "fallback_used": bool(fallback_used),
        "fallback_reason": fallback_reason,
        **source_payload,
    }


def _unavailable_financial_snapshot(
    *,
    freq: str,
    reason: str,
    row: dict[str, Any] | None = None,
    source_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(source_payload or {})
    source_row = dict(row or {})
    return {
        "status": "UNAVAILABLE",
        "freq": freq,
        "period_end": _iso_date_label(source_row.get("period_end")),
        "reason": reason,
        **payload,
    }


def _market_mover_legacy_fundamental_snapshot(
    symbol: str,
    *,
    as_of_date: str,
    freq: str,
    latest_price: float | None,
    fundamental_snapshot_loader: Callable[..., pd.DataFrame],
    fallback_reason: str | None = None,
) -> dict[str, Any]:
    default_payload = {
        "financial_source": LEGACY_BROAD_YFINANCE_SOURCE,
        "financial_source_mode": "legacy_broad_summary",
        "source_table": "finance_fundamental.nyse_fundamentals",
        "source_detail": "yfinance financial statements broad compatibility layer",
        "available_at": None,
        "form_type": None,
        "accession_no": None,
    }
    try:
        frame = fundamental_snapshot_loader(symbols=symbol, as_of_date=as_of_date, freq=freq)
    except Exception as exc:
        return _unavailable_financial_snapshot(
            freq=freq,
            reason=f"legacy broad 재무제표 snapshot 조회 실패: {exc}",
            source_payload=default_payload,
        )
    row = _latest_financial_row(frame, as_of_date=as_of_date)
    if row is None:
        return _unavailable_financial_snapshot(
            freq=freq,
            reason=f"최신 {freq} legacy broad 재무제표 snapshot row가 없습니다.",
            source_payload=default_payload,
        )
    source_payload = _source_payload_from_financial_row(
        row,
        default_source=LEGACY_BROAD_YFINANCE_SOURCE,
        default_mode="legacy_broad_summary",
        default_table="finance_fundamental.nyse_fundamentals",
        default_detail="yfinance financial statements broad compatibility layer",
    )
    return _financial_snapshot_from_row(
        row,
        freq=freq,
        latest_price=latest_price,
        source_payload=source_payload,
        fallback_used=bool(fallback_reason),
        fallback_reason=fallback_reason,
    )


def _market_mover_statement_fundamental_snapshot(
    symbol: str,
    *,
    as_of_date: str,
    freq: str,
    latest_price: float | None,
    statement_fundamentals_loader: Callable[..., pd.DataFrame],
    require_quarterly_10q: bool = False,
) -> dict[str, Any]:
    default_payload = {
        "financial_source": SEC_EDGAR_STATEMENT_SHADOW_SOURCE,
        "financial_source_mode": "statement_shadow",
        "source_table": "finance_fundamental.nyse_fundamentals_statement",
        "source_detail": "SEC EDGAR filing ledger rebuilt statement shadow",
        "available_at": None,
        "form_type": None,
        "accession_no": None,
    }
    try:
        frame = statement_fundamentals_loader(symbols=symbol, freq=freq, end=as_of_date)
    except Exception as exc:
        return _unavailable_financial_snapshot(
            freq=freq,
            reason=f"EDGAR statement shadow 조회 실패: {exc}",
            source_payload=default_payload,
        )
    row = _latest_financial_row(frame, as_of_date=as_of_date)
    if row is None:
        missing_reason = (
            f"최신 {freq} 10-Q / 10-Q/A EDGAR statement shadow row가 없습니다."
            if require_quarterly_10q
            else f"최신 {freq} EDGAR statement shadow row가 없습니다."
        )
        return _unavailable_financial_snapshot(
            freq=freq,
            reason=missing_reason,
            source_payload=default_payload,
        )
    source_payload = _source_payload_from_financial_row(
        row,
        default_source=SEC_EDGAR_STATEMENT_SHADOW_SOURCE,
        default_mode="statement_shadow",
        default_table="finance_fundamental.nyse_fundamentals_statement",
        default_detail="SEC EDGAR filing ledger rebuilt statement shadow",
    )
    form_type = str(source_payload.get("form_type") or "").upper()
    if require_quarterly_10q and form_type not in {"10-Q", "10-Q/A"}:
        return _unavailable_financial_snapshot(
            freq=freq,
            reason="분기 재무제표는 10-Q / 10-Q/A source만 표시합니다. 10-K/FY 보정 전까지 분기값으로 쓰지 않습니다.",
            row=row,
            source_payload=source_payload,
        )
    return _financial_snapshot_from_row(
        row,
        freq=freq,
        latest_price=latest_price,
        source_payload=source_payload,
    )


def _financial_trend_rows_from_frame(
    frame: pd.DataFrame,
    *,
    as_of_date: str,
    freq: str,
    latest_price: float | None,
    default_source_payload: dict[str, Any],
    require_quarterly_10q: bool = False,
    limit: int = 8,
) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return []
    work = frame.copy()
    if "period_end" in work.columns:
        work["period_end"] = pd.to_datetime(work["period_end"], errors="coerce")
    if "available_at" in work.columns:
        work["available_at"] = pd.to_datetime(work["available_at"], errors="coerce")
        as_of_ts = pd.Timestamp(as_of_date)
        work = work[(work["available_at"].isna()) | (work["available_at"] <= as_of_ts)].copy()
    if work.empty:
        return []
    sort_columns = [column for column in ["period_end", "available_at", "accession_no"] if column in work.columns]
    if sort_columns:
        work = work.sort_values(sort_columns)
    rows = work.tail(max(1, int(limit))).to_dict(orient="records")
    trend_rows: list[dict[str, Any]] = []
    for row in rows:
        source_payload = _source_payload_from_financial_row(
            dict(row),
            default_source=str(default_source_payload.get("financial_source") or SEC_EDGAR_STATEMENT_SHADOW_SOURCE),
            default_mode=str(default_source_payload.get("financial_source_mode") or "statement_shadow"),
            default_table=str(default_source_payload.get("source_table") or "finance_fundamental.nyse_fundamentals_statement"),
            default_detail=default_source_payload.get("source_detail"),
        )
        form_type = str(source_payload.get("form_type") or "").upper()
        if require_quarterly_10q and form_type not in {"10-Q", "10-Q/A"}:
            continue
        snapshot = _financial_snapshot_from_row(
            dict(row),
            freq=freq,
            latest_price=latest_price,
            source_payload=source_payload,
        )
        if str(snapshot.get("status") or "").upper() == "OK":
            trend_rows.append(snapshot)
    return trend_rows


def _market_mover_statement_fundamental_trends(
    symbol: str,
    *,
    as_of_date: str,
    freq: str,
    latest_price: float | None,
    statement_fundamentals_loader: Callable[..., pd.DataFrame],
    require_quarterly_10q: bool = False,
) -> list[dict[str, Any]]:
    default_payload = {
        "financial_source": SEC_EDGAR_STATEMENT_SHADOW_SOURCE,
        "financial_source_mode": "statement_shadow",
        "source_table": "finance_fundamental.nyse_fundamentals_statement",
        "source_detail": "SEC EDGAR filing ledger rebuilt statement shadow",
        "available_at": None,
        "form_type": None,
        "accession_no": None,
    }
    try:
        frame = statement_fundamentals_loader(symbols=symbol, freq=freq, end=as_of_date)
    except Exception:
        return []
    trend_limit = FINANCIAL_TREND_QUARTERLY_LIMIT if freq == "quarterly" else FINANCIAL_TREND_ANNUAL_LIMIT
    return _financial_trend_rows_from_frame(
        frame,
        as_of_date=as_of_date,
        freq=freq,
        latest_price=latest_price,
        default_source_payload=default_payload,
        require_quarterly_10q=require_quarterly_10q,
        limit=trend_limit,
    )


def _statement_period_timestamp(item: dict[str, Any]) -> pd.Timestamp | None:
    label = _iso_date_label(dict(item or {}).get("period_end"))
    if not label:
        return None
    try:
        timestamp = pd.Timestamp(label)
    except (TypeError, ValueError):
        return None
    if pd.isna(timestamp):
        return None
    return timestamp.normalize()


def _statement_filing_payload(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    form_type = _clean_optional_text(row.get("form_type"), uppercase=True)
    return {
        "symbol": _clean_optional_text(row.get("symbol"), uppercase=True),
        "form_type": form_type,
        "report_date": _iso_date_label(row.get("report_date")),
        "filing_date": _iso_date_label(row.get("filing_date")),
        "accepted_at": _iso_date_label(row.get("accepted_at")),
        "available_at": _iso_date_label(row.get("available_at")),
        "accession_no": _clean_optional_text(row.get("accession_no")),
    }


def _latest_statement_filing(
    frame: pd.DataFrame,
    *,
    forms: set[str],
    as_of_date: str,
) -> dict[str, Any] | None:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return None
    work = frame.copy()
    if "form_type" not in work.columns or "report_date" not in work.columns:
        return None
    work["form_type"] = work["form_type"].map(lambda value: str(value or "").strip().upper())
    work = work[work["form_type"].isin(forms)].copy()
    if work.empty:
        return None

    for column in ("report_date", "filing_date", "accepted_at", "available_at"):
        if column in work.columns:
            work[column] = pd.to_datetime(work[column], errors="coerce")

    work = work[work["report_date"].notna()].copy()
    if work.empty:
        return None

    as_of_ts = pd.Timestamp(as_of_date).normalize()
    as_of_eod = as_of_ts + pd.Timedelta(days=1)
    work = work[work["report_date"] <= as_of_ts].copy()
    if "available_at" in work.columns:
        available = work["available_at"]
        if "filing_date" in work.columns:
            filing = work["filing_date"]
            work = work[
                ((available.notna()) & (available < as_of_eod))
                | ((available.isna()) & ((filing.isna()) | (filing <= as_of_ts)))
            ].copy()
        else:
            work = work[(available.isna()) | (available < as_of_eod)].copy()
    if work.empty:
        return None

    sort_columns = [
        column
        for column in ("report_date", "available_at", "filing_date", "accession_no")
        if column in work.columns
    ]
    if sort_columns:
        work = work.sort_values(sort_columns)
    return dict(work.iloc[-1])


def _statement_current_period_label(item: dict[str, Any]) -> str:
    return _iso_date_label(dict(item or {}).get("period_end")) or "미반영"


def _statement_collection_current_items(
    *,
    annual_financials: dict[str, Any],
    quarterly_financials: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "label": "DB 연간 반영",
            "value": _statement_current_period_label(annual_financials),
            "detail": "statement shadow",
        },
        {
            "label": "DB 분기 반영",
            "value": _statement_current_period_label(quarterly_financials),
            "detail": "statement shadow",
        },
    ]


def _statement_collection_missing_payload(
    *,
    latest: dict[str, Any],
    current_period: pd.Timestamp | None,
    period_label: str,
) -> dict[str, Any]:
    filing = _statement_filing_payload(latest) or {}
    report_date = str(filing.get("report_date") or "-")
    filing_date = str(filing.get("filing_date") or filing.get("available_at") or "-")
    form_type = str(filing.get("form_type") or "-")
    current_label = current_period.date().isoformat() if current_period is not None else "미반영"
    return {
        **filing,
        "period_label": period_label,
        "current_period_end": current_label,
        "items": [
            {"label": f"최신 EDGAR {form_type}", "value": report_date, "detail": f"공시 {filing_date}"},
            {"label": f"DB {period_label} 반영", "value": current_label, "detail": "statement shadow"},
        ],
    }


def _statement_expected_due_checks(
    *,
    as_of_date: str,
    annual_financials: dict[str, Any],
    quarterly_financials: dict[str, Any],
    latest_quarterly_filing: dict[str, Any] | None,
) -> list[dict[str, str]]:
    annual_period = _statement_period_timestamp(annual_financials)
    if annual_period is None:
        return []

    as_of_ts = pd.Timestamp(as_of_date).normalize()
    quarterly_period = _statement_period_timestamp(quarterly_financials)
    latest_quarter_report = None
    if latest_quarterly_filing:
        latest_quarter_report = _statement_period_timestamp({"period_end": latest_quarterly_filing.get("report_date")})
    reflected_periods = [period for period in (quarterly_period, latest_quarter_report) if period is not None]
    latest_reflected_quarter = max(reflected_periods) if reflected_periods else None

    due: list[dict[str, str]] = []
    for offset in (3, 6, 9):
        expected_period = (annual_period + pd.DateOffset(months=offset)).normalize()
        deadline = expected_period + pd.Timedelta(days=45)
        if deadline > as_of_ts:
            continue
        near_reflected_period = any(abs((expected_period - period).days) <= 14 for period in reflected_periods)
        if near_reflected_period:
            continue
        if latest_reflected_quarter is not None and expected_period <= latest_reflected_quarter:
            continue
        due.append(
            {
                "form_type": "10-Q",
                "report_date": expected_period.date().isoformat(),
                "expected_deadline": deadline.date().isoformat(),
                "basis": "보수적 45일 기준",
            }
        )
    return due


def _build_financial_statement_collection_status(
    *,
    symbol: str,
    as_of_date: str,
    annual_financials: dict[str, Any],
    quarterly_financials: dict[str, Any],
    statement_filings_loader: Callable[..., pd.DataFrame],
) -> dict[str, Any]:
    try:
        filings = statement_filings_loader(
            symbols=symbol,
            forms=["10-K", "10-K/A", "10-Q", "10-Q/A"],
            end=as_of_date,
        )
    except Exception as exc:
        return {
            "status": "UNKNOWN",
            "headline": "재무제표 수집 상태 확인 불가",
            "detail": f"EDGAR filing ledger 조회 실패: {exc}",
            "tone": "neutral",
            "items": _statement_collection_current_items(
                annual_financials=annual_financials,
                quarterly_financials=quarterly_financials,
            ),
            "missing_filings": [],
        }

    latest_annual = _latest_statement_filing(filings, forms={"10-K", "10-K/A"}, as_of_date=as_of_date)
    latest_quarterly = _latest_statement_filing(filings, forms={"10-Q", "10-Q/A"}, as_of_date=as_of_date)
    current_annual_period = _statement_period_timestamp(annual_financials)
    current_quarterly_period = _statement_period_timestamp(quarterly_financials)
    missing: list[dict[str, Any]] = []

    if latest_quarterly:
        latest_quarter_report = _statement_period_timestamp({"period_end": latest_quarterly.get("report_date")})
        if latest_quarter_report is not None and (
            current_quarterly_period is None or latest_quarter_report > current_quarterly_period
        ):
            missing.append(
                _statement_collection_missing_payload(
                    latest=latest_quarterly,
                    current_period=current_quarterly_period,
                    period_label="분기",
                )
            )
    if latest_annual:
        latest_annual_report = _statement_period_timestamp({"period_end": latest_annual.get("report_date")})
        if latest_annual_report is not None and (
            current_annual_period is None or latest_annual_report > current_annual_period
        ):
            missing.append(
                _statement_collection_missing_payload(
                    latest=latest_annual,
                    current_period=current_annual_period,
                    period_label="연간",
                )
            )

    if missing:
        first = missing[0]
        form_type = str(first.get("form_type") or "-")
        report_date = str(first.get("report_date") or "-")
        period_label = str(first.get("period_label") or "재무제표")
        current_label = str(first.get("current_period_end") or "미반영")
        return {
            "status": "ACTION_REQUIRED",
            "headline": "받아야 할 재무제표 있음",
            "detail": f"EDGAR {form_type} {report_date} 공시됨, DB {period_label} 반영은 {current_label}입니다.",
            "tone": "warning",
            "items": list(first.get("items") or []),
            "missing_filings": missing,
        }

    expected_due = _statement_expected_due_checks(
        as_of_date=as_of_date,
        annual_financials=annual_financials,
        quarterly_financials=quarterly_financials,
        latest_quarterly_filing=latest_quarterly,
    )
    if expected_due:
        first_due = expected_due[0]
        return {
            "status": "CHECK_REQUIRED",
            "headline": "재무제표 공시 확인 필요",
            "detail": (
                f"예상 제출 기한이 지난 {first_due['form_type']} {first_due['report_date']} "
                "filing ledger가 아직 확인되지 않았습니다."
            ),
            "tone": "warning",
            "items": [
                {
                    "label": f"예상 {first_due['form_type']}",
                    "value": first_due["report_date"],
                    "detail": f"기한 {first_due['expected_deadline']} · {first_due['basis']}",
                },
                {
                    "label": "DB 분기 반영",
                    "value": _statement_current_period_label(quarterly_financials),
                    "detail": "statement shadow",
                },
            ],
            "missing_filings": expected_due,
        }

    if latest_annual is None and latest_quarterly is None:
        return {
            "status": "UNKNOWN",
            "headline": "재무제표 수집 상태 확인 불가",
            "detail": "EDGAR filing ledger에서 10-K / 10-Q row를 찾지 못했습니다.",
            "tone": "neutral",
            "items": _statement_collection_current_items(
                annual_financials=annual_financials,
                quarterly_financials=quarterly_financials,
            ),
            "missing_filings": [],
        }

    items: list[dict[str, str]] = []
    if latest_quarterly:
        latest_quarter_payload = _statement_filing_payload(latest_quarterly) or {}
        items.append(
            {
                "label": f"최신 EDGAR {latest_quarter_payload.get('form_type') or '10-Q'}",
                "value": str(latest_quarter_payload.get("report_date") or "-"),
                "detail": f"공시 {latest_quarter_payload.get('filing_date') or latest_quarter_payload.get('available_at') or '-'}",
            }
        )
    items.append(
        {
            "label": "DB 분기 반영",
            "value": _statement_current_period_label(quarterly_financials),
            "detail": "statement shadow",
        }
    )
    if latest_annual:
        latest_annual_payload = _statement_filing_payload(latest_annual) or {}
        items.append(
            {
                "label": f"최신 EDGAR {latest_annual_payload.get('form_type') or '10-K'}",
                "value": str(latest_annual_payload.get("report_date") or "-"),
                "detail": f"공시 {latest_annual_payload.get('filing_date') or latest_annual_payload.get('available_at') or '-'}",
            }
        )
    return {
        "status": "OK",
        "headline": "최신 재무제표 반영 완료",
        "detail": "EDGAR filing ledger 기준 최신 공시가 statement shadow에 반영되어 있습니다.",
        "tone": "positive",
        "items": items,
        "missing_filings": [],
    }


def build_market_mover_research_snapshot(
    *,
    mover: dict[str, Any],
    as_of_date: Any | None = None,
    price_history_loader: Callable[..., pd.DataFrame] | None = None,
    statement_fundamentals_loader: Callable[..., pd.DataFrame] | None = None,
    fundamental_snapshot_loader: Callable[..., pd.DataFrame] | None = None,
    statement_filings_loader: Callable[..., pd.DataFrame] | None = None,
    quarterly_eps_loader: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build DB-backed context-only fundamentals for a selected Market Movers row."""

    row = dict(mover or {})
    symbol = _clean_optional_text(row.get("Symbol") or row.get("symbol"), uppercase=True)
    effective_as_of = _research_as_of_date(as_of_date)
    if not symbol:
        return {
            "schema_version": "market_mover_research_snapshot_v2",
            "status": "NO_SYMBOL",
            "symbol": None,
            "as_of_date": effective_as_of,
            "current_market_cap": {"status": "UNAVAILABLE", "reason": "선택 symbol이 없습니다."},
            "market_cap_change": {"status": "UNAVAILABLE", "reason": "선택 symbol이 없습니다."},
            "ytd_return": {"status": "UNAVAILABLE", "reason": "선택 symbol이 없습니다."},
            "annual_financials": {"status": "UNAVAILABLE", "freq": "annual", "reason": "선택 symbol이 없습니다."},
            "quarterly_financials": {"status": "UNAVAILABLE", "freq": "quarterly", "reason": "선택 symbol이 없습니다."},
            "financial_trends": {"annual": [], "quarterly": []},
            "financial_factor_series": {
                "annual": build_financial_factor_series([], freq="annual"),
                "quarterly": build_financial_factor_series([], freq="quarterly"),
            },
            "current_valuation": build_current_ttm_valuation(
                [],
                latest_price=None,
                latest_price_date=None,
            ),
            "financial_statement_collection": {
                "status": "UNKNOWN",
                "headline": "재무제표 수집 상태 확인 불가",
                "detail": "선택 symbol이 없습니다.",
                "tone": "neutral",
                "items": [],
                "missing_filings": [],
            },
            "boundary_note": "Context-only fundamentals snapshot; no trading signal or recommendation is produced.",
        }

    current_market_cap = _coerce_optional_float(row.get("Market Cap") or row.get("market_cap"))
    current_market_cap_item = (
        {"status": "OK", "value": current_market_cap, "basis": "latest asset_profile / mover row"}
        if current_market_cap is not None
        else {"status": "UNAVAILABLE", "reason": "현재 시총이 선택 row에 없습니다."}
    )
    price_loader = price_history_loader or load_price_history
    statement_loader = statement_fundamentals_loader or load_statement_fundamentals_shadow
    legacy_fundamental_loader = fundamental_snapshot_loader or load_fundamental_snapshot
    filings_loader = statement_filings_loader or load_statement_filings
    ytd_return = _market_mover_ytd_snapshot(symbol, as_of_date=effective_as_of, price_history_loader=price_loader)
    latest_price = _coerce_optional_float(ytd_return.get("latest_price"))
    annual_statement = _market_mover_statement_fundamental_snapshot(
        symbol,
        as_of_date=effective_as_of,
        freq="annual",
        latest_price=latest_price,
        statement_fundamentals_loader=statement_loader,
    )
    if str(annual_statement.get("status") or "").upper() == "OK":
        annual_financials = annual_statement
    else:
        annual_financials = _market_mover_legacy_fundamental_snapshot(
            symbol,
            as_of_date=effective_as_of,
            freq="annual",
            latest_price=latest_price,
            fundamental_snapshot_loader=legacy_fundamental_loader,
            fallback_reason=str(annual_statement.get("reason") or "statement annual row unavailable"),
        )
    quarterly_financials = _market_mover_statement_fundamental_snapshot(
        symbol,
        as_of_date=effective_as_of,
        freq="quarterly",
        latest_price=latest_price,
        statement_fundamentals_loader=statement_loader,
        require_quarterly_10q=True,
    )
    annual_trends = _market_mover_statement_fundamental_trends(
        symbol,
        as_of_date=effective_as_of,
        freq="annual",
        latest_price=latest_price,
        statement_fundamentals_loader=statement_loader,
    )
    quarterly_trends = _market_mover_statement_fundamental_trends(
        symbol,
        as_of_date=effective_as_of,
        freq="quarterly",
        latest_price=latest_price,
        statement_fundamentals_loader=statement_loader,
        require_quarterly_10q=True,
    )
    if not annual_trends and str(annual_financials.get("status") or "").upper() == "OK":
        annual_trends = [annual_financials]
    if not quarterly_trends and str(quarterly_financials.get("status") or "").upper() == "OK":
        quarterly_trends = [quarterly_financials]
    annual_factor_series = build_financial_factor_series(annual_trends, freq="annual")
    quarterly_factor_series = build_financial_factor_series(quarterly_trends, freq="quarterly")
    eps_loader = quarterly_eps_loader or load_us_stock_turnaround_inputs
    try:
        eps_inputs = eps_loader(symbol=symbol, as_of_date=effective_as_of)
        quarterly_eps_rows = list(
            dict(eps_inputs.get("series") or {}).get("timeline") or []
        )
    except Exception:
        quarterly_eps_rows = []
    reported_eps_series = build_financial_factor_series(
        quarterly_eps_rows,
        freq="quarterly",
    )["factors"]["diluted_eps"]
    quarterly_factor_series["factors"]["diluted_eps"] = reported_eps_series
    current_valuation = build_current_ttm_valuation(
        quarterly_eps_rows,
        latest_price=latest_price,
        latest_price_date=_iso_date_label(ytd_return.get("end_date")),
    )
    collection_status = _build_financial_statement_collection_status(
        symbol=symbol,
        as_of_date=effective_as_of,
        annual_financials=annual_financials,
        quarterly_financials=quarterly_financials,
        statement_filings_loader=filings_loader,
    )
    return {
        "schema_version": "market_mover_research_snapshot_v2",
        "status": "READY",
        "symbol": symbol,
        "as_of_date": effective_as_of,
        "current_market_cap": current_market_cap_item,
        "market_cap_change": _market_cap_change_snapshot(row),
        "ytd_return": ytd_return,
        "annual_financials": annual_financials,
        "quarterly_financials": quarterly_financials,
        "financial_trends": {"annual": annual_trends, "quarterly": quarterly_trends},
        "financial_factor_series": {
            "annual": annual_factor_series,
            "quarterly": quarterly_factor_series,
        },
        "current_valuation": current_valuation,
        "financial_statement_collection": collection_status,
        "boundary_note": "Context-only fundamentals snapshot; no trading signal or recommendation is produced.",
    }

def _metadata_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        timestamp = value
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    return text or None

def _nested_value(mapping: dict[str, Any], *keys: str) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current

def build_market_mover_metadata_not_requested_state(symbol: str | None = None) -> dict[str, Any]:
    normalized_symbol = _clean_optional_text(symbol, uppercase=True)
    return {
        "status": "NOT_REQUESTED",
        "symbol": normalized_symbol,
        "fetched_at_utc": None,
        "news": _rows_frame([], columns=WHY_IT_MOVED_NEWS_COLUMNS),
        "korean_news": _rows_frame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS),
        "sec_filings": _rows_frame([], columns=WHY_IT_MOVED_SEC_COLUMNS),
        "messages": ["이번 세션에서 메타데이터 조회를 아직 실행하지 않았습니다."],
        "requested_lanes": [],
    }

def _count_metadata_rows(value: Any) -> int:
    if isinstance(value, pd.DataFrame):
        return int(len(value.index))
    if isinstance(value, list):
        return int(len(value))
    return 0

def _row_count_label(count: int) -> str:
    return f"{count}건"

def _metadata_provider_failure_prefixes(provider: str) -> tuple[str, ...]:
    normalized = str(provider or "").strip().lower()
    if normalized == "news":
        return ("news metadata lookup failed:", "뉴스 메타데이터 조회 실패:")
    if normalized in {"korean news", "korean_news", "korean-news", "한국어 뉴스"}:
        return ("korean news metadata lookup failed:", "한국어 뉴스 메타데이터 조회 실패:")
    if normalized == "sec":
        return ("sec metadata lookup failed:", "sec 메타데이터 조회 실패:")
    return (f"{normalized} metadata lookup failed:",)

def _metadata_provider_failed(messages: list[str], provider: str) -> bool:
    prefixes = _metadata_provider_failure_prefixes(provider)
    return any(message.lower().startswith(prefix) for message in messages for prefix in prefixes)

def _metadata_provider_status_item(
    *,
    label: str,
    count: int,
    failed: bool,
    lookup_status: str,
) -> dict[str, Any]:
    if lookup_status == "NOT_REQUESTED":
        return {"label": label, "value": "조회 전", "tone": "neutral", "row_count": 0}
    if failed:
        return {"label": label, "value": "실패", "tone": "error", "row_count": count}
    tone = "success" if count > 0 else "neutral"
    if count == 0 and lookup_status in {"PARTIAL", "NO_METADATA"}:
        tone = "warning"
    return {"label": label, "value": _row_count_label(count), "tone": tone, "row_count": count}

def build_market_mover_metadata_status_strip(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Summarize compact metadata lookup state without implying catalyst judgement."""

    payload = dict(metadata or {})
    status = str(payload.get("status") or "NOT_REQUESTED").strip().upper()
    label, tone = WHY_IT_MOVED_STATUS_LABELS.get(status, (status.replace("_", " ").title(), "neutral"))
    messages = [str(message).strip() for message in payload.get("messages") or [] if str(message).strip()]
    news_count = _count_metadata_rows(payload.get("news"))
    korean_news_count = _count_metadata_rows(payload.get("korean_news"))
    sec_count = _count_metadata_rows(payload.get("sec_filings"))
    news_item = _metadata_provider_status_item(
        label="News",
        count=news_count,
        failed=_metadata_provider_failed(messages, "News"),
        lookup_status=status,
    )
    korean_news_item = _metadata_provider_status_item(
        label="한국어 뉴스",
        count=korean_news_count,
        failed=_metadata_provider_failed(messages, "Korean News"),
        lookup_status=status,
    )
    sec_item = _metadata_provider_status_item(
        label="SEC",
        count=sec_count,
        failed=_metadata_provider_failed(messages, "SEC"),
        lookup_status=status,
    )
    fetched_at = str(payload.get("fetched_at_utc") or "").strip() or "-"
    strip = {
        "status": status,
        "lookup": {"label": "조회 상태", "value": label, "tone": tone},
        "news": news_item,
        "korean_news": korean_news_item,
        "sec": sec_item,
        "fetched_at": {"label": "조회 시각", "value": fetched_at, "tone": "neutral"},
        "storage": {"label": "저장 경계", "value": "세션 전용", "tone": "neutral"},
    }
    strip["items"] = [
        strip["lookup"],
        strip["news"],
        strip["korean_news"],
        strip["sec"],
        strip["fetched_at"],
        strip["storage"],
    ]
    return strip

def build_market_mover_why_it_moved_read_model(
    *,
    mover: dict[str, Any],
    period: str,
    coverage: str,
    rank_source: str = "Return Rank",
) -> dict[str, Any]:
    """Build the session-only manual investigation read model for one selected mover."""

    row = dict(mover or {})
    symbol = _clean_optional_text(row.get("Symbol"), uppercase=True)
    if not symbol:
        return {
            "status": "NO_SYMBOL",
            "mode": "manual_investigation",
            "identity": {},
            "context": {},
            "movement": {},
            "links": _rows_frame([], columns=CATALYST_LINK_COLUMNS),
            "metadata": build_market_mover_metadata_not_requested_state(None),
            "boundary_note": "Manual investigation panel; no automatic catalyst judgement is produced.",
        }

    name = _clean_optional_text(row.get("Name")) or symbol
    context = _market_mover_link_context(
        symbol=symbol,
        name=name,
        period=period,
        coverage=coverage,
        rank=row.get("Rank"),
        rank_source=rank_source,
    )
    identity = {
        "Symbol": symbol,
        "Name": name,
        "Sector": _clean_optional_text(row.get("Sector")) or "Unknown",
        "Industry": _clean_optional_text(row.get("Industry")) or "Unknown",
        "Market Cap": _coerce_optional_int(row.get("Market Cap")),
    }
    movement = {
        "Return %": _coerce_optional_float(row.get("Return %")),
        "Volume": _coerce_optional_int(row.get("Volume")),
        "Dollar Volume": _coerce_optional_float(row.get("Dollar Volume")),
        "Relative Volume": _coerce_optional_float(row.get("Relative Volume")),
        "Current Volume": _coerce_optional_int(row.get("Current Volume")),
        "Avg 10D Volume": _coerce_optional_int(row.get("Avg 10D Volume")),
        "Volume Basis": _clean_optional_text(row.get("Volume Basis")),
        "Avg Daily Volume": _coerce_optional_int(row.get("Avg Daily Volume")),
        "Total Volume": _coerce_optional_int(row.get("Total Volume")),
        "Avg Daily Dollar Volume": _coerce_optional_float(row.get("Avg Daily Dollar Volume")),
        "Total Dollar Volume": _coerce_optional_float(row.get("Total Dollar Volume")),
        "Previous Return %": _coerce_optional_float(row.get("Previous Return %")),
        "Momentum Delta pp": _coerce_optional_float(row.get("Momentum Delta pp")),
    }
    links = build_market_mover_catalyst_links(
        symbol=symbol,
        name=name,
        period=period,
        coverage=coverage,
        rank=row.get("Rank"),
        rank_source=rank_source,
    )
    return {
        "status": "READY",
        "mode": "manual_investigation",
        "identity": identity,
        "context": {
            "Period": context["period_label"],
            "Coverage": context["coverage_label"],
            "Rank Type": context["rank_source_label"],
            "Rank": context["rank_label"],
        },
        "movement": movement,
        "links": links,
        "metadata": build_market_mover_metadata_not_requested_state(symbol),
        "boundary_note": "Manual investigation panel; no automatic catalyst judgement is produced.",
    }

def _normalize_news_metadata(rows: list[dict[str, Any]], *, max_items: int) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for item in rows[: max(0, max_items)]:
        if not isinstance(item, dict):
            continue
        content = item.get("content") if isinstance(item.get("content"), dict) else {}
        provider = content.get("provider") if isinstance(content.get("provider"), dict) else {}
        title = (
            _clean_optional_text(item.get("title"))
            or _clean_optional_text(content.get("title"))
            or _clean_optional_text(item.get("headline"))
        )
        url = (
            _clean_optional_text(item.get("url"))
            or _clean_optional_text(item.get("link"))
            or _clean_optional_text(_nested_value(content, "clickThroughUrl", "url"))
            or _clean_optional_text(_nested_value(content, "canonicalUrl", "url"))
        )
        if not title or not url:
            continue
        source = (
            _clean_optional_text(item.get("publisher"))
            or _clean_optional_text(item.get("source"))
            or _clean_optional_text(provider.get("displayName"))
            or _clean_optional_text(provider.get("name"))
            or "Unknown"
        )
        published_at = (
            _metadata_timestamp(item.get("published_at"))
            or _metadata_timestamp(item.get("providerPublishTime"))
            or _metadata_timestamp(content.get("pubDate"))
            or _metadata_timestamp(content.get("displayTime"))
        )
        out.append(
            {
                "Title": title,
                "Source": source,
                "Published At": published_at,
                "URL": url,
            }
        )
    return _rows_frame(out, columns=WHY_IT_MOVED_NEWS_COLUMNS)

def _clean_news_search_text(value: Any) -> str | None:
    text = _clean_optional_text(value)
    if not text:
        return None
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None

def _source_from_url(url: str | None) -> str | None:
    parsed = urlparse(str(url or "").strip())
    host = parsed.netloc.strip()
    if host.startswith("www."):
        host = host[4:]
    return host or None

def _truncate_metadata_snippet(value: Any, *, limit: int = 240) -> str | None:
    text = _clean_news_search_text(value)
    if not text:
        return None
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "..."

def _normalize_korean_news_metadata(rows: list[dict[str, Any]], *, max_items: int) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for item in rows[: max(0, max_items)]:
        if not isinstance(item, dict):
            continue
        title = _clean_news_search_text(item.get("title"))
        url = _clean_optional_text(item.get("originallink")) or _clean_optional_text(item.get("original_link"))
        url = url or _clean_optional_text(item.get("link")) or _clean_optional_text(item.get("url"))
        if not title or not url:
            continue
        source = (
            _clean_news_search_text(item.get("source"))
            or _clean_news_search_text(item.get("publisher"))
            or _source_from_url(url)
            or "Google News KR RSS"
        )
        out.append(
            {
                "Title": title,
                "Source": source,
                "Published At": _metadata_timestamp(item.get("pubDate")) or _metadata_timestamp(item.get("published_at")),
                "Snippet": _truncate_metadata_snippet(item.get("description")) or "",
                "URL": url,
            }
        )
    return _rows_frame(out, columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS)

def _sec_form_priority_value(form: Any) -> int:
    text = _clean_optional_text(form, uppercase=True) or ""
    normalized = text.split("/", 1)[0]
    return SEC_FILING_FORM_PRIORITY.get(normalized, len(SEC_FILING_FORM_PRIORITY))

def sort_market_mover_sec_filings_by_form_priority(sec_filings: pd.DataFrame) -> pd.DataFrame:
    """Keep SEC metadata compact: newest rows first, prioritized forms within the same date."""

    if not isinstance(sec_filings, pd.DataFrame) or sec_filings.empty:
        return _rows_frame([], columns=WHY_IT_MOVED_SEC_COLUMNS)

    work = sec_filings.copy()
    for column in WHY_IT_MOVED_SEC_COLUMNS:
        if column not in work.columns:
            work[column] = None
    work = work[WHY_IT_MOVED_SEC_COLUMNS].copy()
    work["__date"] = pd.to_datetime(work["Filing Date"], errors="coerce", utc=True)
    work["__form_priority"] = work["Form"].map(_sec_form_priority_value)
    work["__input_order"] = range(len(work))
    work = work.sort_values(
        ["__date", "__form_priority", "__input_order"],
        ascending=[False, True, True],
        na_position="last",
    )
    return work.drop(columns=["__date", "__form_priority", "__input_order"]).reset_index(drop=True)

def _normalize_sec_filing_metadata(rows: list[dict[str, Any]], *, max_items: int) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for item in rows[: max(0, max_items)]:
        if not isinstance(item, dict):
            continue
        form = _clean_optional_text(item.get("form")) or _clean_optional_text(item.get("form_type"))
        filing_date = (
            _metadata_timestamp(item.get("filing_date"))
            or _metadata_timestamp(item.get("filingDate"))
        )
        title = (
            _clean_optional_text(item.get("title"))
            or _clean_optional_text(item.get("description"))
            or _clean_optional_text(item.get("primaryDocDescription"))
            or form
        )
        url = _clean_optional_text(item.get("url")) or _clean_optional_text(item.get("source_ref"))
        if not form or not url:
            continue
        out.append(
            {
                "Form": form,
                "Filing Date": filing_date,
                "Title": title,
                "URL": url,
            }
        )
    return sort_market_mover_sec_filings_by_form_priority(_rows_frame(out, columns=WHY_IT_MOVED_SEC_COLUMNS))

def _fetch_yfinance_news_metadata(symbol: str, max_items: int) -> list[dict[str, Any]]:
    import yfinance as yf

    ticker = yf.Ticker(symbol)
    news = ticker.news or []
    return [item for item in news[: max(0, max_items)] if isinstance(item, dict)]

def _google_news_kr_rss_search_query(symbol: str, name: str | None) -> str:
    normalized_symbol = _clean_optional_text(symbol, uppercase=True) or ""
    normalized_name = _clean_optional_text(name) or ""
    parts = [part for part in [normalized_symbol, normalized_name] if part]
    return " ".join(dict.fromkeys(parts + ["주가", "뉴스", "실적", "공시", "급등", "급락"]))

def _fetch_google_news_kr_rss_metadata(
    symbol: str,
    name: str | None,
    max_items: int,
    request_timeout: float,
) -> list[dict[str, Any]]:
    limit = max(0, int(max_items))
    if limit <= 0:
        return []
    query = _google_news_kr_rss_search_query(symbol, name)
    if not query:
        return []

    url = GOOGLE_NEWS_KR_RSS_SEARCH_URL + "?" + urlencode(
        {
            "q": query,
            "hl": "ko",
            "gl": "KR",
            "ceid": "KR:ko",
        }
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; quant-data-pipeline/1.0)"},
    )
    with urllib.request.urlopen(request, timeout=float(request_timeout)) as response:
        payload = response.read()

    if not payload:
        return []
    root = ElementTree.fromstring(payload)
    rows: list[dict[str, Any]] = []
    for item in root.findall("./channel/item")[:limit]:
        source_node = item.find("source")
        link = _clean_optional_text(item.findtext("link"))
        rows.append(
            {
                "title": item.findtext("title"),
                "link": link,
                "url": link,
                "description": item.findtext("description"),
                "pubDate": item.findtext("pubDate"),
                "source": source_node.text if source_node is not None else "Google News KR RSS",
            }
        )
    return [row for row in rows if row.get("title") and row.get("link")]

def _sec_filing_metadata_url(cik: int, accession_no: str, primary_document: str | None) -> str:
    from finance.data.sec_delisting import SEC_FILING_ARCHIVE_URL_TEMPLATE, SEC_FILING_DIRECTORY_URL_TEMPLATE

    accession_clean = str(accession_no or "").replace("-", "")
    cik_text = str(int(cik))
    if primary_document:
        return SEC_FILING_ARCHIVE_URL_TEMPLATE.format(
            cik=cik_text,
            accession=accession_clean,
            primary_document=primary_document,
        )
    return SEC_FILING_DIRECTORY_URL_TEMPLATE.format(cik=cik_text, accession=accession_clean)

def _fetch_sec_recent_filing_metadata(
    symbol: str,
    max_items: int,
    user_agent: str | None,
    request_timeout: float,
) -> list[dict[str, Any]]:
    from finance.data.sec_delisting import (
        DEFAULT_SEC_USER_AGENT,
        SEC_COMPANY_TICKERS_URL,
        SEC_SUBMISSIONS_URL_TEMPLATE,
        fetch_sec_json,
        normalize_sec_ticker_map,
    )

    normalized_symbol = _clean_optional_text(symbol, uppercase=True)
    if not normalized_symbol:
        return []
    effective_user_agent = str(user_agent or os.getenv("SEC_USER_AGENT") or DEFAULT_SEC_USER_AGENT).strip()
    ticker_map = normalize_sec_ticker_map(fetch_sec_json(SEC_COMPANY_TICKERS_URL, effective_user_agent, request_timeout))
    company = ticker_map.get(normalized_symbol)
    if not company:
        return []
    cik = int(company["cik"])
    submissions = fetch_sec_json(SEC_SUBMISSIONS_URL_TEMPLATE.format(cik=cik), effective_user_agent, request_timeout)
    recent = ((submissions.get("filings") or {}).get("recent") or {}) if isinstance(submissions, dict) else {}
    if not isinstance(recent, dict):
        return []

    columns = {
        "form": recent.get("form") or [],
        "accessionNumber": recent.get("accessionNumber") or [],
        "filingDate": recent.get("filingDate") or [],
        "primaryDocument": recent.get("primaryDocument") or [],
        "primaryDocDescription": recent.get("primaryDocDescription") or [],
    }
    max_len = max((len(values) for values in columns.values() if isinstance(values, list)), default=0)
    rows: list[dict[str, Any]] = []
    for idx in range(max_len):
        if len(rows) >= max(0, max_items):
            break
        accession_no = columns["accessionNumber"][idx] if idx < len(columns["accessionNumber"]) else None
        form = columns["form"][idx] if idx < len(columns["form"]) else None
        if not accession_no or not form:
            continue
        primary_document = columns["primaryDocument"][idx] if idx < len(columns["primaryDocument"]) else None
        filing_date = columns["filingDate"][idx] if idx < len(columns["filingDate"]) else None
        title = columns["primaryDocDescription"][idx] if idx < len(columns["primaryDocDescription"]) else None
        rows.append(
            {
                "form": form,
                "filing_date": filing_date,
                "title": title or form,
                "url": _sec_filing_metadata_url(cik, str(accession_no), str(primary_document or "").strip() or None),
            }
        )
    return rows

def _metadata_empty_frame(lane: str) -> pd.DataFrame:
    if lane == "news":
        return _rows_frame([], columns=WHY_IT_MOVED_NEWS_COLUMNS)
    if lane == "korean_news":
        return _rows_frame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS)
    if lane == "sec_filings":
        return _rows_frame([], columns=WHY_IT_MOVED_SEC_COLUMNS)
    return _rows_frame([], columns=[])

def _metadata_frame(payload: dict[str, Any], lane: str) -> pd.DataFrame:
    value = payload.get(lane)
    if isinstance(value, pd.DataFrame):
        return value.copy()
    return _metadata_empty_frame(lane)

def _normalize_metadata_lanes(values: Sequence[str] | None) -> list[str]:
    normalized: list[str] = []
    for value in values or []:
        lane = str(value or "").strip()
        if lane in WHY_IT_MOVED_METADATA_LANES and lane not in normalized:
            normalized.append(lane)
    return normalized

def _metadata_had_failure(messages: Sequence[str]) -> bool:
    return (
        _metadata_provider_failed(list(messages), "News")
        or _metadata_provider_failed(list(messages), "Korean News")
        or _metadata_provider_failed(list(messages), "SEC")
    )

def _metadata_no_rows_message(symbol: str | None, requested_lanes: Sequence[str]) -> str:
    normalized_symbol = str(symbol or "").strip().upper() or "선택 종목"
    lanes = set(requested_lanes)
    if lanes == {"news", "korean_news"}:
        return f"{normalized_symbol}에 대해 간단 뉴스 또는 한국어 뉴스 메타데이터가 반환되지 않았습니다."
    if lanes == {"sec_filings"}:
        return f"{normalized_symbol}에 대해 SEC 공시 메타데이터가 반환되지 않았습니다."
    return f"{normalized_symbol}에 대해 간단 뉴스, 한국어 뉴스 또는 SEC 공시 메타데이터가 반환되지 않았습니다."

def _metadata_status(
    *,
    news: pd.DataFrame,
    korean_news: pd.DataFrame,
    sec_filings: pd.DataFrame,
    messages: Sequence[str],
    requested_lanes: Sequence[str],
) -> str:
    has_metadata = not news.empty or not korean_news.empty or not sec_filings.empty
    had_failure = _metadata_had_failure(messages)
    if has_metadata and had_failure:
        return "PARTIAL"
    if has_metadata:
        return "OK"
    if had_failure:
        return "FAILED"
    if requested_lanes:
        return "NO_METADATA"
    return "NOT_REQUESTED"

def _build_market_mover_metadata_payload(
    *,
    symbol: str | None,
    fetched_at_utc: str | None,
    news: pd.DataFrame | None = None,
    korean_news: pd.DataFrame | None = None,
    sec_filings: pd.DataFrame | None = None,
    messages: Sequence[str] | None = None,
    requested_lanes: Sequence[str] | None = None,
) -> dict[str, Any]:
    normalized_lanes = _normalize_metadata_lanes(requested_lanes)
    normalized_symbol = _clean_optional_text(symbol, uppercase=True)
    payload_messages = [str(message).strip() for message in messages or [] if str(message).strip()]
    news_frame = news.copy() if isinstance(news, pd.DataFrame) else _metadata_empty_frame("news")
    korean_news_frame = (
        korean_news.copy() if isinstance(korean_news, pd.DataFrame) else _metadata_empty_frame("korean_news")
    )
    sec_frame = sec_filings.copy() if isinstance(sec_filings, pd.DataFrame) else _metadata_empty_frame("sec_filings")
    status = _metadata_status(
        news=news_frame,
        korean_news=korean_news_frame,
        sec_filings=sec_frame,
        messages=payload_messages,
        requested_lanes=normalized_lanes,
    )
    if status == "NO_METADATA" and not payload_messages:
        payload_messages.append(_metadata_no_rows_message(normalized_symbol, normalized_lanes))
    return {
        "status": status,
        "symbol": normalized_symbol,
        "fetched_at_utc": fetched_at_utc,
        "news": news_frame,
        "korean_news": korean_news_frame,
        "sec_filings": sec_frame,
        "messages": payload_messages,
        "requested_lanes": normalized_lanes,
    }

def merge_market_mover_metadata(
    existing: dict[str, Any] | None,
    update: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge a tab-local metadata update without clearing lanes fetched in another tab."""

    base = dict(existing or {})
    patch = dict(update or {})
    base_lanes = _normalize_metadata_lanes(base.get("requested_lanes"))
    update_lanes = _normalize_metadata_lanes(patch.get("requested_lanes"))
    if not update_lanes and patch:
        update_lanes = list(WHY_IT_MOVED_METADATA_LANES)
    merged_lanes = _normalize_metadata_lanes([*base_lanes, *update_lanes])
    merged_frames: dict[str, pd.DataFrame] = {}
    for lane in WHY_IT_MOVED_METADATA_LANES:
        source = patch if lane in update_lanes else base
        merged_frames[lane] = _metadata_frame(source, lane)

    messages: list[str] = []
    for message in [*(base.get("messages") or []), *(patch.get("messages") or [])]:
        text = str(message).strip()
        if not text or text == "이번 세션에서 메타데이터 조회를 아직 실행하지 않았습니다.":
            continue
        if text not in messages:
            messages.append(text)

    return _build_market_mover_metadata_payload(
        symbol=patch.get("symbol") or base.get("symbol"),
        fetched_at_utc=patch.get("fetched_at_utc") or base.get("fetched_at_utc"),
        news=merged_frames["news"],
        korean_news=merged_frames["korean_news"],
        sec_filings=merged_frames["sec_filings"],
        messages=messages,
        requested_lanes=merged_lanes,
    )

def fetch_market_mover_news_metadata(
    symbol: str,
    *,
    name: str | None = None,
    max_news: int = 5,
    max_korean_news: int = 5,
    news_fetcher: Callable[[str, int], list[dict[str, Any]]] | None = None,
    korean_news_fetcher: Callable[[str, str | None, int, float], list[dict[str, Any]]] | None = None,
    request_timeout: float = 8.0,
) -> dict[str, Any]:
    """Fetch only news metadata lanes for the selected Market Mover."""

    normalized_symbol = _clean_optional_text(symbol, uppercase=True)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if not normalized_symbol:
        payload = _build_market_mover_metadata_payload(
            symbol=None,
            fetched_at_utc=fetched_at,
            messages=["Symbol is required for compact metadata lookup."],
            requested_lanes=["news", "korean_news"],
        )
        payload["status"] = "FAILED"
        return payload

    messages: list[str] = []
    news_rows: list[dict[str, Any]] = []
    korean_news_rows: list[dict[str, Any]] = []
    normalized_name = _clean_optional_text(name)

    try:
        news_rows = (news_fetcher or _fetch_yfinance_news_metadata)(normalized_symbol, max(0, int(max_news)))
    except Exception as exc:
        messages.append(f"뉴스 메타데이터 조회 실패: {exc}")

    try:
        korean_news_rows = (korean_news_fetcher or _fetch_google_news_kr_rss_metadata)(
            normalized_symbol,
            normalized_name,
            max(0, int(max_korean_news)),
            float(request_timeout),
        )
    except Exception as exc:
        messages.append(f"한국어 뉴스 메타데이터 조회 실패: {exc}")

    return _build_market_mover_metadata_payload(
        symbol=normalized_symbol,
        fetched_at_utc=fetched_at,
        news=_normalize_news_metadata(news_rows, max_items=max_news),
        korean_news=_normalize_korean_news_metadata(korean_news_rows, max_items=max_korean_news),
        sec_filings=_metadata_empty_frame("sec_filings"),
        messages=messages,
        requested_lanes=["news", "korean_news"],
    )

def fetch_market_mover_sec_metadata(
    symbol: str,
    *,
    max_filings: int = 5,
    sec_fetcher: Callable[[str, int, str | None, float], list[dict[str, Any]]] | None = None,
    user_agent: str | None = None,
    request_timeout: float = 8.0,
) -> dict[str, Any]:
    """Fetch only SEC filing metadata for the selected Market Mover."""

    normalized_symbol = _clean_optional_text(symbol, uppercase=True)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if not normalized_symbol:
        payload = _build_market_mover_metadata_payload(
            symbol=None,
            fetched_at_utc=fetched_at,
            messages=["Symbol is required for compact metadata lookup."],
            requested_lanes=["sec_filings"],
        )
        payload["status"] = "FAILED"
        return payload

    messages: list[str] = []
    sec_rows: list[dict[str, Any]] = []
    try:
        sec_rows = (sec_fetcher or _fetch_sec_recent_filing_metadata)(
            normalized_symbol,
            max(0, int(max_filings)),
            user_agent,
            float(request_timeout),
        )
    except Exception as exc:
        messages.append(f"SEC 메타데이터 조회 실패: {exc}")

    return _build_market_mover_metadata_payload(
        symbol=normalized_symbol,
        fetched_at_utc=fetched_at,
        news=_metadata_empty_frame("news"),
        korean_news=_metadata_empty_frame("korean_news"),
        sec_filings=_normalize_sec_filing_metadata(sec_rows, max_items=max_filings),
        messages=messages,
        requested_lanes=["sec_filings"],
    )

def fetch_market_mover_compact_metadata(
    symbol: str,
    *,
    name: str | None = None,
    max_news: int = 5,
    max_korean_news: int = 5,
    max_filings: int = 5,
    news_fetcher: Callable[[str, int], list[dict[str, Any]]] | None = None,
    korean_news_fetcher: Callable[[str, str | None, int, float], list[dict[str, Any]]] | None = None,
    sec_fetcher: Callable[[str, int, str | None, float], list[dict[str, Any]]] | None = None,
    user_agent: str | None = None,
    request_timeout: float = 8.0,
) -> dict[str, Any]:
    """Fetch compact, session-only news and SEC metadata for one selected mover."""

    normalized_symbol = _clean_optional_text(symbol, uppercase=True)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if not normalized_symbol:
        return {
            "status": "FAILED",
            "symbol": None,
            "fetched_at_utc": fetched_at,
            "news": _rows_frame([], columns=WHY_IT_MOVED_NEWS_COLUMNS),
            "korean_news": _rows_frame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS),
            "sec_filings": _rows_frame([], columns=WHY_IT_MOVED_SEC_COLUMNS),
            "messages": ["Symbol is required for compact metadata lookup."],
            "requested_lanes": list(WHY_IT_MOVED_METADATA_LANES),
        }

    messages: list[str] = []
    had_failure = False
    news_rows: list[dict[str, Any]] = []
    korean_news_rows: list[dict[str, Any]] = []
    sec_rows: list[dict[str, Any]] = []
    normalized_name = _clean_optional_text(name)

    try:
        news_rows = (news_fetcher or _fetch_yfinance_news_metadata)(normalized_symbol, max(0, int(max_news)))
    except Exception as exc:
        had_failure = True
        messages.append(f"뉴스 메타데이터 조회 실패: {exc}")

    try:
        korean_news_rows = (korean_news_fetcher or _fetch_google_news_kr_rss_metadata)(
            normalized_symbol,
            normalized_name,
            max(0, int(max_korean_news)),
            float(request_timeout),
        )
    except Exception as exc:
        had_failure = True
        messages.append(f"한국어 뉴스 메타데이터 조회 실패: {exc}")

    try:
        sec_rows = (sec_fetcher or _fetch_sec_recent_filing_metadata)(
            normalized_symbol,
            max(0, int(max_filings)),
            user_agent,
            float(request_timeout),
        )
    except Exception as exc:
        had_failure = True
        messages.append(f"SEC 메타데이터 조회 실패: {exc}")

    news = _normalize_news_metadata(news_rows, max_items=max_news)
    korean_news = _normalize_korean_news_metadata(korean_news_rows, max_items=max_korean_news)
    sec_filings = _normalize_sec_filing_metadata(sec_rows, max_items=max_filings)
    has_metadata = not news.empty or not korean_news.empty or not sec_filings.empty
    if has_metadata and had_failure:
        status = "PARTIAL"
    elif has_metadata:
        status = "OK"
    elif had_failure:
        status = "FAILED"
    else:
        status = "NO_METADATA"
        messages.append(f"{normalized_symbol}에 대해 간단 뉴스, 한국어 뉴스 또는 SEC 공시 메타데이터가 반환되지 않았습니다.")

    return {
        "status": status,
        "symbol": normalized_symbol,
        "fetched_at_utc": fetched_at,
        "news": news,
        "korean_news": korean_news,
        "sec_filings": sec_filings,
        "messages": messages,
        "requested_lanes": list(WHY_IT_MOVED_METADATA_LANES),
    }

__all__ = [
    "build_market_mover_catalyst_links",
    "build_market_mover_metadata_not_requested_state",
    "build_market_mover_research_snapshot",
    "build_market_mover_metadata_status_strip",
    "build_market_mover_why_it_moved_read_model",
    "fetch_market_mover_compact_metadata",
    "fetch_market_mover_news_metadata",
    "fetch_market_mover_sec_metadata",
    "merge_market_mover_metadata",
    "sort_market_mover_sec_filings_by_form_priority",
]
