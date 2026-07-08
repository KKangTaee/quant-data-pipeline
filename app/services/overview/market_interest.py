from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import pandas as pd

MARKET_INTEREST_LINK_COLUMNS = ["Source", "Lane", "Policy", "Evidence", "Caveat", "URL"]


def _clean_text(value: Any, *, upper: bool = False) -> str | None:
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
    return text.upper() if upper else text


def _rows_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=MARKET_INTEREST_LINK_COLUMNS)


def _google_search_url(query: str) -> str:
    return "https://www.google.com/search?q=" + quote_plus(query)


def _stockanalysis_forecast_url(symbol: str) -> str:
    return f"https://stockanalysis.com/stocks/{symbol.lower()}/forecast/"


def build_market_interest_original_links(*, symbol: str, name: str | None = None) -> pd.DataFrame:
    """Build source-attributed research links without fetching or storing source bodies."""

    normalized_symbol = _clean_text(symbol, upper=True) or ""
    normalized_name = _clean_text(name) or normalized_symbol
    if not normalized_symbol:
        return _rows_frame([])

    analyst_query = f"{normalized_symbol} {normalized_name} analyst upgrade downgrade price target"
    institution_query = f"{normalized_symbol} {normalized_name} 13F institutional holdings"
    return _rows_frame(
        [
            {
                "Source": "StockAnalysis Forecast",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Forecast / analyst page destination",
                "Caveat": "Commercial-data-backed public page; no durable storage in V1.",
                "URL": _stockanalysis_forecast_url(normalized_symbol),
            },
            {
                "Source": "Briefing.com Upgrades / Downgrades",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Daily analyst action calendar destination",
                "Caveat": "Public lead only; storage and scraping are not approved.",
                "URL": "https://www.briefing.com/calendars/updown?Filter=All",
            },
            {
                "Source": "MarketBeat Ratings",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Ratings / target-change destination",
                "Caveat": "Freemium aggregator; use as outbound reference first.",
                "URL": "https://www.marketbeat.com/ratings/",
            },
            {
                "Source": "Yahoo Finance Analysis",
                "Lane": "애널리스트 관심",
                "Policy": "external_research_link",
                "Evidence": "Quote analysis page destination",
                "Caveat": "Dynamic public page; no article/report body collection.",
                "URL": f"https://finance.yahoo.com/quote/{quote_plus(normalized_symbol)}/analysis/",
            },
            {
                "Source": "SEC Company Search",
                "Lane": "뉴스/공시 촉매",
                "Policy": "official_session_lookup",
                "Evidence": "Official company filing search destination",
                "Caveat": "Metadata and source links only unless a separate SEC digest scope is approved.",
                "URL": "https://www.sec.gov/edgar/search/#/q=" + quote_plus(f"{normalized_symbol} 8-K 10-Q 10-K"),
            },
            {
                "Source": "SEC Form 13F Data Sets",
                "Lane": "기관 보유 배경",
                "Policy": "official_durable_candidate",
                "Evidence": "Official quarterly 13F flattened datasets",
                "Caveat": "Requires CUSIP-symbol mapping before selected-symbol durable lookup.",
                "URL": "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets",
            },
            {
                "Source": "SEC 13F FAQ",
                "Lane": "기관 보유 배경",
                "Policy": "official_reference",
                "Evidence": "Official 13F reporting caveats",
                "Caveat": "Use to explain delayed quarterly filing scope.",
                "URL": (
                    "https://www.sec.gov/rules-regulations/staff-guidance/"
                    "division-investment-management-frequently-asked-questions/"
                    "frequently-asked-questions-about-form-13f"
                ),
            },
            {
                "Source": "WhaleWisdom",
                "Lane": "기관 보유 배경",
                "Policy": "external_research_link",
                "Evidence": "13F aggregator destination",
                "Caveat": "Freemium aggregator; SEC remains the durable source candidate.",
                "URL": _google_search_url(f"site:whalewisdom.com {institution_query}"),
            },
            {
                "Source": "Google Analyst Search",
                "Lane": "원문 확인",
                "Policy": "external_research_link",
                "Evidence": "General web search for analyst actions",
                "Caveat": "Search launch point only; no automatic cause judgment.",
                "URL": _google_search_url(analyst_query),
            },
        ]
    )


def _count_rows(value: Any) -> int:
    if isinstance(value, pd.DataFrame):
        return int(len(value.index))
    if isinstance(value, list):
        return int(len(value))
    return 0


def build_market_interest_read_model(*, mover: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a conservative selected-symbol market-interest investigation model."""

    row = dict(mover or {})
    normalized_symbol = _clean_text(row.get("Symbol") or row.get("symbol"), upper=True)
    name = _clean_text(row.get("Name") or row.get("name")) or normalized_symbol or ""
    links = build_market_interest_original_links(symbol=normalized_symbol or "", name=name)
    payload = dict(metadata or {})
    news_count = _count_rows(payload.get("news")) + _count_rows(payload.get("korean_news"))
    sec_count = _count_rows(payload.get("sec_filings"))
    news_sec_state = "관심 근거 있음" if news_count or sec_count else "원문 확인 필요"
    news_sec_detail = f"뉴스 {news_count}건 · SEC {sec_count}건"
    status = "READY" if payload and str(payload.get("status") or "").upper() != "NOT_REQUESTED" else "NOT_REQUESTED"
    summary_items = [
        {
            "id": "analyst_interest",
            "label": "애널리스트 관심",
            "state": "원문 확인 필요",
            "detail": "업그레이드/다운그레이드와 목표가 변경은 외부 원문 링크에서 확인합니다.",
            "tone": "neutral",
        },
        {
            "id": "news_sec",
            "label": "뉴스/공시 촉매",
            "state": news_sec_state,
            "detail": news_sec_detail,
            "tone": "success" if news_count or sec_count else "neutral",
        },
        {
            "id": "institutional_context",
            "label": "기관 보유 배경",
            "state": "지연 자료",
            "detail": "13F는 분기 지연 공시이며 V1은 원문/공식 출처 확인 경로만 제공합니다.",
            "tone": "warning",
        },
        {
            "id": "original_links",
            "label": "원문 확인",
            "state": "원문 확인",
            "detail": f"{len(links.index)}개 출처 링크",
            "tone": "neutral",
        },
    ]
    return {
        "schema_version": "market_interest_evidence_v1",
        "status": status,
        "symbol": normalized_symbol,
        "name": name,
        "summary_items": summary_items,
        "original_links": links,
        "institutional_caveats": [
            "13F는 분기 공시 기반 지연 자료이며 분기 종료 후 최대 45일 늦게 제출될 수 있습니다.",
            "13F는 숏 포지션, 파생, 헤지, 실시간 거래 의도, 전체 포트폴리오 맥락을 완전히 보여주지 않습니다.",
            "선택 종목 기준 공식 DB 조회에는 CUSIP-symbol mapping과 quarter comparison 설계가 필요합니다.",
        ],
        "source_policy_note": (
            "Official SEC sources can become durable data only after schema and mapping approval; "
            "public analyst aggregators stay external links or session-only metadata in V1."
        ),
        "boundary_note": (
            "시장 관심 근거는 조사 보조 정보입니다. 추천, 점수화, 매매 신호, "
            "자동 catalyst 판정, live trading, broker order, auto rebalance와 연결하지 않습니다."
        ),
    }


__all__ = [
    "MARKET_INTEREST_LINK_COLUMNS",
    "build_market_interest_original_links",
    "build_market_interest_read_model",
]
