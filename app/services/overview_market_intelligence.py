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


QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

VALID_PERIODS = {"daily": 1, "weekly": 5, "monthly": 21, "yearly": 252}
PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly", "yearly": "Yearly"}
VALID_GROUPS = {"sector", "industry"}
GROUP_TREND_PERIODS = {
    "daily": {"step": 1, "windows": 21, "window_label": "Last 1M"},
    "weekly": {"step": 5, "windows": 13, "window_label": "Last 3M"},
    "monthly": {"step": 21, "windows": 12, "window_label": "Last 12M"},
}
MARKET_INTRADAY_REFRESH_MINUTES = 5
MARKET_INTRADAY_STALE_MINUTES = 15
EVENT_ESTIMATE_STALE_DAYS = 14
EVENT_RECENT_WINDOW_DAYS = 7
MAJOR_MACRO_EVENT_TYPES = {
    "FOMC_MEETING",
    "MACRO_CPI",
    "MACRO_PPI",
    "MACRO_EMPLOYMENT",
    "MACRO_GDP",
}
UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000 by market cap",
    "TOP2000": "Top 2000 by market cap",
}
MOVERS_COLUMNS = [
    "Rank",
    "Symbol",
    "Name",
    "Return %",
    "Previous Return %",
    "Momentum Delta pp",
    "Volume",
    "Dollar Volume",
    "Start Price",
    "End Price",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Date",
    "End Date",
    "Previous Start Date",
    "Previous End Date",
    "Price Source",
]
VOLUME_COLUMNS = [
    "Rank",
    "Symbol",
    "Name",
    "Volume Metric",
    "Volume Basis",
    "Volume",
    "Dollar Volume",
    "Avg Daily Volume",
    "Total Volume",
    "Avg Daily Dollar Volume",
    "Total Dollar Volume",
    "Volume Days",
    "Return %",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Date",
    "End Date",
    "Price Source",
]
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
MISSING_COLUMNS = [
    "Symbol",
    "Name",
    "Sector",
    "Industry",
    "Reason",
    "Recommended Action",
    "Start Date",
    "End Date",
    "Start Price",
    "End Price",
    "Latest Price Date",
    "Profile Status",
    "Profile Error",
    "Profile Collected At",
]
GROUP_COLUMNS = [
    "Rank",
    "Group",
    "Group Type",
    "Symbols",
    "Positive Symbols",
    "Positive Symbol Share %",
    "Equal Weight Return %",
    "Market Cap Weighted Return %",
    "Cap vs Equal Gap pp",
    "Top 3 Positive Share %",
    "Top Symbol",
    "Top Symbol Return %",
    "Start Date",
    "End Date",
]
GROUP_TREND_COLUMNS = [
    "Date",
    "Group",
    "Group Type",
    "Symbols",
    "Equal Weight Return %",
    "Market Cap Weighted Return %",
    "Top Symbol",
    "Top Symbol Return %",
    "Start Date",
    "End Date",
]
GROUP_TICKER_LEADER_COLUMNS = [
    "Group",
    "Group Type",
    "Rank",
    "Symbol",
    "Name",
    "Return %",
    "Previous Return %",
    "Momentum Delta pp",
    "Positive Return Share %",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Price",
    "End Price",
    "Start Date",
    "End Date",
    "Previous Start Date",
    "Previous End Date",
]
EVENT_COLUMNS = [
    "Date",
    "Days Until",
    "Window",
    "Type",
    "Symbol",
    "Title",
    "Importance",
    "Focus",
    "Source Type",
    "Validation",
    "Freshness",
    "Quality Action",
    "Event Status",
    "Age Days",
    "Source",
    "Confidence",
    "Collected At",
    "Source URL",
]
OPS_COLUMNS = [
    "Area",
    "Status",
    "Data Freshness",
    "Last Success",
    "Last Issue",
    "Last Auto Run",
    "Auto Source",
    "Next Auto Due",
    "Last Manual Run",
    "Failure Streak",
    "Rows",
    "Processed",
    "Failed",
    "Duration Sec",
    "Next Action",
    "Message",
]
SENTIMENT_COLUMNS = [
    "Series",
    "Value",
    "Label",
    "Observation Date",
    "Staleness Days",
    "Status",
    "Source",
]
SENTIMENT_COMPONENT_COLUMNS = [
    "Series",
    "Score",
    "Rating",
    "Observation Date",
    "Status",
]
SENTIMENT_HISTORY_COLUMNS = [
    "Date",
    "Series",
    "Value",
    "Source",
]
SENTIMENT_SERIES_LABELS = {
    "CNN_FEAR_GREED": "CNN Fear & Greed",
    "AAII_BULLISH": "AAII Bullish",
    "AAII_NEUTRAL": "AAII Neutral",
    "AAII_BEARISH": "AAII Bearish",
    "AAII_BULL_BEAR_SPREAD": "AAII Bull-Bear Spread",
    "CNN_FNG_MARKET_MOMENTUM_SP500": "Market Momentum",
    "CNN_FNG_STOCK_PRICE_STRENGTH": "Stock Price Strength",
    "CNN_FNG_STOCK_PRICE_BREADTH": "Stock Price Breadth",
    "CNN_FNG_PUT_CALL_OPTIONS": "Put / Call Options",
    "CNN_FNG_MARKET_VOLATILITY_VIX": "Market Volatility",
    "CNN_FNG_JUNK_BOND_DEMAND": "Junk Bond Demand",
    "CNN_FNG_SAFE_HAVEN_DEMAND": "Safe Haven Demand",
}
AAII_HISTORICAL_AVERAGES = {
    "bullish": 38.0,
    "neutral": 31.5,
    "bearish": 30.5,
}
CNN_COMPONENT_LEARNING_NOTES = {
    "Market Momentum": {
        "label_ko": "지수 추세",
        "what_it_checks": "S&P 500이 125일 이동평균 대비 얼마나 강한지 봅니다.",
        "greed_meaning": "지수 자체의 추세가 강해 투자자들이 위험을 받아들이는 쪽입니다.",
        "fear_meaning": "지수가 중기 평균 아래로 약해져 투자자들이 조심스러워진 상태입니다.",
        "neutral_meaning": "지수 추세가 뚜렷하게 한쪽으로 치우치지 않았습니다.",
    },
    "Stock Price Strength": {
        "label_ko": "신고가 확산",
        "what_it_checks": "NYSE 52주 신고가 종목과 신저가 종목의 균형을 봅니다.",
        "greed_meaning": "많은 종목이 신고가를 만들며 상승 리더십이 넓어지는 상태입니다.",
        "fear_meaning": "신고가보다 약한 종목이 많아 상승 리더십이 좁아진 상태입니다.",
        "neutral_meaning": "신고가와 신저가 압력이 크게 기울지 않았습니다.",
    },
    "Stock Price Breadth": {
        "label_ko": "시장 폭",
        "what_it_checks": "상승 종목 거래량과 하락 종목 거래량의 균형을 봅니다.",
        "greed_meaning": "상승 종목 쪽으로 거래가 넓게 붙어 시장 참여가 강합니다.",
        "fear_meaning": "상승 참여 폭이 약해 지수 상승이 일부 종목에 기대고 있을 수 있습니다.",
        "neutral_meaning": "상승/하락 참여 폭이 뚜렷하게 갈리지 않았습니다.",
    },
    "Put / Call Options": {
        "label_ko": "옵션 포지션",
        "what_it_checks": "풋옵션과 콜옵션 수요의 균형을 봅니다.",
        "greed_meaning": "방어적 풋 수요보다 상승 또는 위험선호 옵션 수요가 강합니다.",
        "fear_meaning": "풋옵션 수요가 늘어 하락 방어 심리가 강합니다.",
        "neutral_meaning": "옵션 시장의 상승/방어 수요가 크게 치우치지 않았습니다.",
    },
    "Market Volatility": {
        "label_ko": "변동성",
        "what_it_checks": "VIX가 50일 평균 대비 얼마나 높거나 낮은지 봅니다.",
        "greed_meaning": "변동성 압력이 낮아 시장이 비교적 안정을 가격에 반영합니다.",
        "fear_meaning": "변동성 압력이 높아 투자자들이 급락 위험을 더 크게 봅니다.",
        "neutral_meaning": "변동성은 현재 공포/탐욕 어느 쪽도 강하게 말하지 않습니다.",
    },
    "Junk Bond Demand": {
        "label_ko": "신용 위험선호",
        "what_it_checks": "고위험 회사채와 우량채의 금리 스프레드를 봅니다.",
        "greed_meaning": "고위험 채권 수요가 강해 신용시장도 위험을 받아들이는 쪽입니다.",
        "fear_meaning": "고위험 채권 수요가 약해 신용시장은 방어적으로 움직입니다.",
        "neutral_meaning": "신용시장의 위험선호가 크게 기울지 않았습니다.",
    },
    "Safe Haven Demand": {
        "label_ko": "주식 vs 안전자산",
        "what_it_checks": "최근 20거래일 주식과 국채 성과 차이를 봅니다.",
        "greed_meaning": "국채보다 주식 선호가 강해 위험자산 선호가 우세합니다.",
        "fear_meaning": "주식보다 국채 선호가 강해 방어적 심리가 우세합니다.",
        "neutral_meaning": "주식과 국채 선호가 크게 갈리지 않았습니다.",
    },
}
OPS_INTRADAY_TARGETS = [
    {
        "area": "S&P 500 Daily Snapshot",
        "universe_code": "SP500",
        "job_names": ["collect_sp500_intraday_snapshot"],
        "missing_action": "Run Update Daily Snapshot for S&P 500.",
        "due_action": "Refresh S&P 500 daily snapshot before using daily movers.",
    },
    {
        "area": "Top1000 Daily Snapshot",
        "universe_code": "TOP1000",
        "job_names": ["collect_top1000_intraday_snapshot"],
        "missing_action": "Run Update Daily Snapshot for Top1000.",
        "due_action": "Refresh Top1000 daily snapshot before using daily movers.",
    },
    {
        "area": "Top2000 Daily Snapshot",
        "universe_code": "TOP2000",
        "job_names": ["collect_top2000_intraday_snapshot"],
        "missing_action": "Run Update Daily Snapshot for Top2000.",
        "due_action": "Refresh Top2000 daily snapshot before using daily movers.",
    },
]
OPS_FUTURES_TARGETS = [
    {
        "area": "Futures Monitor 1m OHLCV",
        "job_names": ["collect_futures_ohlcv"],
        "missing_action": "Run Refresh Futures OHLCV from Overview > Futures Monitor.",
        "due_action": "Refresh Futures OHLCV before using pre-open futures context.",
    },
]
OPS_SENTIMENT_TARGET = {
    "area": "Market Sentiment",
    "job_names": ["collect_market_sentiment"],
    "missing_action": "Run Refresh Market Sentiment from Overview > Sentiment or Ingestion.",
    "due_action": "Refresh CNN Fear & Greed / AAII sentiment before relying on market sentiment context.",
}
OPS_EVENT_TARGETS = [
    {
        "area": "FOMC Calendar",
        "event_type": "FOMC_MEETING",
        "job_names": ["collect_fomc_calendar"],
        "fresh_days": 30,
        "stale_days": 90,
        "missing_action": "Run Refresh FOMC Calendar.",
        "due_action": "Refresh FOMC Calendar from the official Fed page.",
    },
    {
        "area": "Earnings Calendar",
        "event_type": "EARNINGS",
        "job_names": ["collect_earnings_calendar"],
        "fresh_days": 1,
        "stale_days": EVENT_ESTIMATE_STALE_DAYS,
        "missing_action": "Run Refresh Earnings Calendar for latest movers or a bounded batch.",
        "due_action": "Refresh Earnings Calendar before relying on upcoming dates.",
    },
    {
        "area": "Macro Calendar",
        "event_type": "MACRO",
        "event_types": ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT", "MACRO_GDP"],
        "job_names": ["collect_macro_calendar", "import_bls_macro_calendar_ics"],
        "fresh_days": 7,
        "stale_days": 30,
        "missing_action": "Run Refresh Macro Calendar or import the BLS .ics file.",
        "due_action": "Refresh Macro Calendar from official schedules or import the BLS .ics file.",
    },
]
OPS_SCHEDULE_CADENCE_MINUTES = {
    "collect_sp500_universe": 24 * 60,
    "collect_sp500_intraday_snapshot": 5,
    "collect_top1000_intraday_snapshot": 15,
    "collect_top2000_intraday_snapshot": 30,
    "collect_futures_ohlcv": 1,
    "collect_market_sentiment": 24 * 60,
    "collect_fomc_calendar": 24 * 60,
    "collect_earnings_calendar": 24 * 60,
    "collect_macro_calendar": 24 * 60,
}


