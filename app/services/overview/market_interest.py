from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import pandas as pd

MARKET_INTEREST_LINK_COLUMNS = ["Source", "Lane", "Policy", "Evidence", "Caveat", "URL"]
SEC_FORM_DISPLAY_TITLES = {
    "144": "SEC Form 144 · 제한/지배주식 매각 예정 통지",
    "8-K": "SEC Form 8-K · 주요 이벤트 공시",
    "10-Q": "SEC Form 10-Q · 분기 보고서",
    "10-K": "SEC Form 10-K · 연간 보고서",
    "4": "SEC Form 4 · 내부자 거래 보고",
}


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
                "Lane": "SEC 공시 촉매",
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


def _records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, pd.DataFrame):
        return value.fillna("").to_dict("records")
    if isinstance(value, list):
        return [dict(row) for row in value if isinstance(row, dict)]
    return []


def _link_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return []
    return frame.fillna("").to_dict("records")


def _links_for_lane(frame: pd.DataFrame, lane: str) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty or "Lane" not in frame.columns:
        return []
    return _link_records(frame[frame["Lane"] == lane])


def _news_catalyst_rows(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _records(metadata.get("news")):
        rows.append(
            {
                "Kind": "News",
                "Region": "US",
                "Title": _clean_text(row.get("Title")) or "-",
                "Source": _clean_text(row.get("Source")) or "-",
                "Published At": _clean_text(row.get("Published At")) or "-",
                "Snippet": "",
                "Form": "",
                "URL": _clean_text(row.get("URL")) or "",
            }
        )
    for row in _records(metadata.get("korean_news")):
        rows.append(
            {
                "Kind": "News",
                "Region": "KR",
                "Title": _clean_text(row.get("Title")) or "-",
                "Source": _clean_text(row.get("Source")) or "-",
                "Published At": _clean_text(row.get("Published At")) or "-",
                "Snippet": _clean_text(row.get("Snippet")) or "",
                "Form": "",
                "URL": _clean_text(row.get("URL")) or "",
            }
        )
    return rows


def _sec_filing_display_title(*, form: str, title: str | None) -> str:
    clean_form = _clean_text(form, upper=True) or "-"
    clean_title = _clean_text(title)
    fallback = SEC_FORM_DISPLAY_TITLES.get(clean_form, f"SEC Form {clean_form}" if clean_form != "-" else "SEC Filing")
    if not clean_title:
        return fallback
    if clean_title.strip().upper() == clean_form:
        return fallback
    return clean_title


def _sec_filing_catalyst_rows(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _records(metadata.get("sec_filings")):
        form = _clean_text(row.get("Form")) or "-"
        rows.append(
            {
                "Kind": "SEC Filing",
                "Region": "US",
                "Title": _sec_filing_display_title(form=form, title=_clean_text(row.get("Title"))),
                "Source": "SEC EDGAR",
                "Published At": _clean_text(row.get("Filing Date")) or "-",
                "Snippet": "",
                "Form": form,
                "URL": _clean_text(row.get("URL")) or "",
            }
        )
    return rows


def build_market_interest_read_model(*, mover: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a conservative selected-symbol market-interest investigation model."""

    row = dict(mover or {})
    normalized_symbol = _clean_text(row.get("Symbol") or row.get("symbol"), upper=True)
    name = _clean_text(row.get("Name") or row.get("name")) or normalized_symbol or ""
    links = build_market_interest_original_links(symbol=normalized_symbol or "", name=name)
    payload = dict(metadata or {})
    us_news_count = _count_rows(payload.get("news"))
    korean_news_count = _count_rows(payload.get("korean_news"))
    news_count = us_news_count + korean_news_count
    sec_count = _count_rows(payload.get("sec_filings"))
    status = "READY" if payload and str(payload.get("status") or "").upper() != "NOT_REQUESTED" else "NOT_REQUESTED"
    news_state = f"뉴스 {news_count}건" if news_count else ("뉴스 없음" if status == "READY" else "조회 전")
    sec_state = f"공시 {sec_count}건" if sec_count else ("공시 없음" if status == "READY" else "조회 전")
    news_detail = f"US {us_news_count}건 · KR {korean_news_count}건"
    sec_detail = f"SEC issuer filing {sec_count}건"
    source_rows = _link_records(links)
    news_rows = _news_catalyst_rows(payload)
    sec_rows = _sec_filing_catalyst_rows(payload)
    summary_items = [
        {
            "id": "analyst_interest",
            "label": "애널리스트 관심",
            "state": "구조화 소스 미연결",
            "detail": "API key/약관 승인 전이라 애널리스트 action은 외부 확인 링크만 제공합니다.",
            "tone": "neutral",
        },
        {
            "id": "news_catalysts",
            "label": "뉴스 리스트",
            "state": news_state,
            "detail": news_detail,
            "tone": "success" if news_count else "neutral",
        },
        {
            "id": "sec_filing_catalysts",
            "label": "SEC 공시 촉매",
            "state": sec_state,
            "detail": sec_detail,
            "tone": "success" if sec_count else "neutral",
        },
        {
            "id": "institutional_context",
            "label": "기관 보유 배경",
            "state": "13F 지연 자료",
            "detail": "13F는 분기 지연 공시이며 V1은 원문/공식 출처 확인 경로만 제공합니다.",
            "tone": "warning",
        },
        {
            "id": "sources",
            "label": "출처/원문 링크",
            "state": f"출처 {len(source_rows)}개",
            "detail": "섹션별 evidence 아래에서 원문과 source policy를 확인합니다.",
            "tone": "neutral",
        },
    ]
    evidence_sections = [
        {
            "id": "analyst_interest",
            "title": "애널리스트 관심",
            "state": "구조화 소스 미연결",
            "provider_status": "DISCONNECTED",
            "description": "업그레이드/다운그레이드와 목표가 변경은 구조화 source 승인 전까지 외부 링크로만 확인합니다.",
            "rows": [],
            "source_rows": _links_for_lane(links, "애널리스트 관심"),
        },
        {
            "id": "news_catalysts",
            "title": "뉴스 리스트",
            "state": news_state,
            "description": "선택 종목의 뉴스 metadata입니다.",
            "rows": news_rows,
            "source_rows": [],
        },
        {
            "id": "sec_filing_catalysts",
            "title": "SEC 공시 촉매",
            "state": sec_state,
            "description": "선택 종목의 최근 SEC issuer filing metadata입니다.",
            "rows": sec_rows,
            "source_rows": _links_for_lane(links, "SEC 공시 촉매"),
        },
        {
            "id": "institutional_context",
            "title": "기관 보유 배경 · 13F 지연 자료",
            "state": "13F 지연 자료",
            "description": "13F는 issuer 공시가 아니라 기관투자운용사 보유 보고이며 실시간 거래 의도를 보여주지 않습니다.",
            "rows": [
                {"Kind": "13F Caveat", "Region": "US", "Title": caveat, "Source": "SEC", "Published At": "", "URL": ""}
                for caveat in [
                    "분기 공시 기반 지연 자료이며 분기 종료 후 최대 45일 늦게 제출될 수 있습니다.",
                    "숏 포지션, 파생, 헤지, 실시간 거래 의도, 전체 포트폴리오 맥락을 완전히 보여주지 않습니다.",
                    "선택 종목 공식 조회에는 CUSIP-symbol mapping과 quarter comparison 설계가 필요합니다.",
                ]
            ],
            "source_rows": _links_for_lane(links, "기관 보유 배경"),
        },
    ]
    return {
        "schema_version": "market_interest_evidence_v3",
        "status": status,
        "symbol": normalized_symbol,
        "name": name,
        "summary_items": summary_items,
        "evidence_sections": evidence_sections,
        "original_links": links,
        "source_disclosure": {
            "title": "출처/원문 링크",
            "rows": source_rows,
        },
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
