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

from finance.loaders.sentiment import (
    CNN_COMPONENT_SERIES,
    CORE_SENTIMENT_SERIES,
    load_market_sentiment_history,
    load_market_sentiment_snapshot,
)

PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly", "yearly": "Yearly"}

UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000 by market cap",
    "TOP2000": "Top 2000 by market cap",
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
    }

__all__ = [
    "build_market_mover_catalyst_links",
    "build_market_mover_metadata_not_requested_state",
    "build_market_mover_metadata_status_strip",
    "build_market_mover_why_it_moved_read_model",
    "fetch_market_mover_compact_metadata",
    "sort_market_mover_sec_filings_by_form_priority",
]