def _default_query(db_name: str, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    import pymysql

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        port=3306,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cur.execute(f"USE {db_name}")
            cur.execute(sql, params)
            return list(cur.fetchall())
    finally:
        conn.close()


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _iso_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d")


def _display_datetime(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d %H:%M")


def _stale_days(effective_date: str | None, *, today: date | None = None) -> int | None:
    if not effective_date:
        return None
    today_value = pd.Timestamp(today or date.today()).normalize()
    effective_value = pd.Timestamp(effective_date).normalize()
    if pd.isna(effective_value):
        return None
    return max(0, int((today_value - effective_value).days))


def _stale_minutes(snapshot_time: str | None) -> int | None:
    if not snapshot_time:
        return None
    snapshot_value = pd.Timestamp(snapshot_time)
    if pd.isna(snapshot_value):
        return None
    now_value = pd.Timestamp.now(tz="UTC")
    if snapshot_value.tzinfo is None:
        snapshot_value = snapshot_value.tz_localize("UTC")
    else:
        snapshot_value = snapshot_value.tz_convert("UTC")
    return max(0, int((now_value - snapshot_value).total_seconds() // 60))


def _normalize_limit(value: int, *, default: int, min_value: int, max_value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(min_value, min(parsed, max_value))


def _normalize_universe_code(universe_code: str | None, universe_limit: int) -> str:
    normalized = str(universe_code or "").strip().upper()
    if normalized in UNIVERSE_LABELS:
        return normalized
    return "TOP2000" if int(universe_limit or 1000) >= 2000 else "TOP1000"


def _universe_limit_from_code(universe_code: str, fallback: int) -> int:
    if universe_code == "TOP2000":
        return 2000
    if universe_code == "TOP1000":
        return 1000
    return fallback


def _empty_movers_snapshot(
    *,
    status: str,
    period: str,
    universe_code: str,
    universe_limit: int,
    top_n: int,
    message: str,
    sector: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "period": period,
        "period_label": PERIOD_LABELS.get(period, period),
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "sector": sector or "All",
        "top_n": top_n,
        "rows": pd.DataFrame(columns=MOVERS_COLUMNS),
        "volume_rows": pd.DataFrame(columns=VOLUME_COLUMNS),
        "missing_rows": pd.DataFrame(columns=MISSING_COLUMNS),
        "date_window": {},
        "coverage": {
            "universe_count": 0,
            "returnable_count": 0,
            "missing_count": 0,
            "latest_raw_date": None,
            "effective_end_date": None,
            "stale_days": None,
            "price_mode": "Unavailable",
        },
        "warnings": [message] if message else [],
    }


def _empty_group_snapshot(
    *,
    status: str,
    group_by: str,
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "group_by": group_by,
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "period": period,
        "period_label": PERIOD_LABELS.get(period, period),
        "trend_window_label": GROUP_TREND_PERIODS.get(period, {}).get("window_label"),
        "top_n": top_n,
        "rows": pd.DataFrame(columns=GROUP_COLUMNS),
        "trend_rows": pd.DataFrame(columns=GROUP_TREND_COLUMNS),
        "ticker_leader_rows": pd.DataFrame(columns=GROUP_TICKER_LEADER_COLUMNS),
        "missing_rows": pd.DataFrame(columns=MISSING_COLUMNS),
        "date_window": {},
        "coverage": {
            "universe_count": 0,
            "returnable_count": 0,
            "missing_count": 0,
            "latest_raw_date": None,
            "effective_end_date": None,
            "stale_days": None,
        },
        "warnings": [message] if message else [],
    }


def _empty_events_snapshot(
    *,
    status: str,
    start_date: str,
    end_date: str,
    event_type: str | None,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "event_type": event_type or "All",
        "rows": pd.DataFrame(columns=EVENT_COLUMNS),
        "date_window": {"start_date": start_date, "end_date": end_date},
        "coverage": {
            "event_count": 0,
            "next_event_date": None,
            "latest_recent_event_date": None,
            "latest_collected_at": None,
            "source_count": 0,
            "official_count": 0,
            "estimate_count": 0,
            "estimate_only_count": 0,
            "cross_checked_count": 0,
            "not_confirmed_count": 0,
            "stale_estimate_count": 0,
            "action_required_count": 0,
            "high_importance_count": 0,
            "needs_review_count": 0,
            "this_week_count": 0,
            "next_30d_count": 0,
            "recent_event_count": 0,
            "upcoming_event_count": 0,
            "recent_high_importance_count": 0,
            "upcoming_high_importance_count": 0,
            "superseded_count": 0,
        },
        "warnings": [message] if message else [],
    }


def _empty_ops_snapshot(*, message: str) -> dict[str, Any]:
    return {
        "status": "NO_STATUS",
        "rows": pd.DataFrame(columns=OPS_COLUMNS),
        "coverage": {
            "job_count": 0,
            "ok_count": 0,
            "due_count": 0,
            "stale_count": 0,
            "missing_count": 0,
            "failed_count": 0,
            "partial_count": 0,
            "latest_success_at": None,
            "latest_issue_at": None,
        },
        "warnings": [message] if message else [],
    }


def _empty_sentiment_analysis(*, status: str, message: str) -> dict[str, Any]:
    return {
        "phase": "DATA_REVIEW",
        "phase_label": "데이터 확인",
        "tone": "danger" if status == "ERROR" else "warning",
        "headline": "시장 심리 해석에 필요한 데이터가 부족합니다.",
        "summary": message,
        "data_confidence": {
            "status": "Blocked" if status == "ERROR" else "Needs refresh",
            "tone": "danger" if status == "ERROR" else "warning",
            "detail": message,
        },
        "driver_summary": {"greed_count": 0, "fear_count": 0, "neutral_count": 0},
        "driver_groups": {"greed": [], "fear": [], "neutral": []},
        "analysis_steps": [
            {
                "title": "데이터 상태",
                "status": status,
                "tone": "danger" if status == "ERROR" else "warning",
                "detail": message,
            }
        ],
        "next_checks": [
            {
                "target": "Market Sentiment refresh",
                "reason": "CNN / AAII observations must be available before reading sentiment context.",
                "tone": "warning",
            }
        ],
    }


def _empty_sentiment_snapshot(*, status: str, message: str) -> dict[str, Any]:
    return {
        "status": status,
        "rows": pd.DataFrame(columns=SENTIMENT_COLUMNS),
        "component_rows": pd.DataFrame(columns=SENTIMENT_COMPONENT_COLUMNS),
        "history_rows": pd.DataFrame(columns=SENTIMENT_HISTORY_COLUMNS),
        "coverage": {
            "cnn_score": None,
            "cnn_rating": None,
            "aaii_bearish": None,
            "aaii_bull_bear_spread": None,
            "source_count": 0,
            "stale_count": 0,
            "missing_count": 2,
        },
        "analysis": _empty_sentiment_analysis(status=status, message=message),
        "warnings": [message] if message else [],
    }


def _metadata_from_row(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    raw = row.get("missing_fields_json") if isinstance(row, pd.Series) else row.get("missing_fields_json")
    if not raw:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    try:
        parsed = json.loads(str(raw))
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _latest_sentiment_row(frame: pd.DataFrame, series_id: str) -> pd.Series | None:
    if frame.empty or "series_id" not in frame:
        return None
    rows = frame[frame["series_id"].astype(str).str.upper() == series_id].copy()
    if rows.empty:
        return None
    rows["observation_date_sort"] = pd.to_datetime(rows.get("observation_date"), errors="coerce")
    rows = rows.sort_values("observation_date_sort", ascending=False)
    return rows.iloc[0]


def _sentiment_status(row: pd.Series | None) -> str:
    if row is None:
        return "Missing"
    if str(row.get("snapshot_status") or row.get("coverage_status") or "").lower() not in {"actual", "ok"}:
        return "Stale"
    return "OK"


def _sentiment_display_value(series_id: str, value: Any) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "-"
    if series_id == "AAII_BULL_BEAR_SPREAD":
        return f"{numeric:+.1f} pp"
    if series_id.startswith("AAII_"):
        return f"{numeric:.1f}%"
    return f"{numeric:.1f}"


def _sentiment_table_row(row: pd.Series, *, label: str) -> dict[str, Any]:
    series_id = str(row.get("series_id") or "").upper()
    metadata = _metadata_from_row(row)
    return {
        "Series": label,
        "Value": _sentiment_display_value(series_id, row.get("value")),
        "Label": metadata.get("rating") or "-",
        "Observation Date": _iso_date(row.get("observation_date")) or "-",
        "Staleness Days": _safe_float(row.get("staleness_days")),
        "Status": _sentiment_status(row),
        "Source": row.get("source") or "-",
    }


def _sentiment_score_bucket(value: Any) -> dict[str, str]:
    numeric = _safe_float(value)
    if numeric is None:
        return {"label": "Missing", "label_ko": "데이터 없음", "direction": "neutral", "tone": "warning"}
    if numeric < 25:
        return {"label": "Extreme Fear", "label_ko": "극단적 공포", "direction": "fear", "tone": "danger"}
    if numeric < 45:
        return {"label": "Fear", "label_ko": "공포", "direction": "fear", "tone": "warning"}
    if numeric < 55:
        return {"label": "Neutral", "label_ko": "중립", "direction": "neutral", "tone": "neutral"}
    if numeric < 75:
        return {"label": "Greed", "label_ko": "탐욕", "direction": "greed", "tone": "positive"}
    return {"label": "Extreme Greed", "label_ko": "극단적 탐욕", "direction": "greed", "tone": "positive"}


def _cnn_component_note(series: Any) -> dict[str, str]:
    key = str(series or "")
    return CNN_COMPONENT_LEARNING_NOTES.get(
        key,
        {
            "label_ko": key or "-",
            "what_it_checks": "CNN Fear & Greed를 구성하는 세부 시장 행동 지표입니다.",
            "greed_meaning": "이 값이 높으면 해당 지표는 위험선호 쪽으로 해석합니다.",
            "fear_meaning": "이 값이 낮으면 해당 지표는 방어적 심리 쪽으로 해석합니다.",
            "neutral_meaning": "이 값이 중립이면 해당 지표만으로는 방향성이 강하지 않습니다.",
        },
    )


def _cnn_component_current_reading(series: Any, bucket: dict[str, str]) -> str:
    note = _cnn_component_note(series)
    direction = bucket.get("direction")
    label_ko = note.get("label_ko") or str(series or "-")
    if direction == "greed":
        return f"{label_ko}: {note['greed_meaning']}"
    if direction == "fear":
        return f"{label_ko}: {note['fear_meaning']}"
    return f"{label_ko}: {note['neutral_meaning']}"


def _join_component_labels(rows: list[dict[str, Any]]) -> str:
    labels = []
    for row in rows:
        note = _cnn_component_note(row.get("series"))
        labels.append(note.get("label_ko") or str(row.get("series") or "-"))
    return ", ".join(labels) if labels else "해당 신호 없음"


def _sentiment_driver_groups(component_rows: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    groups: dict[str, list[dict[str, Any]]] = {"greed": [], "fear": [], "neutral": []}
    for row in component_rows:
        bucket = _sentiment_score_bucket(row.get("Score"))
        direction = bucket["direction"]
        note = _cnn_component_note(row.get("Series"))
        groups[direction].append(
            {
                "series": row.get("Series") or "-",
                "label_ko": note["label_ko"],
                "score": row.get("Score"),
                "rating": row.get("Rating") or "-",
                "rating_label_ko": bucket["label_ko"],
                "tone": bucket["tone"],
                "direction": direction,
                "what_it_checks": note["what_it_checks"],
                "current_reading": _cnn_component_current_reading(row.get("Series"), bucket),
            }
        )
    summary = {
        "greed_count": len(groups["greed"]),
        "fear_count": len(groups["fear"]),
        "neutral_count": len(groups["neutral"]),
    }
    return groups, summary


def _sentiment_component_explanations(component_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    explanations: list[dict[str, Any]] = []
    for row in component_rows:
        bucket = _sentiment_score_bucket(row.get("Score"))
        note = _cnn_component_note(row.get("Series"))
        explanations.append(
            {
                "series": row.get("Series") or "-",
                "label_ko": note["label_ko"],
                "score": row.get("Score"),
                "rating": row.get("Rating") or "-",
                "rating_label_ko": bucket["label_ko"],
                "direction": bucket["direction"],
                "tone": bucket["tone"],
                "what_it_checks": note["what_it_checks"],
                "greed_meaning": note["greed_meaning"],
                "fear_meaning": note["fear_meaning"],
                "current_reading": _cnn_component_current_reading(row.get("Series"), bucket),
            }
        )
    return explanations


def _aaii_pessimism_status(*, bearish: float | None, spread: float | None) -> dict[str, str]:
    if bearish is None:
        return {
            "status": "데이터 없음",
            "tone": "warning",
            "detail": "AAII bearish sentiment가 아직 없습니다.",
        }
    bearish_gap = bearish - AAII_HISTORICAL_AVERAGES["bearish"]
    spread_text = "-" if spread is None else f"{spread:+.1f}pp"
    if bearish >= 50 or (spread is not None and spread <= -20):
        status = "비관 강함"
        tone = "danger"
    elif bearish >= 35 or (spread is not None and spread < 0):
        status = "비관 우위"
        tone = "warning"
    elif bearish <= 25 and spread is not None and spread > 10:
        status = "낙관 우위"
        tone = "positive"
    else:
        status = "균형"
        tone = "neutral"
    return {
        "status": status,
        "tone": tone,
        "detail": f"Bearish {bearish:.1f}%는 장기 평균보다 {bearish_gap:+.1f}pp 높고, bull-bear spread는 {spread_text}입니다.",
    }


def _market_sentiment_phase(
    *,
    cnn_score: float | None,
    aaii_bearish: float | None,
    aaii_spread: float | None,
    driver_summary: dict[str, int],
    missing_count: int,
    stale_count: int,
) -> dict[str, str]:
    if missing_count or cnn_score is None or aaii_bearish is None:
        return {
            "phase": "DATA_REVIEW",
            "phase_label": "데이터 확인",
            "tone": "warning",
            "headline": "시장 심리 해석에 필요한 핵심 데이터가 부족합니다.",
            "summary": "CNN Fear & Greed와 AAII bearish sentiment를 갱신한 뒤 다시 확인하세요.",
        }
    if stale_count:
        return {
            "phase": "STALE_REVIEW",
            "phase_label": "신선도 확인",
            "tone": "warning",
            "headline": "저장된 시장 심리 데이터가 오래됐습니다.",
            "summary": "해석은 가능하지만 최신 시장 상태로 보기 전에 수집을 갱신하는 편이 안전합니다.",
        }

    greed_count = int(driver_summary.get("greed_count") or 0)
    fear_count = int(driver_summary.get("fear_count") or 0)
    split_drivers = greed_count > 0 and fear_count > 0
    if cnn_score < 25 and aaii_bearish >= 45:
        return {
            "phase": "FEAR_STRESS",
            "phase_label": "공포 압력",
            "tone": "danger",
            "headline": "공포 심리가 강하게 우세합니다.",
            "summary": "CNN score와 AAII bearish가 동시에 방어적입니다. 가격 반등보다 위험 관리 확인이 먼저입니다.",
        }
    if cnn_score >= 75 and aaii_spread is not None and aaii_spread >= 10:
        return {
            "phase": "EUPHORIA_RISK",
            "phase_label": "탐욕 과열",
            "tone": "warning",
            "headline": "탐욕 심리가 과열권에 가깝습니다.",
            "summary": "강한 위험 선호가 보이지만 과열과 crowding 가능성을 함께 확인해야 합니다.",
        }
    if (45 <= cnn_score < 55 and (split_drivers or (aaii_spread is not None and aaii_spread <= 0))) or (
        cnn_score < 60 and split_drivers and aaii_spread is not None and aaii_spread <= 0
    ):
        return {
            "phase": "MIXED_NEUTRAL",
            "phase_label": "혼합 중립",
            "tone": "neutral",
            "headline": "중립이지만 내부는 엇갈린 시장 심리입니다.",
            "summary": "헤드라인 점수는 중립권이지만 일부 CNN 구성요소는 탐욕, 일부는 공포를 가리킵니다. AAII도 약한 비관 쪽입니다.",
        }
    if cnn_score >= 55:
        return {
            "phase": "GREED_LEANING",
            "phase_label": "탐욕 우위",
            "tone": "positive",
            "headline": "탐욕 심리가 우위입니다.",
            "summary": "위험 선호가 우세하지만 AAII와 breadth가 같은 방향인지 확인해야 합니다.",
        }
    return {
        "phase": "FEAR_LEANING",
        "phase_label": "공포 우위",
        "tone": "warning",
        "headline": "공포 심리가 우위입니다.",
        "summary": "방어적 심리가 우세합니다. 반등 신호보다 breadth와 credit confirmation을 먼저 확인하세요.",
    }


def _build_market_sentiment_analysis(
    *,
    coverage: dict[str, Any],
    component_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    cnn_score = _safe_float(coverage.get("cnn_score"))
    aaii_bearish = _safe_float(coverage.get("aaii_bearish"))
    aaii_spread = _safe_float(coverage.get("aaii_bull_bear_spread"))
    missing_count = int(coverage.get("missing_count") or 0)
    stale_count = int(coverage.get("stale_count") or 0)
    driver_groups, driver_summary = _sentiment_driver_groups(component_rows)
    phase = _market_sentiment_phase(
        cnn_score=cnn_score,
        aaii_bearish=aaii_bearish,
        aaii_spread=aaii_spread,
        driver_summary=driver_summary,
        missing_count=missing_count,
        stale_count=stale_count,
    )
    cnn_bucket = _sentiment_score_bucket(cnn_score)
    aaii_status = _aaii_pessimism_status(bearish=aaii_bearish, spread=aaii_spread)
    data_confidence = {
        "status": "High" if missing_count == 0 and stale_count == 0 else "Review",
        "tone": "positive" if missing_count == 0 and stale_count == 0 else "warning",
        "detail": f"{coverage.get('source_count') or 0}개 source 준비, missing {missing_count}, stale {stale_count}.",
    }
    greed_rows = driver_groups["greed"]
    fear_rows = driver_groups["fear"]
    neutral_rows = driver_groups["neutral"]
    greed_labels = _join_component_labels(greed_rows)
    fear_labels = _join_component_labels(fear_rows)
    neutral_clause = "" if not neutral_rows else f" 중립 신호는 {_join_component_labels(neutral_rows)}입니다."
    cnn_score_text = "-" if cnn_score is None else f"{cnn_score:.1f}"
    aaii_spread_text = "-" if aaii_spread is None else f"{aaii_spread:+.1f}pp"
    analysis_steps = [
        {
            "title": "지금 결론",
            "status": phase["phase_label"],
            "tone": phase["tone"],
            "detail": f"{phase['headline']} {phase['summary']}",
        },
        {
            "title": "왜 이렇게 보나",
            "status": f"CNN {cnn_score_text} · AAII spread {aaii_spread_text}",
            "tone": cnn_bucket["tone"],
            "detail": f"CNN 헤드라인은 {cnn_bucket['label_ko']}권이고, {aaii_status['detail']} 그래서 겉으로는 중립에 가깝지만 설문은 약한 비관을 보탭니다.",
        },
        {
            "title": "강한 신호",
            "status": f"{driver_summary['greed_count']}개 탐욕 쪽",
            "tone": "positive" if greed_rows else "neutral",
            "detail": f"{greed_labels} 신호는 위험선호를 가리킵니다.",
        },
        {
            "title": "약한 신호",
            "status": f"{driver_summary['fear_count']}개 공포 쪽",
            "tone": "warning" if fear_rows else "neutral",
            "detail": f"{fear_labels}는 시장 참여 폭, 상승 리더십, 신용시장 중 일부가 약하다는 신호입니다.{neutral_clause}",
        },
        {
            "title": "그래서 어떻게 보나",
            "status": phase["phase_label"],
            "tone": phase["tone"],
            "detail": "지수는 버티지만 내부 체력은 확인이 필요한 상태입니다. 강한 상승장 확신보다는 혼합 중립으로 두고 breadth, credit, macro 확인을 붙입니다.",
        },
        {
            "title": "다음 확인",
            "status": "확인 필요",
            "tone": "neutral",
            "detail": "Market Movers breadth, Futures Macro Thermometer, Events calendar가 같은 방향인지 보면 이 중립이 건강한 중립인지, 취약한 중립인지 갈라집니다.",
        },
    ]
    return {
        **phase,
        "data_confidence": data_confidence,
        "driver_summary": driver_summary,
        "driver_groups": driver_groups,
        "component_explanations": _sentiment_component_explanations(component_rows),
        "analysis_steps": analysis_steps,
        "next_checks": [
            {
                "target": "Market Movers breadth",
                "reason": "상승 종목 비중이 넓으면 건강한 중립, 좁으면 일부 대형주 중심 중립일 수 있습니다.",
                "watch_for": "상승 종목 수, sector breadth, Stock Price Breadth와 같은 방향인지 확인",
                "tone": "neutral",
            },
            {
                "target": "Futures Macro Thermometer",
                "reason": "주식 심리와 금리/달러/원자재 압력이 충돌하면 headline 중립을 그대로 믿기 어렵습니다.",
                "watch_for": "risk-on, rate pressure, dollar pressure가 sentiment와 같은 방향인지 확인",
                "tone": "neutral",
            },
            {
                "target": "Events calendar",
                "reason": "FOMC, CPI, earnings 같은 이벤트가 심리 급변의 원인인지 확인합니다.",
                "watch_for": "다가오는 고중요 이벤트와 stale estimate 여부",
                "tone": "neutral",
            },
        ],
    }


def build_market_sentiment_snapshot(
    *,
    snapshot_rows: pd.DataFrame | None = None,
    history_rows: pd.DataFrame | None = None,
    today: date | None = None,
    max_history_days: int = 180,
) -> dict[str, Any]:
    """Build the Overview sentiment read model from stored CNN / AAII observations."""
    today_value = today or date.today()
    start_date = (pd.Timestamp(today_value) - pd.Timedelta(days=max_history_days)).strftime("%Y-%m-%d")
    end_date = pd.Timestamp(today_value).strftime("%Y-%m-%d")
    try:
        snapshot_frame = (
            snapshot_rows.copy()
            if isinstance(snapshot_rows, pd.DataFrame)
            else load_market_sentiment_snapshot(as_of_date=end_date, max_staleness_days=14)
        )
        history_frame = (
            history_rows.copy()
            if isinstance(history_rows, pd.DataFrame)
            else load_market_sentiment_history(
                series_ids=("CNN_FEAR_GREED", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD"),
                start=start_date,
                end=end_date,
            )
        )
    except Exception as exc:
        return _empty_sentiment_snapshot(status="ERROR", message=f"Market sentiment snapshot failed: {exc}")

    if snapshot_frame.empty:
        return _empty_sentiment_snapshot(
            status="MISSING",
            message="Stored CNN Fear & Greed / AAII sentiment rows are not available. Run Market Sentiment refresh.",
        )

    for frame in (snapshot_frame, history_frame):
        for column in ("observation_date", "collected_at"):
            if column in frame:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
        if "value" in frame:
            frame["value"] = pd.to_numeric(frame["value"], errors="coerce")

    ordered_core = ["CNN_FEAR_GREED", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD", "AAII_BULLISH", "AAII_NEUTRAL"]
    table_rows: list[dict[str, Any]] = []
    missing_core = 0
    stale_count = 0
    for series_id in ordered_core:
        row = _latest_sentiment_row(snapshot_frame, series_id)
        if row is None:
            if series_id in {"CNN_FEAR_GREED", "AAII_BEARISH"}:
                missing_core += 1
            continue
        status = _sentiment_status(row)
        if status != "OK":
            stale_count += 1
        table_rows.append(_sentiment_table_row(row, label=SENTIMENT_SERIES_LABELS.get(series_id, series_id)))

    component_rows: list[dict[str, Any]] = []
    for series_id in CNN_COMPONENT_SERIES:
        row = _latest_sentiment_row(snapshot_frame, series_id)
        if row is None:
            continue
        metadata = _metadata_from_row(row)
        component_rows.append(
            {
                "Series": SENTIMENT_SERIES_LABELS.get(series_id, series_id),
                "Score": round(float(row.get("value")), 1) if _safe_float(row.get("value")) is not None else None,
                "Rating": metadata.get("rating") or "-",
                "Observation Date": _iso_date(row.get("observation_date")) or "-",
                "Status": _sentiment_status(row),
            }
        )

    history_out = pd.DataFrame(columns=SENTIMENT_HISTORY_COLUMNS)
    if isinstance(history_frame, pd.DataFrame) and not history_frame.empty:
        visible_history = history_frame[
            history_frame.get("series_id", pd.Series(dtype=str)).astype(str).str.upper().isin(
                {"CNN_FEAR_GREED", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD"}
            )
        ].copy()
        if not visible_history.empty:
            visible_history["Date"] = visible_history["observation_date"].map(_iso_date)
            visible_history["Series"] = visible_history["series_id"].map(
                lambda value: SENTIMENT_SERIES_LABELS.get(str(value).upper(), str(value))
            )
            visible_history["Value"] = visible_history["value"].map(lambda value: round(float(value), 2) if _safe_float(value) is not None else None)
            visible_history["Source"] = visible_history.get("source", pd.Series(dtype=str))
            history_out = visible_history[SENTIMENT_HISTORY_COLUMNS].dropna(subset=["Date"]).sort_values(["Date", "Series"])

    cnn_row = _latest_sentiment_row(snapshot_frame, "CNN_FEAR_GREED")
    cnn_meta = _metadata_from_row(cnn_row) if cnn_row is not None else {}
    aaii_bearish_row = _latest_sentiment_row(snapshot_frame, "AAII_BEARISH")
    aaii_spread_row = _latest_sentiment_row(snapshot_frame, "AAII_BULL_BEAR_SPREAD")
    warnings: list[str] = []
    if missing_core:
        warnings.append("CNN Fear & Greed or AAII bearish sentiment is missing from stored observations.")
    if stale_count:
        warnings.append("One or more sentiment observations are stale or partial.")
    status = "OK" if missing_core == 0 and stale_count == 0 else "REVIEW" if table_rows else "MISSING"
    coverage = {
        "cnn_score": _safe_float(cnn_row.get("value")) if cnn_row is not None else None,
        "cnn_rating": cnn_meta.get("rating") if cnn_row is not None else None,
        "aaii_bearish": _safe_float(aaii_bearish_row.get("value")) if aaii_bearish_row is not None else None,
        "aaii_bull_bear_spread": _safe_float(aaii_spread_row.get("value")) if aaii_spread_row is not None else None,
        "source_count": len({str(row.get("Source") or "") for row in table_rows if row.get("Source")}),
        "stale_count": stale_count,
        "missing_count": missing_core,
    }
    return {
        "status": status,
        "rows": pd.DataFrame(table_rows, columns=SENTIMENT_COLUMNS),
        "component_rows": pd.DataFrame(component_rows, columns=SENTIMENT_COMPONENT_COLUMNS),
        "history_rows": history_out,
        "coverage": coverage,
        "analysis": _build_market_sentiment_analysis(coverage=coverage, component_rows=component_rows),
        "warnings": warnings,
    }


def _query_latest_raw_date(query_fn: QueryFn) -> str | None:
    rows = query_fn(
        "finance_price",
        """
        SELECT MAX(`date`) AS latest_raw_date
        FROM nyse_price_history
        WHERE timeframe = %s
        """,
        ["1d"],
    )
    if not rows:
        return None
    return _iso_date(rows[0].get("latest_raw_date"))


def _eligible_market_dates(
    *,
    min_price_rows: int,
    limit: int,
    query_fn: QueryFn,
) -> tuple[str | None, list[dict[str, Any]]]:
    latest_raw_date = _query_latest_raw_date(query_fn)
    bounded_since: str | None = None
    latest_raw_ts = pd.Timestamp(latest_raw_date) if latest_raw_date else pd.NaT
    if not pd.isna(latest_raw_ts):
        lookback_days = max(370, int(limit) * 4)
        bounded_since = (latest_raw_ts.normalize() - pd.Timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    def query_dates(*, since: str | None) -> list[dict[str, Any]]:
        conditions = ["timeframe = %s"]
        params: list[Any] = ["1d"]
        if since:
            conditions.append("`date` >= %s")
            params.append(since)
        params.extend([int(min_price_rows), int(limit)])
        return query_fn(
            "finance_price",
            f"""
        SELECT
            `date`,
            SUM(CASE WHEN COALESCE(adj_close, close) IS NOT NULL THEN 1 ELSE 0 END) AS usable_rows
        FROM nyse_price_history FORCE INDEX (ix_date)
        WHERE {" AND ".join(conditions)}
        GROUP BY `date`
        HAVING usable_rows >= %s
        ORDER BY `date` DESC
        LIMIT %s
        """,
            params,
        )

    rows = query_dates(since=bounded_since)
    if bounded_since and len(rows) < int(limit):
        rows = query_dates(since=None)
    eligible = [
        {
            "date": _iso_date(row.get("date")),
            "usable_rows": int(row.get("usable_rows") or 0),
        }
        for row in rows
        if _iso_date(row.get("date"))
    ]
    return latest_raw_date, eligible


def resolve_effective_market_dates(
    *,
    period: str = "daily",
    min_price_rows: int = 1000,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Resolve the latest usable daily price window for overview market scans."""
    normalized_period = str(period or "daily").strip().lower()
    if normalized_period not in VALID_PERIODS:
        raise ValueError(f"Unsupported period: {period!r}")

    query = query_fn or _default_query
    offset = VALID_PERIODS[normalized_period]
    latest_raw_date, eligible = _eligible_market_dates(
        min_price_rows=min_price_rows,
        limit=(offset * 2) + 1,
        query_fn=query,
    )
    if len(eligible) <= offset:
        return {
            "status": "INSUFFICIENT_DATA",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "start_date": None,
            "end_date": eligible[0]["date"] if eligible else None,
            "latest_raw_date": latest_raw_date,
            "effective_end_date": eligible[0]["date"] if eligible else None,
            "eligible_dates": eligible,
            "stale_days": _stale_days(eligible[0]["date"] if eligible else None, today=today),
            "message": "Not enough eligible daily price rows to resolve the requested period.",
        }

    end_row = eligible[0]
    start_row = eligible[offset]
    return {
        "status": "OK",
        "period": normalized_period,
        "period_label": PERIOD_LABELS[normalized_period],
        "start_date": start_row["date"],
        "end_date": end_row["date"],
        "latest_raw_date": latest_raw_date,
        "effective_end_date": end_row["date"],
        "eligible_dates": eligible,
        "stale_days": _stale_days(end_row["date"], today=today),
        "message": "",
    }


def resolve_group_trend_market_dates(
    *,
    period: str = "monthly",
    min_price_rows: int = 1000,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Resolve non-overlapping windows for sector / industry leadership trends."""
    normalized_period = str(period or "monthly").strip().lower()
    if normalized_period not in GROUP_TREND_PERIODS:
        raise ValueError(f"Unsupported group trend period: {period!r}")

    query = query_fn or _default_query
    spec = GROUP_TREND_PERIODS[normalized_period]
    step = int(spec["step"])
    requested_windows = int(spec["windows"])
    latest_raw_date, eligible = _eligible_market_dates(
        min_price_rows=min_price_rows,
        limit=(step * requested_windows) + 1,
        query_fn=query,
    )
    available_windows = min(requested_windows, max(0, (len(eligible) - 1) // step))
    if available_windows <= 0:
        return {
            "status": "INSUFFICIENT_DATA",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "trend_window_label": spec["window_label"],
            "start_date": None,
            "end_date": eligible[0]["date"] if eligible else None,
            "latest_raw_date": latest_raw_date,
            "effective_end_date": eligible[0]["date"] if eligible else None,
            "eligible_dates": eligible,
            "windows": [],
            "stale_days": _stale_days(eligible[0]["date"] if eligible else None, today=today),
            "message": "Not enough eligible daily price rows to resolve group trend windows.",
        }

    windows: list[dict[str, Any]] = []
    for index in range(available_windows):
        end_row = eligible[index * step]
        start_row = eligible[(index + 1) * step]
        windows.append(
            {
                "start_date": start_row["date"],
                "end_date": end_row["date"],
                "label": end_row["date"],
                "usable_rows": end_row["usable_rows"],
            }
        )
    windows.reverse()
    latest_window = windows[-1]
    return {
        "status": "OK",
        "period": normalized_period,
        "period_label": PERIOD_LABELS[normalized_period],
        "trend_window_label": spec["window_label"],
        "start_date": latest_window["start_date"],
        "end_date": latest_window["end_date"],
        "latest_raw_date": latest_raw_date,
        "effective_end_date": latest_window["end_date"],
        "eligible_dates": eligible,
        "windows": windows,
        "stale_days": _stale_days(latest_window["end_date"], today=today),
        "message": "",
    }


def _filter_sector(rows: list[dict[str, Any]], sector: str | None) -> list[dict[str, Any]]:
    normalized = str(sector or "All").strip()
    if not normalized or normalized == "All":
        return rows
    return [row for row in rows if str(row.get("sector") or "Unknown") == normalized]


def _load_universe(
    *,
    universe_code: str,
    universe_limit: int,
    query_fn: QueryFn,
    sector: str | None = None,
) -> list[dict[str, Any]]:
    if universe_code == "SP500":
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                m.symbol,
                COALESCE(NULLIF(p.long_name, ''), NULLIF(m.name, ''), s.name) AS long_name,
                COALESCE(p.sector, m.sector) AS sector,
                COALESCE(p.industry, m.industry) AS industry,
                p.market_cap,
                p.status,
                p.error_msg,
                p.last_collected_at,
                m.as_of_date AS universe_as_of_date,
                m.collected_at AS universe_collected_at,
                m.source AS universe_source,
                m.source_url AS universe_source_url
            FROM market_universe_member m
            LEFT JOIN nyse_asset_profile p
              ON p.symbol = m.symbol
             AND p.kind = %s
            LEFT JOIN nyse_stock s
              ON s.symbol = m.symbol
            WHERE m.universe_code = %s
              AND m.active = 1
            ORDER BY COALESCE(p.market_cap, 0) DESC, m.symbol ASC
            """,
            ["stock", "SP500"],
        )
        return _filter_sector(rows, sector)

    return _filter_sector(
        query_fn(
            "finance_meta",
            """
            SELECT
                p.symbol,
                COALESCE(NULLIF(p.long_name, ''), s.name) AS long_name,
                p.sector,
                p.industry,
                p.market_cap,
                p.status,
                p.error_msg,
                p.last_collected_at,
                NULL AS universe_as_of_date,
                NULL AS universe_collected_at,
                'nyse_asset_profile' AS universe_source,
                NULL AS universe_source_url
            FROM nyse_asset_profile p
            LEFT JOIN nyse_stock s
              ON s.symbol = p.symbol
            WHERE p.kind = %s
              AND p.country = %s
              AND p.market_cap IS NOT NULL
              AND p.market_cap > 0
              AND (p.is_spac IS NULL OR p.is_spac <> 1)
              AND (p.status IS NULL OR LOWER(p.status) NOT IN ('dilist', 'delist', 'delisted'))
            ORDER BY p.market_cap DESC, p.symbol ASC
            LIMIT %s
            """,
            ["stock", "United States", int(universe_limit)],
        ),
        sector,
    )


def load_market_mover_sector_options(
    *,
    universe_code: str = "TOP1000",
    universe_limit: int = 1000,
    query_fn: QueryFn | None = None,
) -> list[str]:
    query = query_fn or _default_query
    try:
        normalized = _normalize_universe_code(universe_code, universe_limit)
        limit = _universe_limit_from_code(normalized, universe_limit)
        rows = _load_universe(universe_code=normalized, universe_limit=limit, query_fn=query)
    except Exception:
        return []
    sectors = sorted({str(row.get("sector") or "Unknown") for row in rows})
    return sectors


def _load_prices_for_dates(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[tuple[str, str], float]:
    points = _load_price_points_for_dates(symbols=symbols, dates=dates, query_fn=query_fn)
    return {
        key: float(value["price"])
        for key, value in points.items()
        if value.get("price") is not None
    }


def _load_price_points_for_dates(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[tuple[str, str], dict[str, float | int | None]]:
    if not symbols or not dates:
        return {}

    symbol_placeholders = ",".join(["%s"] * len(symbols))
    date_placeholders = ",".join(["%s"] * len(dates))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT
            symbol,
            `date`,
            COALESCE(adj_close, close) AS price,
            volume
        FROM nyse_price_history FORCE INDEX (uk_symbol_timeframe_date)
        WHERE symbol IN ({symbol_placeholders})
          AND timeframe = %s
          AND `date` IN ({date_placeholders})
        """,
        list(symbols) + ["1d"] + list(dates),
    )
    points: dict[tuple[str, str], dict[str, float | int | None]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        row_date = _iso_date(row.get("date"))
        price = _safe_float(row.get("price"))
        if not symbol or not row_date or price is None:
            continue
        volume = _safe_float(row.get("volume"))
        points[(symbol, row_date)] = {
            "price": price,
            "volume": int(volume) if volume is not None else None,
        }
    return points


def _previous_period_window(date_window: dict[str, Any], *, period: str) -> dict[str, str] | None:
    normalized_period = str(period or "daily").strip().lower()
    offset = VALID_PERIODS.get(normalized_period)
    if offset is None:
        return None
    eligible = list(date_window.get("eligible_dates") or [])
    if len(eligible) <= offset * 2:
        return None
    previous_start = _iso_date(eligible[offset * 2].get("date"))
    previous_end = _iso_date(eligible[offset].get("date"))
    if not previous_start or not previous_end:
        return None
    return {
        "previous_start_date": previous_start,
        "previous_end_date": previous_end,
    }


def _return_pct(start_price: float | None, end_price: float | None) -> float | None:
    if start_price is None or end_price is None or start_price <= 0:
        return None
    return (float(end_price) / float(start_price) - 1.0) * 100.0


def _previous_return_context(
    *,
    symbols: list[str],
    date_window: dict[str, Any],
    period: str,
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    previous_window = _previous_period_window(date_window, period=period)
    if not previous_window:
        return {}
    previous_start = previous_window["previous_start_date"]
    previous_end = previous_window["previous_end_date"]
    points = _load_price_points_for_dates(
        symbols=symbols,
        dates=[previous_start, previous_end],
        query_fn=query_fn,
    )
    context: dict[str, dict[str, Any]] = {}
    for symbol in symbols:
        start_price = _safe_float((points.get((symbol, previous_start)) or {}).get("price"))
        end_price = _safe_float((points.get((symbol, previous_end)) or {}).get("price"))
        previous_return = _return_pct(start_price, end_price)
        if previous_return is None:
            continue
        context[symbol] = {
            "previous_return_pct": previous_return,
            "previous_start_date": previous_start,
            "previous_end_date": previous_end,
        }
    return context


def _load_latest_price_dates(*, symbols: list[str], query_fn: QueryFn) -> dict[str, str]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT symbol, MAX(`date`) AS latest_price_date
        FROM nyse_price_history
        WHERE symbol IN ({placeholders})
          AND timeframe = %s
          AND COALESCE(adj_close, close) IS NOT NULL
        GROUP BY symbol
        """,
        list(symbols) + ["1d"],
    )
    return {
        str(row.get("symbol") or "").strip().upper(): _iso_date(row.get("latest_price_date")) or ""
        for row in rows
        if row.get("symbol")
    }


def _profile_collected_at(item: dict[str, Any]) -> str | None:
    return _display_datetime(item.get("last_collected_at"))


def _missing_row(
    *,
    item: dict[str, Any],
    reason: str,
    start_date: str,
    end_date: str,
    start_price: float | None,
    end_price: float | None,
    latest_price_date: str | None,
) -> dict[str, Any]:
    return {
        "Symbol": str(item.get("symbol") or "").strip().upper(),
        "Name": item.get("long_name") or "-",
        "Sector": item.get("sector") or "Unknown",
        "Industry": item.get("industry") or "Unknown",
        "Reason": reason,
        "Recommended Action": _missing_recommended_action(reason),
        "Start Date": start_date,
        "End Date": end_date,
        "Start Price": round(float(start_price), 4) if start_price is not None else None,
        "End Price": round(float(end_price), 4) if end_price is not None else None,
        "Latest Price Date": latest_price_date,
        "Profile Status": item.get("status") or "-",
        "Profile Error": item.get("error_msg") or "-",
        "Profile Collected At": _profile_collected_at(item) or "-",
    }


def _missing_recommended_action(reason: str) -> str:
    normalized = str(reason or "").lower()
    if "intraday snapshot row" in normalized:
        return "Run Update Daily Snapshot for this coverage."
    if "latest quote" in normalized or "latest price" in normalized or "intraday return" in normalized:
        return "Refresh the daily snapshot; if it persists, inspect provider quote coverage."
    if "previous close" in normalized or "start price" in normalized:
        return "Refresh daily OHLCV history or inspect previous-close coverage."
    if "end price" in normalized:
        return "Refresh daily OHLCV history for the latest market date."
    if "non-positive" in normalized:
        return "Inspect price history for split or corporate action issues."
    return "Inspect provider data, then rerun the relevant refresh."


def _build_return_rows(
    *,
    universe: list[dict[str, Any]],
    start_date: str,
    end_date: str,
    query_fn: QueryFn,
    previous_context: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    symbols = [str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")]
    price_points = _load_price_points_for_dates(symbols=symbols, dates=[start_date, end_date], query_fn=query_fn)
    previous_context = previous_context or {}
    return_rows: list[dict[str, Any]] = []
    missing_candidates: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []

    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        start_point = price_points.get((symbol, start_date)) or {}
        end_point = price_points.get((symbol, end_date)) or {}
        start_price = _safe_float(start_point.get("price"))
        end_price = _safe_float(end_point.get("price"))
        if start_price is None and end_price is None:
            reason = "missing start and end price"
        elif start_price is None:
            reason = "missing start price"
        elif end_price is None:
            reason = "missing end price"
        elif start_price <= 0:
            reason = "non-positive start price"
        else:
            reason = ""
        if reason:
            missing_candidates.append(
                {
                    "item": item,
                    "symbol": symbol,
                    "reason": reason,
                    "start_price": start_price,
                    "end_price": end_price,
                }
            )
            continue
        return_pct = _return_pct(start_price, end_price)
        if return_pct is None:
            continue
        volume = _safe_float(end_point.get("volume"))
        previous = previous_context.get(symbol) or {}
        previous_return = _safe_float(previous.get("previous_return_pct"))
        return_rows.append(
            {
                "symbol": symbol,
                "name": item.get("long_name") or "",
                "sector": item.get("sector") or "Unknown",
                "industry": item.get("industry") or "Unknown",
                "market_cap": _safe_float(item.get("market_cap")) or 0.0,
                "start_price": start_price,
                "end_price": end_price,
                "return_pct": return_pct,
                "previous_return_pct": previous_return,
                "momentum_delta_pp": (return_pct - previous_return) if previous_return is not None else None,
                "volume": int(volume) if volume is not None else None,
                "dollar_volume": (float(end_price) * float(volume)) if volume is not None else None,
                "start_date": start_date,
                "end_date": end_date,
                "previous_start_date": previous.get("previous_start_date"),
                "previous_end_date": previous.get("previous_end_date"),
                "price_source": "EOD DB",
            }
        )
    if missing_candidates:
        latest_dates = _load_latest_price_dates(
            symbols=[str(row["symbol"]) for row in missing_candidates],
            query_fn=query_fn,
        )
        for row in missing_candidates:
            missing_rows.append(
                _missing_row(
                    item=row["item"],
                    reason=str(row["reason"]),
                    start_date=start_date,
                    end_date=end_date,
                    start_price=_safe_float(row.get("start_price")),
                    end_price=_safe_float(row.get("end_price")),
                    latest_price_date=latest_dates.get(str(row["symbol"])),
                )
            )
    return return_rows, missing_rows


def _build_return_rows_from_price_map(
    *,
    universe: list[dict[str, Any]],
    start_date: str,
    end_date: str,
    price_map: dict[tuple[str, str], float],
) -> list[dict[str, Any]]:
    return_rows: list[dict[str, Any]] = []
    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        start_price = price_map.get((symbol, start_date))
        end_price = price_map.get((symbol, end_date))
        if start_price is None or end_price is None or start_price <= 0:
            continue
        return_rows.append(
            {
                "symbol": symbol,
                "name": item.get("long_name") or "",
                "sector": item.get("sector") or "Unknown",
                "industry": item.get("industry") or "Unknown",
                "market_cap": _safe_float(item.get("market_cap")) or 0.0,
                "start_price": start_price,
                "end_price": end_price,
                "return_pct": (float(end_price) / float(start_price) - 1.0) * 100.0,
                "start_date": start_date,
                "end_date": end_date,
                "price_source": "EOD DB",
            }
        )
    return return_rows


def _group_leadership_rows(
    *,
    return_rows: list[dict[str, Any]],
    group_by: str,
    min_group_size: int,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in return_rows:
        group_name = str(row.get(group_by) or "Unknown").strip() or "Unknown"
        grouped.setdefault(group_name, []).append(row)

    group_rows: list[dict[str, Any]] = []
    for group_name, rows in grouped.items():
        if len(rows) < int(min_group_size):
            continue
        equal_weight_return = sum(float(row["return_pct"]) for row in rows) / len(rows)
        weighted_denominator = sum(max(float(row.get("market_cap") or 0.0), 0.0) for row in rows)
        if weighted_denominator > 0:
            weighted_return = (
                sum(max(float(row.get("market_cap") or 0.0), 0.0) * float(row["return_pct"]) for row in rows)
                / weighted_denominator
            )
        else:
            weighted_return = equal_weight_return
        top_symbol = max(rows, key=lambda row: float(row["return_pct"]))
        positive_symbols = sum(1 for row in rows if float(row.get("return_pct") or 0.0) > 0)
        positive_symbol_share = (positive_symbols / len(rows)) * 100.0 if rows else 0.0
        positive_returns = sorted(
            [max(float(row.get("return_pct") or 0.0), 0.0) for row in rows],
            reverse=True,
        )
        positive_return_total = sum(positive_returns)
        top3_positive_share = (
            (sum(positive_returns[:3]) / positive_return_total) * 100.0
            if positive_return_total > 0
            else None
        )
        group_rows.append(
            {
                "group": group_name,
                "group_type": group_by.title(),
                "symbols": len(rows),
                "positive_symbols": positive_symbols,
                "positive_symbol_share": positive_symbol_share,
                "equal_weight_return": equal_weight_return,
                "market_cap_weighted_return": weighted_return,
                "cap_vs_equal_gap_pp": weighted_return - equal_weight_return,
                "top3_positive_share": top3_positive_share,
                "top_symbol": top_symbol["symbol"],
                "top_symbol_return": top_symbol["return_pct"],
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    return group_rows


def _rank_group_rows(group_rows: list[dict[str, Any]], *, top_n: int | None = None) -> list[dict[str, Any]]:
    ranked = sorted(
        group_rows,
        key=lambda row: (
            -float(row["market_cap_weighted_return"]),
            -float(row["equal_weight_return"]),
            row["group"],
        ),
    )
    return ranked[:top_n] if top_n is not None else ranked


def _group_rows_frame(group_rows: list[dict[str, Any]]) -> pd.DataFrame:
    rows = [
        {
            "Rank": index,
            "Group": row["group"],
            "Group Type": row["group_type"],
            "Symbols": row["symbols"],
            "Positive Symbols": row.get("positive_symbols"),
            "Positive Symbol Share %": round(float(row.get("positive_symbol_share") or 0.0), 2),
            "Equal Weight Return %": round(float(row["equal_weight_return"]), 2),
            "Market Cap Weighted Return %": round(float(row["market_cap_weighted_return"]), 2),
            "Cap vs Equal Gap pp": round(float(row.get("cap_vs_equal_gap_pp") or 0.0), 2),
            "Top 3 Positive Share %": round(float(row["top3_positive_share"]), 2)
            if row.get("top3_positive_share") is not None
            else None,
            "Top Symbol": row["top_symbol"],
            "Top Symbol Return %": round(float(row["top_symbol_return"]), 2),
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
        }
        for index, row in enumerate(group_rows, start=1)
    ]
    return pd.DataFrame(rows, columns=GROUP_COLUMNS)


def _group_trend_rows_frame(
    *,
    windows: list[dict[str, Any]],
    universe: list[dict[str, Any]],
    groups: set[str],
    group_by: str,
    min_group_size: int,
    query_fn: QueryFn,
) -> pd.DataFrame:
    if not windows or not groups:
        return pd.DataFrame(columns=GROUP_TREND_COLUMNS)
    symbols = [str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")]
    dates = sorted({str(window["start_date"]) for window in windows} | {str(window["end_date"]) for window in windows})
    price_map = _load_prices_for_dates(symbols=symbols, dates=dates, query_fn=query_fn)
    trend_rows: list[dict[str, Any]] = []
    for window in windows:
        return_rows = _build_return_rows_from_price_map(
            universe=universe,
            start_date=str(window["start_date"]),
            end_date=str(window["end_date"]),
            price_map=price_map,
        )
        group_rows = _group_leadership_rows(
            return_rows=return_rows,
            group_by=group_by,
            min_group_size=min_group_size,
            start_date=str(window["start_date"]),
            end_date=str(window["end_date"]),
        )
        for row in group_rows:
            if row["group"] not in groups:
                continue
            trend_rows.append(
                {
                    "Date": window["end_date"],
                    "Group": row["group"],
                    "Group Type": row["group_type"],
                    "Symbols": row["symbols"],
                    "Equal Weight Return %": round(float(row["equal_weight_return"]), 2),
                    "Market Cap Weighted Return %": round(float(row["market_cap_weighted_return"]), 2),
                    "Top Symbol": row["top_symbol"],
                    "Top Symbol Return %": round(float(row["top_symbol_return"]), 2),
                    "Start Date": row["start_date"],
                    "End Date": row["end_date"],
                }
            )
    return pd.DataFrame(trend_rows, columns=GROUP_TREND_COLUMNS)


def _group_trend_rows_from_group_rows(
    *,
    group_rows: list[dict[str, Any]],
    groups: set[str],
    date_value: str,
) -> pd.DataFrame:
    trend_rows = [
        {
            "Date": date_value,
            "Group": row["group"],
            "Group Type": row["group_type"],
            "Symbols": row["symbols"],
            "Equal Weight Return %": round(float(row["equal_weight_return"]), 2),
            "Market Cap Weighted Return %": round(float(row["market_cap_weighted_return"]), 2),
            "Top Symbol": row["top_symbol"],
            "Top Symbol Return %": round(float(row["top_symbol_return"]), 2),
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
        }
        for row in group_rows
        if row["group"] in groups
    ]
    return pd.DataFrame(trend_rows, columns=GROUP_TREND_COLUMNS)


def _group_ticker_leader_rows_frame(
    *,
    return_rows: list[dict[str, Any]],
    positive_groups: set[str],
    group_by: str,
) -> pd.DataFrame:
    if not return_rows or not positive_groups:
        return pd.DataFrame(columns=GROUP_TICKER_LEADER_COLUMNS)

    normalized_groups = {str(group).strip() for group in positive_groups if str(group).strip()}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in return_rows:
        group_name = str(row.get(group_by) or "Unknown").strip() or "Unknown"
        if group_name not in normalized_groups:
            continue
        return_pct = _safe_float(row.get("return_pct"))
        if return_pct is None or return_pct <= 0:
            continue
        grouped.setdefault(group_name, []).append(row)

    leader_rows: list[dict[str, Any]] = []
    for group_name in sorted(grouped):
        rows = sorted(
            grouped[group_name],
            key=lambda row: (
                -float(row.get("return_pct") or 0.0),
                str(row.get("symbol") or ""),
            ),
        )
        positive_return_total = sum(max(float(row.get("return_pct") or 0.0), 0.0) for row in rows)
        for rank, row in enumerate(rows, start=1):
            return_pct = float(row.get("return_pct") or 0.0)
            previous_return = _safe_float(row.get("previous_return_pct"))
            leader_rows.append(
                {
                    "Group": group_name,
                    "Group Type": group_by.title(),
                    "Rank": rank,
                    "Symbol": str(row.get("symbol") or "").strip().upper(),
                    "Name": row.get("name") or "-",
                    "Return %": round(return_pct, 2),
                    "Previous Return %": round(float(previous_return), 2)
                    if previous_return is not None
                    else None,
                    "Momentum Delta pp": round(float(return_pct - previous_return), 2)
                    if previous_return is not None
                    else None,
                    "Positive Return Share %": round(
                        (return_pct / positive_return_total) * 100.0,
                        2,
                    )
                    if positive_return_total > 0
                    else None,
                    "Sector": row.get("sector") or "Unknown",
                    "Industry": row.get("industry") or "Unknown",
                    "Market Cap": round(float(row.get("market_cap") or 0.0), 2),
                    "Start Price": round(float(row.get("start_price") or 0.0), 4),
                    "End Price": round(float(row.get("end_price") or 0.0), 4),
                    "Start Date": row.get("start_date"),
                    "End Date": row.get("end_date"),
                    "Previous Start Date": row.get("previous_start_date") or "-",
                    "Previous End Date": row.get("previous_end_date") or "-",
                }
            )

    return pd.DataFrame(leader_rows, columns=GROUP_TICKER_LEADER_COLUMNS)


def _coverage(
    *,
    universe_count: int,
    returnable_count: int,
    date_window: dict[str, Any],
    price_mode: str = "EOD DB",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    missing_count = max(0, universe_count - returnable_count)
    returnable_ratio = (returnable_count / universe_count) if universe_count else None
    coverage = {
        "universe_count": universe_count,
        "returnable_count": returnable_count,
        "missing_count": missing_count,
        "failed_count": missing_count,
        "returnable_ratio": round(returnable_ratio, 4) if returnable_ratio is not None else None,
        "returnable_pct": round(returnable_ratio * 100, 2) if returnable_ratio is not None else None,
        "latest_raw_date": date_window.get("latest_raw_date"),
        "effective_end_date": date_window.get("effective_end_date"),
        "stale_days": date_window.get("stale_days"),
        "price_mode": price_mode,
    }
    if extra:
        coverage.update(extra)
    return coverage


def _intraday_refresh_state(
    *,
    snapshot_status: str,
    period: str,
    coverage: dict[str, Any],
) -> dict[str, Any] | None:
    if period != "daily":
        return None
    price_mode = str(coverage.get("price_mode") or "")
    stale_minutes_value = coverage.get("snapshot_stale_minutes")
    stale_minutes = int(stale_minutes_value) if stale_minutes_value is not None else None
    missing_count = int(coverage.get("missing_count") or 0)
    returnable_count = int(coverage.get("returnable_count") or 0)
    universe_count = int(coverage.get("universe_count") or 0)
    returnable_pct = coverage.get("returnable_pct")
    next_due_in = (
        max(0, MARKET_INTRADAY_REFRESH_MINUTES - stale_minutes)
        if stale_minutes is not None
        else None
    )

    if snapshot_status != "OK":
        status = "failed"
        label = "Failed"
        detail = "snapshot build failed"
        action = "Open warnings and rerun the relevant refresh."
    elif price_mode != "Intraday Snapshot":
        status = "failed"
        label = "Snapshot missing"
        detail = "using EOD fallback"
        action = "Run Update Daily Snapshot; refresh S&P 500 universe first if no rows are available."
    elif returnable_count <= 0:
        status = "failed"
        label = "Failed"
        detail = "no returnable symbols"
        action = "Run Update Daily Snapshot and inspect Coverage Diagnostics."
    elif stale_minutes is None:
        status = "due"
        label = "Update due"
        detail = "snapshot age unavailable"
        action = "Run Update Daily Snapshot."
    elif stale_minutes >= MARKET_INTRADAY_STALE_MINUTES:
        status = "stale"
        label = "Stale"
        detail = f"{stale_minutes}m old"
        action = "Run Update Daily Snapshot."
    elif stale_minutes >= MARKET_INTRADAY_REFRESH_MINUTES:
        status = "due"
        label = "Update due"
        detail = f"{stale_minutes}m old"
        action = "Run Update Daily Snapshot."
    elif missing_count:
        status = "partial"
        label = "Partial"
        detail = f"{stale_minutes}m old, {missing_count} missing"
        action = "Open Coverage Diagnostics; rerun refresh if missing count is unexpected."
    else:
        status = "fresh"
        label = "Fresh"
        detail = f"{stale_minutes}m old, next check in {next_due_in}m"
        action = "No action needed yet."

    if status in {"due", "stale", "failed"} and missing_count and "missing" not in detail:
        detail = f"{detail}, {missing_count} missing"

    return {
        "status": status,
        "label": label,
        "detail": detail,
        "recommended_action": action,
        "refresh_due": status in {"due", "stale", "failed"},
        "is_partial": missing_count > 0,
        "stale_minutes": stale_minutes,
        "missing_count": missing_count,
        "returnable_count": returnable_count,
        "universe_count": universe_count,
        "returnable_pct": returnable_pct,
        "next_due_in_minutes": next_due_in,
        "check_interval_minutes": MARKET_INTRADAY_REFRESH_MINUTES,
        "stale_after_minutes": MARKET_INTRADAY_STALE_MINUTES,
        "tone": {
            "fresh": "positive",
            "partial": "warning",
            "due": "warning",
            "stale": "danger",
            "failed": "danger",
        }.get(status, "neutral"),
    }


def _coverage_warnings(coverage: dict[str, Any], *, date_window: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if coverage.get("latest_raw_date") and coverage.get("effective_end_date"):
        if coverage["latest_raw_date"] != coverage["effective_end_date"]:
            warnings.append(
                "Latest raw price date is sparse or unusable; rankings use the latest effective market date."
            )
    missing_count = int(coverage.get("missing_count") or 0)
    if missing_count:
        warnings.append(f"{missing_count} symbols in the selected universe are missing returnable price rows.")
    if date_window.get("status") != "OK":
        warnings.append(str(date_window.get("message") or "Market date window is unavailable."))
    snapshot_stale = coverage.get("snapshot_stale_minutes")
    if snapshot_stale is not None and int(snapshot_stale) > 15:
        warnings.append(f"Latest intraday snapshot is {snapshot_stale} minutes old.")
    return warnings


def _universe_metadata(universe: list[dict[str, Any]], *, universe_code: str) -> dict[str, Any]:
    if not universe:
        return {}
    if universe_code == "SP500":
        first = universe[0]
        return {
            "universe_as_of_date": _iso_date(first.get("universe_as_of_date")),
            "universe_collected_at": _display_datetime(first.get("universe_collected_at")),
            "universe_source": first.get("universe_source"),
            "universe_source_url": first.get("universe_source_url"),
            "coverage_basis": "Current S&P 500 constituents",
        }
    collected = [
        _display_datetime(row.get("last_collected_at"))
        for row in universe
        if _display_datetime(row.get("last_collected_at"))
    ]
    return {
        "profile_collected_at_max": max(collected) if collected else None,
        "coverage_basis": "Latest asset_profile.market_cap snapshot",
    }


def _rows_frame(rows: list[dict[str, Any]], *, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)


def _normalize_event_type_value(value: str | None) -> str | None:
    normalized = str(value or "").strip().upper().replace(" ", "_")
    return normalized or None


def _load_market_event_rows(
    *,
    start_date: str,
    end_date: str,
    event_type: str | None,
    limit: int,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    conditions = ["event_date >= %s", "event_date <= %s"]
    params: list[Any] = [start_date, end_date]
    normalized_type = _normalize_event_type_value(event_type)
    if normalized_type and normalized_type != "ALL":
        if normalized_type == "MACRO":
            conditions.append("event_type LIKE %s")
            params.append("MACRO_%")
        else:
            conditions.append("event_type = %s")
            params.append(normalized_type)
    bounded_limit = _normalize_limit(limit, default=200, min_value=1, max_value=1000)
    active_conditions = conditions + ["COALESCE(event_status, 'active') <> %s"]
    active_params = params + ["superseded", bounded_limit]
    try:
        return query_fn(
            "finance_meta",
            f"""
            SELECT
                event_date,
                event_type,
                symbol,
                title,
                source,
                source_type,
                validation_status,
                event_status,
                superseded_by_event_key,
                superseded_at,
                source_url,
                confidence,
                collected_at
            FROM market_event_calendar
            WHERE {" AND ".join(active_conditions)}
            ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
            LIMIT %s
            """,
            active_params,
        )
    except Exception:
        try:
            return query_fn(
                "finance_meta",
                f"""
                SELECT
                    event_date,
                    event_type,
                    symbol,
                    title,
                    source,
                    source_url,
                    confidence,
                    collected_at
                FROM market_event_calendar
                WHERE {" AND ".join(conditions)}
                ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
                LIMIT %s
                """,
                params + [bounded_limit],
            )
        except Exception:
            return []


def _event_source_type(row: dict[str, Any]) -> str:
    persisted = str(row.get("source_type") or "").strip().lower()
    if persisted == "official":
        return "Official"
    if persisted == "provider_estimate":
        return "Provider Estimate"
    if persisted == "unknown":
        return "Unknown"
    event_type = _normalize_event_type_value(row.get("event_type"))
    source = str(row.get("source") or "").strip().lower()
    if source == "federal_reserve_fomc_calendar":
        return "Official"
    if event_type == "MACRO" or str(event_type or "").startswith("MACRO_"):
        if any(term in source for term in ["bureau_labor_statistics", "bureau_economic_analysis", "bea"]):
            return "Official"
    if event_type == "EARNINGS":
        if "official" in source or "company" in source:
            return "Official"
        return "Provider Estimate"
    if source:
        return "Provider"
    return "Unknown"


def _event_validation_label(row: dict[str, Any]) -> str:
    status = str(row.get("validation_status") or "").strip().lower()
    if not status and _event_source_type(row) == "Provider Estimate":
        status = "estimate_only"
    labels = {
        "official": "Official",
        "estimate_only": "Estimate only",
        "cross_checked": "Cross-checked",
        "not_confirmed": "Not confirmed",
        "conflict": "Conflict",
        "unknown": "Unknown",
    }
    return labels.get(status, "Unknown" if not status else status.replace("_", " ").title())


def _event_status_label(row: dict[str, Any]) -> str:
    status = str(row.get("event_status") or "active").strip().lower()
    labels = {
        "active": "Active",
        "superseded": "Superseded",
        "stale": "Stale",
    }
    return labels.get(status, status.replace("_", " ").title())


def _event_collected_age_days(row: dict[str, Any], *, today: date) -> int | None:
    value = row.get("collected_at")
    if value in (None, ""):
        return None
    try:
        collected_at = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(collected_at):
        return None
    if collected_at.tzinfo is not None:
        collected_at = collected_at.tz_convert(None)
    age = pd.Timestamp(today).normalize() - collected_at.normalize()
    return max(0, int(age.days))


def _event_freshness(row: dict[str, Any], *, today: date) -> str:
    event_status = str(row.get("event_status") or "active").strip().lower()
    if event_status == "superseded":
        return "Superseded"
    if event_status == "stale":
        return "Stale estimate"
    source_type = _event_source_type(row)
    age_days = _event_collected_age_days(row, today=today)
    if source_type == "Official":
        return "Official"
    if source_type == "Provider Estimate":
        if age_days is None:
            return "Estimate age unknown"
        if age_days > EVENT_ESTIMATE_STALE_DAYS:
            return "Stale estimate"
        return "Current estimate"
    if age_days is None:
        return "Collection age unknown"
    if age_days > EVENT_ESTIMATE_STALE_DAYS:
        return "Stale source"
    return "Current source"


def _event_quality_action(row: dict[str, Any], *, today: date) -> str:
    event_type = _normalize_event_type_value(row.get("event_type"))
    validation = _event_validation_label(row)
    freshness = _event_freshness(row, today=today)
    source_type = _event_source_type(row)
    if freshness == "Stale estimate":
        return "Refresh earnings calendar"
    if event_type == "EARNINGS":
        if validation == "Cross-checked":
            return "No action"
        if validation == "Not confirmed":
            return "Treat as unconfirmed; retry later or inspect source"
        if validation == "Estimate only":
            return "Enable cross-check or refresh closer to date"
        if source_type == "Official":
            return "No action"
        return "Inspect provider source"
    if source_type == "Official":
        return "No action"
    return "Inspect source freshness"


def _event_days_until(row: dict[str, Any], *, today: date) -> int | None:
    event_date = row.get("event_date")
    if event_date in (None, ""):
        return None
    try:
        event_value = pd.Timestamp(event_date).normalize()
    except (TypeError, ValueError):
        return None
    if pd.isna(event_value):
        return None
    today_value = pd.Timestamp(today).normalize()
    return int((event_value - today_value).days)


def _is_major_macro_event_type(value: Any) -> bool:
    normalized = _normalize_event_type_value(value)
    return bool(normalized in MAJOR_MACRO_EVENT_TYPES)


def _event_window_label(row: dict[str, Any], *, today: date, recent_days: int = EVENT_RECENT_WINDOW_DAYS) -> str:
    days_until = _event_days_until(row, today=today)
    if days_until is None:
        return "Unknown"
    if days_until < 0:
        return "Recent" if abs(days_until) <= max(0, int(recent_days or 0)) else "Past"
    return "Upcoming"


def _event_sort_key(row: dict[str, Any], *, today: date, recent_days: int) -> tuple[int, int, int, str, str]:
    days_until = _event_days_until(row, today=today)
    major_rank = 0 if _is_major_macro_event_type(row.get("event_type")) else 1
    if days_until is None:
        return (5, major_rank, 9999, str(row.get("event_type") or ""), str(row.get("title") or ""))
    if _is_major_macro_event_type(row.get("event_type")) and days_until < 0 and abs(days_until) <= recent_days:
        return (0, major_rank, abs(days_until), str(row.get("event_type") or ""), str(row.get("title") or ""))
    if _is_major_macro_event_type(row.get("event_type")) and days_until >= 0:
        return (1, major_rank, days_until, str(row.get("event_type") or ""), str(row.get("title") or ""))
    if days_until >= 0:
        return (2, major_rank, days_until, str(row.get("event_type") or ""), str(row.get("title") or ""))
    if abs(days_until) <= recent_days:
        return (3, major_rank, abs(days_until), str(row.get("event_type") or ""), str(row.get("title") or ""))
    return (4, major_rank, abs(days_until), str(row.get("event_type") or ""), str(row.get("title") or ""))


def _prioritize_event_rows(rows: list[dict[str, Any]], *, today: date, recent_days: int) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: _event_sort_key(row, today=today, recent_days=recent_days))


def _event_importance_label(row: dict[str, Any]) -> str:
    event_type = _normalize_event_type_value(row.get("event_type"))
    if event_type == "FOMC_MEETING" or event_type == "MACRO" or str(event_type or "").startswith("MACRO_"):
        return "High"
    if event_type == "EARNINGS":
        return "Medium"
    return "Low"


def _event_focus_label(row: dict[str, Any], *, today: date) -> str:
    if _event_quality_action(row, today=today) != "No action":
        return "Needs Review"
    days_until = _event_days_until(row, today=today)
    if days_until is None:
        return "Unknown"
    if days_until < 0:
        return "Past"
    if days_until == 0:
        return "Today"
    if days_until <= 7:
        return "This Week"
    if days_until <= 30:
        return "Next 30D"
    return "Later"


def _event_coverage(rows: list[dict[str, Any]], *, today: date, recent_days: int = EVENT_RECENT_WINDOW_DAYS) -> dict[str, Any]:
    source_types = [_event_source_type(row) for row in rows]
    freshness = [_event_freshness(row, today=today) for row in rows]
    validation = [_event_validation_label(row) for row in rows]
    statuses = [_event_status_label(row) for row in rows]
    importance = [_event_importance_label(row) for row in rows]
    focus = [_event_focus_label(row, today=today) for row in rows]
    days_until = [_event_days_until(row, today=today) for row in rows]
    upcoming_pairs = [(row, days) for row, days in zip(rows, days_until) if days is not None and days >= 0]
    recent_pairs = [
        (row, days)
        for row, days in zip(rows, days_until)
        if days is not None and days < 0 and abs(days) <= max(0, int(recent_days or 0))
    ]
    recent_major_pairs = [
        (row, days) for row, days in recent_pairs if _is_major_macro_event_type(row.get("event_type"))
    ]
    upcoming_major_pairs = [
        (row, days) for row, days in upcoming_pairs if _is_major_macro_event_type(row.get("event_type"))
    ]
    next_row = min(upcoming_pairs, key=lambda item: (item[1], str(item[0].get("event_type") or "")))[0] if upcoming_pairs else None
    latest_recent_source = recent_major_pairs or recent_pairs
    latest_recent_row = (
        max(latest_recent_source, key=lambda item: (_iso_date(item[0].get("event_date")) or "", str(item[0].get("event_type") or "")))[0]
        if latest_recent_source
        else None
    )
    latest_collected_at = max(
        (_display_datetime(row.get("collected_at")) or "" for row in rows),
        default="",
    ) or None
    return {
        "event_count": len(rows),
        "next_event_date": _iso_date(next_row.get("event_date")) if next_row else None,
        "latest_recent_event_date": _iso_date(latest_recent_row.get("event_date")) if latest_recent_row else None,
        "latest_collected_at": latest_collected_at,
        "source_count": len({str(row.get("source") or "") for row in rows if row.get("source")}),
        "official_count": source_types.count("Official"),
        "estimate_count": source_types.count("Provider Estimate"),
        "estimate_only_count": validation.count("Estimate only"),
        "cross_checked_count": validation.count("Cross-checked"),
        "not_confirmed_count": validation.count("Not confirmed"),
        "stale_estimate_count": freshness.count("Stale estimate"),
        "action_required_count": sum(
            1
            for row in rows
            if _event_quality_action(row, today=today) != "No action"
        ),
        "high_importance_count": importance.count("High"),
        "needs_review_count": focus.count("Needs Review"),
        "this_week_count": sum(1 for value in focus if value in {"Today", "This Week"}),
        "next_30d_count": sum(1 for value in days_until if value is not None and 0 <= value <= 30),
        "recent_event_count": len(recent_pairs),
        "upcoming_event_count": len(upcoming_pairs),
        "recent_high_importance_count": len(recent_major_pairs),
        "upcoming_high_importance_count": len(upcoming_major_pairs),
        "superseded_count": statuses.count("Superseded"),
    }


def _event_warnings(coverage: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    stale_estimates = int(coverage.get("stale_estimate_count") or 0)
    if stale_estimates > 0:
        warnings.append(
            f"{stale_estimates} earnings estimate row(s) were collected more than "
            f"{EVENT_ESTIMATE_STALE_DAYS} days ago. Refresh Earnings Calendar before acting on those dates."
        )
    not_confirmed = int(coverage.get("not_confirmed_count") or 0)
    if not_confirmed > 0:
        warnings.append(
            f"{not_confirmed} earnings estimate row(s) were not confirmed by the alternate Nasdaq calendar cross-check."
        )
    return warnings


def _event_rows_frame(
    rows: list[dict[str, Any]],
    *,
    today: date,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
) -> pd.DataFrame:
    out = [
        {
            "Date": _iso_date(row.get("event_date")) or "-",
            "Days Until": _event_days_until(row, today=today),
            "Window": _event_window_label(row, today=today, recent_days=recent_days),
            "Type": row.get("event_type") or "-",
            "Symbol": row.get("symbol") or "-",
            "Title": row.get("title") or "-",
            "Importance": _event_importance_label(row),
            "Focus": _event_focus_label(row, today=today),
            "Source Type": _event_source_type(row),
            "Validation": _event_validation_label(row),
            "Freshness": _event_freshness(row, today=today),
            "Quality Action": _event_quality_action(row, today=today),
            "Event Status": _event_status_label(row),
            "Age Days": _event_collected_age_days(row, today=today),
            "Source": row.get("source") or "-",
            "Confidence": (
                round(float(row["confidence"]), 2)
                if _safe_float(row.get("confidence")) is not None
                else None
            ),
            "Collected At": _display_datetime(row.get("collected_at")) or "-",
            "Source URL": row.get("source_url") or "-",
        }
        for row in rows
    ]
    return pd.DataFrame(out, columns=EVENT_COLUMNS)


def build_market_events_snapshot(
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    event_type: str | None = "FOMC_MEETING",
    horizon_days: int = 365,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
    limit: int = 200,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    today_value = today or date.today()
    bounded_recent_days = max(0, int(recent_days or 0))
    normalized_start = _iso_date(start_date) or (today_value - timedelta(days=bounded_recent_days)).isoformat()
    normalized_end = _iso_date(end_date) or (today_value + timedelta(days=int(horizon_days or 365))).isoformat()
    normalized_type = _normalize_event_type_value(event_type)
    query = query_fn or _default_query
    try:
        rows = _load_market_event_rows(
            start_date=normalized_start,
            end_date=normalized_end,
            event_type=normalized_type,
            limit=limit,
            query_fn=query,
        )
        if not rows:
            return _empty_events_snapshot(
                status="NO_EVENTS",
                start_date=normalized_start,
                end_date=normalized_end,
                event_type=normalized_type,
                message="No stored market events match the selected window. Run a matching event calendar collector first.",
            )
        rows = _prioritize_event_rows(rows, today=today_value, recent_days=bounded_recent_days)
        coverage = _event_coverage(rows, today=today_value, recent_days=bounded_recent_days)
        return {
            "status": "OK",
            "event_type": normalized_type or "All",
            "rows": _event_rows_frame(rows, today=today_value, recent_days=bounded_recent_days),
            "date_window": {"start_date": normalized_start, "end_date": normalized_end},
            "coverage": coverage,
            "warnings": _event_warnings(coverage),
        }
    except Exception as exc:
        return _empty_events_snapshot(
            status="ERROR",
            start_date=normalized_start,
            end_date=normalized_end,
            event_type=normalized_type,
            message=f"Market events snapshot failed: {exc}",
        )


def _timestamp_sort_value(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError):
        return str(value)
    if pd.isna(parsed):
        return ""
    return parsed.isoformat()


def _display_run_time(value: Any) -> str:
    return _display_datetime(value) or "-"


def _latest_history_item(history_rows: Sequence[dict[str, Any]], job_names: Sequence[str]) -> dict[str, Any] | None:
    job_name_set = set(job_names)
    matched = [row for row in history_rows if str(row.get("job_name") or "") in job_name_set]
    if not matched:
        return None
    return max(matched, key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")))


def _latest_history_item_with_status(
    history_rows: Sequence[dict[str, Any]],
    job_names: Sequence[str],
    statuses: set[str],
) -> dict[str, Any] | None:
    normalized_statuses = {status.lower() for status in statuses}
    matched = [
        row
        for row in history_rows
        if str(row.get("job_name") or "") in set(job_names)
        and str(row.get("status") or "").lower() in normalized_statuses
    ]
    if not matched:
        return None
    return max(matched, key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")))


def _history_execution_mode(row: dict[str, Any]) -> str:
    metadata = row.get("run_metadata")
    if isinstance(metadata, dict):
        mode = str(metadata.get("execution_mode") or "").strip().lower()
        if mode:
            return mode
    return str(row.get("execution_mode") or "").strip().lower() or "manual"


def _latest_history_item_with_mode(
    history_rows: Sequence[dict[str, Any]],
    job_names: Sequence[str],
    execution_mode: str,
) -> dict[str, Any] | None:
    return _latest_history_item_with_modes(history_rows, job_names, {execution_mode})


def _latest_history_item_with_modes(
    history_rows: Sequence[dict[str, Any]],
    job_names: Sequence[str],
    execution_modes: set[str],
) -> dict[str, Any] | None:
    job_name_set = set(job_names)
    normalized_modes = {str(mode or "").strip().lower() for mode in execution_modes if str(mode or "").strip()}
    matched = [
        row
        for row in history_rows
        if str(row.get("job_name") or "") in job_name_set
        and _history_execution_mode(row) in normalized_modes
    ]
    if not matched:
        return None
    return max(matched, key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")))


def _automation_source_label(row: dict[str, Any] | None) -> str:
    mode = _history_execution_mode(row or {}) if row else ""
    if mode == "browser_auto":
        return "Browser Auto"
    if mode == "scheduled":
        return "Scheduled"
    if not mode:
        return "-"
    return mode.replace("_", " ").title()


def _failure_streak(history_rows: Sequence[dict[str, Any]], job_names: Sequence[str]) -> int:
    job_name_set = set(job_names)
    matched = [
        row for row in history_rows
        if str(row.get("job_name") or "") in job_name_set
    ]
    matched = sorted(
        matched,
        key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")),
        reverse=True,
    )
    streak = 0
    for row in matched:
        status = str(row.get("status") or "").lower()
        if status == "success":
            break
        if status in {"failed", "partial_success"}:
            streak += 1
            continue
        break
    return streak


def _next_auto_due_text(
    latest_auto: dict[str, Any] | None,
    job_names: Sequence[str],
) -> str:
    cadence_values = [
        OPS_SCHEDULE_CADENCE_MINUTES[job_name]
        for job_name in job_names
        if job_name in OPS_SCHEDULE_CADENCE_MINUTES
    ]
    if not cadence_values:
        return "-"
    cadence_minutes = min(cadence_values)
    if latest_auto is None:
        return "Due now"
    raw_time = latest_auto.get("finished_at") or latest_auto.get("started_at")
    if raw_time in (None, ""):
        return "Due now"
    ts = pd.Timestamp(raw_time)
    if pd.isna(ts):
        return "Due now"
    next_time = ts + pd.Timedelta(minutes=cadence_minutes)
    return _display_datetime(next_time) or "Due now"


def _history_status_overlay(
    base_status: str,
    *,
    latest_run: dict[str, Any] | None,
    latest_success: dict[str, Any] | None,
) -> str:
    if latest_run is None:
        return base_status
    run_status = str(latest_run.get("status") or "").lower()
    if run_status == "failed":
        success_time = _timestamp_sort_value((latest_success or {}).get("finished_at") or (latest_success or {}).get("started_at"))
        run_time = _timestamp_sort_value(latest_run.get("finished_at") or latest_run.get("started_at"))
        if not success_time or run_time >= success_time:
            return "Failed"
    if run_status == "partial_success":
        return "Partial"
    return base_status


def _history_metrics(
    *,
    latest_run: dict[str, Any] | None,
    latest_success: dict[str, Any] | None,
    latest_auto: dict[str, Any] | None,
    latest_manual: dict[str, Any] | None,
    job_names: Sequence[str],
    failure_streak: int,
) -> dict[str, Any]:
    source = latest_run or latest_success or {}
    failed_symbols = source.get("failed_symbols") or []
    if not isinstance(failed_symbols, list):
        failed_symbols = []
    return {
        "Last Success": _display_run_time((latest_success or {}).get("finished_at") or (latest_success or {}).get("started_at")),
        "Last Issue": _display_run_time(source.get("finished_at") or source.get("started_at"))
        if str(source.get("status") or "").lower() in {"failed", "partial_success"}
        else "-",
        "Last Auto Run": _display_run_time((latest_auto or {}).get("finished_at") or (latest_auto or {}).get("started_at")),
        "Auto Source": _automation_source_label(latest_auto),
        "Next Auto Due": _next_auto_due_text(latest_auto, job_names),
        "Last Manual Run": _display_run_time((latest_manual or {}).get("finished_at") or (latest_manual or {}).get("started_at")),
        "Failure Streak": failure_streak,
        "Rows": source.get("rows_written") if source else None,
        "Processed": source.get("symbols_processed") if source else None,
        "Failed": len(failed_symbols),
        "Duration Sec": source.get("duration_sec") if source else None,
        "Message": source.get("message") or "-",
    }


def _age_days(value: Any, *, today: date) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert(None)
    return max(0, int((pd.Timestamp(today).normalize() - parsed.normalize()).days))


def _latest_intraday_ops_rows(query_fn: QueryFn) -> dict[str, dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_price",
            """
            SELECT universe_code, interval_code, MAX(snapshot_time_utc) AS latest_snapshot_time
            FROM market_intraday_snapshot
            WHERE interval_code = %s
            GROUP BY universe_code, interval_code
            """,
            ["5m"],
        )
    except Exception:
        return {}
    return {str(row.get("universe_code") or "").upper(): row for row in rows}


def _latest_universe_ops_rows(query_fn: QueryFn) -> dict[str, dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                universe_code,
                COUNT(*) AS active_symbols,
                MAX(collected_at) AS latest_collected_at,
                MAX(as_of_date) AS latest_as_of_date
            FROM market_universe_member
            WHERE active = 1
            GROUP BY universe_code
            """,
            None,
        )
    except Exception:
        return {}
    return {str(row.get("universe_code") or "").upper(): row for row in rows}


def _latest_event_ops_rows(query_fn: QueryFn, *, today: date) -> dict[str, dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                event_type,
                COUNT(*) AS active_events,
                SUM(CASE WHEN event_date >= %s THEN 1 ELSE 0 END) AS future_events,
                MIN(CASE WHEN event_date >= %s THEN event_date ELSE NULL END) AS next_event_date,
                MAX(collected_at) AS latest_collected_at
            FROM market_event_calendar
            WHERE COALESCE(event_status, 'active') <> 'superseded'
            GROUP BY event_type
            """,
            [today.isoformat(), today.isoformat()],
        )
    except Exception:
        try:
            rows = query_fn(
                "finance_meta",
                """
                SELECT
                    event_type,
                    COUNT(*) AS active_events,
                    SUM(CASE WHEN event_date >= %s THEN 1 ELSE 0 END) AS future_events,
                    MIN(CASE WHEN event_date >= %s THEN event_date ELSE NULL END) AS next_event_date,
                    MAX(collected_at) AS latest_collected_at
                FROM market_event_calendar
                GROUP BY event_type
                """,
                [today.isoformat(), today.isoformat()],
            )
        except Exception:
            return {}
    return {str(row.get("event_type") or "").upper(): row for row in rows}


def _latest_futures_ops_row(query_fn: QueryFn) -> dict[str, Any] | None:
    try:
        rows = query_fn(
            "finance_price",
            """
            SELECT
                MAX(candle_time_utc) AS latest_candle_time,
                COUNT(DISTINCT provider_symbol) AS active_symbols,
                COUNT(*) AS candle_rows
            FROM futures_ohlcv
            WHERE interval_code = %s
            """,
            ["1m"],
        )
    except Exception:
        return None
    return dict(rows[0]) if rows else None


def _latest_sentiment_ops_row(query_fn: QueryFn) -> dict[str, Any] | None:
    try:
        placeholders = ",".join(["%s"] * len(CORE_SENTIMENT_SERIES))
        rows = query_fn(
            "finance_meta",
            f"""
            SELECT
                MAX(observation_date) AS latest_observation_date,
                MAX(collected_at) AS latest_collected_at,
                COUNT(DISTINCT series_id) AS series_count
            FROM macro_series_observation
            WHERE series_id IN ({placeholders})
              AND source IN (%s, %s)
            """,
            [*CORE_SENTIMENT_SERIES, "cnn_fear_greed", "aaii_sentiment_survey"],
        )
    except Exception:
        return None
    return dict(rows[0]) if rows else None


def _intraday_ops_status(row: dict[str, Any] | None) -> tuple[str, str, str]:
    if not row or not row.get("latest_snapshot_time"):
        return "Missing", "No stored 5m snapshot", "Run the daily snapshot collector."
    age = _stale_minutes(row.get("latest_snapshot_time"))
    if age is None:
        return "Missing", "Snapshot age unknown", "Run the daily snapshot collector."
    if age <= MARKET_INTRADAY_REFRESH_MINUTES:
        return "OK", f"{age}m old", "No action needed."
    if age <= MARKET_INTRADAY_STALE_MINUTES:
        return "Due", f"{age}m old", "Refresh if you need live daily movers."
    return "Stale", f"{age}m old", "Refresh before using daily movers."


def _futures_ops_status(row: dict[str, Any] | None) -> tuple[str, str, str]:
    if not row or not row.get("latest_candle_time") or int(row.get("active_symbols") or 0) <= 0:
        return "Missing", "No stored 1m futures candles", "Run Refresh Futures OHLCV."
    age = _stale_minutes(row.get("latest_candle_time"))
    if age is None:
        return "Missing", "Futures candle age unknown", "Run Refresh Futures OHLCV."
    active_symbols = int(row.get("active_symbols") or 0)
    if age <= 2:
        return "OK", f"{age}m old; {active_symbols} symbols", "No action needed."
    if age <= 10:
        return "Due", f"{age}m old; {active_symbols} symbols", "Refresh if you need current pre-open context."
    return "Stale", f"{age}m old; {active_symbols} symbols", "Refresh before using futures context."


def _sentiment_ops_status(row: dict[str, Any] | None, *, today: date) -> tuple[str, str, str]:
    series_count = int((row or {}).get("series_count") or 0)
    latest_observation = _iso_date((row or {}).get("latest_observation_date"))
    if not row or not latest_observation or series_count <= 0:
        return "Missing", "No stored CNN / AAII sentiment observations", "Run Refresh Market Sentiment."
    age = _stale_days(latest_observation, today=today)
    if age is None:
        return "Due", f"Latest date unknown; {series_count}/5 series", "Run Refresh Market Sentiment."
    freshness = f"{age}d old; latest {latest_observation}; {series_count}/5 series"
    if series_count < 2:
        return "Due", freshness, "Refresh CNN Fear & Greed and AAII sentiment."
    if age <= 7:
        return "OK", freshness, "No action needed."
    if age <= 14:
        return "Due", freshness, "Refresh sentiment if you need current market context."
    return "Stale", freshness, "Refresh before using sentiment context."


def _days_based_ops_status(
    *,
    latest_collected_at: Any,
    active_count: int,
    fresh_days: int,
    stale_days: int,
    today: date,
    missing_text: str,
) -> tuple[str, str]:
    if active_count <= 0:
        return "Missing", missing_text
    age = _age_days(latest_collected_at, today=today)
    if age is None:
        return "Due", "Collection age unknown"
    if age <= fresh_days:
        return "OK", f"{age}d old"
    if age <= stale_days:
        return "Due", f"{age}d old"
    return "Stale", f"{age}d old"


def _combined_event_ops_row(
    event_rows: dict[str, dict[str, Any]],
    event_types: Sequence[str],
) -> dict[str, Any] | None:
    rows = [event_rows.get(str(event_type).upper()) for event_type in event_types]
    rows = [row for row in rows if row]
    if not rows:
        return None
    covered_event_types = sorted(
        {
            str(row.get("event_type") or "").upper()
            for row in rows
            if row.get("event_type")
        }
    )
    future_events = sum(int(row.get("future_events") or 0) for row in rows)
    active_events = sum(int(row.get("active_events") or 0) for row in rows)
    next_dates = [_iso_date(row.get("next_event_date")) for row in rows if _iso_date(row.get("next_event_date"))]
    collected = [row.get("latest_collected_at") for row in rows if row.get("latest_collected_at")]
    return {
        "future_events": future_events,
        "active_events": active_events,
        "next_event_date": min(next_dates) if next_dates else None,
        "latest_collected_at": max(collected, key=_timestamp_sort_value) if collected else None,
        "covered_event_types": covered_event_types,
    }


def _ops_row(
    *,
    area: str,
    base_status: str,
    data_freshness: str,
    next_action: str,
    job_names: Sequence[str],
    history_rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    latest_run = _latest_history_item(history_rows, job_names)
    latest_success = _latest_history_item_with_status(history_rows, job_names, {"success"})
    latest_auto = _latest_history_item_with_modes(history_rows, job_names, {"scheduled", "browser_auto"})
    latest_manual = _latest_history_item_with_mode(history_rows, job_names, "manual")
    failure_streak = _failure_streak(history_rows, job_names)
    status = _history_status_overlay(base_status, latest_run=latest_run, latest_success=latest_success)
    metrics = _history_metrics(
        latest_run=latest_run,
        latest_success=latest_success,
        latest_auto=latest_auto,
        latest_manual=latest_manual,
        job_names=job_names,
        failure_streak=failure_streak,
    )
    if status == "OK":
        action = "No action needed."
    elif status == "Failed":
        action = "Open run history details and rerun after checking the failure message."
    elif status == "Partial":
        action = "Inspect failed symbols, then rerun a bounded collection."
    else:
        action = next_action
    return {
        "Area": area,
        "Status": status,
        "Data Freshness": data_freshness,
        **metrics,
        "Next Action": action,
    }


def _ops_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(row.get("Status") or "") for row in rows]
    success_times = [row.get("Last Success") for row in rows if row.get("Last Success") not in (None, "-")]
    issue_times = [row.get("Last Issue") for row in rows if row.get("Last Issue") not in (None, "-")]
    auto_times = [
        row.get("Last Auto Run") for row in rows
        if row.get("Last Auto Run") not in (None, "-")
    ]
    failure_streaks = [
        int(row.get("Failure Streak") or 0) for row in rows
        if str(row.get("Failure Streak") or "").isdigit() or isinstance(row.get("Failure Streak"), int)
    ]
    return {
        "job_count": len(rows),
        "ok_count": statuses.count("OK"),
        "due_count": statuses.count("Due"),
        "stale_count": statuses.count("Stale"),
        "missing_count": statuses.count("Missing"),
        "failed_count": statuses.count("Failed"),
        "partial_count": statuses.count("Partial"),
        "latest_success_at": max(success_times) if success_times else None,
        "latest_issue_at": max(issue_times) if issue_times else None,
        "latest_auto_at": max(auto_times) if auto_times else None,
        "max_failure_streak": max(failure_streaks) if failure_streaks else 0,
    }


def build_collection_ops_snapshot(
    *,
    history_rows: Sequence[dict[str, Any]] | None = None,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Build the Overview Data Health read model from stored DB freshness and local job history."""
    query = query_fn or _default_query
    today_value = today or date.today()
    history = list(history_rows or [])

    try:
        intraday_rows = _latest_intraday_ops_rows(query)
        universe_rows = _latest_universe_ops_rows(query)
        event_rows = _latest_event_ops_rows(query, today=today_value)
        futures_row = _latest_futures_ops_row(query)
        sentiment_row = _latest_sentiment_ops_row(query)
    except Exception as exc:
        return _empty_ops_snapshot(message=f"Collection ops snapshot failed: {exc}")

    rows: list[dict[str, Any]] = []
    sp500_universe = universe_rows.get("SP500")
    universe_status, universe_freshness = _days_based_ops_status(
        latest_collected_at=(sp500_universe or {}).get("latest_collected_at"),
        active_count=int((sp500_universe or {}).get("active_symbols") or 0),
        fresh_days=7,
        stale_days=30,
        today=today_value,
        missing_text="No active S&P 500 universe rows",
    )
    rows.append(
        _ops_row(
            area="S&P 500 Universe",
            base_status=universe_status,
            data_freshness=universe_freshness,
            next_action="Refresh S&P 500 universe membership.",
            job_names=["collect_sp500_universe"],
            history_rows=history,
        )
    )

    for target in OPS_INTRADAY_TARGETS:
        base_status, freshness, default_action = _intraday_ops_status(
            intraday_rows.get(str(target["universe_code"]))
        )
        rows.append(
            _ops_row(
                area=str(target["area"]),
                base_status=base_status,
                data_freshness=freshness,
                next_action=str(target["missing_action"] if base_status == "Missing" else target["due_action"] or default_action),
                job_names=list(target["job_names"]),
                history_rows=history,
            )
        )

    for target in OPS_FUTURES_TARGETS:
        base_status, freshness, default_action = _futures_ops_status(futures_row)
        rows.append(
            _ops_row(
                area=str(target["area"]),
                base_status=base_status,
                data_freshness=freshness,
                next_action=str(target["missing_action"] if base_status == "Missing" else target["due_action"] or default_action),
                job_names=list(target["job_names"]),
                history_rows=history,
            )
        )

    sentiment_status, sentiment_freshness, sentiment_default_action = _sentiment_ops_status(
        sentiment_row,
        today=today_value,
    )
    rows.append(
        _ops_row(
            area=str(OPS_SENTIMENT_TARGET["area"]),
            base_status=sentiment_status,
            data_freshness=sentiment_freshness,
            next_action=str(
                OPS_SENTIMENT_TARGET["missing_action"]
                if sentiment_status == "Missing"
                else OPS_SENTIMENT_TARGET["due_action"] or sentiment_default_action
            ),
            job_names=list(OPS_SENTIMENT_TARGET["job_names"]),
            history_rows=history,
        )
    )

    for target in OPS_EVENT_TARGETS:
        target_event_types = list(target.get("event_types") or [target["event_type"]])
        event_row = _combined_event_ops_row(event_rows, target_event_types)
        active_count = int((event_row or {}).get("future_events") or (event_row or {}).get("active_events") or 0)
        base_status, freshness = _days_based_ops_status(
            latest_collected_at=(event_row or {}).get("latest_collected_at"),
            active_count=active_count,
            fresh_days=int(target["fresh_days"]),
            stale_days=int(target["stale_days"]),
            today=today_value,
            missing_text=f"No future {target['event_type']} rows",
        )
        required_event_types = list(target.get("event_types") or [])
        if event_row and required_event_types:
            covered_count = len(event_row.get("covered_event_types") or [])
            required_count = len(required_event_types)
            freshness = f"{freshness}; covered {covered_count}/{required_count}"
            if covered_count < required_count and base_status == "OK":
                base_status = "Due"
        next_event = _iso_date((event_row or {}).get("next_event_date"))
        if next_event and freshness != "No future rows":
            freshness = f"{freshness}; next {next_event}"
        rows.append(
            _ops_row(
                area=str(target["area"]),
                base_status=base_status,
                data_freshness=freshness,
                next_action=str(target["missing_action"] if base_status == "Missing" else target["due_action"]),
                job_names=list(target["job_names"]),
                history_rows=history,
            )
        )

    coverage = _ops_coverage(rows)
    review_count = sum(
        int(coverage.get(key) or 0)
        for key in ("due_count", "stale_count", "missing_count", "failed_count", "partial_count")
    )
    status = "OK" if review_count == 0 else "REVIEW"
    warnings: list[str] = []
    if int(coverage.get("failed_count") or 0) > 0:
        warnings.append("One or more market intelligence collection jobs failed after the last successful run.")
    if int(coverage.get("missing_count") or 0) > 0:
        warnings.append("One or more market intelligence data sets are missing stored rows.")
    if int(coverage.get("stale_count") or 0) > 0:
        warnings.append("One or more market intelligence data sets are stale and should be refreshed.")
    return {
        "status": status,
        "rows": pd.DataFrame(rows, columns=OPS_COLUMNS),
        "coverage": coverage,
        "warnings": warnings,
    }


def _cockpit_error_snapshot(label: str, exc: Exception) -> dict[str, Any]:
    return {
        "status": "ERROR",
        "message": f"{label} snapshot failed: {exc}",
        "coverage": {},
        "rows": pd.DataFrame(),
    }


def _cockpit_frame(snapshot: dict[str, Any], key: str = "rows") -> pd.DataFrame:
    rows = snapshot.get(key)
    if isinstance(rows, pd.DataFrame):
        return rows
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame()


def _cockpit_first_row(snapshot: dict[str, Any], key: str = "rows") -> dict[str, Any]:
    frame = _cockpit_frame(snapshot, key=key)
    if frame.empty:
        return {}
    return dict(frame.iloc[0].dropna().to_dict())


def _cockpit_int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def _cockpit_status_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("label") or value.get("status") or "").strip()
    return str(value or "").strip()


def _cockpit_status_tone(status: Any) -> str:
    if isinstance(status, dict) and status.get("tone"):
        return str(status.get("tone"))
    normalized = _cockpit_status_text(status).lower()
    if normalized in {"ok", "success", "actual", "high", "fresh"}:
        return "positive"
    if normalized in {"failed", "error", "missing", "no_universe", "insufficient_data"}:
        return "danger"
    if normalized in {"review", "due", "stale", "partial", "not_run", "no_data"}:
        return "warning"
    return "neutral"


DATA_HEALTH_HANDOFF_TARGETS: dict[str, dict[str, str]] = {
    "S&P 500 Universe": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > 유니버스 갱신",
        "collection_action": "Run S&P 500 universe refresh through the existing Overview action facade.",
    },
    "S&P 500 Daily Snapshot": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > 일중 스냅샷 갱신",
        "collection_action": "Run the S&P 500 intraday snapshot refresh from Market Movers.",
    },
    "Top1000 Daily Snapshot": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > Top1000 > 일중 스냅샷 갱신",
        "collection_action": "Run the Top1000 intraday snapshot refresh from Market Movers.",
    },
    "Top2000 Daily Snapshot": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > Top2000 > 일중 스냅샷 갱신",
        "collection_action": "Run the Top2000 intraday snapshot refresh from Market Movers.",
    },
    "Futures Monitor 1m OHLCV": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 선물 OHLCV 수집",
        "alternate_surface": "Workspace > Overview > Futures Monitor",
        "collection_action": "Run futures OHLCV collection; Overview bounded refresh is also available for the Futures Monitor.",
    },
    "Market Sentiment": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 심리 수집",
        "alternate_surface": "Workspace > Overview > Sentiment",
        "collection_action": "Run Market Sentiment collection for CNN Fear & Greed / AAII rows.",
    },
    "FOMC Calendar": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > FOMC 일정",
        "alternate_surface": "Workspace > Overview > Events",
        "collection_action": "Run FOMC calendar collection from the existing market events collector.",
    },
    "Macro Calendar": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > 매크로 발표",
        "alternate_surface": "Workspace > Overview > Events",
        "collection_action": "Run official macro calendar collection or import the BLS .ics file.",
    },
    "Earnings Calendar": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > 실적 발표",
        "alternate_surface": "Workspace > Overview > Events",
        "collection_action": "Run earnings calendar collection with a bounded symbol source.",
    },
}
DATA_HEALTH_HANDOFF_STATUS_ORDER = {
    "FAILED": 0,
    "MISSING": 1,
    "STALE": 2,
    "PARTIAL": 3,
    "DUE": 4,
    "REVIEW": 5,
}
DATA_HEALTH_HANDOFF_SEVERITY = {
    "FAILED": "critical",
    "MISSING": "critical",
    "STALE": "high",
    "PARTIAL": "high",
    "DUE": "medium",
    "REVIEW": "medium",
}


def _handoff_status(value: Any) -> str:
    status = str(value or "").strip()
    return status or "Unknown"


def _handoff_status_rank(status: Any) -> int:
    return DATA_HEALTH_HANDOFF_STATUS_ORDER.get(_handoff_status(status).upper(), 99)


def _handoff_counts(rows: pd.DataFrame) -> dict[str, int]:
    if rows.empty or "Status" not in rows:
        return {}
    counts = rows["Status"].fillna("Unknown").astype(str).value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def _handoff_reason(row: dict[str, Any]) -> str:
    parts = [
        _handoff_status(row.get("Status")),
        str(row.get("Data Freshness") or "-"),
    ]
    failure_streak = _cockpit_int(row.get("Failure Streak"))
    failed_count = _cockpit_int(row.get("Failed"))
    last_issue = row.get("Last Issue")
    if failure_streak:
        parts.append(f"Failure streak {failure_streak}")
    if failed_count:
        parts.append(f"{failed_count} failed")
    if last_issue not in (None, "", "-"):
        parts.append(f"Last issue {last_issue}")
    return " · ".join(parts)


def _handoff_target(area: str) -> dict[str, str]:
    target = dict(DATA_HEALTH_HANDOFF_TARGETS.get(area) or {})
    if target:
        return target
    return {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터",
        "collection_action": "Open the matching Ingestion collector and rerun a bounded collection.",
    }


def build_overview_data_health_ingestion_handoff(
    collection_ops_snapshot: dict[str, Any] | None = None,
    *,
    limit: int = 5,
) -> dict[str, Any]:
    """Turn Overview Data Health rows into read-only handoff guidance for the owning collection surfaces."""
    snapshot = collection_ops_snapshot or {}
    rows = _cockpit_frame(snapshot)
    counts = _handoff_counts(rows)
    if rows.empty:
        return {
            "schema_version": "overview_data_health_ingestion_handoff_v1",
            "status": "NO_DATA",
            "summary": {
                "headline": "No Data Health handoff available",
                "detail": str(snapshot.get("message") or "No collection ops rows are available yet."),
                "review_count": 0,
                "top_priority": None,
                "next_target_surface": None,
            },
            "counts": counts,
            "priority_items": [],
            "boundary_note": (
                "Read-only handoff: Overview Data Health does not execute collection jobs, write registries, "
                "write saved setup, change DB schema, or fetch providers during render."
            ),
        }

    review_rows = rows[
        ~rows.get("Status", pd.Series(dtype=str)).fillna("").astype(str).str.upper().isin({"OK", "SUCCESS"})
    ].copy()
    if review_rows.empty:
        return {
            "schema_version": "overview_data_health_ingestion_handoff_v1",
            "status": "OK",
            "summary": {
                "headline": "Data Health handoff clear",
                "detail": "All tracked Overview collection targets are currently OK.",
                "review_count": 0,
                "top_priority": None,
                "next_target_surface": None,
            },
            "counts": counts,
            "priority_items": [],
            "boundary_note": (
                "Read-only handoff: Overview Data Health does not execute collection jobs, write registries, "
                "write saved setup, change DB schema, or fetch providers during render."
            ),
        }

    review_rows["_status_rank"] = review_rows["Status"].map(_handoff_status_rank)
    if "Failure Streak" not in review_rows:
        review_rows["Failure Streak"] = 0
    review_rows["_failure_streak"] = review_rows["Failure Streak"].map(_cockpit_int)
    review_rows = review_rows.sort_values(
        by=["_status_rank", "_failure_streak", "Area"],
        ascending=[True, False, True],
        kind="mergesort",
    )

    priority_items: list[dict[str, Any]] = []
    for rank, (_, item_row) in enumerate(review_rows.head(max(1, int(limit or 5))).iterrows(), start=1):
        row = dict(item_row.drop(labels=["_status_rank", "_failure_streak"], errors="ignore").to_dict())
        area = str(row.get("Area") or "Unknown")
        status = _handoff_status(row.get("Status"))
        target = _handoff_target(area)
        priority_items.append(
            {
                "rank": rank,
                "area": area,
                "status": status,
                "severity": DATA_HEALTH_HANDOFF_SEVERITY.get(status.upper(), "low"),
                "tone": _cockpit_status_tone(status),
                "freshness": str(row.get("Data Freshness") or "-"),
                "reason": _handoff_reason(row),
                "next_action": str(row.get("Next Action") or target.get("collection_action") or "-"),
                "collection_action": target.get("collection_action") or str(row.get("Next Action") or "-"),
                "owner_surface": target.get("owner_surface") or "Workspace > Ingestion",
                "target_surface": target.get("target_surface") or "Workspace > Ingestion",
                "alternate_surface": target.get("alternate_surface"),
                "last_success": row.get("Last Success") or "-",
                "last_issue": row.get("Last Issue") or "-",
            }
        )

    review_count = int(len(review_rows))
    top_item = priority_items[0] if priority_items else {}
    return {
        "schema_version": "overview_data_health_ingestion_handoff_v1",
        "status": "REVIEW" if review_count else "OK",
        "summary": {
            "headline": f"{review_count} Data Health targets need handoff" if review_count else "Data Health handoff clear",
            "detail": (
                "Open the owning collection surface for the highest-priority stale, missing, partial, due, or failed target."
                if review_count
                else "All tracked Overview collection targets are currently OK."
            ),
            "review_count": review_count,
            "top_priority": top_item.get("area"),
            "next_target_surface": top_item.get("target_surface"),
        },
        "counts": counts,
        "priority_items": priority_items,
        "boundary_note": (
            "Read-only handoff: Overview Data Health does not execute collection jobs, write registries, "
            "write saved setup, change DB schema, or fetch providers during render."
        ),
    }


def _cockpit_card_status(*values: Any) -> str:
    for value in values:
        normalized = _cockpit_status_text(value)
        if normalized and normalized.upper() not in {"OK", "SUCCESS", "ACTUAL"}:
            return normalized
    return "OK"


def _cockpit_percent(value: Any, *, digits: int = 1) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:+.{digits}f}%"


def _overview_round(value: Any, *, digits: int = 1) -> float | None:
    numeric = _safe_float(value)
    if numeric is None:
        return None
    return round(numeric, digits)


def _overview_percent_label(value: Any, *, digits: int = 0, signed: bool = False) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "-"
    sign = "+" if signed else ""
    return f"{numeric:{sign}.{digits}f}%"


def _overview_breadth_participation_label(positive_share: float | None) -> str:
    if positive_share is None:
        return "unknown"
    if positive_share >= 65.0:
        return "broad"
    if positive_share <= 45.0:
        return "narrow"
    return "mixed"


def _overview_breadth_concentration_label(top_share: float | None, cap_equal_gap: float | None) -> str:
    if top_share is None and cap_equal_gap is None:
        return "unknown"
    if (top_share is not None and top_share >= 65.0) or (cap_equal_gap is not None and abs(cap_equal_gap) >= 2.0):
        return "concentrated"
    return "balanced"


def _overview_breadth_row_tone(row: dict[str, Any]) -> str:
    weighted = _safe_float(row.get("Market Cap Weighted Return %"))
    positive_share = _safe_float(row.get("Positive Symbol Share %"))
    if weighted is not None and weighted < 0:
        return "danger"
    if positive_share is not None and positive_share < 45.0:
        return "warning"
    if weighted is not None and weighted > 0:
        return "positive"
    return "neutral"


def build_overview_breadth_heatmap_summary(
    group_leadership_snapshot: dict[str, Any] | None = None,
    *,
    limit: int = 10,
) -> dict[str, Any]:
    """Compress an existing group leadership snapshot into a context-only breadth heatmap summary."""
    snapshot = group_leadership_snapshot or {}
    rows = _cockpit_frame(snapshot)
    coverage = dict(snapshot.get("coverage") or {})
    date_window = dict(snapshot.get("date_window") or {})
    if rows.empty:
        return {
            "schema_version": "overview_breadth_heatmap_summary_v1",
            "status": "NO_DATA",
            "summary": {
                "headline": "Breadth context unavailable",
                "detail": str(snapshot.get("message") or "No stored group leadership rows are available."),
                "participation_label": "unknown",
                "concentration_label": "unknown",
                "leader": None,
            },
            "coverage": {
                "group_count": 0,
                "returnable_count": coverage.get("returnable_count"),
                "universe_count": coverage.get("universe_count"),
                "price_mode": coverage.get("price_mode"),
                "freshness": coverage.get("snapshot_time_utc") or coverage.get("effective_end_date"),
            },
            "cards": [],
            "heatmap_rows": [],
            "boundary_note": (
                "Context-only breadth summary: not a trade signal, not validation, not Final Review, "
                "and not monitoring guidance."
            ),
        }

    numeric_positive = rows.get("Positive Symbol Share %", pd.Series(dtype=float)).map(_safe_float).dropna()
    numeric_weighted = rows.get("Market Cap Weighted Return %", pd.Series(dtype=float)).map(_safe_float).dropna()
    negative_count = int((numeric_weighted < 0).sum()) if not numeric_weighted.empty else 0
    positive_group_count = int((numeric_weighted > 0).sum()) if not numeric_weighted.empty else 0
    average_positive_share = round(float(numeric_positive.mean()), 1) if not numeric_positive.empty else None
    average_weighted_return = round(float(numeric_weighted.mean()), 2) if not numeric_weighted.empty else None
    top_row = dict(rows.iloc[0].dropna().to_dict())
    leader = str(top_row.get("Group") or "-")
    leader_return = _safe_float(top_row.get("Market Cap Weighted Return %"))
    top_share = _safe_float(top_row.get("Top 3 Positive Share %"))
    cap_equal_gap = _safe_float(top_row.get("Cap vs Equal Gap pp"))
    participation_label = _overview_breadth_participation_label(average_positive_share)
    concentration_label = _overview_breadth_concentration_label(top_share, cap_equal_gap)

    heatmap_rows: list[dict[str, Any]] = []
    for fallback_rank, (_, row_value) in enumerate(rows.head(max(1, int(limit or 10))).iterrows(), start=1):
        row = dict(row_value.dropna().to_dict())
        heatmap_rows.append(
            {
                "rank": _cockpit_int(row.get("Rank")) or fallback_rank,
                "group": str(row.get("Group") or "-"),
                "symbols": _cockpit_int(row.get("Symbols")),
                "positive_symbols": _cockpit_int(row.get("Positive Symbols")),
                "positive_symbol_share_pct": _overview_round(row.get("Positive Symbol Share %")),
                "market_cap_weighted_return_pct": _overview_round(row.get("Market Cap Weighted Return %")),
                "equal_weight_return_pct": _overview_round(row.get("Equal Weight Return %")),
                "top_3_positive_share_pct": _overview_round(row.get("Top 3 Positive Share %")),
                "top_symbol": str(row.get("Top Symbol") or "-"),
                "top_symbol_return_pct": _overview_round(row.get("Top Symbol Return %")),
                "tone": _overview_breadth_row_tone(row),
            }
        )

    group_label = "groups" if len(rows) != 1 else "group"
    cards = [
        {
            "title": "Participation",
            "value": _overview_percent_label(average_positive_share),
            "detail": f"{participation_label} average positive share across {len(rows)} {group_label}",
            "tone": "positive" if participation_label == "broad" else "warning" if participation_label == "narrow" else "neutral",
        },
        {
            "title": "Leadership",
            "value": leader,
            "detail": f"{_overview_percent_label(leader_return, digits=1, signed=True)} cap-weighted return",
            "tone": _overview_breadth_row_tone(top_row),
        },
        {
            "title": "Concentration",
            "value": concentration_label,
            "detail": f"Top 3 positive share {_overview_percent_label(top_share)} · cap/equal gap {_overview_percent_label(cap_equal_gap, digits=1, signed=True)}",
            "tone": "warning" if concentration_label == "concentrated" else "positive" if concentration_label == "balanced" else "neutral",
        },
        {
            "title": "Negative Groups",
            "value": str(negative_count),
            "detail": f"{positive_group_count} positive groups · avg cap-weighted {_overview_percent_label(average_weighted_return, digits=2, signed=True)}",
            "tone": "warning" if negative_count else "positive",
        },
    ]

    return {
        "schema_version": "overview_breadth_heatmap_summary_v1",
        "status": snapshot.get("status") or "OK",
        "summary": {
            "headline": f"{participation_label.title()} participation, {concentration_label} leadership",
            "detail": (
                f"{leader} leads the selected universe; use the heatmap to see whether movement is broad or group-specific."
            ),
            "participation_label": participation_label,
            "concentration_label": concentration_label,
            "leader": leader,
        },
        "coverage": {
            "group_count": int(len(rows)),
            "returnable_count": coverage.get("returnable_count"),
            "universe_count": coverage.get("universe_count"),
            "price_mode": coverage.get("price_mode") or "EOD DB",
            "freshness": coverage.get("snapshot_time_utc")
            or coverage.get("effective_end_date")
            or date_window.get("effective_end_date")
            or date_window.get("end_date"),
        },
        "cards": cards,
        "heatmap_rows": heatmap_rows,
        "boundary_note": (
            "Context-only breadth summary: not a trade signal, not validation, not Final Review, "
            "and not monitoring guidance."
        ),
    }


def _macro_week_cluster_label(event_type: Any) -> str:
    normalized = str(event_type or "").strip().upper()
    if normalized in {"FOMC_MEETING", "FOMC"}:
        return "FOMC"
    if normalized in {"MACRO_CPI", "CPI"}:
        return "CPI"
    if normalized in {"MACRO_PPI", "PPI"}:
        return "PPI"
    if normalized in {"MACRO_EMPLOYMENT", "EMPLOYMENT", "JOBS"}:
        return "Employment"
    if normalized in {"MACRO_GDP", "GDP"}:
        return "GDP"
    if normalized in {"EARNINGS", "EARNINGS CALENDAR"}:
        return "Earnings"
    if normalized.startswith("MACRO_"):
        return normalized.replace("MACRO_", "").replace("_", " ").title()
    return "Other"


def _macro_week_event_needs_review(row: dict[str, Any]) -> bool:
    action = str(row.get("Quality Action") or "").strip().lower()
    freshness = str(row.get("Freshness") or "").strip().lower()
    validation = str(row.get("Validation") or "").strip().lower()
    if action and action != "no action":
        return True
    return any(token in freshness for token in ("stale", "unknown")) or any(
        token in validation for token in ("not confirmed", "estimate only")
    )


def _macro_week_item_tone(row: dict[str, Any]) -> str:
    if _macro_week_event_needs_review(row):
        return "warning"
    cluster = _macro_week_cluster_label(row.get("Type"))
    if cluster == "Earnings":
        return "earnings"
    if cluster in {"FOMC", "CPI", "PPI", "Employment", "GDP"}:
        return "macro"
    return "neutral"


def _macro_week_is_major_macro(row: dict[str, Any]) -> bool:
    return _macro_week_cluster_label(row.get("Type")) in {"FOMC", "CPI", "PPI", "Employment", "GDP"}


def _macro_week_item_from_row(row: dict[str, Any], *, days_until: int | None, window: str) -> dict[str, Any]:
    return {
        "date": str(row.get("Date") or "-"),
        "days_until": days_until,
        "window": window,
        "type": str(row.get("Type") or "-"),
        "cluster": _macro_week_cluster_label(row.get("Type")),
        "title": str(row.get("Title") or "-"),
        "symbol": str(row.get("Symbol") or "-"),
        "source_type": str(row.get("Source Type") or "-"),
        "validation": str(row.get("Validation") or "-"),
        "freshness": str(row.get("Freshness") or "-"),
        "quality_action": str(row.get("Quality Action") or "-"),
        "importance": str(row.get("Importance") or "-"),
        "tone": _macro_week_item_tone(row),
    }


def build_overview_macro_week_lane(
    events_snapshot: dict[str, Any] | None = None,
    *,
    horizon_days: int = 14,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
    limit: int = 8,
) -> dict[str, Any]:
    """Summarize existing event-calendar rows into a recent + upcoming macro context lane."""
    snapshot = events_snapshot or {}
    rows = _cockpit_frame(snapshot)
    coverage = dict(snapshot.get("coverage") or {})
    bounded_horizon_days = max(0, int(horizon_days or 14))
    bounded_recent_days = max(0, int(recent_days or 0))
    boundary_note = (
        "Context-only event calendar: not a trading signal, not Practical Validation, "
        "not Final Review decision, and not monitoring signal."
    )
    if rows.empty or "Days Until" not in rows:
        return {
            "schema_version": "overview_macro_week_lane_v2",
            "status": "NO_DATA",
            "summary": {
                "headline": "Macro week context unavailable",
                "detail": str(snapshot.get("message") or "No stored event rows are available."),
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "next_event_label": "No event in view",
            },
            "coverage": {
                "event_count": coverage.get("event_count"),
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "official_count": coverage.get("official_count"),
                "estimate_count": coverage.get("estimate_count"),
                "latest_collected_at": coverage.get("latest_collected_at"),
            },
            "clusters": {},
            "recent_items": [],
            "upcoming_items": [],
            "items": [],
            "boundary_note": boundary_note,
        }

    working = rows.copy()
    if "Type" not in working.columns:
        working["Type"] = working["Type Label"] if "Type Label" in working.columns else "Other"
    elif "Type Label" in working.columns:
        type_values = working["Type"].astype(str).str.strip()
        working["Type"] = working["Type"].where(type_values.ne("") & type_values.ne("nan"), working["Type Label"])
    working["_days_until"] = working["Days Until"].map(_safe_float)
    recent_rows = working[
        working["_days_until"].notna()
        & (working["_days_until"] < 0)
        & (working["_days_until"] >= -bounded_recent_days)
    ].copy()
    if not recent_rows.empty:
        recent_rows = recent_rows[
            recent_rows.apply(lambda row_value: _macro_week_is_major_macro(dict(row_value.dropna().to_dict())), axis=1)
        ].copy()
    upcoming_rows = working[
        working["_days_until"].notna()
        & (working["_days_until"] >= 0)
        & (working["_days_until"] <= bounded_horizon_days)
    ].copy()
    near_rows = pd.concat([recent_rows, upcoming_rows], ignore_index=True)
    if near_rows.empty:
        return {
            "schema_version": "overview_macro_week_lane_v2",
            "status": snapshot.get("status") or "OK",
            "summary": {
                "headline": f"No stored major events from the last {bounded_recent_days} days through the next {bounded_horizon_days} days",
                "detail": "Open Events for the full calendar and source quality view.",
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "next_event_label": "No event in view",
            },
            "coverage": {
                "event_count": coverage.get("event_count"),
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "official_count": coverage.get("official_count"),
                "estimate_count": coverage.get("estimate_count"),
                "latest_collected_at": coverage.get("latest_collected_at"),
            },
            "clusters": {},
            "recent_items": [],
            "upcoming_items": [],
            "items": [],
            "boundary_note": boundary_note,
        }

    recent_rows = recent_rows.sort_values(by=["_days_until", "Date", "Type"], ascending=[False, False, True], kind="mergesort")
    upcoming_rows = upcoming_rows.sort_values(by=["_days_until", "Date", "Type"], kind="mergesort")
    near_rows = pd.concat([recent_rows, upcoming_rows], ignore_index=True)
    recent_items: list[dict[str, Any]] = []
    upcoming_items: list[dict[str, Any]] = []
    cluster_order = ["FOMC", "CPI", "PPI", "Employment", "GDP", "Earnings", "Other"]
    clusters: dict[str, dict[str, Any]] = {
        label: {"label": label, "count": 0, "review_count": 0, "next_date": None, "tone": "neutral"}
        for label in cluster_order
    }

    for _, row_value in near_rows.iterrows():
        row = dict(row_value.drop(labels=["_days_until"], errors="ignore").dropna().to_dict())
        days_until = _cockpit_int(row_value.get("_days_until"))
        cluster = _macro_week_cluster_label(row.get("Type"))
        if cluster not in clusters:
            clusters[cluster] = {"label": cluster, "count": 0, "review_count": 0, "next_date": None, "tone": "neutral"}
        needs_review = _macro_week_event_needs_review(row)
        tone = _macro_week_item_tone(row)
        clusters[cluster]["count"] += 1
        clusters[cluster]["review_count"] += 1 if needs_review else 0
        clusters[cluster]["next_date"] = clusters[cluster]["next_date"] or str(row.get("Date") or "-")
        clusters[cluster]["tone"] = "warning" if clusters[cluster]["review_count"] else tone
        item = _macro_week_item_from_row(
            row,
            days_until=days_until,
            window="recent" if days_until is not None and days_until < 0 else "upcoming",
        )
        if item["window"] == "recent":
            recent_items.append(item)
        else:
            upcoming_items.append(item)

    clusters = {label: value for label, value in clusters.items() if int(value.get("count") or 0) > 0}
    review_count = sum(1 for _, row_value in near_rows.iterrows() if _macro_week_event_needs_review(dict(row_value.to_dict())))
    items = (recent_items + upcoming_items)[: max(1, int(limit or 8))]
    recent_items = recent_items[: max(1, int(limit or 8))]
    upcoming_items = upcoming_items[: max(1, int(limit or 8))]
    next_item = upcoming_items[0] if upcoming_items else {}
    next_event_label = (
        f"{next_item.get('type')} in {next_item.get('days_until')}d"
        if next_item
        else "No event in view"
    )
    official_near_count = int(
        near_rows.get("Source Type", pd.Series(dtype=str)).fillna("").astype(str).str.lower().eq("official").sum()
    )
    earnings_near_count = int(
        near_rows.get("Type", pd.Series(dtype=str)).fillna("").astype(str).str.upper().eq("EARNINGS").sum()
    )

    return {
        "schema_version": "overview_macro_week_lane_v2",
        "status": "REVIEW" if review_count else (snapshot.get("status") or "OK"),
        "summary": {
            "headline": (
                f"{len(recent_items)} recent major event(s) and {len(upcoming_rows)} upcoming event(s) in view"
                if recent_items
                else f"{len(upcoming_rows)} upcoming event(s) in the next {bounded_horizon_days} days"
            ),
            "detail": f"{official_near_count} official macro rows · {earnings_near_count} earnings rows · {review_count} need source review",
            "near_event_count": int(len(near_rows)),
            "recent_event_count": int(len(recent_rows)),
            "upcoming_event_count": int(len(upcoming_rows)),
            "next_event_label": next_event_label,
        },
        "coverage": {
            "event_count": coverage.get("event_count"),
            "near_event_count": int(len(near_rows)),
            "recent_event_count": int(len(recent_rows)),
            "upcoming_event_count": int(len(upcoming_rows)),
            "official_count": coverage.get("official_count"),
            "estimate_count": coverage.get("estimate_count"),
            "latest_collected_at": coverage.get("latest_collected_at"),
            "review_count": review_count,
        },
        "clusters": clusters,
        "recent_items": recent_items,
        "upcoming_items": upcoming_items,
        "items": items,
        "boundary_note": boundary_note,
    }


def _source_confidence_status(
    snapshot: dict[str, Any],
    *,
    review_hint: bool = False,
    no_data_if_empty: bool = False,
    row_key: str = "rows",
) -> str:
    rows = _cockpit_frame(snapshot, key=row_key)
    if no_data_if_empty and rows.empty:
        return "NO_DATA"
    status = _cockpit_card_status(snapshot.get("status"))
    normalized = status.strip().upper()
    if review_hint or normalized in {"REVIEW", "DUE", "STALE", "PARTIAL", "MISSING", "FAILED", "ERROR", "NO_DATA"}:
        return "REVIEW" if normalized != "NO_DATA" else "NO_DATA"
    return "OK"


def _source_confidence_item(
    *,
    item_id: str,
    title: str,
    surface: str,
    source: str,
    owner: str,
    status: str,
    freshness: Any,
    detail: str,
    caveat: str,
    next_check: str,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "surface": surface,
        "source": source,
        "owner": owner,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "freshness": str(freshness or "-"),
        "freshness_label": _cockpit_freshness_label(freshness),
        "detail": detail,
        "caveat": caveat,
        "next_check": next_check,
    }


def _source_confidence_data_review_count(collection_ops_snapshot: dict[str, Any]) -> int:
    coverage = dict(collection_ops_snapshot.get("coverage") or {})
    return sum(
        _cockpit_int(coverage.get(key))
        for key in ("due_count", "stale_count", "partial_count", "missing_count", "failed_count")
    )


def build_overview_source_confidence_catalog(
    *,
    market_movers_snapshot: dict[str, Any] | None = None,
    group_leadership_snapshot: dict[str, Any] | None = None,
    futures_macro_snapshot: dict[str, Any] | None = None,
    sentiment_snapshot: dict[str, Any] | None = None,
    events_snapshot: dict[str, Any] | None = None,
    collection_ops_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only source/provider confidence catalog from already loaded Overview snapshots."""
    movers = market_movers_snapshot or {}
    movers_coverage = dict(movers.get("coverage") or {})
    refresh_state = movers_coverage.get("refresh_state")
    refresh_label = _cockpit_status_text(refresh_state)
    refresh_detail = refresh_state.get("detail") if isinstance(refresh_state, dict) else None
    prices_review = bool(refresh_label and refresh_label.upper() not in {"OK", "SUCCESS", "FRESH"})
    prices_status = _source_confidence_status(movers, review_hint=prices_review, no_data_if_empty=True)
    prices_returnable = _cockpit_int(movers_coverage.get("returnable_count"))
    prices_universe = _cockpit_int(movers_coverage.get("universe_count"))

    groups = group_leadership_snapshot or {}
    group_coverage = dict(groups.get("coverage") or {})
    breadth_status = _source_confidence_status(groups, no_data_if_empty=True)

    futures = futures_macro_snapshot or {}
    futures_coverage = dict(futures.get("coverage") or {})
    futures_status = _source_confidence_status(futures)
    standardized_count = _cockpit_int(futures_coverage.get("standardized_count"))
    futures_symbol_count = _cockpit_int(futures_coverage.get("symbol_count"))

    sentiment = sentiment_snapshot or {}
    sentiment_analysis = dict(sentiment.get("analysis") or {})
    sentiment_confidence = dict(sentiment_analysis.get("data_confidence") or {})
    sentiment_status_text = str(sentiment_confidence.get("status") or sentiment.get("status") or "NO_DATA")
    sentiment_status_normalized = sentiment_status_text.strip().lower()
    if sentiment_status_normalized in {"high", "ok", "fresh"}:
        sentiment_status = "OK"
    elif sentiment_status_normalized == "no_data":
        sentiment_status = "NO_DATA"
    else:
        sentiment_status = _source_confidence_status(sentiment, review_hint=True)
    sentiment_coverage = dict(sentiment.get("coverage") or {})

    events = events_snapshot or {}
    events_coverage = dict(events.get("coverage") or {})
    event_review_count = max(
        _cockpit_int(events_coverage.get("needs_review_count")),
        _cockpit_int(events_coverage.get("action_required_count")),
        _cockpit_int(events_coverage.get("stale_estimate_count")),
    )
    events_status = _source_confidence_status(
        events,
        review_hint=event_review_count > 0,
        no_data_if_empty=True,
    )

    data_health = collection_ops_snapshot or {}
    data_coverage = dict(data_health.get("coverage") or {})
    data_review_count = _source_confidence_data_review_count(data_health)
    data_status = _source_confidence_status(data_health, review_hint=data_review_count > 0, no_data_if_empty=True)

    items = [
        _source_confidence_item(
            item_id="prices",
            title="Prices / Movers",
            surface="Market Movers",
            source="Stored price rows and intraday snapshot tables",
            owner="Workspace > Ingestion plus approved Overview bounded refresh",
            status=prices_status,
            freshness=movers_coverage.get("snapshot_time_utc")
            or refresh_detail
            or movers_coverage.get("effective_end_date"),
            detail=f"{prices_returnable}/{prices_universe} symbols returnable · 갱신 상태 {refresh_label or _cockpit_status_label(prices_status)}",
            caveat="가격 맥락은 오래됐거나 부분적일 수 있으며, 주문 실행용 가격이 아닙니다.",
            next_check="Market Movers에서 수익률 기준일과 누락 여부를 확인합니다.",
        ),
        _source_confidence_item(
            item_id="breadth",
            title="Breadth / Groups",
            surface="Sector / Industry",
            source="Stored price rows plus profile sector / industry metadata",
            owner="Overview group leadership read model",
            status=breadth_status,
            freshness=group_coverage.get("snapshot_time_utc") or group_coverage.get("effective_end_date"),
            detail=f"{_cockpit_int(group_coverage.get('returnable_count'))}/{_cockpit_int(group_coverage.get('universe_count'))} symbols grouped",
            caveat="시장 폭은 참여도와 집중도를 요약할 뿐 종목 선택 규칙이 아닙니다.",
            next_check="Sector / Industry에서 그룹 자료가 오래됐거나 부족한지 확인합니다.",
        ),
        _source_confidence_item(
            item_id="futures",
            title="Futures Context",
            surface="Futures Monitor",
            source="Stored futures OHLCV read by Macro Thermometer",
            owner="Workspace > Ingestion futures collector / Overview bounded refresh",
            status=futures_status,
            freshness=futures_coverage.get("latest_date") or futures_coverage.get("latest_candle_time"),
            detail=f"{standardized_count}/{futures_symbol_count} futures symbols standardized",
            caveat="무료 선물 provider 기반의 배경 자료입니다. 오래됨과 공백은 그대로 보이며 신뢰 보장이 아닙니다.",
            next_check="Futures Monitor에서 risk-on, 금리 압력, 안전자산 배경 근거를 확인합니다.",
        ),
        _source_confidence_item(
            item_id="sentiment",
            title="Sentiment",
            surface="Sentiment",
            source="CNN Fear & Greed and AAII sentiment observations",
            owner="Market sentiment ingestion and loader",
            status=sentiment_status,
            freshness=sentiment_confidence.get("detail") or sentiment_coverage.get("latest_observation_date"),
            detail=(
                f"CNN {_overview_round(sentiment_coverage.get('cnn_score'))} · "
                f"AAII spread {_overview_round(sentiment_coverage.get('aaii_bull_bear_spread'))}"
            ),
            caveat="심리는 배경 자료일 뿐 validation, Final Review, monitoring gate를 바꾸지 않습니다.",
            next_check="Sentiment에서 출처 수, 오래된 자료, 신뢰도 저하 여부를 확인합니다.",
        ),
        _source_confidence_item(
            item_id="events",
            title="Events",
            surface="Events",
            source="Official macro calendars plus provider-estimated earnings rows",
            owner="Market event calendar collectors",
            status=events_status,
            freshness=events_coverage.get("latest_collected_at"),
            detail=(
                f"{_cockpit_int(events_coverage.get('event_count'))} events · "
                f"{_cockpit_int(events_coverage.get('official_count'))} official · "
                f"{_cockpit_int(events_coverage.get('estimate_count'))} estimates · "
                f"확인 필요 {event_review_count}"
            ),
            caveat="공식 macro 일정과 provider 추정 실적 일정은 구분해서 읽어야 합니다.",
            next_check="Events에서 추정 일정이 오래됐거나 확인이 필요한지 봅니다.",
        ),
        _source_confidence_item(
            item_id="data_health",
            title="Data Health",
            surface="Data Health",
            source="DB freshness summaries and local run history",
            owner="Data Health read model and owning collection surfaces",
            status=data_status,
            freshness=data_coverage.get("latest_success_at") or data_coverage.get("latest_auto_at"),
            detail=(
                f"OK {_cockpit_int(data_coverage.get('ok_count'))} · "
                f"확인 필요 {data_review_count}"
            ),
            caveat="Data Health는 확인 위치를 안내할 뿐 여기서 job queue를 만들거나 저장하지 않습니다.",
            next_check="Data Health에서 예정, 오래됨, 부분, 누락, 실패 자료의 확인 위치를 봅니다.",
        ),
    ]

    review_items = [item for item in items if item["status"] != "OK"]
    status = "REVIEW" if review_items else "OK"
    return {
        "schema_version": "overview_source_confidence_catalog_v1",
        "status": status,
        "summary": {
            "headline": (
                f"확인할 자료 영역 {len(review_items)}개"
                if review_items
                else "자료 기준 정상"
            ),
            "detail": "같은 저장 자료의 출처, 기준일, 관리 위치, 참고 위치입니다.",
            "review_count": len(review_items),
        },
        "items": items,
        "next_checks": [
            {
                "surface": item["surface"],
                "title": item["title"],
                "reason": item["detail"],
                "action": item["next_check"],
                "tone": item["tone"],
            }
            for item in review_items[:4]
        ],
        "boundary_note": (
            "자료 기준은 context 전용입니다. trade signal, validation PASS/BLOCKER, Final Review decision, "
            "monitoring signal, provider fetch, write action을 만들지 않습니다."
        ),
    }


def _cockpit_count_label(value: int, noun: str) -> str:
    return f"{value} {noun}" if value != 1 else f"1 {noun.rstrip('s')}"


def _cockpit_status_label(status: Any) -> str:
    normalized = _cockpit_status_text(status).strip().lower()
    if normalized in {"ok", "success", "actual", "fresh", "high"}:
        return "자료 정상"
    if normalized in {"review", "due", "partial"}:
        return "자료 확인 필요"
    if normalized == "stale":
        return "자료 오래됨"
    if normalized in {"missing", "no_data", "not_run", "insufficient_data", "no_universe"}:
        return "자료 부족"
    if normalized in {"failed", "error"}:
        return "확인 실패"
    return _cockpit_status_text(status) or "상태 미확인"


def _cockpit_badge_label(label: Any) -> str:
    text = str(label or "").strip()
    mapping = {
        "coverage": "자료 범위",
        "state": "자료 상태",
        "participation": "참여 비율",
        "confidence": "자료 신뢰도",
        "AAII spread": "AAII 온도차",
        "events": "일정",
        "review": "확인 필요",
        "OK": "정상",
        "Risk-On": "위험선호",
        "Rate Pressure": "금리 압력",
        "Safe Haven": "안전자산",
    }
    return mapping.get(text, text)


def _cockpit_freshness_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return "기준일 없음"
    return text


def _cockpit_copy_value(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return fallback
    return text


def _build_cockpit_summary_copy(
    cards: Sequence[dict[str, Any]],
    *,
    context_review_count: int,
) -> tuple[str, str]:
    movement_card = cards[0] if len(cards) > 0 else {}
    breadth_card = cards[1] if len(cards) > 1 else {}
    futures_card = cards[2] if len(cards) > 2 else {}
    movement_value = _cockpit_copy_value(movement_card.get("value"), "")
    breadth_value = _cockpit_copy_value(breadth_card.get("value"), "섹터 리더십 미확인")
    futures_value = _cockpit_copy_value(futures_card.get("value"), "혼재된 매크로 흐름")

    headline = (
        f"오늘 가장 큰 움직임은 {movement_value}입니다."
        if movement_value
        else "오늘은 아직 뚜렷한 상위 변동 종목이 없습니다."
    )
    breadth_clause = (
        "섹터 리더십은 아직 뚜렷하지 않고"
        if breadth_value == "섹터 리더십 미확인"
        else f"{breadth_value} 리더십이 확인되고"
    )
    if context_review_count:
        next_sentence = (
            f"확인할 자료 {context_review_count}개를 먼저 본 뒤 Market Movers, Sector, Futures 흐름을 함께 읽으세요."
        )
    else:
        next_sentence = "저장된 DB 자료 기준으로 Market Movers, Sector, Futures 흐름을 바로 이어서 읽을 수 있습니다."
    detail = f"{breadth_clause}, 선물/매크로 배경은 {futures_value}입니다. {next_sentence}"
    return headline, detail


def _cockpit_score_badges(scores: pd.DataFrame, *, limit: int = 3) -> list[dict[str, Any]]:
    badges: list[dict[str, Any]] = []
    if scores.empty:
        return badges
    for _, row in scores.head(limit).iterrows():
        score_name = str(row.get("Score") or row.get("score") or "-").replace(" Score", "")
        score_value = row.get("Value") if "Value" in row else row.get("value")
        tone = row.get("Tone") if "Tone" in row else row.get("tone")
        badges.append(
            {
                "label": _cockpit_badge_label(score_name),
                "value": "-" if score_value in (None, "") else str(score_value),
                "tone": tone or _cockpit_status_tone(score_value),
            }
        )
    return badges


def _build_cockpit_movement_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    top_row = _cockpit_first_row(snapshot)
    symbol = str(top_row.get("Symbol") or "-")
    move = _cockpit_percent(top_row.get("Return %"))
    name = top_row.get("Name") or symbol
    sector = top_row.get("Sector") or "Unknown sector"
    period = snapshot.get("period_label") or snapshot.get("period") or "Market"
    universe = snapshot.get("universe_label") or snapshot.get("universe_code") or "selected universe"
    refresh_state = coverage.get("refresh_state")
    refresh_detail = refresh_state.get("detail") if isinstance(refresh_state, dict) else None
    status = _cockpit_card_status(refresh_state, snapshot.get("status"))
    if not top_row:
        value = str(snapshot.get("status") or "No data")
        detail = str(snapshot.get("message") or "No stored mover rows are available.")
    else:
        value = f"{symbol} {move}"
        detail = f"{name} · {sector} · {period} · {universe}"
    return {
        "id": "movement",
        "title": "Market Movement",
        "question": "지금 무엇이 움직이나요?",
        "value": value,
        "detail": detail,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "source": "Market Movers",
        "freshness": coverage.get("effective_end_date") or refresh_detail or coverage.get("snapshot_time_utc") or "-",
        "freshness_label": _cockpit_freshness_label(
            coverage.get("effective_end_date") or refresh_detail or coverage.get("snapshot_time_utc")
        ),
        "target_tab": "Market Movers",
        "badges": [
            {"label": "자료 범위", "value": f"{coverage.get('returnable_count') or 0}/{coverage.get('universe_count') or 0}", "tone": "neutral"},
            {"label": "자료 상태", "value": _cockpit_status_label(status), "tone": _cockpit_status_tone(status)},
        ],
    }


def _build_cockpit_breadth_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    top_row = _cockpit_first_row(snapshot)
    status = _cockpit_card_status(snapshot.get("status"))
    if not top_row:
        value = str(snapshot.get("status") or "No data")
        detail = str(snapshot.get("message") or "No stored sector / industry leadership rows are available.")
        share_value = "-"
    else:
        group = str(top_row.get("Group") or "-")
        weighted = _cockpit_percent(top_row.get("Market Cap Weighted Return %"))
        positive_share = _safe_float(top_row.get("Positive Symbol Share %"))
        share_value = "-" if positive_share is None else f"{positive_share:.0f}%"
        breadth_label = "넓게 확산" if positive_share is not None and positive_share >= 65 else "일부 그룹 집중"
        value = group
        detail = f"{group} 리더십: 시총가중 {weighted} · 상승 종목 {share_value} · {breadth_label}"
    return {
        "id": "breadth",
        "title": "Breadth / Concentration",
        "question": "움직임이 넓게 퍼졌나요, 일부에 집중됐나요?",
        "value": value,
        "detail": detail,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "source": "Sector / Industry",
        "freshness": coverage.get("effective_end_date") or "-",
        "freshness_label": _cockpit_freshness_label(coverage.get("effective_end_date")),
        "target_tab": "Sector / Industry",
        "badges": [
            {"label": "자료 범위", "value": f"{coverage.get('returnable_count') or 0}/{coverage.get('universe_count') or 0}", "tone": "neutral"},
            {"label": "참여 비율", "value": share_value, "tone": "positive" if share_value != "-" else "neutral"},
        ],
    }


def _build_cockpit_futures_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    summary = dict(snapshot.get("summary") or {})
    scores = _cockpit_frame(snapshot, key="scores")
    status = _cockpit_card_status(snapshot.get("status"))
    scenario = str(summary.get("scenario") or snapshot.get("status") or "Futures context pending")
    detail = str(summary.get("summary") or "Stored futures daily OHLCV provides context only.")
    return {
        "id": "futures",
        "title": "Futures Background",
        "question": "risk-on, rate pressure, safe-haven 중 어떤 배경인가요?",
        "value": scenario,
        "detail": detail,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "source": "Futures Macro Thermometer",
        "freshness": coverage.get("latest_date") or "-",
        "freshness_label": _cockpit_freshness_label(coverage.get("latest_date")),
        "target_tab": "Futures Monitor",
        "badges": _cockpit_score_badges(scores) or [
            {"label": "자료 범위", "value": f"{coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}", "tone": "neutral"}
        ],
    }


def _build_cockpit_sentiment_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    confidence = dict(analysis.get("data_confidence") or {})
    confidence_status = confidence.get("status") or snapshot.get("status")
    status = _cockpit_card_status(snapshot.get("status"))
    cnn_score = coverage.get("cnn_score")
    cnn_rating = coverage.get("cnn_rating") or "-"
    spread = coverage.get("aaii_bull_bear_spread")
    return {
        "id": "sentiment",
        "title": "Sentiment Backdrop",
        "question": "시장 심리 배경은 어떤가요?",
        "value": analysis.get("phase_label") or cnn_rating or status,
        "detail": analysis.get("headline") or "CNN Fear & Greed / AAII context is unavailable.",
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(confidence_status),
        "source": "CNN Fear & Greed / AAII",
        "freshness": confidence.get("detail") or "-",
        "freshness_label": _cockpit_freshness_label(confidence.get("detail")),
        "target_tab": "Sentiment",
        "badges": [
            {"label": "CNN", "value": "-" if cnn_score in (None, "") else f"{float(cnn_score):.1f} {cnn_rating}", "tone": "neutral"},
            {"label": "AAII 온도차", "value": "-" if spread in (None, "") else f"{float(spread):+.1f}pp", "tone": "neutral"},
            {"label": "자료 신뢰도", "value": _cockpit_status_label(confidence_status), "tone": _cockpit_status_tone(confidence_status)},
        ],
    }


def _cockpit_event_label(row: dict[str, Any]) -> str:
    type_label = str(row.get("Type Label") or "").strip()
    if type_label and type_label != "-":
        return type_label
    return _macro_week_cluster_label(row.get("Type"))


def _cockpit_event_days_value(row: dict[str, Any]) -> int | None:
    value = row.get("Days Until") if row else None
    if value in (None, ""):
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    safe_value = _safe_float(value)
    return int(safe_value) if safe_value is not None else None


def _cockpit_event_days_korean(days: int | None) -> str:
    if days is None:
        return "일정일 확인 필요"
    if days < 0:
        return f"{abs(days)}일 전"
    if days == 0:
        return "오늘"
    return f"{days}일 후"


def _cockpit_major_event_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty or "Type" not in rows:
        return pd.DataFrame()
    return rows[rows["Type"].map(_is_major_macro_event_type)].copy()


def _build_cockpit_events_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    rows = _cockpit_frame(snapshot)
    major_rows = _cockpit_major_event_rows(rows)
    if not major_rows.empty and "Days Until" in major_rows:
        major_rows["Days Until"] = pd.to_numeric(major_rows["Days Until"], errors="coerce")
    recent_major = pd.DataFrame()
    upcoming_major = pd.DataFrame()
    if not major_rows.empty and "Days Until" in major_rows:
        recent_major = major_rows[(major_rows["Days Until"] < 0) & (major_rows["Days Until"] >= -EVENT_RECENT_WINDOW_DAYS)].sort_values(
            ["Days Until", "Date", "Type"],
            ascending=[False, False, True],
            kind="mergesort",
        )
        upcoming_major = major_rows[major_rows["Days Until"] >= 0].sort_values(
            ["Days Until", "Date", "Type"],
            kind="mergesort",
        )
    row = dict(recent_major.iloc[0].dropna().to_dict()) if not recent_major.empty else _cockpit_first_row(snapshot)
    next_major = dict(upcoming_major.iloc[0].dropna().to_dict()) if not upcoming_major.empty else {}
    status = _cockpit_card_status(snapshot.get("status"))
    next_date = coverage.get("next_event_date") or next_major.get("Date") or row.get("Date") or row.get("event_date")
    title = row.get("Title") or row.get("title") or row.get("Type Label") or "Upcoming events"
    days = _cockpit_event_days_value(row)
    event_count = _cockpit_int(coverage.get("event_count"))
    review_count = _cockpit_int(coverage.get("needs_review_count"))
    event_label = _cockpit_event_label(row)
    if row and days is not None and days < 0 and _is_major_macro_event_type(row.get("Type")):
        value = f"최근 {event_label} 발표 확인 필요"
    elif next_major:
        next_days = _cockpit_event_days_value(next_major)
        value = f"다음 {_cockpit_event_label(next_major)} {_cockpit_event_days_korean(next_days)}"
    else:
        value = str(next_date or "No upcoming event")
    detail_parts = [str(title), _cockpit_event_days_korean(days)]
    if next_major and row and next_major.get("Type") != row.get("Type"):
        next_days = _cockpit_event_days_value(next_major)
        detail_parts.append(f"다음 {_cockpit_event_label(next_major)} {_cockpit_event_days_korean(next_days)}")
    detail_parts.append(f"주요 일정 {event_count}개")
    return {
        "id": "events",
        "title": "Near Events",
        "question": "가까운 주요 이벤트가 있나요?",
        "value": value,
        "detail": " · ".join(part for part in detail_parts if part and part != "-"),
        "status": "Review" if review_count else status,
        "status_label": _cockpit_status_label("Review" if review_count else status),
        "tone": "warning" if review_count else _cockpit_status_tone(status),
        "source": "Market Event Calendar",
        "freshness": coverage.get("latest_collected_at") or "-",
        "freshness_label": _cockpit_freshness_label(coverage.get("latest_collected_at")),
        "target_tab": "Events",
        "badges": [
            {"label": "일정", "value": str(event_count), "tone": "neutral"},
            {"label": "확인 필요", "value": str(review_count), "tone": "warning" if review_count else "positive"},
        ],
    }


def _build_cockpit_data_card(snapshot: dict[str, Any]) -> tuple[dict[str, Any], int]:
    coverage = dict(snapshot.get("coverage") or {})
    review_count = sum(
        _cockpit_int(coverage.get(key))
        for key in ("due_count", "stale_count", "partial_count", "missing_count", "failed_count")
    )
    status = "REVIEW" if review_count else _cockpit_card_status(snapshot.get("status"))
    value = "일부 자료 확인 필요" if review_count else "자료 정상"
    detail = (
        f"해석 전에 Data Health에서 확인할 자료 {review_count}개를 먼저 봅니다."
        if review_count
        else "현재 추적 중인 Overview 자료는 바로 참고할 수 있습니다."
    )
    return (
        {
            "id": "data",
            "title": "Data Confidence",
            "question": "이 context를 그대로 참고해도 되나요?",
            "value": value,
            "detail": detail,
            "status": status,
            "status_label": _cockpit_status_label(status),
            "tone": _cockpit_status_tone(status),
            "source": "Data Health",
            "freshness": coverage.get("latest_success_at") or coverage.get("latest_auto_at") or "-",
            "freshness_label": _cockpit_freshness_label(coverage.get("latest_success_at") or coverage.get("latest_auto_at")),
            "target_tab": "Data Health",
            "badges": [
                {"label": "정상", "value": str(coverage.get("ok_count") or 0), "tone": "positive"},
                {"label": "확인 필요", "value": str(review_count), "tone": "warning" if review_count else "positive"},
            ],
        },
        review_count,
    )


def _cockpit_ops_next_check(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    rows = _cockpit_frame(snapshot)
    if rows.empty or "Status" not in rows:
        return None
    review_rows = rows[~rows["Status"].astype(str).str.upper().isin(["OK", "SUCCESS"])]
    if review_rows.empty:
        return None
    row = dict(review_rows.iloc[0].dropna().to_dict())
    return {
        "target_tab": "Data Health",
        "title": str(row.get("Area") or "Data Health"),
        "reason": f"{_cockpit_status_label(row.get('Status') or 'Review')} · 자료 기준 {_cockpit_freshness_label(row.get('Data Freshness'))}",
        "action": "Data Health에서 확인 위치와 필요한 갱신 경로를 먼저 봅니다.",
        "tone": _cockpit_status_tone(row.get("Status")),
    }


def _cockpit_event_next_check(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    coverage = dict(snapshot.get("coverage") or {})
    needs_review = _cockpit_int(coverage.get("needs_review_count"))
    rows = _cockpit_frame(snapshot)
    major_rows = _cockpit_major_event_rows(rows)
    row: dict[str, Any] = {}
    if not major_rows.empty and "Days Until" in major_rows:
        major_rows = major_rows.copy()
        major_rows["Days Until"] = pd.to_numeric(major_rows["Days Until"], errors="coerce")
        recent = major_rows[(major_rows["Days Until"] < 0) & (major_rows["Days Until"] >= -EVENT_RECENT_WINDOW_DAYS)].sort_values(
            ["Days Until", "Date", "Type"],
            ascending=[False, False, True],
            kind="mergesort",
        )
        upcoming = major_rows[major_rows["Days Until"] >= 0].sort_values(["Days Until", "Date", "Type"], kind="mergesort")
        if not recent.empty:
            row = dict(recent.iloc[0].dropna().to_dict())
        elif not upcoming.empty:
            row = dict(upcoming.iloc[0].dropna().to_dict())
    if not row:
        row = _cockpit_first_row(snapshot)
    days = _cockpit_event_days_value(row)
    if not row and not needs_review:
        return None
    if needs_review or (days is not None and -EVENT_RECENT_WINDOW_DAYS <= days <= 7):
        return {
            "target_tab": "Events",
            "title": str(row.get("Title") or row.get("Type Label") or "Upcoming event"),
            "reason": _cockpit_event_days_korean(days) if row else f"확인할 일정 {needs_review}개",
            "action": "시장 context를 해석하기 전에 Events를 확인하세요.",
            "tone": "warning" if needs_review else "primary",
        }
    return None


def _cockpit_brief_row(card: dict[str, Any], *, label: str) -> dict[str, Any]:
    """Project an existing cockpit card into a sentence-first brief row."""
    return {
        "id": card.get("id"),
        "label": label,
        "value": card.get("value"),
        "detail": card.get("detail"),
        "status": card.get("status"),
        "status_label": card.get("status_label"),
        "tone": card.get("tone"),
        "target_tab": card.get("target_tab"),
        "source": card.get("source"),
        "freshness_label": card.get("freshness_label"),
        "badges": card.get("badges"),
    }


def build_overview_macro_context_cockpit(
    *,
    market_movers_snapshot: dict[str, Any] | None = None,
    group_leadership_snapshot: dict[str, Any] | None = None,
    futures_macro_snapshot: dict[str, Any] | None = None,
    sentiment_snapshot: dict[str, Any] | None = None,
    events_snapshot: dict[str, Any] | None = None,
    collection_ops_snapshot: dict[str, Any] | None = None,
    historical_analog_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a summary-first Overview cockpit from existing read-only market context snapshots."""
    if market_movers_snapshot is None:
        try:
            market_movers_snapshot = build_market_movers_snapshot(
                universe_code="SP500",
                period="daily",
                top_n=10,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            market_movers_snapshot = _cockpit_error_snapshot("Market movers", exc)
    if group_leadership_snapshot is None:
        try:
            group_leadership_snapshot = build_group_leadership_snapshot(
                universe_code="SP500",
                group_by="sector",
                period="daily",
                top_n=10,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            group_leadership_snapshot = _cockpit_error_snapshot("Sector leadership", exc)
    if futures_macro_snapshot is None:
        try:
            from app.services.futures_macro_thermometer import load_overview_futures_macro_snapshot

            futures_macro_snapshot = load_overview_futures_macro_snapshot()
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            futures_macro_snapshot = _cockpit_error_snapshot("Futures macro", exc)
    if sentiment_snapshot is None:
        try:
            sentiment_snapshot = build_market_sentiment_snapshot()
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            sentiment_snapshot = _cockpit_error_snapshot("Market sentiment", exc)
    if events_snapshot is None:
        try:
            events_snapshot = build_market_events_snapshot(event_type=None, horizon_days=60, limit=100)
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            events_snapshot = _cockpit_error_snapshot("Market events", exc)
    if collection_ops_snapshot is None:
        try:
            collection_ops_snapshot = build_collection_ops_snapshot()
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            collection_ops_snapshot = _cockpit_error_snapshot("Data Health", exc)

    cards = [
        _build_cockpit_movement_card(market_movers_snapshot),
        _build_cockpit_breadth_card(group_leadership_snapshot),
        _build_cockpit_futures_card(futures_macro_snapshot),
        _build_cockpit_sentiment_card(sentiment_snapshot),
        _build_cockpit_events_card(events_snapshot),
    ]
    data_card, data_review_count = _build_cockpit_data_card(collection_ops_snapshot)
    cards.append(data_card)

    review_cards = [
        card for card in cards
        if _cockpit_status_tone(card.get("status")) in {"warning", "danger"}
    ]
    status = "REVIEW" if review_cards else "OK"
    source_confidence = build_overview_source_confidence_catalog(
        market_movers_snapshot=market_movers_snapshot,
        group_leadership_snapshot=group_leadership_snapshot,
        futures_macro_snapshot=futures_macro_snapshot,
        sentiment_snapshot=sentiment_snapshot,
        events_snapshot=events_snapshot,
        collection_ops_snapshot=collection_ops_snapshot,
    )
    next_checks = [
        item
        for item in [
            _cockpit_ops_next_check(collection_ops_snapshot),
            _cockpit_event_next_check(events_snapshot),
            {
                "target_tab": "Futures Monitor",
                "title": "Futures 배경 확인",
                "reason": str(cards[2].get("value") or "-"),
                "action": "위험선호 / 금리 압력 / 안전자산 근거는 Futures Monitor에서 확인하세요.",
                "tone": cards[2].get("tone") or "neutral",
            },
            {
                "target_tab": "Market Movers",
                "title": "시장 움직임 확인",
                "reason": str(cards[0].get("value") or "-"),
                "action": "수익률, 거래량, Why It Moved 단서는 Market Movers에서 확인하세요.",
                "tone": cards[0].get("tone") or "neutral",
            },
        ]
        if item is not None
    ][:4]
    context_review_count = max(data_review_count, len(review_cards))
    next_path = " → ".join(
        str(item.get("target_tab") or "-")
        for item in next_checks
        if str(item.get("target_tab") or "").strip()
    ) or "필요한 deep tab 없음"
    source_status = str(source_confidence.get("status") or status)
    sector_pressure = build_overview_breadth_heatmap_summary(group_leadership_snapshot, limit=8)
    event_timeline = build_overview_macro_week_lane(events_snapshot, horizon_days=14, limit=6)
    summary_headline, summary_detail = _build_cockpit_summary_copy(
        cards,
        context_review_count=context_review_count,
    )
    rail = [
        {
            "label": "자료 상태",
            "value": "일부 자료 확인 필요" if status == "REVIEW" else "자료 정상",
            "detail": f"확인할 자료 {context_review_count}개" if context_review_count else "바로 참고 가능",
            "tone": _cockpit_status_tone(status),
        },
        {
            "label": "Top Mover",
            "value": str(cards[0].get("value") or "-"),
            "detail": str(cards[0].get("freshness_label") or cards[0].get("target_tab") or "Market Movers"),
            "tone": cards[0].get("tone") or "neutral",
        },
        {
            "label": "Breadth",
            "value": str(cards[1].get("value") or "-"),
            "detail": str(cards[1].get("freshness_label") or cards[1].get("target_tab") or "Group Leadership"),
            "tone": cards[1].get("tone") or "neutral",
        },
        {
            "label": "Macro",
            "value": str(cards[2].get("value") or "-"),
            "detail": str(cards[2].get("freshness_label") or cards[2].get("target_tab") or "Futures Monitor"),
            "tone": cards[2].get("tone") or "neutral",
        },
        {
            "label": "Next Event",
            "value": str(cards[4].get("value") or "-"),
            "detail": str(cards[4].get("freshness_label") or cards[4].get("target_tab") or "Events"),
            "tone": cards[4].get("tone") or "neutral",
        },
    ]
    for index, card in enumerate(cards):
        card["group"] = "core" if index < 3 else "supporting"
        card["priority_label"] = "시장 브리프" if index < 3 else ("근거" if card.get("id") == "data" else "다음 맥락")

    brief_rows = [
        _cockpit_brief_row(cards[0], label="무엇이 움직였나"),
        _cockpit_brief_row(cards[1], label="확산/집중인가"),
        _cockpit_brief_row(cards[2], label="Futures/Macro 배경"),
    ]
    interpretation_cues = [
        _cockpit_brief_row(cards[4], label="이벤트 압력"),
        _cockpit_brief_row(cards[3], label="심리 확인"),
        _cockpit_brief_row(cards[2], label="매크로 확인"),
    ]

    return {
        "schema_version": "overview_macro_context_cockpit_v1",
        "status": status,
        "summary": {
            "headline": summary_headline,
            "detail": summary_detail,
            "tone": _cockpit_status_tone(status),
            "review_count": context_review_count,
            "data_review_count": data_review_count,
            "next_path": next_path,
            "rail": rail,
        },
        "brief_rows": brief_rows,
        "interpretation_cues": interpretation_cues,
        "sector_pressure": sector_pressure,
        "event_timeline": event_timeline,
        "historical_analog": historical_analog_snapshot or {},
        "cards": cards,
        "next_checks": next_checks,
        "source_confidence": source_confidence,
        "boundary_note": (
            "context 전용 market backdrop입니다. 이 cockpit은 trade signal, validation PASS/BLOCKER, "
            "Final Review decision, monitoring signal, registry write, saved setup write, broker order, auto rebalance를 만들지 않습니다."
        ),
    }


def _ranked_movers_frame(rows: list[dict[str, Any]], *, top_n: int) -> pd.DataFrame:
    ranked = sorted(rows, key=lambda row: (-float(row["return_pct"]), row["symbol"]))[:top_n]
    out = [
        {
            "Rank": index,
            "Symbol": row["symbol"],
            "Name": row["name"] or "-",
            "Return %": round(float(row["return_pct"]), 2),
            "Previous Return %": round(float(row["previous_return_pct"]), 2)
            if row.get("previous_return_pct") is not None
            else None,
            "Momentum Delta pp": round(float(row["momentum_delta_pp"]), 2)
            if row.get("momentum_delta_pp") is not None
            else None,
            "Volume": int(row["volume"]) if row.get("volume") is not None else None,
            "Dollar Volume": round(float(row["dollar_volume"]), 2)
            if row.get("dollar_volume") is not None
            else None,
            "Start Price": round(float(row["start_price"]), 4),
            "End Price": round(float(row["end_price"]), 4),
            "Sector": row["sector"],
            "Industry": row["industry"],
            "Market Cap": int(row["market_cap"]) if row["market_cap"] else None,
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
            "Previous Start Date": row.get("previous_start_date") or "-",
            "Previous End Date": row.get("previous_end_date") or "-",
            "Price Source": row.get("price_source") or "EOD DB",
        }
        for index, row in enumerate(ranked, start=1)
    ]
    return _rows_frame(out, columns=MOVERS_COLUMNS)


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


def _current_period_volume_dates(date_window: dict[str, Any], *, period: str) -> list[str]:
    normalized_period = str(period or "daily").strip().lower()
    offset = VALID_PERIODS.get(normalized_period, 1)
    dates = [
        row_date
        for row in list(date_window.get("eligible_dates") or [])[: max(1, offset)]
        if (row_date := _iso_date(row.get("date")))
    ]
    if dates:
        return dates
    end_date = _iso_date(date_window.get("end_date"))
    return [end_date] if end_date else []


def _load_period_volume_stats(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    if not symbols or not dates:
        return {}
    symbol_placeholders = ",".join(["%s"] * len(symbols))
    date_placeholders = ",".join(["%s"] * len(dates))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT
            symbol,
            SUM(CASE WHEN volume IS NOT NULL THEN volume ELSE 0 END) AS total_volume,
            AVG(volume) AS avg_daily_volume,
            SUM(
                CASE
                    WHEN volume IS NOT NULL AND COALESCE(adj_close, close) IS NOT NULL
                    THEN COALESCE(adj_close, close) * volume
                    ELSE 0
                END
            ) AS total_dollar_volume,
            AVG(
                CASE
                    WHEN volume IS NOT NULL AND COALESCE(adj_close, close) IS NOT NULL
                    THEN COALESCE(adj_close, close) * volume
                    ELSE NULL
                END
            ) AS avg_daily_dollar_volume,
            COUNT(volume) AS volume_days
        FROM nyse_price_history FORCE INDEX (uk_symbol_timeframe_date)
        WHERE symbol IN ({symbol_placeholders})
          AND timeframe = %s
          AND `date` IN ({date_placeholders})
        GROUP BY symbol
        """,
        list(symbols) + ["1d"] + list(dates),
    )
    stats: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        stats[symbol] = {
            "total_volume": _safe_float(row.get("total_volume")),
            "avg_daily_volume": _safe_float(row.get("avg_daily_volume")),
            "total_dollar_volume": _safe_float(row.get("total_dollar_volume")),
            "avg_daily_dollar_volume": _safe_float(row.get("avg_daily_dollar_volume")),
            "volume_days": int(row.get("volume_days") or 0),
        }
    return stats


def _volume_metric(*values: Any) -> float | None:
    for value in values:
        numeric = _safe_float(value)
        if numeric is not None and numeric > 0:
            return numeric
    return None


def _ranked_volume_frame(
    return_rows: list[dict[str, Any]],
    *,
    top_n: int,
    period: str,
    volume_stats: dict[str, dict[str, Any]] | None = None,
) -> pd.DataFrame:
    normalized_period = str(period or "daily").strip().lower()
    volume_stats = volume_stats or {}
    ranked_rows: list[dict[str, Any]] = []
    for row in return_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        volume = _safe_float(row.get("volume"))
        dollar_volume = _safe_float(row.get("dollar_volume"))
        if normalized_period == "daily":
            avg_daily_volume = volume
            total_volume = volume
            avg_daily_dollar_volume = dollar_volume
            total_dollar_volume = dollar_volume
            volume_days = 1 if volume is not None else 0
            volume_basis = "Daily dollar volume"
            metric = _volume_metric(dollar_volume, volume)
        else:
            stats = volume_stats.get(symbol) or {}
            avg_daily_volume = _safe_float(stats.get("avg_daily_volume"))
            total_volume = _safe_float(stats.get("total_volume"))
            avg_daily_dollar_volume = _safe_float(stats.get("avg_daily_dollar_volume"))
            total_dollar_volume = _safe_float(stats.get("total_dollar_volume"))
            volume_days = int(stats.get("volume_days") or 0)
            volume_basis = "Avg daily dollar volume"
            metric = _volume_metric(
                avg_daily_dollar_volume,
                total_dollar_volume,
                avg_daily_volume,
                total_volume,
            )
        if metric is None:
            continue
        ranked_rows.append(
            {
                "symbol": symbol,
                "name": row.get("name") or "-",
                "volume_metric": metric,
                "volume_basis": volume_basis,
                "volume": avg_daily_volume if normalized_period != "daily" else volume,
                "dollar_volume": avg_daily_dollar_volume if normalized_period != "daily" else dollar_volume,
                "avg_daily_volume": avg_daily_volume,
                "total_volume": total_volume,
                "avg_daily_dollar_volume": avg_daily_dollar_volume,
                "total_dollar_volume": total_dollar_volume,
                "volume_days": volume_days,
                "return_pct": row.get("return_pct"),
                "sector": row.get("sector") or "Unknown",
                "industry": row.get("industry") or "Unknown",
                "market_cap": row.get("market_cap"),
                "start_date": row.get("start_date"),
                "end_date": row.get("end_date"),
                "price_source": row.get("price_source") or "EOD DB",
            }
        )

    ranked = sorted(ranked_rows, key=lambda item: (-float(item["volume_metric"]), item["symbol"]))[:top_n]
    out = [
        {
            "Rank": index,
            "Symbol": row["symbol"],
            "Name": row["name"] or "-",
            "Volume Metric": round(float(row["volume_metric"]), 2),
            "Volume Basis": row["volume_basis"],
            "Volume": int(round(float(row["volume"]))) if row.get("volume") is not None else None,
            "Dollar Volume": round(float(row["dollar_volume"]), 2)
            if row.get("dollar_volume") is not None
            else None,
            "Avg Daily Volume": int(round(float(row["avg_daily_volume"])))
            if row.get("avg_daily_volume") is not None
            else None,
            "Total Volume": int(round(float(row["total_volume"]))) if row.get("total_volume") is not None else None,
            "Avg Daily Dollar Volume": round(float(row["avg_daily_dollar_volume"]), 2)
            if row.get("avg_daily_dollar_volume") is not None
            else None,
            "Total Dollar Volume": round(float(row["total_dollar_volume"]), 2)
            if row.get("total_dollar_volume") is not None
            else None,
            "Volume Days": int(row.get("volume_days") or 0),
            "Return %": round(float(row["return_pct"]), 2) if row.get("return_pct") is not None else None,
            "Sector": row["sector"],
            "Industry": row["industry"],
            "Market Cap": int(row["market_cap"]) if row.get("market_cap") else None,
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
            "Price Source": row["price_source"],
        }
        for index, row in enumerate(ranked, start=1)
    ]
    return _rows_frame(out, columns=VOLUME_COLUMNS)


def _latest_intraday_snapshot_time(
    *,
    universe_code: str,
    interval: str,
    query_fn: QueryFn,
) -> str | None:
    try:
        rows = query_fn(
            "finance_price",
            """
            SELECT MAX(snapshot_time_utc) AS snapshot_time_utc
            FROM market_intraday_snapshot
            WHERE universe_code = %s
              AND interval_code = %s
            """,
            [universe_code, interval],
        )
    except Exception:
        return None
    if not rows:
        return None
    return _display_datetime(rows[0].get("snapshot_time_utc"))


def _load_intraday_snapshot_rows(
    *,
    universe_code: str,
    interval: str,
    snapshot_time: str,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    try:
        return query_fn(
            "finance_price",
            """
            SELECT
                s.symbol,
                s.interval_code,
                s.snapshot_time_utc,
                s.quote_time_utc,
                s.previous_close,
                s.latest_price,
                s.return_pct,
                s.volume,
                s.provider_status,
                s.error_msg,
                s.source,
                s.source_ref
            FROM market_intraday_snapshot s
            WHERE s.universe_code = %s
              AND s.interval_code = %s
              AND s.snapshot_time_utc = %s
            """,
            [universe_code, interval, snapshot_time],
        )
    except Exception:
        return []


def _build_intraday_return_payload(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    period: str,
    interval: str,
    min_price_rows: int,
    today: date | None,
    query_fn: QueryFn,
) -> dict[str, Any] | None:
    snapshot_time = _latest_intraday_snapshot_time(universe_code=universe_code, interval=interval, query_fn=query_fn)
    if not snapshot_time:
        return None
    rows = _load_intraday_snapshot_rows(
        universe_code=universe_code,
        interval=interval,
        snapshot_time=snapshot_time,
        query_fn=query_fn,
    )
    if not rows:
        return None

    row_map = {str(row.get("symbol") or "").strip().upper(): row for row in rows}
    symbols = [str(item.get("symbol") or "").strip().upper() for item in universe if item.get("symbol")]
    effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
    previous_date_window = resolve_effective_market_dates(
        period="daily",
        min_price_rows=effective_min_rows,
        today=today,
        query_fn=query_fn,
    )
    previous_context = (
        _previous_return_context(
            symbols=symbols,
            date_window=previous_date_window,
            period="daily",
            query_fn=query_fn,
        )
        if previous_date_window.get("status") == "OK"
        else {}
    )
    return_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        row = row_map.get(symbol)
        if not row:
            missing_rows.append(
                _missing_row(
                    item=item,
                    reason="missing intraday snapshot row",
                    start_date="Previous Close",
                    end_date=snapshot_time,
                    start_price=None,
                    end_price=None,
                    latest_price_date=None,
                )
            )
            continue
        previous_close = _safe_float(row.get("previous_close"))
        latest_price = _safe_float(row.get("latest_price"))
        return_pct = _safe_float(row.get("return_pct"))
        volume = _safe_float(row.get("volume"))
        quote_time = _display_datetime(row.get("quote_time_utc")) or snapshot_time
        if row.get("provider_status") != "ok" or previous_close is None or latest_price is None or return_pct is None:
            missing_rows.append(
                _missing_row(
                    item=item,
                    reason=row.get("error_msg") or "missing intraday return",
                    start_date="Previous Close",
                    end_date=quote_time,
                    start_price=previous_close,
                    end_price=latest_price,
                    latest_price_date=_iso_date(row.get("quote_time_utc")),
                )
            )
            continue
        previous = previous_context.get(symbol) or {}
        previous_return = _safe_float(previous.get("previous_return_pct"))
        return_rows.append(
            {
                "symbol": symbol,
                "name": item.get("long_name") or "",
                "sector": item.get("sector") or "Unknown",
                "industry": item.get("industry") or "Unknown",
                "market_cap": _safe_float(item.get("market_cap")) or 0.0,
                "start_price": previous_close,
                "end_price": latest_price,
                "return_pct": return_pct,
                "previous_return_pct": previous_return,
                "momentum_delta_pp": (return_pct - previous_return) if previous_return is not None else None,
                "volume": int(volume) if volume is not None else None,
                "dollar_volume": (float(latest_price) * float(volume)) if volume is not None else None,
                "start_date": "Previous Close",
                "end_date": quote_time,
                "previous_start_date": previous.get("previous_start_date"),
                "previous_end_date": previous.get("previous_end_date"),
                "price_source": "Yahoo Quote" if row.get("source") == "yahoo_quote" else f"Intraday {interval}",
            }
        )

    date_window = {
        "status": "OK",
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "start_date": "Previous Close",
        "end_date": snapshot_time,
        "latest_raw_date": None,
        "effective_end_date": snapshot_time,
        "stale_days": None,
        "message": "",
    }
    coverage = _coverage(
        universe_count=len(universe),
        returnable_count=len(return_rows),
        date_window=date_window,
        price_mode="Intraday Snapshot",
        extra={
            **_universe_metadata(universe, universe_code=universe_code),
            "snapshot_time_utc": snapshot_time,
            "snapshot_stale_minutes": _stale_minutes(snapshot_time),
            "intraday_interval": interval,
        },
    )
    coverage["refresh_state"] = _intraday_refresh_state(
        snapshot_status="OK",
        period=period,
        coverage=coverage,
    )
    return {
        "snapshot_time": snapshot_time,
        "return_rows": return_rows,
        "missing_rows": missing_rows,
        "date_window": date_window,
        "coverage": coverage,
    }


def _build_intraday_movers_snapshot(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    sector: str | None,
    min_price_rows: int,
    today: date | None,
    interval: str,
    query_fn: QueryFn,
) -> dict[str, Any] | None:
    payload = _build_intraday_return_payload(
        universe=universe,
        universe_code=universe_code,
        period=period,
        interval=interval,
        min_price_rows=min_price_rows,
        today=today,
        query_fn=query_fn,
    )
    if payload is None:
        return None
    return_rows = list(payload["return_rows"])
    missing_rows = list(payload["missing_rows"])
    date_window = dict(payload["date_window"])
    coverage = dict(payload["coverage"])
    return {
        "status": "OK",
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "sector": sector or "All",
        "top_n": top_n,
        "rows": _ranked_movers_frame(return_rows, top_n=top_n),
        "volume_rows": _ranked_volume_frame(return_rows, top_n=top_n, period=period),
        "missing_rows": _rows_frame(missing_rows, columns=MISSING_COLUMNS),
        "date_window": date_window,
        "coverage": coverage,
        "warnings": _coverage_warnings(coverage, date_window=date_window),
    }


def build_market_movers_snapshot(
    *,
    universe_limit: int = 1000,
    universe_code: str | None = None,
    period: str = "daily",
    top_n: int = 20,
    sector: str | None = None,
    min_price_rows: int = 1000,
    today: date | None = None,
    prefer_intraday: bool = True,
    intraday_interval: str = "5m",
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    normalized_period = str(period or "daily").strip().lower()
    normalized_top_n = _normalize_limit(top_n, default=20, min_value=5, max_value=100)
    normalized_universe = _normalize_universe_code(universe_code, universe_limit)
    normalized_limit = _universe_limit_from_code(
        normalized_universe,
        _normalize_limit(universe_limit, default=1000, min_value=100, max_value=3000),
    )
    query = query_fn or _default_query

    if normalized_period not in VALID_PERIODS:
        raise ValueError(f"Unsupported period: {period!r}")

    try:
        universe = _load_universe(
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            sector=sector,
            query_fn=query,
        )
        if not universe:
            return _empty_movers_snapshot(
                status="NO_UNIVERSE",
                period=normalized_period,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                top_n=normalized_top_n,
                sector=sector,
                message="Selected universe has no symbols. For S&P 500, run the universe refresh first.",
            )

        if normalized_period == "daily" and prefer_intraday:
            intraday_snapshot = _build_intraday_movers_snapshot(
                universe=universe,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                period=normalized_period,
                top_n=normalized_top_n,
                sector=sector,
                min_price_rows=min_price_rows,
                today=today,
                interval=intraday_interval,
                query_fn=query,
            )
            if intraday_snapshot is not None:
                return intraday_snapshot

        effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
        date_window = resolve_effective_market_dates(
            period=normalized_period,
            min_price_rows=effective_min_rows,
            today=today,
            query_fn=query,
        )
        if date_window.get("status") != "OK":
            snapshot = _empty_movers_snapshot(
                status="INSUFFICIENT_DATA",
                period=normalized_period,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                top_n=normalized_top_n,
                sector=sector,
                message=str(date_window.get("message") or ""),
            )
            snapshot["date_window"] = date_window
            snapshot["coverage"].update(
                {
                    "universe_count": len(universe),
                    "latest_raw_date": date_window.get("latest_raw_date"),
                    "effective_end_date": date_window.get("effective_end_date"),
                    "stale_days": date_window.get("stale_days"),
                    **_universe_metadata(universe, universe_code=normalized_universe),
                }
            )
            return snapshot

        previous_context = _previous_return_context(
            symbols=[str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")],
            date_window=date_window,
            period=normalized_period,
            query_fn=query,
        )
        return_rows, missing_rows = _build_return_rows(
            universe=universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
            previous_context=previous_context,
        )
        volume_stats: dict[str, dict[str, Any]] = {}
        if normalized_period != "daily":
            volume_dates = _current_period_volume_dates(date_window, period=normalized_period)
            volume_stats = _load_period_volume_stats(
                symbols=[str(row.get("symbol") or "").strip().upper() for row in return_rows],
                dates=volume_dates,
                query_fn=query,
            )
        coverage = _coverage(
            universe_count=len(universe),
            returnable_count=len(return_rows),
            date_window=date_window,
            price_mode="EOD DB",
            extra=_universe_metadata(universe, universe_code=normalized_universe),
        )
        if normalized_period == "daily" and prefer_intraday:
            coverage["refresh_state"] = _intraday_refresh_state(
                snapshot_status="OK",
                period=normalized_period,
                coverage=coverage,
            )
        warnings = _coverage_warnings(coverage, date_window=date_window)
        if normalized_period == "daily" and prefer_intraday:
            warnings.insert(0, "No intraday snapshot found for the selected universe; using daily DB close data.")
        return {
            "status": "OK",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "universe_code": normalized_universe,
            "universe_label": UNIVERSE_LABELS.get(normalized_universe, normalized_universe),
            "universe_limit": normalized_limit,
            "sector": sector or "All",
            "top_n": normalized_top_n,
            "rows": _ranked_movers_frame(return_rows, top_n=normalized_top_n),
            "volume_rows": _ranked_volume_frame(
                return_rows,
                top_n=normalized_top_n,
                period=normalized_period,
                volume_stats=volume_stats,
            ),
            "missing_rows": _rows_frame(missing_rows, columns=MISSING_COLUMNS),
            "date_window": date_window,
            "coverage": coverage,
            "warnings": warnings,
        }
    except Exception as exc:
        return _empty_movers_snapshot(
            status="ERROR",
            period=normalized_period,
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            top_n=normalized_top_n,
            sector=sector,
            message=f"Market movers snapshot failed: {exc}",
        )


def _build_intraday_group_leadership_snapshot(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    universe_limit: int,
    group_by: str,
    period: str,
    top_n: int,
    min_group_size: int,
    min_price_rows: int,
    today: date | None,
    interval: str,
    trend_groups: Sequence[str] | None,
    query_fn: QueryFn,
) -> dict[str, Any] | None:
    payload = _build_intraday_return_payload(
        universe=universe,
        universe_code=universe_code,
        period=period,
        interval=interval,
        min_price_rows=min_price_rows,
        today=today,
        query_fn=query_fn,
    )
    if payload is None:
        return None

    date_window = dict(payload["date_window"])
    return_rows = list(payload["return_rows"])
    missing_rows = list(payload["missing_rows"])
    group_rows = _group_leadership_rows(
        return_rows=return_rows,
        group_by=group_by,
        min_group_size=min_group_size,
        start_date=str(date_window["start_date"]),
        end_date=str(date_window["end_date"]),
    )
    ranked = _rank_group_rows(group_rows, top_n=top_n)
    top_groups = {str(row["group"]) for row in ranked}
    requested_trend_groups = {str(group).strip() for group in (trend_groups or []) if str(group).strip()}
    trend_group_set = top_groups | requested_trend_groups
    positive_groups = {
        str(row["group"])
        for row in ranked
        if float(row.get("market_cap_weighted_return") or 0.0) > 0
    }

    trend_rows = pd.DataFrame(columns=GROUP_TREND_COLUMNS)
    trend_warnings: list[str] = []
    effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
    trend_date_window = resolve_group_trend_market_dates(
        period=period,
        min_price_rows=effective_min_rows,
        today=today,
        query_fn=query_fn,
    )
    if trend_date_window.get("status") == "OK":
        trend_rows = _group_trend_rows_frame(
            windows=list(trend_date_window.get("windows") or []),
            universe=universe,
            groups=trend_group_set,
            group_by=group_by,
            min_group_size=min_group_size,
            query_fn=query_fn,
        )
    else:
        trend_warnings.append(
            str(trend_date_window.get("message") or "Historical daily trend windows are unavailable.")
        )

    current_trend_rows = _group_trend_rows_from_group_rows(
        group_rows=group_rows,
        groups=trend_group_set,
        date_value=str(date_window["end_date"]),
    )
    if not current_trend_rows.empty:
        trend_rows = pd.concat([trend_rows, current_trend_rows], ignore_index=True)

    ticker_leader_rows = _group_ticker_leader_rows_frame(
        return_rows=return_rows,
        positive_groups=positive_groups,
        group_by=group_by,
    )
    coverage = dict(payload["coverage"])
    warnings = _coverage_warnings(coverage, date_window=date_window)
    warnings.extend(trend_warnings)
    return {
        "status": "OK",
        "group_by": group_by,
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "trend_window_label": GROUP_TREND_PERIODS[period]["window_label"],
        "top_n": top_n,
        "rows": _group_rows_frame(ranked),
        "trend_rows": trend_rows,
        "ticker_leader_rows": ticker_leader_rows,
        "missing_rows": pd.DataFrame(missing_rows, columns=MISSING_COLUMNS),
        "date_window": date_window,
        "coverage": coverage,
        "warnings": warnings,
    }


def build_group_leadership_snapshot(
    *,
    universe_limit: int = 2000,
    universe_code: str | None = None,
    group_by: str = "sector",
    period: str = "monthly",
    top_n: int = 10,
    min_group_size: int = 5,
    min_price_rows: int = 1000,
    today: date | None = None,
    prefer_intraday: bool = True,
    intraday_interval: str = "5m",
    trend_groups: Sequence[str] | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    normalized_group = str(group_by or "sector").strip().lower()
    if normalized_group not in VALID_GROUPS:
        raise ValueError(f"Unsupported group_by: {group_by!r}")
    normalized_period = str(period or "monthly").strip().lower()
    if normalized_period not in GROUP_TREND_PERIODS:
        raise ValueError(f"Unsupported group leadership period: {period!r}")

    normalized_universe = _normalize_universe_code(universe_code, universe_limit)
    normalized_limit = _universe_limit_from_code(
        normalized_universe,
        _normalize_limit(universe_limit, default=2000, min_value=100, max_value=3000),
    )
    normalized_top_n = _normalize_limit(top_n, default=10, min_value=5, max_value=100)
    query = query_fn or _default_query

    try:
        universe = _load_universe(
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            query_fn=query,
        )
        if normalized_period == "daily" and prefer_intraday:
            intraday_snapshot = _build_intraday_group_leadership_snapshot(
                universe=universe,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                group_by=normalized_group,
                period=normalized_period,
                top_n=normalized_top_n,
                min_group_size=min_group_size,
                min_price_rows=min_price_rows,
                today=today,
                interval=intraday_interval,
                trend_groups=trend_groups,
                query_fn=query,
            )
            if intraday_snapshot is not None:
                return intraday_snapshot

        effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
        date_window = resolve_group_trend_market_dates(
            period=normalized_period,
            min_price_rows=effective_min_rows,
            today=today,
            query_fn=query,
        )
        if date_window.get("status") != "OK":
            snapshot = _empty_group_snapshot(
                status="INSUFFICIENT_DATA",
                group_by=normalized_group,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                period=normalized_period,
                top_n=normalized_top_n,
                message=str(date_window.get("message") or ""),
            )
            snapshot["date_window"] = date_window
            snapshot["coverage"].update(
                {
                    "universe_count": len(universe),
                    "latest_raw_date": date_window.get("latest_raw_date"),
                    "effective_end_date": date_window.get("effective_end_date"),
                    "stale_days": date_window.get("stale_days"),
                    **_universe_metadata(universe, universe_code=normalized_universe),
                }
            )
            return snapshot

        previous_context = _previous_return_context(
            symbols=[str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")],
            date_window=date_window,
            period=normalized_period,
            query_fn=query,
        )
        return_rows, missing_rows = _build_return_rows(
            universe=universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
            previous_context=previous_context,
        )

        group_rows = _group_leadership_rows(
            return_rows=return_rows,
            group_by=normalized_group,
            min_group_size=min_group_size,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
        )
        ranked = _rank_group_rows(group_rows, top_n=normalized_top_n)
        top_groups = {str(row["group"]) for row in ranked}
        requested_trend_groups = {str(group).strip() for group in (trend_groups or []) if str(group).strip()}
        trend_group_set = top_groups | requested_trend_groups
        positive_groups = {
            str(row["group"])
            for row in ranked
            if float(row.get("market_cap_weighted_return") or 0.0) > 0
        }
        trend_rows = _group_trend_rows_frame(
            windows=list(date_window.get("windows") or []),
            universe=universe,
            groups=trend_group_set,
            group_by=normalized_group,
            min_group_size=min_group_size,
            query_fn=query,
        )
        ticker_leader_rows = _group_ticker_leader_rows_frame(
            return_rows=return_rows,
            positive_groups=positive_groups,
            group_by=normalized_group,
        )
        coverage = _coverage(
            universe_count=len(universe),
            returnable_count=len(return_rows),
            date_window=date_window,
            extra=_universe_metadata(universe, universe_code=normalized_universe),
        )
        if normalized_period == "daily" and prefer_intraday:
            coverage["refresh_state"] = _intraday_refresh_state(
                snapshot_status="OK",
                period=normalized_period,
                coverage=coverage,
            )
        warnings = _coverage_warnings(coverage, date_window=date_window)
        if normalized_period == "daily" and prefer_intraday:
            warnings.insert(0, "No intraday snapshot found for the selected universe; using daily DB close data.")
        return {
            "status": "OK",
            "group_by": normalized_group,
            "universe_code": normalized_universe,
            "universe_label": UNIVERSE_LABELS.get(normalized_universe, normalized_universe),
            "universe_limit": normalized_limit,
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "trend_window_label": GROUP_TREND_PERIODS[normalized_period]["window_label"],
            "top_n": normalized_top_n,
            "rows": _group_rows_frame(ranked),
            "trend_rows": trend_rows,
            "ticker_leader_rows": ticker_leader_rows,
            "missing_rows": pd.DataFrame(missing_rows, columns=MISSING_COLUMNS),
            "date_window": date_window,
            "coverage": coverage,
            "warnings": warnings,
        }
    except Exception as exc:
        return _empty_group_snapshot(
            status="ERROR",
            group_by=normalized_group,
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            period=normalized_period,
            top_n=normalized_top_n,
            message=f"Group leadership snapshot failed: {exc}",
        )
