from __future__ import annotations

import calendar
import importlib
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from html import escape
from typing import Any, Callable
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs import overview_actions as overview_actions_module
from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_browser_auto_refresh,
    run_overview_earnings_calendar,
    run_overview_fomc_calendar,
    run_overview_futures_daily_ohlcv,
    run_overview_futures_ohlcv,
    run_overview_historical_analog_ohlcv,
    run_overview_macro_calendar,
    run_overview_market_context_refresh_all,
    run_overview_market_context_refresh_smart,
    run_overview_market_intraday_snapshot,
    run_overview_market_sentiment,
    run_overview_quote_gap_diagnostics,
    run_overview_sp500_universe,
)
from app.services.futures_macro_thermometer import (
    clear_overview_futures_macro_snapshot_cache,
    load_overview_futures_macro_snapshot,
)
from app.services.futures_macro_validation import build_current_scenario_validation_summary
from app.services.futures_market_monitoring import load_overview_futures_monitor_snapshot
from app.services.overview_market_intelligence import (
    build_market_mover_metadata_status_strip,
    build_market_mover_why_it_moved_read_model,
    fetch_market_mover_compact_metadata,
    sort_market_mover_sec_filings_by_form_priority,
)
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.overview_dashboard_helpers import (
    load_overview_breadth_heatmap_summary,
    load_overview_group_leadership_snapshot,
    load_overview_market_context_historical_analog,
    load_overview_macro_context_cockpit,
    load_overview_macro_week_lane,
    load_overview_market_events_snapshot,
    load_overview_market_mover_sectors,
    load_overview_market_movers_snapshot,
    load_overview_market_sentiment_snapshot,
)
from app.web.overview_ui_components import (
    OVERVIEW_COLOR_DANGER,
    OVERVIEW_COLOR_BORDER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_PRIMARY,
    OVERVIEW_COLOR_PURPLE,
    OVERVIEW_COLOR_SOFT,
    OVERVIEW_COLOR_SURFACE,
    OVERVIEW_COLOR_SURFACE_ALT,
    OVERVIEW_COLOR_SURFACE_SUBTLE,
    OVERVIEW_COLOR_TEXT,
    OVERVIEW_COLOR_TEXT_MUTED,
    OVERVIEW_COLOR_TEXT_SUBTLE,
    OVERVIEW_COLOR_TEXT_INVERSE,
    OVERVIEW_COLOR_WARNING,
    OVERVIEW_DIVERGING_RANGE,
    OVERVIEW_SECTOR_COLOR_MAP,
    OVERVIEW_SERIES_COLORS,
    render_auto_refresh_countdown,
    render_auto_refresh_timing_static,
    render_breadth_heatmap_summary,
    render_event_agenda_sections,
    render_event_source_lane,
    render_event_warning_strip,
    render_events_summary_strip,
    render_macro_context_cockpit,
    render_macro_week_lane,
    render_market_session_banner,
    render_market_auto_message,
    render_market_auto_waiting_panel,
    render_overview_toolbar_label,
    render_market_refresh_status_bar,
    render_market_snapshot_meta_strip,
    render_macro_context_reading_flow,
)


MARKET_INTRADAY_REFRESH_MINUTES = 5
BROWSER_AUTO_REFRESH_SECONDS = 300
FUTURES_DEFAULT_AUTO_REFRESH_SECONDS = 60
FUTURES_FAST_AUTO_REFRESH_SECONDS = 20
BROWSER_AUTO_REFRESH_JOB_CONFIG = {
    "SP500": {"profile": "browser_safe", "job_id": "sp500_intraday"},
    "TOP1000": {"profile": "intraday", "job_id": "top1000_intraday"},
    "TOP2000": {"profile": "intraday", "job_id": "top2000_intraday"},
}
MARKET_MOVER_TABLE_CHROME_HEIGHT = 44
MARKET_COVERAGE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
    "NASDAQ": "Nasdaq-listed current snapshot",
}
MARKET_COVERAGE_OPTIONS = tuple(MARKET_COVERAGE_LABELS.keys())
MARKET_UNIVERSE_LIMITS = {
    "SP500": 500,
    "TOP1000": 1000,
    "TOP2000": 2000,
    "NASDAQ": 5000,
}
MARKET_MOVER_PERIOD_LABELS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "yearly": "Yearly",
}
OVERVIEW_DEEP_TAB_KEY = "overview_active_deep_tab"
OVERVIEW_DEEP_TAB_WIDGET_KEY = "overview_active_deep_tab_widget"
OVERVIEW_DEEP_TAB_QUERY_PARAM = "overview_tab"
OVERVIEW_DEEP_TAB_OPTIONS = (
    "Market Context",
    "Market Movers",
    "Futures Macro",
    "Sentiment",
    "Events",
)
OVERVIEW_DEEP_TAB_DISPLAY = {
    "Market Context": ("시장 맥락", "Market Context"),
    "Market Movers": ("변동 종목", "Market Movers"),
    "Futures Macro": ("선물 매크로", "Futures Macro"),
    "Sentiment": ("심리", "Sentiment"),
    "Events": ("일정", "Events"),
}
OVERVIEW_DEEP_TAB_SLUGS = {
    "Market Context": "market-context",
    "Market Movers": "market-movers",
    "Futures Macro": "futures-macro",
    "Sentiment": "sentiment",
    "Events": "events",
}
GROUP_LEADERSHIP_PERIOD_LABELS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
}
GROUP_BY_LABELS = {
    "sector": "Sector",
    "industry": "Industry",
}
FUTURES_GROUP_OPTIONS = (
    "Pre-open Core",
    "Equity Index",
    "Rates",
    "Commodities",
    "FX Futures",
    "All",
)
FUTURES_GROUP_LABELS = {
    "Pre-open Core": "개장 전 핵심",
    "Equity Index": "주가지수",
    "Rates": "금리",
    "Commodities": "원자재",
    "FX Futures": "환율",
    "All": "전체 보기",
}
FUTURES_LOOKBACK_OPTIONS = {
    "2H": 120,
    "6H": 360,
    "12H": 720,
    "1D": 1440,
}
FUTURES_CHART_INTERVAL_OPTIONS = ("1m", "5m", "15m", "60m")
FUTURES_COMPACT_CHART_LIMIT = 6
FUTURES_CHART_SCOPE_OPTIONS = ("compact_6", "all_with_data")
FUTURES_STATE_LABELS = {
    "Calm": "안정",
    "Moving": "움직임",
    "Sharp": "급변",
    "Stale": "오래됨",
    "Missing": "자료 없음",
    "OK": "정상",
    "REVIEW": "확인 필요",
    "MISSING": "자료 없음",
}
FUTURES_RUN_STATUS_LABELS = {
    "success": "성공",
    "partial_success": "부분 성공",
    "failed": "실패",
}
MACRO_CONFIDENCE_LABELS = {
    "High Confidence": "근거 강도 높음",
    "Medium Confidence": "근거 강도 보통",
    "Low Confidence": "근거 강도 낮음",
    "Not Enough History": "근거 부족",
}
MACRO_CONFIDENCE_SHORT_LABELS = {
    "High Confidence": "높음",
    "Medium Confidence": "보통",
    "Low Confidence": "낮음",
    "Not Enough History": "부족",
}
MACRO_SCORE_LABELS = {
    "Risk-On Score": "위험선호",
    "Growth Score": "성장",
    "Rate Pressure Score": "금리",
    "Dollar Pressure Score": "달러",
    "Safe Haven Score": "안전자산",
    "Inflation Pressure Score": "물가",
}
MACRO_EVIDENCE_TEXT_LABELS = {
    "Risk-On": "위험선호",
    "Growth": "성장",
    "Rate Pressure": "금리 부담",
    "Dollar Pressure": "달러 압력",
    "Safe Haven": "안전자산",
    "Inflation": "물가 압력",
}
GROUP_TREND_HEATMAP_MIN_HEIGHT = 280
GROUP_TREND_HEATMAP_ROW_HEIGHT = 54
CHART_VALUE_LABEL_STYLE = {
    "color": OVERVIEW_COLOR_TEXT_INVERSE,
    "stroke": OVERVIEW_COLOR_TEXT,
    "strokeWidth": 1.15,
    "strokeOpacity": 0.75,
}
EVENT_TYPE_LABELS = {
    "ALL": "All",
    "FOMC_MEETING": "FOMC",
    "EARNINGS": "Earnings",
    "MACRO": "Macro",
}
MARKET_CONTEXT_REFRESH_RESULT_KEY = "overview_market_context_refresh_all_result"
MARKET_CONTEXT_ANALOG_REFRESH_RESULT_KEY = "overview_market_context_historical_analog_ohlcv_result"
MARKET_CONTEXT_REFRESH_REFLECTION_KEY = "overview_market_context_refresh_reflection"
MARKET_CONTEXT_ANALOG_AS_OF_OPTIONS = {
    "latest": "latest",
    "selected": "과거 기준일",
}
MARKET_CONTEXT_ANALOG_PATTERN_OPTIONS = {
    "5D": "5D",
    "20D": "20D",
    "MONTHLY": "monthly",
}
US_EASTERN_TZ = ZoneInfo("America/New_York")
KOREA_TZ = ZoneInfo("Asia/Seoul")
US_MARKET_OPEN_TIME = time(9, 30)
US_MARKET_CLOSE_TIME = time(16, 0)
US_MARKET_EARLY_CLOSE_TIME = time(13, 0)


@dataclass(frozen=True)
class MarketSessionInfo:
    session_date: date
    is_trading_day: bool
    phase: str
    reason: str
    open_at: datetime | None
    close_at: datetime | None
    next_open_at: datetime | None = None
    next_close_at: datetime | None = None
    early_close_reason: str | None = None


@dataclass(frozen=True)
class MarketMoverControls:
    coverage: str
    universe_limit: int
    period: str
    sector: str
    top_n: int


@dataclass(frozen=True)
class GroupLeadershipControls:
    coverage: str
    universe_limit: int
    group_by: str
    period: str
    top_n: int
    min_group_size: int


def _coverage_label(value: str) -> str:
    return MARKET_COVERAGE_LABELS.get(value, value)


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


def _universe_limit(value: str) -> int:
    return MARKET_UNIVERSE_LIMITS.get(value, 500)


def _market_mover_period_label(value: str) -> str:
    return MARKET_MOVER_PERIOD_LABELS.get(value, value.title())


def _group_leadership_period_label(value: str) -> str:
    return GROUP_LEADERSHIP_PERIOD_LABELS.get(value, value.title())


def _group_by_label(value: str) -> str:
    return GROUP_BY_LABELS.get(value, value.title())


def _futures_refresh_mode_label(value: str) -> str:
    return {
        "manual": "수동",
        "auto_60s": "60초 자동 확인",
        "fast_20s": "20초 빠른 확인",
    }.get(value, value)


def _futures_interval_label(value: str) -> str:
    return {
        "1m": "1분",
        "5m": "5분",
        "15m": "15분",
        "60m": "60분",
        "1h": "60분",
    }.get(value, value)


def _futures_group_label(value: str) -> str:
    return FUTURES_GROUP_LABELS.get(value, value)


def _futures_state_label(value: Any) -> str:
    return FUTURES_STATE_LABELS.get(str(value or ""), str(value or "-"))


def _futures_run_status_label(value: Any) -> str:
    return FUTURES_RUN_STATUS_LABELS.get(str(value or ""), str(value or "-"))


def _macro_confidence_label(value: Any) -> str:
    return MACRO_CONFIDENCE_LABELS.get(str(value or ""), str(value or "근거 부족"))


def _macro_confidence_short_label(value: Any) -> str:
    return MACRO_CONFIDENCE_SHORT_LABELS.get(str(value or ""), _macro_confidence_label(value))


def _macro_evidence_summary_label(value: Any) -> str:
    text = str(value or "")
    for source_label, display_label in MACRO_EVIDENCE_TEXT_LABELS.items():
        text = text.replace(source_label, display_label)
    return text


def _macro_validation_status_label(value: Any) -> str:
    normalized = str(value or "")
    if normalized == "OK":
        return "점검 가능"
    if normalized == "REVIEW":
        return "확인 필요"
    if normalized == "MISSING":
        return "자료 부족"
    if normalized == "ERROR":
        return "점검 실패"
    return normalized or "-"


def _macro_confidence_reason_label(value: Any) -> str:
    text = str(value or "")
    if text.startswith("Latest daily futures candle is ") and text.endswith(" days old."):
        age = text.removeprefix("Latest daily futures candle is ").removesuffix(" days old.")
        return f"최근 선물 일봉 기준이 {age}일 전이라 오늘 해석은 신선도를 확인해야 합니다."
    if text.startswith("Latest daily candle is ") and text.endswith(" days old."):
        age = text.removeprefix("Latest daily candle is ").removesuffix(" days old.")
        return f"최근 일봉 기준이 {age}일 전이라 오늘 해석은 신선도를 확인해야 합니다."
    if "futures symbols have no daily rows" in text:
        return text.replace("futures symbols have no daily rows", "개 선물의 일봉 데이터가 없습니다").replace(":", ":")
    if "symbols have less than 6 months of daily data" in text:
        return "일부 선물의 일봉 이력이 6개월 미만이라 표준화 움직임이 불안정할 수 있습니다."
    translations = {
        "Most core symbols have 60D standardized moves.": "대부분의 핵심 선물이 60D 표준화 이동을 계산할 수 있습니다.",
        "Most, but not all, core symbols have 60D standardized moves.": "대부분의 핵심 선물이 60D 표준화 이동을 계산할 수 있습니다.",
        "Daily standardized coverage is partial.": "일봉 표준화 계산 가능 범위가 일부에 그칩니다.",
        "Current interpretation has multiple strong standardized components.": "현재 해석에 힘을 보태는 강한 표준화 움직임이 여러 개 있습니다.",
        "Weak components outnumber strong components.": "강한 근거보다 약한 구성요소가 더 많습니다.",
        "Latest daily candle is recent.": "최근 일봉 데이터가 비교적 최신입니다.",
        "Historical validation has no usable point-in-time records.": "과거 점검에 쓸 PIT 기록이 부족합니다.",
        "Current scenario has a useful directional historical sample.": "현재 시나리오와 비슷한 과거 방향성 표본이 충분합니다.",
        "Current scenario has a moderate directional historical sample.": "현재 시나리오와 비슷한 과거 방향성 표본이 보통 수준입니다.",
        "Current scenario has a small directional historical sample.": "현재 시나리오와 비슷한 과거 방향성 표본이 작습니다.",
        "Current mixed scenario has historical occurrences, but no directional hit-rate rule.": "혼재 시나리오는 과거 발생 횟수만 보고, 방향성 적중률로 억지 평가하지 않습니다.",
        "Current scenario directional historical sample is too small.": "현재 시나리오의 방향성 과거 표본이 너무 작습니다.",
        "Current scenario 5D hit rate is above a basic consistency threshold.": "현재 시나리오의 5D 과거 일관성이 기본 기준보다 높습니다.",
        "Current scenario 5D hit rate is below a basic consistency threshold.": "현재 시나리오의 5D 과거 일관성이 기본 기준보다 낮습니다.",
        "Current scenario is not forced into a directional hit-rate rule.": "현재 시나리오는 방향성 적중률 규칙에 억지로 넣지 않습니다.",
        "60D volatility or daily history is not sufficient for current symbols.": "현재 선물들의 60D 변동성 또는 일봉 이력이 부족합니다.",
        "Historical validation could not run.": "과거 점검을 실행하지 못했습니다.",
    }
    return translations.get(text, text or "근거 점검 대기")


def _futures_warning_label(value: Any) -> str:
    text = str(value or "")
    if "futures symbols are stale; refresh before relying on pre-open context." in text:
        count = text.split(" futures symbols are stale", 1)[0].strip()
        return f"{count}개 선물 candle이 오래됐습니다. 개장 전 맥락에 사용하기 전 1분봉 갱신을 확인하세요."
    if text.startswith("Latest daily futures candle is ") and text.endswith(" days old."):
        age = text.removeprefix("Latest daily futures candle is ").removesuffix(" days old.")
        return f"최근 선물 일봉 기준이 {age}일 전입니다. 최신 해석이 필요한 경우 일봉 매크로 갱신을 확인하세요."
    if text.startswith("Stored futures daily OHLCV rows are not available yet."):
        return "저장된 선물 일봉 OHLCV가 아직 없습니다. 일봉 매크로 갱신을 먼저 확인하세요."
    if "futures symbols have no daily rows" in text:
        return text.replace("futures symbols have no daily rows", "개 선물의 일봉 데이터가 없습니다")
    if "symbols have less than 6 months of daily data" in text:
        return "일부 선물의 일봉 이력이 6개월 미만입니다. 표준화 움직임은 보수적으로 해석하세요."
    if text == "Some symbols could not compute 60D volatility standardized moves.":
        return "일부 선물은 60D 변동성 표준화 움직임을 계산하지 못했습니다."
    return text


def _macro_caution_label(value: Any) -> str:
    text = str(value or "")
    translations = {
        "Historical validation is an ex-post consistency check, not a prediction guarantee.": "과거 점검은 사후 일관성 확인이며 예측 보장이 아닙니다.",
        "Futures targets use stored yfinance continuous futures rows when available.": "선물 대상은 저장된 yfinance 연속 선물 row가 있으면 그것을 사용합니다.",
        "ETF proxy targets are labeled separately and do not prove futures contract performance.": "ETF proxy 대상은 별도로 표시되며 선물 계약 성과를 증명하지 않습니다.",
        "yfinance continuous futures can differ from exchange roll and maturity behavior.": "yfinance 연속 선물은 거래소 roll / 만기 구조와 다를 수 있습니다.",
        "Historical validation sample is small; confidence should be downgraded.": "과거 점검 표본이 작아 근거 강도는 낮춰 읽어야 합니다.",
        "Some target validation may use ETF proxy rows when futures targets are unavailable.": "일부 과거 점검은 선물 대상이 없을 때 ETF proxy row를 사용할 수 있습니다.",
        "Historical validation은 과거 일관성 평가이며 예측 보장이 아닙니다.": "과거 점검은 과거 일관성 평가이며 예측 보장이 아닙니다.",
        "yfinance continuous futures는 실제 roll / 만기 구조와 다를 수 있습니다.": "yfinance 연속 선물은 실제 roll / 만기 구조와 다를 수 있습니다.",
    }
    if text.startswith("Historical validation has less than ") and text.endswith(" years of stored daily futures history."):
        years = text.removeprefix("Historical validation has less than ").removesuffix(" years of stored daily futures history.")
        return f"저장된 일봉 선물 이력이 {years}년 미만이라 과거 점검 표본을 보수적으로 읽어야 합니다."
    if text.startswith("Historical validation could not run:"):
        return f"과거 점검을 실행하지 못했습니다: {text.split(':', 1)[1].strip()}"
    return translations.get(text, text)


def _event_filter_label(value: str) -> str:
    return EVENT_TYPE_LABELS.get(value, value.replace("_", " ").title())


def _nth_weekday(year: int, month: int, weekday: int, occurrence: int) -> date:
    current = date(year, month, 1)
    days_until_weekday = (weekday - current.weekday()) % 7
    return current + timedelta(days=days_until_weekday + 7 * (occurrence - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    if month == 12:
        current = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        current = date(year, month + 1, 1) - timedelta(days=1)
    return current - timedelta(days=(current.weekday() - weekday) % 7)


def _observed_fixed_holiday(year: int, month: int, day: int) -> date:
    holiday = date(year, month, day)
    if holiday.weekday() == 5:
        return holiday - timedelta(days=1)
    if holiday.weekday() == 6:
        return holiday + timedelta(days=1)
    return holiday


def _easter_date(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _nyse_holidays(year: int) -> dict[date, str]:
    holidays: dict[date, str] = {
        _nth_weekday(year, 1, 0, 3): "Martin Luther King Jr. Day",
        _nth_weekday(year, 2, 0, 3): "Washington's Birthday",
        _easter_date(year) - timedelta(days=2): "Good Friday",
        _last_weekday(year, 5, 0): "Memorial Day",
        _nth_weekday(year, 9, 0, 1): "Labor Day",
        _nth_weekday(year, 11, 3, 4): "Thanksgiving Day",
    }
    for holiday_year, label, month, day in [
        (year, "New Year's Day", 1, 1),
        (year + 1, "New Year's Day", 1, 1),
        (year, "Juneteenth National Independence Day", 6, 19),
        (year, "Independence Day", 7, 4),
        (year, "Christmas Day", 12, 25),
    ]:
        observed = _observed_fixed_holiday(holiday_year, month, day)
        if observed.year == year:
            suffix = " (observed)" if observed != date(holiday_year, month, day) else ""
            holidays[observed] = f"{label}{suffix}"
    return holidays


def _nyse_early_closes(year: int) -> dict[date, str]:
    holidays = _nyse_holidays(year)
    thanksgiving = _nth_weekday(year, 11, 3, 4)
    candidates = {
        thanksgiving + timedelta(days=1): "Day after Thanksgiving",
        date(year, 7, 3): "Independence Day early close",
        date(year, 12, 24): "Christmas Eve",
    }
    return {
        value: reason
        for value, reason in candidates.items()
        if value.weekday() < 5 and value not in holidays
    }


def _market_datetime(session_date: date, session_time: time) -> datetime:
    return datetime.combine(session_date, session_time, tzinfo=US_EASTERN_TZ)


def _market_session_for_date(session_date: date) -> MarketSessionInfo:
    if session_date.weekday() >= 5:
        return MarketSessionInfo(
            session_date=session_date,
            is_trading_day=False,
            phase="휴장",
            reason="주말",
            open_at=None,
            close_at=None,
        )
    holidays = _nyse_holidays(session_date.year)
    if session_date in holidays:
        return MarketSessionInfo(
            session_date=session_date,
            is_trading_day=False,
            phase="휴장",
            reason=holidays[session_date],
            open_at=None,
            close_at=None,
        )
    early_close_reason = _nyse_early_closes(session_date.year).get(session_date)
    close_time = US_MARKET_EARLY_CLOSE_TIME if early_close_reason else US_MARKET_CLOSE_TIME
    return MarketSessionInfo(
        session_date=session_date,
        is_trading_day=True,
        phase="거래일",
        reason="조기 종료" if early_close_reason else "정규장",
        open_at=_market_datetime(session_date, US_MARKET_OPEN_TIME),
        close_at=_market_datetime(session_date, close_time),
        early_close_reason=early_close_reason,
    )


def _next_market_session(start_date: date) -> MarketSessionInfo:
    for offset in range(1, 15):
        candidate = _market_session_for_date(start_date + timedelta(days=offset))
        if candidate.is_trading_day:
            return candidate
    return _market_session_for_date(start_date)


def _previous_market_session(start_date: date) -> MarketSessionInfo:
    for offset in range(1, 15):
        candidate = _market_session_for_date(start_date - timedelta(days=offset))
        if candidate.is_trading_day:
            return candidate
    return _market_session_for_date(start_date)


def _current_market_session_info(now: datetime | None = None) -> MarketSessionInfo:
    now_et = (now or datetime.now(tz=US_EASTERN_TZ)).astimezone(US_EASTERN_TZ)
    session = _market_session_for_date(now_et.date())
    if not session.is_trading_day:
        next_session = _next_market_session(session.session_date)
        return MarketSessionInfo(
            session_date=session.session_date,
            is_trading_day=False,
            phase="휴장",
            reason=session.reason,
            open_at=None,
            close_at=None,
            next_open_at=next_session.open_at,
            next_close_at=next_session.close_at,
        )
    if session.open_at and now_et < session.open_at:
        phase = "장 시작 전"
    elif session.close_at and now_et <= session.close_at:
        phase = "장중"
    else:
        phase = "장 종료"
    return MarketSessionInfo(
        session_date=session.session_date,
        is_trading_day=True,
        phase=phase,
        reason=session.reason,
        open_at=session.open_at,
        close_at=session.close_at,
        early_close_reason=session.early_close_reason,
    )


def _format_et_time(value: datetime | None) -> str:
    return value.strftime("%H:%M ET") if value else "-"


def _format_kst_time(value: datetime | None) -> str:
    return value.astimezone(KOREA_TZ).strftime("%m-%d %H:%M KST") if value else "-"


def _format_session_time_item(label: str, value: datetime | None) -> dict[str, str]:
    return {
        "label": label,
        "value": _format_kst_time(value),
        "detail": _format_et_time(value),
    }


def _market_session_banner_model(now: datetime | None = None) -> dict[str, Any]:
    session = _current_market_session_info(now)
    if session.is_trading_day:
        detail = session.reason
        if session.early_close_reason:
            detail = f"{detail}: {session.early_close_reason}"
        return {
            "tone": "positive" if session.phase == "장중" else "neutral",
            "status": session.phase,
            "title": f"미국장 세션 · {session.session_date.isoformat()} ET",
            "detail": detail,
            "items": [
                _format_session_time_item("Open", session.open_at),
                _format_session_time_item("Close", session.close_at),
                {"label": "Timezone", "value": "KST", "detail": "ET shown below"},
            ],
        }
    return {
        "tone": "warning",
        "status": "휴장",
        "title": f"미국장 휴장 · {session.session_date.isoformat()} ET",
        "detail": f"사유: {session.reason}",
        "items": [
            {"label": "Reason", "value": session.reason, "detail": "NYSE closed"},
            _format_session_time_item("Next Open", session.next_open_at),
            _format_session_time_item("Next Close", session.next_close_at),
        ],
    }


def _market_context_session_payload(now: datetime | None = None) -> dict[str, Any]:
    session = _current_market_session_info(now)
    basis_session = (
        session
        if session.is_trading_day and session.phase in {"장중", "장 종료"}
        else _previous_market_session(session.session_date)
    )
    return {
        "phase": session.phase,
        "is_trading_day": session.is_trading_day,
        "is_market_open_now": session.is_trading_day and session.phase == "장중",
        "session_date": session.session_date.isoformat(),
        "basis_date": basis_session.session_date.isoformat(),
        "reason": session.reason,
    }


def _option_index(options: list[str], current: Any, *, default: int = 0) -> int:
    try:
        return options.index(str(current))
    except ValueError:
        return default


# Return a compact display value for market-intelligence snapshot metadata.
def _snapshot_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def _price_basis_status_item(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    price_mode = str(coverage.get("price_mode") or "")
    latest_raw = coverage.get("latest_raw_date")
    effective_end = coverage.get("effective_end_date")
    snapshot_time = coverage.get("snapshot_time_utc")

    if snapshot_time or price_mode == "Intraday Snapshot":
        title = "Effective Quote Time"
        value = snapshot_time or effective_end
        detail = f"{price_mode or 'Intraday Snapshot'} · previous close basis"
    else:
        title = "Effective EOD Date"
        value = effective_end
        if latest_raw and effective_end and str(latest_raw) != str(effective_end):
            detail = f"latest raw {latest_raw} is sparse; using {effective_end}"
        elif latest_raw:
            detail = f"latest raw {latest_raw}"
        else:
            detail = price_mode or "EOD DB"

    return {
        "title": title,
        "value": _snapshot_value(value),
        "detail": detail,
        "tone": "positive" if value else "warning",
    }


def _snapshot_status_items(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    coverage = dict(snapshot.get("coverage") or {})
    refresh_state = dict(coverage.get("refresh_state") or {})
    stale_days = coverage.get("stale_days")
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is not None:
        age_value = f"{int(stale_minutes)}m"
        age_detail = "from intraday snapshot"
        age_tone = refresh_state.get("tone") or ("positive" if int(stale_minutes) <= 10 else "warning")
    else:
        age_value = _snapshot_value(stale_days)
        age_detail = "calendar days from effective date"
        age_tone = "positive" if stale_days is not None and int(stale_days) <= 3 else "warning"
    returnable = coverage.get("returnable_count") or 0
    universe_count = coverage.get("universe_count") or 0
    coverage_text = f"{returnable} / {universe_count}" if universe_count else "-"
    returnable_pct = coverage.get("returnable_pct")
    coverage_detail = f"{float(returnable_pct):.2f}% returnable" if returnable_pct is not None else None
    missing_count = coverage.get("missing_count") or 0
    failed_count = coverage.get("failed_count") or missing_count
    status_title = "Refresh State" if refresh_state else "Snapshot Status"
    status_value = refresh_state.get("label") or snapshot.get("status") or "-"
    status_detail = refresh_state.get("detail") or coverage.get("coverage_basis") or snapshot.get("universe_label") or "-"
    status_tone = refresh_state.get("tone") or ("positive" if snapshot.get("status") == "OK" else "warning")
    return [
        _price_basis_status_item(snapshot),
        {
            "title": "Returnable Coverage",
            "value": coverage_text,
            "detail": coverage_detail or f"missing: {missing_count}, failed: {failed_count}",
            "tone": "positive" if returnable else "warning",
        },
        {
            "title": "Snapshot Age",
            "value": age_value,
            "detail": age_detail,
            "tone": age_tone,
        },
        {
            "title": status_title,
            "value": status_value,
            "detail": status_detail,
            "tone": status_tone,
        },
    ]


def _render_snapshot_status_cards(snapshot: dict[str, Any]) -> None:
    render_status_card_grid(_snapshot_status_items(snapshot))


def _render_snapshot_warnings(snapshot: dict[str, Any]) -> None:
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))


def _symmetric_return_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_abs = max(1.0, float(numeric.abs().max()) if not numeric.empty else 1.0)
    return [-max_abs, 0, max_abs]


def _signed_return_axis_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_abs = max(1.0, float(numeric.abs().max()) if not numeric.empty else 1.0)
    return [-max_abs * 1.12, max_abs * 1.12]


def _symmetric_return_scale(values: pd.Series) -> alt.Scale:
    return alt.Scale(domain=_symmetric_return_domain(values), range=OVERVIEW_DIVERGING_RANGE)


def _positive_return_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_value = max(1.0, float(numeric.max()) if not numeric.empty else 1.0)
    return [0, max_value * 1.16]


def _market_mover_chart_height(row_count: int) -> int:
    if row_count <= 20:
        return 540
    if row_count <= 30:
        return 660
    if row_count <= 50:
        return 880
    if row_count <= 75:
        return 1120
    return 1360


def _compact_number(value: Any, *, prefix: str = "") -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    amount = float(numeric)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    for suffix, divisor in (("T", 1_000_000_000_000), ("B", 1_000_000_000), ("M", 1_000_000), ("K", 1_000)):
        if amount >= divisor:
            return f"{sign}{prefix}{amount / divisor:.1f}{suffix}"
    return f"{sign}{prefix}{amount:,.0f}"


def _sector_bar_color(sector: Any, return_pct: Any | None = None) -> str:
    numeric_return = pd.to_numeric(return_pct, errors="coerce") if return_pct is not None else None
    if numeric_return is not None and pd.notna(numeric_return) and float(numeric_return) < 0:
        return OVERVIEW_COLOR_DANGER
    return OVERVIEW_SECTOR_COLOR_MAP.get(str(sector or "Unknown"), OVERVIEW_SECTOR_COLOR_MAP["Unknown"])


def _build_return_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    if not chart_rows.empty and "Return %" in chart_rows:
        chart_rows["Return %"] = pd.to_numeric(chart_rows["Return %"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Return %"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Symbol": "No Data", "Return %": 0.0}])
    if "Rank" in chart_rows:
        chart_rows = chart_rows.sort_values("Rank")
    chart_rows["Return Magnitude %"] = chart_rows["Return %"].abs()
    chart_rows["Return Label"] = chart_rows["Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    if "Previous Return %" in chart_rows:
        chart_rows["Previous Return %"] = pd.to_numeric(chart_rows["Previous Return %"], errors="coerce")
    else:
        chart_rows["Previous Return %"] = pd.NA
    chart_rows["Previous Return Magnitude %"] = chart_rows["Previous Return %"].abs()
    chart_rows["Previous Return Label"] = chart_rows["Previous Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows["Previous Marker Color"] = chart_rows["Previous Return %"].map(
        lambda value: OVERVIEW_COLOR_DANGER
        if pd.notna(value) and float(value) < 0
        else OVERVIEW_COLOR_TEXT
        if pd.notna(value) and float(value) > 0
        else OVERVIEW_COLOR_TEXT_MUTED
    )
    if "Momentum Delta pp" in chart_rows:
        chart_rows["Momentum Delta pp"] = pd.to_numeric(chart_rows["Momentum Delta pp"], errors="coerce")
    else:
        chart_rows["Momentum Delta pp"] = pd.NA
    chart_rows["Momentum Label"] = chart_rows["Momentum Delta pp"].map(
        lambda value: f"{float(value):+.2f}pp" if pd.notna(value) else "-"
    )
    chart_rows["Bar Color"] = chart_rows.apply(
        lambda row: _sector_bar_color(row.get("Sector"), row.get("Return %")),
        axis=1,
    )
    symbol_order = chart_rows["Symbol"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Return Magnitude %:Q",
            title="Move Magnitude %",
            stack=None,
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Return Magnitude %"])),
        ),
        y=alt.Y("Symbol:N", sort=symbol_order, title=None, axis=alt.Axis(labelLimit=80)),
        tooltip=[
            "Rank:O",
            "Symbol:N",
            "Name:N",
            "Return Label:N",
            "Previous Return Label:N",
            "Momentum Label:N",
            "Sector:N",
            "Industry:N",
        ],
    )
    bars = (
        base
        .mark_bar(cornerRadiusEnd=3)
        .encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    )
    previous_marker_halo = (
        base
        .transform_filter("isValid(datum['Previous Return Magnitude %'])")
        .mark_tick(thickness=5, size=20, color=OVERVIEW_COLOR_SURFACE)
        .encode(x=alt.X("Previous Return Magnitude %:Q"))
    )
    previous_markers = (
        base
        .transform_filter("isValid(datum['Previous Return Magnitude %'])")
        .mark_tick(thickness=2, size=18)
        .encode(
            x=alt.X("Previous Return Magnitude %:Q"),
            color=alt.Color("Previous Marker Color:N", scale=None, legend=None),
        )
    )
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT)
        .encode(
            text=alt.Text("Return Label:N"),
        )
    )
    return (bars + previous_marker_halo + previous_markers + labels).properties(
        height=_market_mover_chart_height(len(chart_rows))
    )


def _build_volume_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    metric_column = next(
        (
            candidate
            for candidate in ("Volume Metric", "Dollar Volume", "Avg Daily Dollar Volume", "Volume")
            if candidate in chart_rows
        ),
        "Volume",
    )
    if not chart_rows.empty and metric_column in chart_rows:
        chart_rows[metric_column] = pd.to_numeric(chart_rows[metric_column], errors="coerce")
        chart_rows = chart_rows.dropna(subset=[metric_column])
    elif not chart_rows.empty:
        chart_rows = pd.DataFrame()
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [
                {
                    "Symbol": "No Data",
                    "Name": "-",
                    "Volume Metric": 0.0,
                    "Volume Basis": "Volume",
                    "Volume": 0.0,
                    "Dollar Volume": 0.0,
                    "Avg Daily Volume": 0.0,
                    "Total Volume": 0.0,
                    "Avg Daily Dollar Volume": 0.0,
                    "Total Dollar Volume": 0.0,
                    "Volume Days": 0,
                    "Return %": None,
                    "Sector": "Unknown",
                    "Industry": "-",
                }
            ]
        )
        metric_column = "Volume Metric"
    if "Rank" in chart_rows:
        chart_rows = chart_rows.sort_values("Rank").reset_index(drop=True)
        chart_rows["Volume Rank"] = chart_rows["Rank"]
    else:
        chart_rows = chart_rows.sort_values([metric_column, "Symbol"], ascending=[False, True]).reset_index(drop=True)
        chart_rows["Volume Rank"] = chart_rows.index + 1
    if metric_column != "Volume Metric":
        chart_rows["Volume Metric"] = chart_rows[metric_column]
    if "Volume Basis" not in chart_rows:
        chart_rows["Volume Basis"] = "Dollar volume" if "Dollar" in metric_column else "Volume"
    chart_rows["Volume Metric"] = pd.to_numeric(chart_rows["Volume Metric"], errors="coerce").fillna(0.0)
    chart_rows["Volume Metric Label"] = chart_rows.apply(
        lambda row: _compact_number(
            row.get("Volume Metric"),
            prefix="$" if "dollar" in str(row.get("Volume Basis") or metric_column).lower() else "",
        ),
        axis=1,
    )
    if "Volume" not in chart_rows:
        chart_rows["Volume"] = pd.NA
    chart_rows["Volume"] = pd.to_numeric(chart_rows["Volume"], errors="coerce")
    chart_rows["Volume Label"] = chart_rows["Volume"].map(_compact_number)
    if "Dollar Volume" in chart_rows:
        chart_rows["Dollar Volume"] = pd.to_numeric(chart_rows["Dollar Volume"], errors="coerce")
    else:
        chart_rows["Dollar Volume"] = pd.NA
    chart_rows["Dollar Volume Label"] = chart_rows["Dollar Volume"].map(lambda value: _compact_number(value, prefix="$"))
    for source_column, label_column, prefix in [
        ("Avg Daily Volume", "Avg Daily Volume Label", ""),
        ("Total Volume", "Total Volume Label", ""),
        ("Avg Daily Dollar Volume", "Avg Daily Dollar Volume Label", "$"),
        ("Total Dollar Volume", "Total Dollar Volume Label", "$"),
    ]:
        if source_column not in chart_rows:
            chart_rows[source_column] = pd.NA
        chart_rows[source_column] = pd.to_numeric(chart_rows[source_column], errors="coerce")
        chart_rows[label_column] = chart_rows[source_column].map(lambda value, p=prefix: _compact_number(value, prefix=p))
    if "Volume Days" not in chart_rows:
        chart_rows["Volume Days"] = pd.NA
    if "Return %" in chart_rows:
        chart_rows["Return %"] = pd.to_numeric(chart_rows["Return %"], errors="coerce")
    else:
        chart_rows["Return %"] = pd.NA
    chart_rows["Return Label"] = chart_rows["Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows["Bar Color"] = chart_rows["Sector"].map(lambda value: _sector_bar_color(value))
    symbol_order = chart_rows["Symbol"].drop_duplicates().tolist()
    max_volume = max(1.0, float(chart_rows["Volume Metric"].max()) if not chart_rows.empty else 1.0)
    basis_values = [str(value) for value in chart_rows["Volume Basis"].dropna().unique().tolist() if str(value)]
    axis_title = basis_values[0] if len(basis_values) == 1 else "Volume Metric"
    base = alt.Chart(chart_rows).encode(
        x=alt.X("Volume Metric:Q", title=axis_title, scale=alt.Scale(domain=[0, max_volume * 1.12])),
        y=alt.Y("Symbol:N", sort=symbol_order, title=None, axis=alt.Axis(labelLimit=80)),
        tooltip=[
            "Volume Rank:O",
            "Symbol:N",
            "Name:N",
            "Volume Basis:N",
            "Volume Metric Label:N",
            "Volume Label:N",
            "Dollar Volume Label:N",
            "Avg Daily Volume Label:N",
            "Total Volume Label:N",
            "Avg Daily Dollar Volume Label:N",
            "Total Dollar Volume Label:N",
            "Volume Days:O",
            "Return Label:N",
            "Sector:N",
            "Industry:N",
        ],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT)
        .encode(text=alt.Text("Volume Metric Label:N"))
    )
    return (bars + labels).properties(height=_market_mover_chart_height(len(chart_rows)))


def _build_market_mover_sector_chart(rows: pd.DataFrame) -> alt.Chart:
    source_row_count = len(rows)
    if rows.empty or "Sector" not in rows or "Return %" not in rows:
        chart_rows = pd.DataFrame([{"Sector": "No Data", "Average Return %": 0.0, "Count": 0, "Top Return %": 0.0}])
    else:
        chart_rows = (
            rows.assign(
                Sector=rows["Sector"].fillna("Unknown"),
                **{"Return %": pd.to_numeric(rows["Return %"], errors="coerce")},
            )
            .dropna(subset=["Return %"])
            .groupby("Sector", as_index=False)
            .agg(
                **{
                    "Average Return %": ("Return %", "mean"),
                    "Top Return %": ("Return %", "max"),
                    "Count": ("Symbol", "count"),
                }
            )
            .sort_values(["Average Return %", "Top Return %"], ascending=[False, False])
            .head(12)
        )
        if chart_rows.empty:
            chart_rows = pd.DataFrame([{"Sector": "No Data", "Average Return %": 0.0, "Count": 0, "Top Return %": 0.0}])
    chart_rows["Average Return Magnitude %"] = chart_rows["Average Return %"].abs()
    chart_rows["Average Return Label"] = chart_rows["Average Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows["Top Return Label"] = chart_rows["Top Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows["Bar Color"] = chart_rows.apply(
        lambda row: _sector_bar_color(row.get("Sector"), row.get("Average Return %")),
        axis=1,
    )
    sector_order = chart_rows["Sector"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Average Return Magnitude %:Q",
            title="Avg Move Magnitude %",
            stack=None,
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Average Return Magnitude %"])),
        ),
        y=alt.Y("Sector:N", sort=sector_order, title=None, axis=alt.Axis(labelLimit=150)),
        tooltip=["Sector:N", "Count:Q", "Average Return Label:N", "Top Return Label:N"],
    )
    bars = (
        base
        .mark_bar(cornerRadiusEnd=3)
        .encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    )
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT)
        .encode(
            text=alt.Text("Average Return Label:N"),
        )
    )
    return (bars + labels).properties(height=_market_mover_chart_height(source_row_count))


def _build_group_leadership_heatmap(rows: pd.DataFrame) -> alt.Chart:
    metric_columns = [
        "Equal Weight Return %",
        "Market Cap Weighted Return %",
        "Top Symbol Return %",
    ]
    if rows.empty:
        chart_rows = pd.DataFrame(
            [{"Group": "No Data", "Metric": "Equal Weight", "Return %": 0.0, "Symbols": 0, "Top Symbol": "-"}]
        )
    else:
        available_metrics = [column for column in metric_columns if column in rows.columns]
        chart_rows = rows.melt(
            id_vars=[column for column in ["Group", "Symbols", "Top Symbol"] if column in rows.columns],
            value_vars=available_metrics,
            var_name="Metric",
            value_name="Return %",
        )
        chart_rows["Metric"] = chart_rows["Metric"].replace(
            {
                "Equal Weight Return %": "Equal Weight",
                "Market Cap Weighted Return %": "Cap Weighted",
                "Top Symbol Return %": "Top Symbol",
            }
        )
        chart_rows["Return %"] = pd.to_numeric(chart_rows["Return %"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Return %"])
        if chart_rows.empty:
            chart_rows = pd.DataFrame(
                [{"Group": "No Data", "Metric": "Equal Weight", "Return %": 0.0, "Symbols": 0, "Top Symbol": "-"}]
            )
        chart_rows["Return Label"] = chart_rows["Return %"].map(
            lambda value: f"{float(value):.2f}%" if pd.notna(value) else "-"
        )
    group_order = chart_rows["Group"].drop_duplicates().tolist() if "Group" in chart_rows else ["No Data"]
    base = (
        alt.Chart(chart_rows)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X("Metric:N", title=None),
            y=alt.Y("Group:N", sort=group_order, title=None, axis=alt.Axis(labelLimit=190)),
            color=alt.Color(
                "Return %:Q",
                scale=_symmetric_return_scale(chart_rows["Return %"]),
                legend=alt.Legend(title="Return %", orient="bottom"),
            ),
            tooltip=["Group:N", "Metric:N", "Return Label:N", "Symbols:Q", "Top Symbol:N"],
        )
    )
    text = (
        alt.Chart(chart_rows)
        .mark_text(fontSize=11)
        .encode(
            x=alt.X("Metric:N", title=None),
            y=alt.Y("Group:N", sort=group_order, title=None),
            text=alt.Text("Return Label:N"),
            color=alt.condition(
                "datum['Return %'] >= 8 || datum['Return %'] <= -8",
                alt.value(OVERVIEW_COLOR_TEXT_INVERSE),
                alt.value(OVERVIEW_COLOR_TEXT),
            ),
        )
    )
    return (base + text).properties(height=max(240, min(620, 30 * len(group_order))))


def _build_group_leadership_rank_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    metric = "Market Cap Weighted Return %"
    if not chart_rows.empty and metric in chart_rows:
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=[metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [{"Rank": 1, "Group": "No Data", metric: 0.0, "Equal Weight Return %": 0.0, "Symbols": 0, "Top Symbol": "-"}]
        )
    chart_rows = chart_rows.sort_values("Rank") if "Rank" in chart_rows else chart_rows
    chart_rows["Return Magnitude %"] = chart_rows[metric].abs()
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    group_order = chart_rows["Group"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Return Magnitude %:Q",
            title="Cap Weighted Return %",
            stack=None,
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Return Magnitude %"])),
        ),
        y=alt.Y("Group:N", sort=group_order, title=None, axis=alt.Axis(labelLimit=220)),
        tooltip=[
            "Rank:O",
            "Group:N",
            "Symbols:Q",
            "Return Label:N",
            "Equal Weight Return %:Q",
            "Top Symbol:N",
            "Top Symbol Return %:Q",
        ],
    )
    bars = (
        base
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            color=alt.condition(
                f"datum['{metric}'] < 0",
                alt.value(OVERVIEW_COLOR_DANGER),
                alt.value(OVERVIEW_COLOR_POSITIVE),
            )
        )
    )
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT)
        .encode(text=alt.Text("Return Label:N"))
    )
    return (bars + labels).properties(height=max(320, min(680, 34 * len(chart_rows))))


def _build_group_leadership_trend_chart(rows: pd.DataFrame) -> alt.Chart:
    metric = "Market Cap Weighted Return %"
    chart_rows = rows.copy()
    if not chart_rows.empty and metric in chart_rows and "Date" in chart_rows:
        chart_rows["Date"] = pd.to_datetime(chart_rows["Date"], errors="coerce")
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Date", metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Date": pd.Timestamp.today().normalize(), "Group": "No Data", metric: 0.0}])
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    line = (
        alt.Chart(chart_rows)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y(f"{metric}:Q", title="Cap Weighted Return %"),
            color=alt.Color(
                "Group:N",
                scale=alt.Scale(range=OVERVIEW_SERIES_COLORS),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=["Date:T", "Group:N", "Return Label:N", "Symbols:Q", "Top Symbol:N"],
        )
    )
    return line.properties(height=420)


def _build_group_leadership_trend_heatmap(rows: pd.DataFrame) -> alt.Chart:
    metric = "Market Cap Weighted Return %"
    chart_rows = rows.copy()
    if not chart_rows.empty and metric in chart_rows and "Date" in chart_rows:
        chart_rows["Date"] = pd.to_datetime(chart_rows["Date"], errors="coerce")
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Date", metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [{"Date": pd.Timestamp.today().normalize(), "Group": "No Data", metric: 0.0, "Symbols": 0}]
        )
    chart_rows["Date Label"] = chart_rows["Date"].dt.strftime("%m-%d")
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    date_order = (
        chart_rows.sort_values("Date")["Date Label"].drop_duplicates().tolist()
        if "Date Label" in chart_rows
        else []
    )
    group_order = chart_rows["Group"].drop_duplicates().tolist() if "Group" in chart_rows else ["No Data"]
    chart_height = max(GROUP_TREND_HEATMAP_MIN_HEIGHT, GROUP_TREND_HEATMAP_ROW_HEIGHT * len(group_order))
    base = (
        alt.Chart(chart_rows)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X(
                "Date Label:N",
                sort=date_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=10),
            ),
            y=alt.Y(
                "Group:N",
                sort=group_order,
                title=None,
                axis=alt.Axis(labelLimit=240, labelFontSize=12),
            ),
            color=alt.Color(
                f"{metric}:Q",
                scale=_symmetric_return_scale(chart_rows[metric]),
                legend=alt.Legend(title="Return %", orient="bottom"),
            ),
            tooltip=["Date:T", "Group:N", "Return Label:N", "Symbols:Q", "Top Symbol:N"],
        )
    )
    text = (
        alt.Chart(chart_rows)
        .mark_text(fontSize=11)
        .encode(
            x=alt.X("Date Label:N", sort=date_order, title=None),
            y=alt.Y("Group:N", sort=group_order, title=None),
            text=alt.Text("Return Label:N"),
            color=alt.condition(
                f"datum['{metric}'] >= 8 || datum['{metric}'] <= -8",
                alt.value(OVERVIEW_COLOR_TEXT_INVERSE),
                alt.value(OVERVIEW_COLOR_TEXT),
            ),
        )
    )
    return (base + text).properties(height=chart_height)


def _latest_group_trend_delta_rows(rows: pd.DataFrame) -> pd.DataFrame:
    metric = "Market Cap Weighted Return %"
    if rows.empty or "Group" not in rows or "Date" not in rows or metric not in rows:
        return pd.DataFrame(
            columns=["Group", "Latest Date", "Previous Date", "Latest Return %", "Previous Return %", "Delta pp"]
        )
    source = rows.copy()
    source["Date"] = pd.to_datetime(source["Date"], errors="coerce")
    source[metric] = pd.to_numeric(source[metric], errors="coerce")
    source = source.dropna(subset=["Date", metric])
    out: list[dict[str, Any]] = []
    for group_name, group_rows in source.sort_values("Date").groupby("Group"):
        ordered = group_rows.sort_values("Date")
        latest = ordered.iloc[-1]
        previous = ordered.iloc[-2] if len(ordered) >= 2 else None
        latest_return = float(latest[metric])
        previous_return = float(previous[metric]) if previous is not None else None
        out.append(
            {
                "Group": str(group_name),
                "Latest Date": latest["Date"],
                "Previous Date": previous["Date"] if previous is not None else pd.NaT,
                "Latest Return %": latest_return,
                "Previous Return %": previous_return,
                "Delta pp": (latest_return - previous_return) if previous_return is not None else None,
                "Symbols": latest.get("Symbols"),
                "Top Symbol": latest.get("Top Symbol"),
            }
        )
    return pd.DataFrame(out)


def _build_group_leadership_delta_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = _latest_group_trend_delta_rows(rows)
    if not chart_rows.empty:
        chart_rows["Delta pp"] = pd.to_numeric(chart_rows["Delta pp"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Delta pp"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Group": "No Data", "Delta pp": 0.0, "Latest Return %": 0.0}])
    chart_rows["Delta Label"] = chart_rows["Delta pp"].map(lambda value: f"{float(value):+.2f}pp")
    chart_rows["Latest Return Label"] = chart_rows["Latest Return %"].map(lambda value: f"{float(value):+.2f}%")
    chart_rows["Previous Return Label"] = chart_rows["Previous Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows = chart_rows.sort_values(["Delta pp", "Group"], ascending=[False, True])
    group_order = chart_rows["Group"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Delta pp:Q",
            title="Latest vs Previous pp",
            scale=alt.Scale(domain=_signed_return_axis_domain(chart_rows["Delta pp"])),
        ),
        y=alt.Y("Group:N", sort=group_order, title=None, axis=alt.Axis(labelLimit=180)),
        tooltip=[
            "Group:N",
            "Delta Label:N",
            "Latest Return Label:N",
            "Previous Return Label:N",
            "Symbols:Q",
            "Top Symbol:N",
        ],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(
        color=alt.condition(
            "datum['Delta pp'] < 0",
            alt.value(OVERVIEW_COLOR_DANGER),
            alt.value(OVERVIEW_COLOR_PRIMARY),
        )
    )
    zero = alt.Chart(pd.DataFrame([{"x": 0}])).mark_rule(color=OVERVIEW_COLOR_TEXT_MUTED).encode(x="x:Q")
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, **CHART_VALUE_LABEL_STYLE)
        .encode(text=alt.Text("Delta Label:N"))
    )
    return (bars + zero + labels).properties(height=max(280, min(620, 34 * len(chart_rows))))


def _format_signed(value: Any, *, suffix: str = "%") -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):+.2f}{suffix}"


def _format_percent(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):.1f}%"


def _group_leadership_insight_cards(rows: pd.DataFrame, trend_rows: pd.DataFrame | None) -> list[dict[str, Any]]:
    if rows.empty:
        return []
    source = rows.copy()
    for column in [
        "Positive Symbol Share %",
        "Cap vs Equal Gap pp",
        "Top 3 Positive Share %",
        "Market Cap Weighted Return %",
    ]:
        if column in source:
            source[column] = pd.to_numeric(source[column], errors="coerce")

    cards: list[dict[str, Any]] = []
    if "Positive Symbol Share %" in source and not source["Positive Symbol Share %"].dropna().empty:
        row = source.sort_values(["Positive Symbol Share %", "Market Cap Weighted Return %"], ascending=False).iloc[0]
        cards.append(
            {
                "title": "Best Breadth",
                "value": f"{row.get('Group')} {_format_percent(row.get('Positive Symbol Share %'))}",
                "detail": f"{int(row.get('Positive Symbols') or 0)} / {int(row.get('Symbols') or 0)} positive",
                "tone": "positive" if float(row.get("Positive Symbol Share %") or 0.0) >= 60 else "neutral",
            }
        )

    if "Cap vs Equal Gap pp" in source and not source["Cap vs Equal Gap pp"].dropna().empty:
        skew_rows = source.assign(_abs_gap=source["Cap vs Equal Gap pp"].abs()).sort_values("_abs_gap", ascending=False)
        row = skew_rows.iloc[0]
        gap = float(row.get("Cap vs Equal Gap pp") or 0.0)
        cards.append(
            {
                "title": "Cap vs Equal",
                "value": f"{row.get('Group')} {_format_signed(gap, suffix='pp')}",
                "detail": "positive means large-cap leadership",
                "tone": "warning" if abs(gap) >= 2 else "neutral",
            }
        )

    if "Top 3 Positive Share %" in source and not source["Top 3 Positive Share %"].dropna().empty:
        row = source.sort_values("Top 3 Positive Share %", ascending=False).iloc[0]
        concentration = float(row.get("Top 3 Positive Share %") or 0.0)
        cards.append(
            {
                "title": "Concentration",
                "value": f"{row.get('Group')} {_format_percent(concentration)}",
                "detail": "top 3 positive-return share",
                "tone": "warning" if concentration >= 70 else "neutral",
            }
        )

    if isinstance(trend_rows, pd.DataFrame) and not trend_rows.empty:
        delta_rows = _latest_group_trend_delta_rows(trend_rows)
        if not delta_rows.empty and "Delta pp" in delta_rows:
            delta_rows["Delta pp"] = pd.to_numeric(delta_rows["Delta pp"], errors="coerce")
            delta_rows = delta_rows.dropna(subset=["Delta pp"])
            if not delta_rows.empty:
                row = delta_rows.sort_values("Delta pp", ascending=False).iloc[0]
                cards.append(
                    {
                        "title": "Improving",
                        "value": f"{row.get('Group')} {_format_signed(row.get('Delta pp'), suffix='pp')}",
                        "detail": "latest window vs previous",
                        "tone": "positive" if float(row.get("Delta pp") or 0.0) > 0 else "danger",
                    }
                )
    return cards


def _build_group_ticker_leader_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    metric = "Return %"
    chart_rows = rows.copy()
    if not chart_rows.empty and metric in chart_rows:
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=[metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [
                {
                    "Symbol": "No Data",
                    "Name": "-",
                    metric: 0.0,
                    "Positive Return Share %": 0.0,
                    "Sector": "-",
                    "Industry": "-",
                }
            ]
        )
    elif "Positive Return Share %" not in chart_rows:
        chart_rows["Positive Return Share %"] = None
    chart_rows = chart_rows.sort_values("Rank") if "Rank" in chart_rows else chart_rows
    chart_rows["Return Magnitude %"] = chart_rows[metric].abs()
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    if "Previous Return %" in chart_rows:
        chart_rows["Previous Return %"] = pd.to_numeric(chart_rows["Previous Return %"], errors="coerce")
    else:
        chart_rows["Previous Return %"] = pd.NA
    chart_rows["Previous Return Magnitude %"] = chart_rows["Previous Return %"].abs()
    chart_rows["Previous Return Label"] = chart_rows["Previous Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    if "Momentum Delta pp" in chart_rows:
        chart_rows["Momentum Delta pp"] = pd.to_numeric(chart_rows["Momentum Delta pp"], errors="coerce")
    else:
        chart_rows["Momentum Delta pp"] = pd.NA
    chart_rows["Momentum Label"] = chart_rows["Momentum Delta pp"].map(
        lambda value: f"{float(value):+.2f}pp" if pd.notna(value) else "-"
    )
    chart_rows["Previous Marker Color"] = chart_rows["Previous Return %"].map(
        lambda value: OVERVIEW_COLOR_DANGER
        if pd.notna(value) and float(value) < 0
        else OVERVIEW_COLOR_TEXT
        if pd.notna(value) and float(value) > 0
        else OVERVIEW_COLOR_TEXT_MUTED
    )
    chart_rows["Bar Color"] = chart_rows.apply(
        lambda row: _sector_bar_color(row.get("Sector"), row.get(metric)),
        axis=1,
    )
    chart_rows["Share Label"] = chart_rows["Positive Return Share %"].map(
        lambda value: f"{float(value):.2f}%" if pd.notna(value) else "-"
    )
    symbol_order = chart_rows["Symbol"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Return Magnitude %:Q",
            title="Ticker Return %",
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Return Magnitude %"])),
        ),
        y=alt.Y("Symbol:N", sort=symbol_order, title=None, axis=alt.Axis(labelLimit=120)),
        tooltip=[
            "Symbol:N",
            "Name:N",
            "Return Label:N",
            "Previous Return Label:N",
            "Momentum Label:N",
            "Share Label:N",
            "Sector:N",
            "Industry:N",
        ],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    previous_marker_halo = (
        base
        .transform_filter("isValid(datum['Previous Return Magnitude %'])")
        .mark_tick(thickness=5, size=20, color=OVERVIEW_COLOR_SURFACE)
        .encode(x=alt.X("Previous Return Magnitude %:Q"))
    )
    previous_markers = (
        base
        .transform_filter("isValid(datum['Previous Return Magnitude %'])")
        .mark_tick(thickness=2, size=18)
        .encode(
            x=alt.X("Previous Return Magnitude %:Q"),
            color=alt.Color("Previous Marker Color:N", scale=None, legend=None),
        )
    )
    labels = (
        base.mark_text(align="left", baseline="middle", dx=5, fontSize=11, **CHART_VALUE_LABEL_STYLE)
        .encode(text=alt.Text("Return Label:N"))
    )
    return (bars + previous_marker_halo + previous_markers + labels).properties(
        height=max(260, min(560, 34 * len(chart_rows)))
    )


def _build_group_ticker_contribution_donut(rows: pd.DataFrame, *, top_n: int) -> alt.Chart:
    source_rows = rows.copy()
    if "Positive Return Share %" not in source_rows:
        source_rows = pd.DataFrame()
    elif not source_rows.empty:
        source_rows["Positive Return Share %"] = pd.to_numeric(
            source_rows["Positive Return Share %"],
            errors="coerce",
        )
        source_rows = source_rows.dropna(subset=["Positive Return Share %"])
    if not source_rows.empty and "Return %" in source_rows:
        source_rows["Return %"] = pd.to_numeric(source_rows["Return %"], errors="coerce")
    source_rows = source_rows[source_rows["Positive Return Share %"] > 0] if not source_rows.empty else source_rows

    if source_rows.empty:
        chart_rows = pd.DataFrame([{"Label": "No Data", "Share %": 1.0, "Return Label": "-"}])
    else:
        visible = source_rows.sort_values("Rank").head(int(top_n))
        chart_values = [
            {
                "Label": str(row.get("Symbol") or "-"),
                "Share %": float(row.get("Positive Return Share %") or 0.0),
                "Return Label": f"{float(row.get('Return %') or 0.0):+.2f}%",
            }
            for _, row in visible.iterrows()
        ]
        visible_share = sum(float(item["Share %"]) for item in chart_values)
        remaining_share = max(0.0, 100.0 - visible_share)
        if remaining_share >= 0.05:
            chart_values.append({"Label": "Etc", "Share %": remaining_share, "Return Label": "-"})
        chart_rows = pd.DataFrame(chart_values)

    return (
        alt.Chart(chart_rows)
        .mark_arc(innerRadius=64, outerRadius=104, stroke=OVERVIEW_COLOR_TEXT_INVERSE)
        .encode(
            theta=alt.Theta("Share %:Q", stack=True),
            color=alt.Color(
                "Label:N",
                scale=alt.Scale(
                    range=OVERVIEW_SERIES_COLORS
                ),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=["Label:N", alt.Tooltip("Share %:Q", format=".2f"), "Return Label:N"],
        )
        .properties(height=300)
    )


def _resample_futures_candles(candles: pd.DataFrame, *, interval: str) -> pd.DataFrame:
    if not isinstance(candles, pd.DataFrame) or candles.empty or interval == "1m":
        return candles if isinstance(candles, pd.DataFrame) else pd.DataFrame()
    rule = {"5m": "5min", "15m": "15min", "60m": "60min", "1h": "60min"}.get(interval)
    if not rule or "Candle Time" not in candles:
        return candles
    frame = candles.copy()
    frame["Candle Time"] = pd.to_datetime(frame["Candle Time"], errors="coerce")
    frame = frame.dropna(subset=["Candle Time"]).sort_values("Candle Time")
    if frame.empty:
        return pd.DataFrame(columns=candles.columns)
    return (
        frame.set_index("Candle Time")
        .resample(rule)
        .agg(
            {
                "Symbol": "last",
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        .dropna(subset=["Open", "High", "Low", "Close"])
        .reset_index()
    )


def _build_futures_candlestick_chart(
    candles: pd.DataFrame,
    *,
    height: int = 360,
    body_size: int = 5,
    y_title: str | None = "Price",
) -> alt.LayerChart:
    chart_rows = candles.copy() if isinstance(candles, pd.DataFrame) else pd.DataFrame()
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [
                {
                    "Candle Time": pd.Timestamp(datetime.now()),
                    "Open": 0.0,
                    "High": 0.0,
                    "Low": 0.0,
                    "Close": 0.0,
                    "Volume": 0.0,
                }
            ]
        )
    chart_rows["Candle Time"] = pd.to_datetime(chart_rows["Candle Time"], errors="coerce")
    chart_rows = chart_rows.dropna(subset=["Candle Time"])
    chart_rows["Direction"] = [
        "Up" if float(close or 0.0) >= float(open_value or 0.0) else "Down"
        for open_value, close in zip(chart_rows["Open"], chart_rows["Close"], strict=False)
    ]
    color = alt.Color(
        "Direction:N",
        scale=alt.Scale(
            domain=["Up", "Down"],
            range=[OVERVIEW_COLOR_POSITIVE, OVERVIEW_COLOR_DANGER],
        ),
        legend=None,
    )
    base = alt.Chart(chart_rows).encode(x=alt.X("Candle Time:T", title=None))
    wick = base.mark_rule(size=1.2).encode(
        y=alt.Y("Low:Q", title=y_title, scale=alt.Scale(zero=False)),
        y2="High:Q",
        color=color,
        tooltip=[
            alt.Tooltip("Candle Time:T", title="Time"),
            alt.Tooltip("Open:Q", format=",.4f"),
            alt.Tooltip("High:Q", format=",.4f"),
            alt.Tooltip("Low:Q", format=",.4f"),
            alt.Tooltip("Close:Q", format=",.4f"),
            alt.Tooltip("Volume:Q", format=",.0f"),
        ],
    )
    body = base.mark_bar(size=body_size).encode(
        y=alt.Y("Open:Q", scale=alt.Scale(zero=False)),
        y2="Close:Q",
        color=color,
    )
    return (wick + body).properties(height=height)


def _render_quote_gap_diagnostics_result(result_key: str, *, universe_code: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    details = dict(result.get("details") or {})
    if details.get("universe_code") and str(details.get("universe_code")) != universe_code:
        return
    status = str(result.get("status") or "unknown")
    message = str(result.get("message") or "")
    if status in {"success", "partial_success"}:
        st.success(message or "Quote gap diagnosis completed.")
    elif status == "failed":
        st.error(message or "Quote gap diagnosis failed.")
    else:
        st.info(message or f"Quote gap diagnosis status: {status}")
    counts = dict(details.get("diagnosis_counts") or {})
    if counts:
        st.caption("Diagnosis counts: " + ", ".join(f"{key} ({value})" for key, value in counts.items()))
    rows = list(details.get("diagnostics") or [])
    if rows:
        display_columns = [
            column
            for column in [
                "Symbol",
                "Diagnosis",
                "Confidence",
                "Evidence Summary",
                "Recommended Action",
                "Quote Single Status",
                "Fast Info Status",
                "History Status",
                "DB Price Status",
                "Profile Status",
                "DB Latest Date",
            ]
            if column in rows[0]
        ]
        st.dataframe(pd.DataFrame(rows)[display_columns], width="stretch", hide_index=True)
    issue_history = list(details.get("issue_history") or [])
    if issue_history:
        st.caption(
            "Persistent issue history: "
            f"{details.get('issue_rows_written') or 0} row(s) updated in market_data_issue."
        )
        issue_frame = pd.DataFrame(issue_history)
        rename_map = {
            "universe_code": "Universe",
            "symbol": "Symbol",
            "diagnosis": "Latest Diagnosis",
            "latest_status": "Status",
            "occurrence_count": "Occurrences",
            "first_seen_at": "First Seen",
            "last_seen_at": "Last Seen",
            "last_snapshot_time_utc": "Last Snapshot",
            "latest_confidence": "Confidence",
            "latest_recommended_action": "Recommended Action",
        }
        issue_frame = issue_frame.rename(columns=rename_map)
        issue_columns = [column for column in rename_map.values() if column in issue_frame]
        st.dataframe(issue_frame[issue_columns], width="stretch", hide_index=True)


def _render_missing_diagnostics(snapshot: dict[str, Any], *, universe_code: str, period: str) -> None:
    missing_rows = snapshot.get("missing_rows")
    if not isinstance(missing_rows, pd.DataFrame) or missing_rows.empty:
        return
    with st.expander(f"Coverage Diagnostics ({len(missing_rows)} missing)", expanded=False):
        reason_counts = missing_rows["Reason"].value_counts().head(3) if "Reason" in missing_rows else pd.Series()
        if not reason_counts.empty:
            st.caption(
                "Top issues: "
                + ", ".join(f"{reason} ({count})" for reason, count in reason_counts.items())
            )
        st.dataframe(missing_rows, width="stretch", hide_index=True)
        coverage = dict(snapshot.get("coverage") or {})
        if period == "daily" and coverage.get("price_mode") == "Intraday Snapshot" and "Symbol" in missing_rows:
            symbols = (
                missing_rows["Symbol"]
                .dropna()
                .astype(str)
                .str.strip()
                .replace("", pd.NA)
                .dropna()
                .head(50)
                .tolist()
            )
            result_key = f"overview_{universe_code.lower()}_quote_gap_diagnostic_result"
            cols = st.columns([1, 2], gap="small", vertical_alignment="center")
            if cols[0].button(
                "Diagnose Missing Quotes",
                key=f"overview_{universe_code.lower()}_quote_gap_diagnose",
                use_container_width=True,
                disabled=not symbols,
                help="Runs a bounded diagnostic for missing daily quote rows using single-symbol Yahoo quote, yfinance fast_info/history, DB price, and asset profile evidence.",
            ):
                with st.spinner(f"Diagnosing {len(symbols)} missing quote row(s)..."):
                    _store_overview_job_result(
                        result_key,
                        run_overview_quote_gap_diagnostics(
                            symbols=symbols,
                            universe_code=universe_code,
                            interval_code=str(coverage.get("intraday_interval") or "5m"),
                            snapshot_time_utc=coverage.get("snapshot_time_utc"),
                            max_symbols=50,
                        ),
                    )
            cols[1].caption(
                "Evidence-based hint only: quote endpoint, 5D history, DB EOD price, profile, and fast_info when needed."
            )
            _render_quote_gap_diagnostics_result(result_key, universe_code=universe_code)


def _render_market_job_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = result.get("status")
    message = result.get("message") or ""
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    details = result.get("details") or {}
    if details:
        source = details.get("source") or "-"
        method = details.get("method") or details.get("method_requested") or "-"
        duration = result.get("duration_sec")
        if result.get("symbols_requested") is None and result.get("symbols_processed") is None:
            st.caption(
                "Rows: "
                f"{result.get('rows_written') or 0}, "
                f"Events: {details.get('events_found') or '-'}, "
                f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
            )
        else:
            st.caption(
                "Rows: "
                f"{result.get('rows_written') or 0}, "
                f"Processed: {result.get('symbols_processed') or 0} / {result.get('symbols_requested') or 0}, "
                f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
            )
            if details.get("universe_code") and details.get("snapshot_time_utc"):
                with st.expander("Snapshot Diagnostics", expanded=False):
                    metric_cols = st.columns(4)
                    metric_cols[0].metric("Snapshot Time", _snapshot_value(details.get("snapshot_time_utc")))
                    metric_cols[1].metric("Rows Written", result.get("rows_written") or 0)
                    metric_cols[2].metric("Failed", len(result.get("failed_symbols") or []))
                    metric_cols[3].metric("Method", method)
                    diagnostics = details.get("diagnostics") or {}
                    if diagnostics:
                        diag_rows = [
                            {"Key": key, "Value": str(value)}
                            for key, value in diagnostics.items()
                            if value not in (None, "", [], {})
                        ]
                        if diag_rows:
                            st.dataframe(pd.DataFrame(diag_rows), width="stretch", hide_index=True)
    failed_symbols = result.get("failed_symbols") or []
    if failed_symbols:
        with st.expander(f"Failed / Missing Symbols ({len(failed_symbols)})", expanded=False):
            st.write(", ".join(str(symbol) for symbol in failed_symbols[:100]))
    diagnostics = [item for item in details.get("symbol_diagnostics") or [] if isinstance(item, dict)]
    if diagnostics:
        issue_rows = [
            {
                "Symbol": item.get("symbol") or "-",
                "Status": item.get("status") or "-",
                "Reason": item.get("reason") or "-",
                "Detail": item.get("detail") or "-",
                "Provider Dates": ", ".join(str(value) for value in item.get("provider_dates") or []),
                "Event Dates": ", ".join(str(value) for value in item.get("event_dates") or []),
            }
            for item in diagnostics
            if item.get("status") != "event_found"
        ]
        with st.expander(f"Earnings Diagnostics ({len(issue_rows)} issue symbols)", expanded=False):
            metric_cols = st.columns(4)
            metric_cols[0].metric("With Events", details.get("symbols_with_events") or 0)
            metric_cols[1].metric("Missing", details.get("symbols_missing_count") or len(details.get("missing_symbols") or []))
            metric_cols[2].metric("Failed", details.get("symbols_failed_count") or len(details.get("failed_symbols") or []))
            metric_cols[3].metric("Events Found", details.get("events_found") or 0)
            reason_rows = [
                {"Status": "missing", "Reason": key, "Count": value}
                for key, value in (details.get("missing_reason_counts") or {}).items()
            ] + [
                {"Status": "failed", "Reason": key, "Count": value}
                for key, value in (details.get("failed_reason_counts") or {}).items()
            ]
            if reason_rows:
                st.caption("Issue reason counts")
                st.dataframe(pd.DataFrame(reason_rows), width="stretch", hide_index=True)
            if issue_rows:
                st.caption("Symbol-level issues")
                st.dataframe(pd.DataFrame(issue_rows), width="stretch", hide_index=True)
            else:
                st.success("All requested symbols had at least one earnings date in the selected window.")


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _clear_overview_market_context_caches() -> None:
    for loader in (
        load_overview_group_leadership_snapshot,
        load_overview_market_context_historical_analog,
        load_overview_market_sentiment_snapshot,
        load_overview_macro_context_cockpit,
    ):
        clear = getattr(loader, "clear", None)
        if callable(clear):
            clear()
    clear_overview_futures_macro_snapshot_cache()


def _status_tone(status: Any) -> str:
    normalized = str(status or "").lower()
    if normalized in {"success", "dry_run"}:
        return "positive"
    if normalized in {"partial_success", "skipped", "locked"}:
        return "warning"
    if normalized in {"failed", "error"}:
        return "danger"
    return "neutral"


def _overview_market_context_refresh_reflection_state(
    result: dict[str, Any],
    *,
    reflected_at: datetime | None = None,
) -> dict[str, Any]:
    status = str(result.get("status") or "unknown").lower()
    reflected_at_text = (reflected_at or datetime.now()).strftime("%Y-%m-%d %H:%M")
    jobs_failed = int(result.get("jobs_failed") or 0)
    jobs_run = int(result.get("jobs_run") or 0)
    reflected = status in {"success", "partial_success"}

    if status == "success":
        label = "방금 갱신을 반영했습니다"
        detail = f"상단 브리프는 새 snapshot을 다시 읽었습니다 · {reflected_at_text}"
    elif status == "partial_success":
        label = "일부 자료만 반영했습니다"
        detail = (
            f"성공한 자료는 다시 읽었고, 오래된 항목은 자료 상태를 참고하세요 · "
            f"{reflected_at_text}"
        )
    elif status in {"failed", "error"}:
        label = "갱신 실패 - 기존 자료를 계속 표시합니다"
        detail = f"상단 브리프는 기존 자료 기준이며 새로 반영된 자료처럼 표시하지 않습니다 · {reflected_at_text}"
    elif status in {"skipped", "locked"}:
        label = "갱신이 실행되지 않았습니다"
        detail = f"기존 자료를 계속 표시합니다 · {reflected_at_text}"
    else:
        label = "갱신 상태 보기"
        detail = f"기존 자료를 기준으로 표시 중입니다 · {reflected_at_text}"

    if status == "partial_success" and jobs_failed:
        detail = f"{detail} · 실패 {jobs_failed}개"
    elif status == "success" and jobs_run:
        detail = f"{detail} · 완료 {jobs_run}개"

    return {
        "status": status,
        "tone": _status_tone(status),
        "label": label,
        "detail": detail,
        "reflected": reflected,
        "reflected_at": reflected_at_text,
    }


def _render_overview_market_context_refresh_reflection() -> None:
    payload = st.session_state.get(MARKET_CONTEXT_REFRESH_REFLECTION_KEY)
    if not isinstance(payload, dict):
        return
    tone = str(payload.get("tone") or "neutral")
    tone_color = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
    }.get(tone, OVERVIEW_COLOR_NEUTRAL)
    st.markdown(
        (
            f'<div class="ov-macro-cockpit-refresh-reflection" style="--ov-refresh-reflection-tone:{tone_color};">'
            f'<span class="ov-macro-cockpit-refresh-reflection-label">{escape(str(payload.get("label") or ""))}</span>'
            f'<span class="ov-macro-cockpit-refresh-reflection-detail">{escape(str(payload.get("detail") or ""))}</span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_overview_market_context_refresh_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = str(result.get("status") or "-")
    message = str(result.get("message") or "")
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    _render_overview_market_context_refresh_impact_summary(result)
    rows = []
    for item in result.get("results") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "작업": item.get("label") or item.get("job_name") or "-",
                "상태": item.get("status") or "-",
                "저장 rows": item.get("rows_written") or 0,
                "메시지": item.get("message") or "",
            }
        )
    if rows:
        with st.expander("갱신 상세", expanded=False):
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _render_overview_historical_analog_repair_action(cockpit_model: dict[str, Any]) -> None:
    historical_analog = dict(cockpit_model.get("historical_analog") or {})
    repair_action = dict(historical_analog.get("repair_action") or {})
    symbols = [str(symbol).strip().upper() for symbol in repair_action.get("symbols") or [] if str(symbol).strip()]
    if not symbols:
        return
    period = str(repair_action.get("period") or "10y")
    interval = str(repair_action.get("interval") or "1d")
    target_table = str(repair_action.get("target_table") or "finance_price.nyse_price_history")
    label = str(repair_action.get("label") or "부족 ETF 가격 이력 보강")
    symbol_text = ", ".join(symbols)
    stale_basis = bool(repair_action.get("stale_basis"))
    requested_as_of = str(repair_action.get("requested_as_of") or "").strip()
    effective_as_of = str(repair_action.get("effective_as_of") or "").strip()

    st.markdown("#### 과거 유사 맥락 자료 수집")
    if stale_basis:
        st.caption(
            f"`{symbol_text}` 가격 기준이 선택일보다 오래되어 과거 유사 맥락이 "
            f"{effective_as_of or '이전'} 기준으로 계산되고 있습니다. "
            f"아래 버튼을 누르면 기존 OHLCV 수집 경로로 `{target_table}`에 {period} {interval} 이력을 갱신합니다."
        )
    else:
        st.caption(
            f"`{symbol_text}` 가격 이력이 부족해 과거 유사 맥락 표를 계산하지 못하고 있습니다. "
            f"아래 버튼을 누르면 기존 OHLCV 수집 경로로 `{target_table}`에 {period} {interval} 이력을 저장합니다."
        )
    cols = st.columns([1.45, 0.82], gap="small", vertical_alignment="center")
    with cols[0]:
        if stale_basis:
            st.caption(
                f"이 작업은 요청 기준일 {requested_as_of or 'selected'}까지 맞추는 데 제한이 된 가격 자료만 대상으로 실행합니다."
            )
        else:
            st.caption("이 작업은 현재 리더십 섹터 proxy와 부족 비교 자산만 대상으로 실행합니다.")
    if cols[1].button(
        label,
        key="overview_market_context_historical_analog_ohlcv",
        width="stretch",
        type="secondary",
        help=f"{symbol_text} OHLCV를 기존 collect_ohlcv 경로로 수집합니다.",
    ):
        spinner_copy = "과거 유사 맥락 가격 기준을 최신화하는 중입니다..." if stale_basis else "과거 유사 맥락에 필요한 ETF 가격 이력을 보강하는 중입니다..."
        with st.spinner(spinner_copy):
            result = run_overview_historical_analog_ohlcv(
                symbols=symbols,
                period=period,
                interval=interval,
            )
            _store_overview_job_result(MARKET_CONTEXT_ANALOG_REFRESH_RESULT_KEY, result)
            st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = {
                "tone": _status_tone(result.get("status")),
                "label": "과거 유사 맥락 가격 기준을 다시 읽었습니다" if stale_basis else "과거 유사 맥락 자료 보강을 반영했습니다",
                "detail": f"{symbol_text} 가격 이력 수집 후 Market Context를 다시 읽었습니다.",
                "reflected": str(result.get("status") or "").lower() in {"success", "partial_success"},
                "reflected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            _clear_overview_market_context_caches()
        st.rerun()
    _render_overview_market_context_refresh_result(MARKET_CONTEXT_ANALOG_REFRESH_RESULT_KEY)


def _overview_market_context_refresh_expander_label(cockpit_model: dict[str, Any]) -> str:
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    summary = dict(refresh_plan.get("summary") or {})
    headline = str(summary.get("headline") or "").strip()
    if headline:
        return f"필요 자료 보강 · {headline}"
    checks = [
        dict(item or {})
        for item in list(cockpit_model.get("context_findings") or cockpit_model.get("next_checks") or [])
        if isinstance(item, dict)
    ]
    if not checks:
        return "필요 자료 보강"
    review_checks = [
        check
        for check in checks
        if str(check.get("status") or "").upper() not in {"OK", "SUCCESS", "ACTUAL"}
        or str(check.get("repair_hint") or "").strip()
    ]
    top = review_checks[0] if review_checks else checks[0]
    source = str(top.get("source_area") or top.get("label") or top.get("title") or "자료 상태").strip()
    return f"필요 자료 보강 · {source}"


def _render_overview_market_context_smart_refresh_plan(cockpit_model: dict[str, Any]) -> list[str]:
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    items = [dict(item or {}) for item in list(refresh_plan.get("items") or []) if isinstance(item, dict)]
    return [str(item.get("action_id")) for item in items if str(item.get("action_id") or "").strip()]


def _overview_market_context_refresh_plan_parts(
    cockpit_model: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    summary = dict(refresh_plan.get("summary") or {})
    items = [dict(item or {}) for item in list(refresh_plan.get("items") or []) if isinstance(item, dict)]
    excluded_items = [
        dict(item or {})
        for item in list(refresh_plan.get("excluded_items") or [])
        if isinstance(item, dict)
    ]
    return summary, items, excluded_items


def _overview_market_context_refresh_tone_color(has_actions: bool) -> str:
    return OVERVIEW_COLOR_WARNING if has_actions else OVERVIEW_COLOR_POSITIVE


def _overview_market_context_refresh_item_html(
    item: dict[str, Any],
    *,
    muted: bool = False,
) -> str:
    source = str(item.get("source_area") or item.get("label") or "-")
    resolution = str(item.get("resolution_label") or ("보강 제외" if muted else "보강 대상"))
    reason = str(item.get("reason") or "-")
    limitation = str(item.get("limitation") or "").strip()
    meta = f"{reason} · {limitation}" if limitation else reason
    return (
        '<div class="ov-refresh-status-row">'
        f'<div class="ov-refresh-status-source">{escape(source)}</div>'
        f'<div class="ov-refresh-status-copy">{escape(meta)}</div>'
        '<div class="ov-refresh-status-meta">'
        f'<span class="ov-refresh-status-pill">{escape(resolution)}</span>'
        "</div>"
        "</div>"
    )


def _render_overview_market_context_refresh_status_panel(
    cockpit_model: dict[str, Any],
    *,
    action_ids: list[str],
) -> None:
    summary, items, excluded_items = _overview_market_context_refresh_plan_parts(cockpit_model)
    has_actions = bool(action_ids)
    title = "현재 보강할 자료 이슈" if has_actions else "현재 보강할 자료 이슈 없음"
    badge = f"{len(action_ids)}개 실행 가능" if has_actions else "보강 없음"
    detail = str(
        summary.get("detail")
        or (
            "현재 화면에서 실제 갱신 가능한 자료만 기존 Overview action boundary로 실행합니다."
            if has_actions
            else "현재 브리프 자료는 저장 snapshot 기준으로 읽을 수 있으며, 참고 제한 항목은 보강 대상에서 제외합니다."
        )
    )
    active_action_ids = set(action_ids)
    active_items = [
        item
        for item in items
        if str(item.get("action_id") or "").strip() in active_action_ids
    ]
    if has_actions and not active_items:
        active_items = items
    rows_html = "".join(_overview_market_context_refresh_item_html(item) for item in active_items[:5])
    excluded_html = ""
    if excluded_items:
        excluded_rows = " ".join(
            f"{str(item.get('source_area') or item.get('label') or '-')}: {str(item.get('reason') or '-')}"
            for item in excluded_items[:3]
        )
        excluded_html = f'<div class="ov-refresh-status-muted">보강 제외 · {escape(excluded_rows)}</div>'
    no_action_note = ""
    if not has_actions:
        no_action_note = (
            '<div class="ov-refresh-status-muted">'
            "미국장 휴장 / 장외 시간에는 장중 snapshot 시간만으로 보강하지 않습니다. 필요하면 전체 보강을 수동으로 실행합니다."
            "</div>"
        )
    rows_block = f'<div class="ov-refresh-status-list">{rows_html}</div>' if rows_html else ""
    panel_html = (
        f'<div class="ov-refresh-status-panel" style="--ov-refresh-status-tone:{_overview_market_context_refresh_tone_color(has_actions)};">'
        '<div class="ov-refresh-status-head">'
        f'<div class="ov-refresh-status-title">{escape(title)}</div>'
        f'<div class="ov-refresh-status-badge">{escape(badge)}</div>'
        "</div>"
        f'<div class="ov-refresh-status-detail">{escape(detail)}</div>'
        f"{rows_block}"
        f"{excluded_html}"
        f"{no_action_note}"
        "</div>"
    )
    st.markdown(
        panel_html,
        unsafe_allow_html=True,
    )


def _overview_market_context_refresh_impact(label: str) -> str:
    if label == "S&P 500 Market Movers":
        return "움직임 / 확산 자료를 다시 읽습니다."
    if label == "Futures Monitor 1m OHLCV":
        return "Futures/Macro 보류 여부를 다시 판정합니다."
    if label == "Futures Macro Daily OHLCV":
        return "Macro thermometer daily proxy를 다시 읽습니다."
    if label == "Market Sentiment":
        return "Sentiment 배경 자료를 다시 읽습니다."
    if label == "FOMC Calendar":
        return "공식 FOMC 일정 배경을 다시 읽습니다."
    if label == "Macro Calendar":
        return "공식 macro 일정 배경을 다시 읽습니다."
    if label == "Earnings Calendar":
        return "실적 일정 rows를 갱신하지만 추정 일정은 직접 원인 근거로 쓰지 않습니다."
    return "관련 저장 자료를 다시 읽습니다."


def _render_overview_market_context_refresh_impact_summary(result: dict[str, Any]) -> None:
    rows = []
    for item in result.get("results") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("job_name") or "-")
        rows.append(
            {
                "자료": label,
                "상태": item.get("status") or "-",
                "브리프 반영": _overview_market_context_refresh_impact(label),
            }
        )
    if rows:
        st.markdown("#### 반영 결과")
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _render_overview_market_context_refresh_bar(cockpit_model: dict[str, Any]) -> None:
    result_key = MARKET_CONTEXT_REFRESH_RESULT_KEY
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    summary = dict(refresh_plan.get("summary") or {})
    with st.expander(_overview_market_context_refresh_expander_label(cockpit_model), expanded=False):
        st.markdown(
            '<div class="ov-macro-cockpit-refresh-assist">현재 화면은 저장된 DB snapshot을 읽고, 갱신은 기존 Overview action boundary로만 실행합니다.</div>',
            unsafe_allow_html=True,
        )
        action_ids = _render_overview_market_context_smart_refresh_plan(cockpit_model)
        _render_overview_market_context_refresh_status_panel(cockpit_model, action_ids=action_ids)
        if not action_ids:
            cols = st.columns([1.4, 0.82], gap="small", vertical_alignment="center")
            with cols[0]:
                st.caption(
                    "현재 실행할 이슈별 보강은 없습니다. 필요하면 전체 저장 snapshot 보강을 수동으로 실행합니다."
                )
            if cols[1].button(
                str(summary.get("full_refresh_label") or "전체 Market Context 자료 보강"),
                key="overview_market_context_refresh_all",
                use_container_width=True,
                type="secondary",
                help="S&P 500 movers, futures 1m/daily, sentiment, FOMC/earnings/macro calendar를 모두 갱신합니다.",
            ):
                current_year = datetime.now().year
                with st.spinner("Market Context 전체 자료를 갱신하는 중입니다..."):
                    result = run_overview_market_context_refresh_all(years=(current_year, current_year + 1))
                    _store_overview_job_result(result_key, result)
                    st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = (
                        _overview_market_context_refresh_reflection_state(result)
                    )
                    _clear_overview_market_context_caches()
                st.rerun()
        else:
            cols = st.columns([1.4, 0.72, 0.82], gap="small", vertical_alignment="center")
            with cols[0]:
                st.caption(
                    "자료 보강 후 Market Context cache를 비우고 같은 화면을 다시 읽습니다. raw job rows는 상세에만 표시합니다."
                )
            if cols[1].button(
                str(summary.get("primary_button_label") or "현재 이슈만 보강"),
                key="overview_market_context_refresh_smart",
                use_container_width=True,
                type="secondary",
                help="현재 Market Context에서 실제 보강 가능한 항목만 기존 Overview action boundary로 갱신합니다.",
            ):
                current_year = datetime.now().year
                with st.spinner("Market Context 자료를 갱신하는 중입니다..."):
                    result = run_overview_market_context_refresh_smart(
                        action_ids=action_ids,
                        years=(current_year, current_year + 1),
                    )
                    _store_overview_job_result(result_key, result)
                    st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = (
                        _overview_market_context_refresh_reflection_state(result)
                    )
                    _clear_overview_market_context_caches()
                st.rerun()
            if cols[2].button(
                str(summary.get("full_refresh_label") or "전체 Market Context 자료 보강"),
                key="overview_market_context_refresh_all",
                use_container_width=True,
                type="secondary",
                help="S&P 500 movers, futures 1m/daily, sentiment, FOMC/earnings/macro calendar를 모두 갱신합니다.",
            ):
                current_year = datetime.now().year
                with st.spinner("Market Context 전체 자료를 갱신하는 중입니다..."):
                    result = run_overview_market_context_refresh_all(years=(current_year, current_year + 1))
                    _store_overview_job_result(result_key, result)
                    st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = (
                        _overview_market_context_refresh_reflection_state(result)
                    )
                    _clear_overview_market_context_caches()
                st.rerun()
        _render_overview_market_context_refresh_result(result_key)


def _render_overview_historical_analog_controls() -> dict[str, str | None]:
    st.markdown("#### 과거 유사 맥락 기준 선택")
    st.caption(
        "아래 기준은 이어지는 과거 참고 통계에만 적용됩니다. "
        "상단 시장 브리프는 현재 세션 상태에 따라 장중 snapshot 또는 마지막 거래일 기준 자료를 사용합니다. "
        "비교 자산의 공통 daily 가격 범위가 짧으면 실제 계산 기준일이 선택일보다 이른 날짜로 낮아질 수 있습니다."
    )
    cols = st.columns([0.9, 1.0, 0.9], gap="small", vertical_alignment="bottom")
    basis = cols[0].selectbox(
        "기준 시점",
        options=list(MARKET_CONTEXT_ANALOG_AS_OF_OPTIONS.keys()),
        format_func=lambda value: MARKET_CONTEXT_ANALOG_AS_OF_OPTIONS.get(value, value),
        index=0,
        key="overview_market_context_analog_as_of_mode",
        help="latest는 저장된 DB 공통 가격의 최신 usable 기준일을 사용합니다.",
    )
    stored_date = st.session_state.get("overview_market_context_analog_as_of_date")
    default_date = stored_date if isinstance(stored_date, date) else date.today()
    selected_date = cols[1].date_input(
        "기준일",
        value=default_date,
        max_value=date.today(),
        disabled=basis == "latest",
        key="overview_market_context_analog_as_of_date",
        help="과거 기준일을 선택하면 해당 날짜 이하의 DB 가격 이력만 사용합니다. 비교 자산 가격이 더 오래되면 실제 계산 기준일이 낮아집니다.",
    )
    pattern_window = cols[2].selectbox(
        "패턴 기간",
        options=list(MARKET_CONTEXT_ANALOG_PATTERN_OPTIONS.keys()),
        format_func=lambda value: MARKET_CONTEXT_ANALOG_PATTERN_OPTIONS.get(value, value),
        index=0,
        key="overview_market_context_analog_pattern_window",
        help="리더십 sector와 sector ETF 상대강도 조건을 읽는 기간입니다.",
    )
    as_of_date = selected_date.isoformat() if basis == "selected" and isinstance(selected_date, date) else None
    return {
        "as_of_date": as_of_date,
        "pattern_window": str(pattern_window or "5D"),
    }


def _overview_historical_analog_control_state() -> dict[str, str | None]:
    basis = str(st.session_state.get("overview_market_context_analog_as_of_mode") or "latest")
    selected_date = st.session_state.get("overview_market_context_analog_as_of_date")
    pattern_window = str(st.session_state.get("overview_market_context_analog_pattern_window") or "5D")
    as_of_date = selected_date.isoformat() if basis == "selected" and isinstance(selected_date, date) else None
    return {
        "as_of_date": as_of_date,
        "pattern_window": pattern_window,
    }


def _render_overview_market_context_tab() -> None:
    st.markdown("### 시장 맥락")
    st.caption("저장된 시장 자료로 현재 세션의 움직임, 확산, 이벤트 배경을 빠르게 확인합니다.")
    _render_overview_market_context_refresh_reflection()
    market_session_context = _market_context_session_payload()
    cockpit_model = load_overview_macro_context_cockpit(
        market_session_context=market_session_context,
    )
    render_macro_context_cockpit(cockpit_model, include_reading_flow=False)
    _render_overview_market_context_refresh_bar(cockpit_model)


def _summarize_auto_refresh_plan(summary: dict[str, Any]) -> str:
    plan = summary.get("plan")
    if not isinstance(plan, list) or not plan:
        return "-"
    row = dict(plan[0] or {})
    label = _auto_refresh_job_label(row.get("label") or row.get("job_id") or "-")
    reason = _auto_refresh_reason_label(row.get("reason") or "-")
    return f"{label}: {reason}"


def _auto_refresh_job_label(value: Any) -> str:
    text = str(value or "-")
    mapping = {
        "S&P 500 Daily Snapshot": "S&P 500 일중 스냅샷",
        "Top1000 Daily Snapshot": "Top1000 일중 스냅샷",
        "Top2000 Daily Snapshot": "Top2000 일중 스냅샷",
        "sp500_intraday": "S&P 500 일중 스냅샷",
        "top1000_intraday": "Top1000 일중 스냅샷",
        "top2000_intraday": "Top2000 일중 스냅샷",
    }
    return mapping.get(text, text)


def _auto_refresh_reason_label(value: Any) -> str:
    reason = str(value or "-").strip().lower()
    mapping = {
        "cadence not due": "아직 5분 갱신 주기가 지나지 않았습니다.",
        "outside us market hours": "미국 정규장 시간이 아니라 수집하지 않았습니다.",
        "due": "수집 조건이 충족되었습니다.",
        "forced": "강제 실행으로 수집을 진행합니다.",
    }
    return mapping.get(reason, str(value or "-"))


def _auto_refresh_status_label(value: Any) -> str:
    status = str(value or "-").strip().lower()
    mapping = {
        "success": "완료",
        "partial_success": "부분 완료",
        "skipped": "건너뜀",
        "locked": "대기 중",
        "failed": "실패",
        "dry_run": "Dry run",
    }
    return mapping.get(status, str(value or "-"))


def _browser_auto_refresh_plan_row(summary: dict[str, Any] | None) -> dict[str, Any]:
    plan = (summary or {}).get("plan")
    if isinstance(plan, list) and plan:
        return dict(plan[0] or {})
    return {}


def _format_auto_refresh_remaining(seconds: int | None) -> str:
    if seconds is None:
        return "-"
    remaining = max(0, int(seconds))
    minutes, secs = divmod(remaining, 60)
    if minutes <= 0:
        return f"{secs}초"
    if secs == 0:
        return f"{minutes}분"
    return f"{minutes}분 {secs}초"


def _browser_auto_refresh_timing(summary: dict[str, Any] | None, *, now: datetime | None = None) -> dict[str, Any]:
    row = _browser_auto_refresh_plan_row(summary)
    reason = str(row.get("reason") or "").strip().lower()
    cadence_minutes = int(row.get("cadence_minutes") or MARKET_INTRADAY_REFRESH_MINUTES)
    cadence_seconds = max(1, cadence_minutes * 60)
    job_label = _auto_refresh_job_label(row.get("label") or row.get("job_id") or "선택한 일중 스냅샷")
    now_ts = pd.Timestamp(now or datetime.now())
    last_finished = pd.to_datetime(row.get("last_finished_at"), errors="coerce")
    next_due = pd.to_datetime(row.get("next_due_at"), errors="coerce")
    summary_status = str((summary or {}).get("status") or "").strip().lower()
    completed_current_check = summary_status in {"success", "partial_success"} and bool(row.get("should_run"))
    if completed_current_check:
        finished_at = pd.to_datetime((summary or {}).get("finished_at"), errors="coerce")
        if pd.notna(finished_at):
            last_finished = finished_at
            next_due = finished_at + pd.Timedelta(seconds=cadence_seconds)
            reason = "cadence not due"

    remaining_seconds: int | None = None
    progress_pct = 100
    if pd.notna(next_due):
        remaining_seconds = max(0, int((next_due - now_ts).total_seconds()))
        if pd.notna(last_finished):
            elapsed = max(0, int((now_ts - last_finished).total_seconds()))
            progress_pct = max(0, min(100, int(round((elapsed / cadence_seconds) * 100))))
        elif remaining_seconds:
            progress_pct = max(0, min(100, int(round(((cadence_seconds - remaining_seconds) / cadence_seconds) * 100))))

    if reason == "outside us market hours":
        title = "미국 정규장 대기"
        detail = f"장이 열리면 {cadence_minutes}분 주기 조건에 맞춰 {job_label}을 확인합니다."
        progress_pct = 0
    elif reason == "cadence not due":
        prefix = "방금 갱신됨. " if completed_current_check else ""
        title = f"{prefix}다음 갱신까지 {_format_auto_refresh_remaining(remaining_seconds)}"
        detail = f"{cadence_minutes}분 갱신 주기가 지나면 다음 확인에서 수집을 시도합니다."
    elif reason == "due":
        title = "갱신 조건 충족"
        detail = f"이번 확인에서 {job_label} 수집을 시도합니다."
        progress_pct = 100
    elif reason == "forced":
        title = "강제 실행"
        detail = "수동/강제 실행으로 갱신 조건을 건너뛰고 수집합니다."
        progress_pct = 100
    else:
        title = "자동 갱신 대기"
        detail = "토글을 켜면 5분마다 수집 조건을 확인합니다."
        progress_pct = 0

    return {
        "title": title,
        "detail": detail,
        "progress_pct": progress_pct,
        "remaining_seconds": remaining_seconds,
        "cadence_seconds": cadence_seconds,
        "next_due_at": next_due.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(next_due) else row.get("next_due_at") or "-",
        "reason": reason or "-",
    }


def _should_run_browser_auto_refresh_check(
    summary: dict[str, Any] | None,
    *,
    checked_at: str | None = None,
    now: datetime | None = None,
) -> bool:
    if not summary:
        return True
    now_ts = pd.Timestamp(now or datetime.now())
    timing = _browser_auto_refresh_timing(summary, now=now)
    next_due = pd.to_datetime(timing.get("next_due_at"), errors="coerce")
    if pd.notna(next_due):
        return bool(now_ts >= next_due)
    checked_ts = pd.to_datetime(checked_at or summary.get("finished_at") or summary.get("started_at"), errors="coerce")
    if pd.notna(checked_ts):
        return bool((now_ts - checked_ts).total_seconds() >= BROWSER_AUTO_REFRESH_SECONDS)
    return False


def _browser_auto_refresh_completion_label(summary: dict[str, Any]) -> str:
    status = str(summary.get("status") or "-")
    row = _browser_auto_refresh_plan_row(summary)
    job_label = _auto_refresh_job_label(row.get("label") or row.get("job_id") or "S&P 500 스냅샷")
    if status == "success":
        return f"{job_label} 갱신이 완료되었습니다."
    if status == "skipped":
        return _summarize_auto_refresh_plan(summary)
    if status == "locked":
        return "다른 Overview 갱신 작업이 이미 실행 중입니다."
    if status == "partial_success":
        return f"{job_label} 갱신이 일부 이슈와 함께 완료되었습니다."
    if status == "failed":
        return f"{job_label} 갱신에 실패했습니다."
    return f"자동 갱신 상태: {_auto_refresh_status_label(status)}"


def _render_browser_auto_refresh_timing(
    summary: dict[str, Any] | None,
    *,
    live_countdown: bool = False,
    auto_reload: bool = False,
    key_suffix: str = "default",
) -> None:
    timing = _browser_auto_refresh_timing(summary)
    if live_countdown and timing.get("reason") == "cadence not due" and timing.get("remaining_seconds") is not None:
        render_auto_refresh_countdown(
            timing,
            auto_reload=auto_reload,
            key_suffix=key_suffix,
            default_cadence_seconds=BROWSER_AUTO_REFRESH_SECONDS,
        )
        return

    render_auto_refresh_timing_static(timing)


def _browser_auto_refresh_state_keys(universe_code: str) -> tuple[str, str]:
    normalized = str(universe_code or "SP500").strip().lower()
    return (
        f"overview_{normalized}_browser_auto_refresh_summary",
        f"overview_{normalized}_browser_auto_refresh_checked_at",
    )


def _browser_auto_refresh_job_config(universe_code: str) -> dict[str, str]:
    normalized = str(universe_code or "SP500").strip().upper()
    return dict(BROWSER_AUTO_REFRESH_JOB_CONFIG.get(normalized, BROWSER_AUTO_REFRESH_JOB_CONFIG["SP500"]))


def _get_browser_auto_refresh_state(universe_code: str) -> tuple[dict[str, Any] | None, str | None]:
    summary_key, checked_key = _browser_auto_refresh_state_keys(universe_code)
    summary = st.session_state.get(summary_key)
    checked_at = st.session_state.get(checked_key)
    if not isinstance(summary, dict):
        summary = None
    return summary, str(checked_at) if checked_at else None


def _store_browser_auto_refresh_state(
    universe_code: str,
    summary: dict[str, Any],
    checked_at: str,
) -> None:
    summary_key, checked_key = _browser_auto_refresh_state_keys(universe_code)
    st.session_state[summary_key] = summary
    st.session_state[checked_key] = checked_at
    st.session_state["overview_browser_auto_refresh_summary"] = summary
    st.session_state["overview_browser_auto_refresh_checked_at"] = checked_at


def _run_browser_auto_refresh_check(*, universe_code: str = "SP500") -> dict[str, Any]:
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config = _browser_auto_refresh_job_config(universe_code)
    profile = config["profile"]
    job_id = config["job_id"]
    summary = run_overview_browser_auto_refresh(
        profile=profile,
        job_id=job_id,
        universe_code=universe_code,
        checked_at=checked_at,
    )
    _store_browser_auto_refresh_state(universe_code, summary, checked_at)
    return summary


def _is_daily_intraday_refresh_due(snapshot: dict[str, Any], *, period: str) -> bool:
    if period != "daily":
        return False
    coverage = dict(snapshot.get("coverage") or {})
    if coverage.get("price_mode") != "Intraday Snapshot":
        return True
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is None:
        return True
    return int(stale_minutes) >= MARKET_INTRADAY_REFRESH_MINUTES


def _run_market_intraday_snapshot_action(
    *,
    universe_code: str,
    universe_limit: int,
) -> dict[str, Any]:
    return run_overview_market_intraday_snapshot(
        universe_code=universe_code,
        universe_limit=universe_limit,
    )


def _run_nasdaq_symbol_directory_action() -> dict[str, Any]:
    action = getattr(overview_actions_module, "run_overview_nasdaq_symbol_directory", None)
    if not callable(action):
        action = getattr(importlib.reload(overview_actions_module), "run_overview_nasdaq_symbol_directory")
    return action()


def _run_market_movers_eod_history_action(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> dict[str, Any]:
    action = getattr(overview_actions_module, "run_overview_market_movers_eod_history", None)
    if not callable(action):
        action = getattr(importlib.reload(overview_actions_module), "run_overview_market_movers_eod_history")
    return action(
        universe_code=universe_code,
        universe_limit=universe_limit,
        period=period,
    )


def _load_market_movers_snapshot(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    sector: str,
) -> dict[str, Any]:
    return load_overview_market_movers_snapshot(
        universe_limit=universe_limit,
        universe_code=universe_code,
        period=period,
        top_n=top_n,
        sector=None if sector == "All" else sector,
    )


def _get_market_movers_refresh_state(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> dict[str, str | bool] | None:
    if period != "daily":
        return None

    coverage = dict(snapshot.get("coverage") or {})
    service_state = dict(coverage.get("refresh_state") or {})
    if service_state:
        status = str(service_state.get("status") or "unknown")
        dot_color = {
            "fresh": OVERVIEW_COLOR_POSITIVE,
            "partial": OVERVIEW_COLOR_WARNING,
            "due": OVERVIEW_COLOR_WARNING,
            "stale": OVERVIEW_COLOR_DANGER,
            "failed": OVERVIEW_COLOR_DANGER,
        }.get(status, OVERVIEW_COLOR_NEUTRAL)
        return {
            "dot_color": dot_color,
            "label": str(service_state.get("label") or status.title()),
            "detail": str(service_state.get("recommended_action") or service_state.get("detail") or ""),
            "refresh_due": bool(service_state.get("refresh_due")),
        }

    price_mode = str(coverage.get("price_mode") or "")
    stale_minutes = coverage.get("snapshot_stale_minutes")
    refresh_due = _is_daily_intraday_refresh_due(snapshot, period=period)
    if price_mode != "Intraday Snapshot":
        dot_color = OVERVIEW_COLOR_DANGER
        label = "Update needed"
        detail = "using EOD fallback"
    elif refresh_due:
        dot_color = OVERVIEW_COLOR_DANGER
        label = "Update needed"
        detail = f"{int(stale_minutes or 0)}m old"
    else:
        dot_color = OVERVIEW_COLOR_POSITIVE
        label = "Fresh"
        detail = f"{int(stale_minutes or 0)}m old"
    return {
        "dot_color": dot_color,
        "label": label,
        "detail": detail,
        "refresh_due": refresh_due,
    }


def _market_refresh_mode_label(value: str) -> str:
    return {"manual": "수동 갱신", "auto": "자동 갱신"}.get(value, value)


def _render_market_movers_controls() -> MarketMoverControls:
    render_overview_toolbar_label("스캔 조건")
    controls = st.columns([1.1, 1.2, 1.1, 0.8], gap="small", vertical_alignment="bottom")
    coverage = str(
        controls[0].selectbox(
            "Coverage",
            list(MARKET_COVERAGE_OPTIONS),
            index=0,
            format_func=_coverage_label,
            key="overview_market_movers_coverage",
        )
    )
    universe_limit = _universe_limit(coverage)
    period = str(
        controls[1].selectbox(
            "Period",
            list(MARKET_MOVER_PERIOD_LABELS.keys()),
            index=0,
            format_func=_market_mover_period_label,
            key="overview_market_movers_period",
        )
    )
    sector_options = ["All"] + load_overview_market_mover_sectors(
        universe_code=coverage,
        universe_limit=universe_limit,
    )
    sector = str(
        controls[2].selectbox(
            "Sector",
            sector_options,
            index=0,
            key="overview_market_movers_sector",
        )
    )
    top_n = int(
        controls[3].number_input(
            "Top N",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            key="overview_market_movers_top_n",
        )
    )
    return MarketMoverControls(
        coverage=coverage,
        universe_limit=universe_limit,
        period=period,
        sector=sector,
        top_n=top_n,
    )


def _render_group_leadership_controls() -> GroupLeadershipControls:
    controls = st.columns([1.1, 1, 1, 0.8, 0.9], gap="small", vertical_alignment="bottom")
    coverage = str(
        controls[0].selectbox(
            "Coverage",
            list(MARKET_COVERAGE_OPTIONS),
            index=0,
            format_func=_coverage_label,
            key="overview_group_leadership_coverage_code",
        )
    )
    group_by = str(
        controls[1].selectbox(
            "Group",
            list(GROUP_BY_LABELS.keys()),
            index=0,
            format_func=_group_by_label,
            key="overview_group_leadership_group",
        )
    )
    period = str(
        controls[2].selectbox(
            "Period",
            list(GROUP_LEADERSHIP_PERIOD_LABELS.keys()),
            index=2,
            format_func=_group_leadership_period_label,
            key="overview_group_leadership_period",
        )
    )
    top_n = int(
        controls[3].number_input(
            "Top N",
            min_value=5,
            max_value=100,
            value=10,
            step=5,
            key="overview_group_leadership_top_n",
        )
    )
    min_group_size = int(
        controls[4].number_input(
            "Min Symbols",
            min_value=1,
            max_value=50,
            value=5,
            step=1,
            key="overview_group_leadership_min_symbols",
        )
    )
    return GroupLeadershipControls(
        coverage=coverage,
        universe_limit=_universe_limit(coverage),
        group_by=group_by,
        period=period,
        top_n=top_n,
        min_group_size=min_group_size,
    )


def _run_futures_ohlcv_action(
    *,
    symbols: list[str],
    cadence_mode: str,
) -> dict[str, Any]:
    return run_overview_futures_ohlcv(symbols=symbols, cadence_mode=cadence_mode)


def _run_futures_daily_ohlcv_action() -> dict[str, Any]:
    return run_overview_futures_daily_ohlcv()


def _futures_state_tone(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"calm", "ok"}:
        return "positive"
    if normalized in {"moving", "due", "review"}:
        return "warning"
    if normalized in {"sharp", "stale", "missing", "failed"}:
        return "danger"
    return "neutral"


def _futures_metric_for_symbol(rows: Any, symbol: str) -> dict[str, Any]:
    if not isinstance(rows, pd.DataFrame) or rows.empty or "Symbol" not in rows:
        return {}
    matches = rows[rows["Symbol"] == symbol]
    return dict(matches.iloc[0]) if not matches.empty else {}


def _futures_selected_symbols(snapshot: dict[str, Any]) -> list[str]:
    symbols = [str(symbol) for symbol in snapshot.get("symbols") or [] if str(symbol).strip()]
    ordered: list[str] = []
    for symbol in symbols:
        if symbol and symbol not in ordered:
            ordered.append(symbol)
    return ordered


def _futures_symbols_with_candles(snapshot: dict[str, Any], selected_symbols: list[str] | None = None) -> list[str]:
    selected = selected_symbols if selected_symbols is not None else _futures_selected_symbols(snapshot)
    all_candles = snapshot.get("all_candles")
    if not isinstance(all_candles, pd.DataFrame) or all_candles.empty or "Symbol" not in all_candles:
        return []
    chartable = {str(symbol) for symbol in all_candles["Symbol"].dropna().unique()}
    return [symbol for symbol in selected if symbol in chartable]


def _futures_chart_symbols(snapshot: dict[str, Any], *, chart_scope: str = "compact_6") -> list[str]:
    selected = _futures_selected_symbols(snapshot)
    chartable = _futures_symbols_with_candles(snapshot, selected)
    if chart_scope == "all_with_data":
        return chartable
    candidates = chartable or selected
    return candidates[:FUTURES_COMPACT_CHART_LIMIT]


def _futures_chart_scope_label(scope: str) -> str:
    if scope == "all_with_data":
        return "데이터 있는 전체"
    return "핵심 6개"


def _futures_chart_scope_detail(snapshot: dict[str, Any], *, chart_scope: str) -> str:
    selected_count = len(_futures_selected_symbols(snapshot))
    chartable_count = len(_futures_symbols_with_candles(snapshot))
    shown_count = len(_futures_chart_symbols(snapshot, chart_scope=chart_scope))
    if chart_scope == "all_with_data":
        return f"선택 {selected_count}개 중 데이터 있는 {shown_count}개 표시"
    return f"차트 가능 {chartable_count or selected_count}개 중 {shown_count}개 표시"


def _format_futures_percent(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "-"


def _format_futures_age(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):.0f}분"
    except (TypeError, ValueError):
        return "-"


def _futures_value_tone(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "neutral"
        numeric = float(value)
    except (TypeError, ValueError):
        return "neutral"
    if numeric > 0:
        return "positive"
    if numeric < 0:
        return "danger"
    return "neutral"


def _futures_chart_metric_chip(label: str, value: str, tone: str) -> str:
    return (
        f'<span class="ov-futures-mini-metric" style="--ov-chip-tone:{_overview_tone_color(tone)};">'
        f'<span class="ov-futures-mini-metric-label">{escape(label)}</span>'
        f'<span class="ov-futures-mini-metric-value">{escape(value)}</span>'
        "</span>"
    )


def _render_futures_chart_card_header(metric: dict[str, Any], symbol: str) -> None:
    state = str(metric.get("State") or "Missing")
    state_tone = _futures_state_tone(state)
    metric_html = "".join(
        [
            _futures_chart_metric_chip(
                "60분",
                _format_futures_percent(metric.get("60m %")),
                _futures_value_tone(metric.get("60m %")),
            ),
            _futures_chart_metric_chip(
                "15분",
                _format_futures_percent(metric.get("15m %")),
                _futures_value_tone(metric.get("15m %")),
            ),
            _futures_chart_metric_chip("지연", _format_futures_age(metric.get("Age Min")), state_tone),
        ]
    )
    st.markdown(
        f"""
        <div class="ov-futures-chart-head">
          <div>
            <div class="ov-futures-chart-title">{escape(symbol)}</div>
            <div class="ov-futures-chart-subtitle">{escape(_futures_contract_title(metric, symbol))}</div>
          </div>
          <span class="ov-futures-chart-state" style="--ov-chart-tone:{_overview_tone_color(state_tone)};">{escape(_futures_state_label(state))} · {_format_futures_age(metric.get("Age Min"))}</span>
        </div>
        <div class="ov-futures-chart-metrics">{metric_html}</div>
        """,
        unsafe_allow_html=True,
    )


def _futures_contract_title(metric: dict[str, Any], symbol: str) -> str:
    name = str(metric.get("Name") or "").strip()
    group = str(metric.get("Group") or "").strip()
    if name and group:
        return f"{name} · {_futures_group_label(group)}"
    if name:
        return name
    return symbol


def _overview_tone_color(tone: str) -> str:
    normalized = str(tone or "").strip().lower()
    if normalized == "positive":
        return OVERVIEW_COLOR_POSITIVE
    if normalized == "warning":
        return OVERVIEW_COLOR_WARNING
    if normalized == "danger":
        return OVERVIEW_COLOR_DANGER
    if normalized == "primary":
        return OVERVIEW_COLOR_PRIMARY
    return OVERVIEW_COLOR_NEUTRAL


def _futures_feed_state(snapshot: dict[str, Any], *, refresh_mode: str) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    latest_age = coverage.get("latest_age_minutes")
    oldest_age = coverage.get("oldest_age_minutes")
    status = str(snapshot.get("status") or "MISSING")
    if latest_age is None or pd.isna(latest_age):
        label = "자료 없음"
        detail = "저장 candle 없음"
        tone = "danger"
    else:
        age_value = int(latest_age or 0)
        if age_value <= 2 and status == "OK":
            label = "신선함"
            detail = f"최신 {age_value}분"
            tone = "positive"
        elif age_value <= 10:
            label = "확인 필요"
            detail = f"최신 {age_value}분"
            tone = "warning"
        else:
            label = "오래됨"
            detail = f"최신 {age_value}분"
            tone = "danger"
    cadence = "수동 확인"
    if refresh_mode == "auto_60s":
        cadence = "60초 자동 확인"
    elif refresh_mode == "fast_20s":
        cadence = "20초 자동 확인"
    return {
        "label": label,
        "detail": detail,
        "tone": tone,
        "cadence": cadence,
        "latest_age": latest_age,
        "oldest_age": oldest_age,
    }


def _futures_data_action_hint(feed: dict[str, Any]) -> str:
    tone = str(feed.get("tone") or "neutral")
    cadence = str(feed.get("cadence") or "-")
    if tone == "positive":
        return f"확인 완료 · {cadence}"
    if str(feed.get("label") or "") == "자료 없음":
        return f"1분봉 갱신 필요 · {cadence}"
    return f"갱신 필요 · {cadence}"


def _futures_next_action_state(feed: dict[str, Any]) -> dict[str, str]:
    label = str(feed.get("label") or "")
    tone = str(feed.get("tone") or "neutral")
    cadence = str(feed.get("cadence") or "-")
    detail = str(feed.get("detail") or "-")
    if tone == "positive":
        return {
            "value": "자료 양호",
            "detail": f"{detail} · {cadence}",
            "tone": "positive",
        }
    if label in {"자료 없음", "오래됨"} or tone == "danger":
        return {
            "value": "갱신 필요",
            "detail": f"{detail} · {cadence}",
            "tone": "danger",
        }
    return {
        "value": "확인 필요",
        "detail": f"{detail} · {cadence}",
        "tone": tone or "warning",
    }


def _futures_compact_symbols_label(selected_symbols: list[str]) -> str:
    if not selected_symbols:
        return "-"
    if len(selected_symbols) <= 4:
        return ", ".join(selected_symbols)
    return f"{', '.join(selected_symbols[:4])} 외 {len(selected_symbols) - 4}개"


def _futures_command_summary_items(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    refresh_mode: str,
) -> list[dict[str, Any]]:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    top_move = dict(snapshot.get("top_move") or {})
    return [
        {
            "label": "관찰 범위",
            "value": f"{_futures_group_label(group)} · {len(selected_symbols)}개",
            "detail": _futures_compact_symbols_label(selected_symbols),
            "tone": "neutral",
            "pills": [str(feed.get("cadence") or "-")],
            "pill_tones": ["neutral"],
        },
        {
            "label": "데이터 상태",
            "value": str(feed.get("label") or "-"),
            "detail": _futures_data_action_hint(feed),
            "tone": str(feed.get("tone") or "neutral"),
            "pills": [str(feed.get("detail") or "-")],
            "pill_tones": [str(feed.get("tone") or "neutral")],
        },
        {
            "label": "단기 움직임",
            "value": str(top_move.get("Symbol") or "-"),
            "detail": (
                f"15분 {_format_futures_percent(top_move.get('15m %'))} · 60분 {_format_futures_percent(top_move.get('60m %'))}"
                if top_move.get("Symbol")
                else "저장 candle 대기"
            ),
            "tone": _futures_state_tone(str(top_move.get("State") or "")),
            "pills": [
                _futures_state_label(top_move.get("State") or "대기"),
                f"{lookback_label} · {_futures_interval_label(chart_interval)} 봉",
            ],
            "pill_tones": [
                _futures_state_tone(str(top_move.get("State") or "")),
                "neutral",
            ],
        },
    ]


def _futures_workbench_context_items(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    chart_scope: str,
    refresh_mode: str,
) -> list[dict[str, Any]]:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    next_action = _futures_next_action_state(feed)
    return [
        {
            "label": "관찰",
            "value": f"{_futures_group_label(group)} · {len(selected_symbols)}개",
            "detail": _futures_compact_symbols_label(selected_symbols),
            "tone": "neutral",
        },
        {
            "label": "차트",
            "value": f"{lookback_label} · {_futures_interval_label(chart_interval)} 봉 · {_futures_chart_scope_label(chart_scope)}",
            "detail": _futures_chart_scope_detail(snapshot, chart_scope=chart_scope),
            "tone": "neutral",
        },
        {
            "label": "자료",
            "value": str(feed.get("label") or "-"),
            "detail": str(feed.get("detail") or "-"),
            "tone": str(feed.get("tone") or "neutral"),
        },
        {
            "label": "다음 행동",
            "value": next_action["value"],
            "detail": next_action["detail"],
            "tone": next_action["tone"],
        },
    ]


def _futures_daily_coverage_label(coverage: dict[str, Any]) -> str:
    standardized_count = int(coverage.get("standardized_count") or 0)
    symbol_count = int(coverage.get("symbol_count") or 0)
    if symbol_count <= 0:
        return "0/0"
    return f"{standardized_count}/{symbol_count}"


def _futures_refresh_module_model(
    *,
    snapshot: dict[str, Any],
    macro: dict[str, Any],
    selected_symbols: list[str],
    refresh_mode: str,
) -> dict[str, Any]:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    macro_coverage = dict(macro.get("coverage") or {})
    latest_age = _format_futures_age(feed.get("latest_age"))
    live_status = _futures_next_action_state(feed)
    macro_basis = _snapshot_value(macro_coverage.get("latest_daily_date"))
    macro_coverage_label = _futures_daily_coverage_label(macro_coverage)
    macro_standardized = int(macro_coverage.get("standardized_count") or 0)
    macro_symbol_count = int(macro_coverage.get("symbol_count") or 0)
    macro_ok = macro_symbol_count > 0 and macro_standardized >= macro_symbol_count
    return {
        "title": "자료 갱신",
        "sources": [
            {
                "label": "실시간 차트 자료",
                "basis": "1분봉",
                "status": live_status["value"],
                "detail": f"선택 선물 {len(selected_symbols)}개 · 최신 candle {latest_age} · 60초 자동 확인 대상",
                "tone": live_status["tone"],
            },
            {
                "label": "매크로 일봉 자료",
                "basis": "1D OHLCV",
                "status": "자료 양호" if macro_ok else "확인 필요",
                "detail": f"macro context 기준일 {macro_basis} · daily coverage {macro_coverage_label}",
                "tone": "positive" if macro_ok else "warning",
            },
        ],
        "actions": [
            {"label": "1분봉 갱신", "kind": "live"},
            {"label": "일봉 매크로 갱신", "kind": "macro_daily"},
            {"label": "화면 다시 읽기", "kind": "reload"},
        ],
        "modes": [
            {"label": "수동", "value": "manual"},
            {"label": "60초 자동 확인", "value": "auto_60s"},
        ],
    }


def _render_futures_workbench_context_bar(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    chart_scope: str,
    refresh_mode: str,
) -> None:
    items = _futures_workbench_context_items(
        snapshot=snapshot,
        group=group,
        selected_symbols=selected_symbols,
        lookback_label=lookback_label,
        chart_interval=chart_interval,
        chart_scope=chart_scope,
        refresh_mode=refresh_mode,
    )
    html_items: list[str] = []
    for item in items:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        html_items.append(
            f'<div class="ov-futures-workbench-item" style="--ov-workbench-tone:{tone_color};">'
            f'<div class="ov-futures-workbench-label">{escape(str(item.get("label") or "-"))}</div>'
            f'<div class="ov-futures-workbench-value">{escape(str(item.get("value") or "-"))}</div>'
            f'<div class="ov-futures-workbench-detail">{escape(str(item.get("detail") or ""))}</div>'
            "</div>"
        )
    st.markdown(
        f"""
        <div class="ov-futures-workbench-bar">
          {"".join(html_items)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_futures_refresh_module(
    *,
    snapshot: dict[str, Any],
    selected_symbols: list[str],
    refresh_mode: str,
) -> str:
    macro = load_overview_futures_macro_snapshot(include_validation=False)
    model = _futures_refresh_module_model(
        snapshot=snapshot,
        macro=macro,
        selected_symbols=selected_symbols,
        refresh_mode=refresh_mode,
    )
    source_html: list[str] = []
    for source in model["sources"]:
        tone_color = _overview_tone_color(str(source.get("tone") or "neutral"))
        source_html.append(
            f'<div class="ov-futures-refresh-source" style="--ov-refresh-tone:{tone_color};">'
            f'<div class="ov-futures-refresh-source-label">{escape(str(source.get("label") or "-"))}</div>'
            f'<div class="ov-futures-refresh-source-main">'
            f'<strong>{escape(str(source.get("basis") or "-"))}</strong>'
            f'<span>{escape(str(source.get("status") or "-"))}</span>'
            f"</div>"
            f'<div class="ov-futures-refresh-source-detail">{escape(str(source.get("detail") or ""))}</div>'
            "</div>"
        )
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="ov-futures-refresh-module">
              <div class="ov-futures-refresh-head">
                <div class="ov-futures-refresh-title">{escape(str(model["title"]))}</div>
                <div class="ov-futures-refresh-meta">현재 확인 방식: {escape(_futures_refresh_mode_label(refresh_mode))}</div>
              </div>
              <div class="ov-futures-refresh-sources">
                {"".join(source_html)}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        action_cols = st.columns([1, 1, 1, 1.25], gap="small", vertical_alignment="bottom")
        if action_cols[0].button(
            "1분봉 갱신",
            key="overview_futures_manual_refresh",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("선택 선물 1분봉을 yfinance에서 수집하는 중입니다..."):
                _store_overview_job_result(
                    "overview_futures_ohlcv_result",
                    _run_futures_ohlcv_action(symbols=selected_symbols, cadence_mode="manual"),
                )
            st.rerun()
        if action_cols[1].button(
            "일봉 매크로 갱신",
            key="overview_futures_macro_daily_refresh",
            use_container_width=True,
        ):
            with st.spinner("선물 5년 일봉을 yfinance에서 수집하는 중입니다..."):
                _store_overview_job_result(
                    "overview_futures_daily_ohlcv_result",
                    _run_futures_daily_ohlcv_action(),
                )
                clear_overview_futures_macro_snapshot_cache()
                st.session_state["overview_futures_macro_daily_refreshed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
        if action_cols[2].button("화면 다시 읽기", key="overview_futures_reload", use_container_width=True):
            st.session_state["overview_futures_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
        mode_options = [str(mode.get("value")) for mode in model["modes"]]
        segmented_control = getattr(st, "segmented_control", None)
        with action_cols[3]:
            if callable(segmented_control):
                selected_mode = segmented_control(
                    "확인 방식",
                    mode_options,
                    key="overview_futures_refresh_mode",
                    format_func=_futures_refresh_mode_label,
                    help="자동 확인은 현재 브라우저 세션이 열려 있을 때만 60초마다 실시간 차트 자료를 확인합니다.",
                )
            else:
                selected_mode = st.radio(
                    "확인 방식",
                    mode_options,
                    key="overview_futures_refresh_mode",
                    format_func=_futures_refresh_mode_label,
                    horizontal=True,
                    help="자동 확인은 현재 브라우저 세션이 열려 있을 때만 60초마다 실시간 차트 자료를 확인합니다.",
                )
    return str(selected_mode or refresh_mode)


def _futures_watch_strip_items(snapshot: dict[str, Any], selected_symbols: list[str]) -> list[dict[str, Any]]:
    rows = snapshot.get("rows")
    items: list[dict[str, Any]] = []
    for symbol in selected_symbols:
        metric = _futures_metric_for_symbol(rows, symbol)
        state = str(metric.get("State") or "Missing")
        items.append(
            {
                "symbol": symbol,
                "title": _futures_contract_title(metric, symbol),
                "state": _futures_state_label(state),
                "move": (
                    f"15분 {_format_futures_percent(metric.get('15m %'))} · "
                    f"60분 {_format_futures_percent(metric.get('60m %'))}"
                ),
                "age": _format_futures_age(metric.get("Age Min")),
                "tone": _futures_state_tone(state),
            }
        )
    return items


def _render_futures_watch_strip(snapshot: dict[str, Any], selected_symbols: list[str]) -> None:
    items = _futures_watch_strip_items(snapshot, selected_symbols)
    if not items:
        return
    html_items: list[str] = []
    for item in items:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        html_items.append(
            f'<div class="ov-futures-watch-item" style="--ov-watch-tone:{tone_color};">'
            f'<div class="ov-futures-watch-symbol">{escape(str(item.get("symbol") or "-"))}</div>'
            f'<div class="ov-futures-watch-title">{escape(str(item.get("title") or ""))}</div>'
            f'<div class="ov-futures-watch-move">{escape(str(item.get("move") or ""))}</div>'
            f'<div class="ov-futures-watch-meta"><span>{escape(str(item.get("state") or "-"))}</span><span>{escape(str(item.get("age") or "-"))}</span></div>'
            "</div>"
        )
    st.markdown(
        f"""
        <div class="ov-futures-watch-strip">
          <div class="ov-futures-watch-head">
            <div class="ov-futures-watch-label">관찰 선물</div>
            <div class="ov-futures-watch-note">선택 심볼의 단기 움직임과 데이터 상태</div>
          </div>
          <div class="ov-futures-watch-list">{"".join(html_items)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_futures_command_center(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    refresh_mode: str,
) -> None:
    items = _futures_command_summary_items(
        snapshot=snapshot,
        group=group,
        selected_symbols=selected_symbols,
        lookback_label=lookback_label,
        chart_interval=chart_interval,
        refresh_mode=refresh_mode,
    )
    cells = []
    for item in items:
        pill_tones = list(item.get("pill_tones") or [])
        pills = "".join(
            (
                f'<span class="ov-futures-feed-pill" style="--ov-feed-tone: '
                f'{_overview_tone_color(str(pill_tones[index] if index < len(pill_tones) else "neutral"))};">'
                f'{escape(str(pill))}</span>'
            )
            for index, pill in enumerate(item.get("pills") or [])
        )
        cells.append(
            f"""
          <div class="ov-futures-command-cell">
            <div class="ov-futures-kicker">{escape(str(item.get("label") or "-"))}</div>
            <div class="ov-futures-title">{escape(str(item.get("value") or "-"))}</div>
            <div class="ov-futures-detail">{escape(str(item.get("detail") or ""))}</div>
            <div class="ov-futures-feed-row">{pills}</div>
          </div>
            """
        )
    st.markdown(
        f"""
        <div class="ov-futures-command">
          {"".join(cells)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_futures_section_header(title: str, detail: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="ov-futures-section-head">
          <div class="ov-futures-section-title">{escape(title)}</div>
          <div class="ov-futures-section-meta">{escape(detail or "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_macro_score(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):+.0f}"
    except (TypeError, ValueError):
        return "-"


def _macro_score_cards(scores: Any) -> list[dict[str, Any]]:
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return [
            {
                "title": "Macro Scores",
                "value": "-",
                "detail": "waiting for daily futures data",
                "tone": "neutral",
            }
        ]
    cards: list[dict[str, Any]] = []
    for _, row in scores.iterrows():
        cards.append(
            {
                "title": str(row.get("Score") or "-"),
                "value": _format_macro_score(row.get("Value")),
                "detail": f"{row.get('Direction') or '-'} · {row.get('Coverage') or '-'}",
                "tone": str(row.get("Tone") or "neutral"),
            }
        )
    return cards


def _macro_score_badges(scores: Any) -> list[dict[str, Any]]:
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return [{"label": "매크로", "value": "-", "tone": "neutral"}]
    badges: list[dict[str, Any]] = []
    for _, row in scores.iterrows():
        score_name = str(row.get("Score") or "-")
        badges.append(
            {
                "label": MACRO_SCORE_LABELS.get(score_name, score_name.replace(" Score", "")),
                "value": _format_macro_score(row.get("Value")),
                "tone": str(row.get("Tone") or "neutral"),
            }
        )
    return badges


def _format_macro_percent(value: Any, *, digits: int = 1) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):.{digits}f}%"
    except (TypeError, ValueError):
        return "-"


def _macro_validation_cards(macro: dict[str, Any]) -> list[dict[str, Any]]:
    confidence = dict(macro.get("confidence") or {})
    validation = dict(macro.get("validation") or {})
    validation_coverage = dict(validation.get("coverage") or {})
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    sample = confidence.get("sample_size")
    if sample is None:
        sample = current_metrics.get("Sample 5D") or 0
    occurrence_count = confidence.get("occurrence_count")
    if occurrence_count is None:
        occurrence_count = current_metrics.get("Occurrence Count") or 0
    hit_rate = confidence.get("hit_rate_5d")
    if hit_rate is None:
        hit_rate = current_metrics.get("Hit Rate 5D %")
    hit_applicable = bool(confidence.get("hit_applicable"))
    span = validation_coverage.get("history_span_years")
    validation_dates = validation_coverage.get("validation_dates") or 0
    hit_detail = (
        f"5D sample {sample or 0} · hit {_format_macro_percent(hit_rate)}"
        if hit_applicable
        else f"directional hit n/a · occurrences {occurrence_count or 0}"
    )
    return [
        {
            "title": "Interpretation Confidence",
            "value": confidence.get("label") or "Not Enough History",
            "detail": hit_detail,
            "tone": confidence.get("tone") or "warning",
        },
        {
            "title": "Historical Validation",
            "value": validation.get("status") or "MISSING",
            "detail": f"{validation_dates} PIT dates · {span or '-'}y stored history",
            "tone": "positive" if validation.get("status") == "OK" else "warning",
        },
        {
            "title": "Current Scenario History",
            "value": f"{sample or occurrence_count or 0}",
            "detail": (
                f"mean 5D {_format_macro_percent(current_metrics.get('Mean 5D %'), digits=2)}"
                if hit_applicable
                else "mixed scenario occurrence count"
            ),
            "tone": "positive" if int(sample or occurrence_count or 0) >= 60 else "warning",
        },
        {
            "title": "Validation Source",
            "value": "futures / proxy",
            "detail": "ETF rows are labeled fallback targets",
            "tone": "neutral",
        },
    ]


def _macro_support_items(macro: dict[str, Any]) -> list[dict[str, Any]]:
    confidence = dict(macro.get("confidence") or {})
    validation = dict(macro.get("validation") or {})
    validation_coverage = dict(validation.get("coverage") or {})
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    sample = confidence.get("sample_size")
    if sample is None:
        sample = current_metrics.get("Sample 5D") or 0
    occurrence_count = confidence.get("occurrence_count")
    if occurrence_count is None:
        occurrence_count = current_metrics.get("Occurrence Count") or 0
    hit_rate = confidence.get("hit_rate_5d")
    if hit_rate is None:
        hit_rate = current_metrics.get("Hit Rate 5D %")
    hit_applicable = bool(confidence.get("hit_applicable"))
    validation_dates = validation_coverage.get("validation_dates") or 0
    span = validation_coverage.get("history_span_years")
    return [
        {
            "label": "근거 강도",
            "value": _macro_confidence_short_label(confidence.get("label")),
            "detail": _macro_confidence_reason_label((list(confidence.get("reasons") or [])[:1] or [""])[0]),
            "tone": confidence.get("tone") or "warning",
        },
        {
            "label": "과거 점검",
            "value": _macro_validation_status_label(validation.get("status")),
            "detail": f"{validation_dates}개 PIT 날짜 · {span or '-'}년",
            "tone": "positive" if validation.get("status") == "OK" else "warning",
        },
        {
            "label": "유사 구간",
            "value": sample or occurrence_count or 0,
            "detail": (
                f"5D 적중 {_format_macro_percent(hit_rate)}"
                if hit_applicable
                else "발생 횟수, 적중률 n/a"
            ),
            "tone": "positive" if int(sample or occurrence_count or 0) >= 60 else "warning",
        },
    ]


def _futures_market_brief_model(macro: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(macro.get("coverage") or {})
    summary = dict(macro.get("summary") or {})
    sentences = [str(sentence) for sentence in macro.get("summary_sentences") or [] if str(sentence).strip()]
    evidence_chips = [
        _macro_evidence_summary_label(item)
        for item in macro.get("evidence") or []
        if str(item).strip()
    ]
    support_items = _macro_support_items(macro)
    support_items.append(
        {
            "label": "자료 기준",
            "value": f"{coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}개",
            "detail": f"기준일 {_snapshot_value(coverage.get('latest_daily_date'))}",
            "tone": "neutral",
        }
    )
    return {
        "eyebrow": "오늘 기준 시장 브리프",
        "scenario": str(summary.get("scenario") or "시장 해석 대기"),
        "sub_scenario": str(summary.get("sub_scenario") or ""),
        "regime_hint": str(summary.get("regime_hint") or ""),
        "mixed_reason": str(summary.get("mixed_reason") or ""),
        "sentence": sentences[0] if sentences else "저장된 일봉 선물 데이터로 시장 흐름을 해석합니다.",
        "support_items": support_items,
        "evidence_chips": evidence_chips[:4],
    }


def _render_futures_market_brief(macro: dict[str, Any]) -> None:
    model = _futures_market_brief_model(macro)
    support_html: list[str] = []
    for item in model["support_items"]:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        support_html.append(
            f'<div class="ov-futures-brief-support-item" style="--ov-brief-tone:{tone_color};">'
            f'<div class="ov-futures-brief-support-label">{escape(str(item.get("label") or "-"))}</div>'
            f'<div class="ov-futures-brief-support-value">{escape(str(item.get("value") or "-"))}</div>'
            f'<div class="ov-futures-brief-support-detail">{escape(str(item.get("detail") or ""))}</div>'
            "</div>"
        )
    evidence_html = "".join(
        f'<span class="ov-futures-brief-evidence-chip">{escape(str(chip))}</span>'
        for chip in model["evidence_chips"]
    )
    if not evidence_html:
        evidence_html = '<span class="ov-futures-brief-evidence-chip">상세 근거는 아래 disclosure에서 확인</span>'
    sub_scenario = str(model.get("sub_scenario") or "").strip()
    regime_hint = str(model.get("regime_hint") or "").strip()
    subscenario_text = " · ".join(item for item in [sub_scenario, regime_hint] if item)
    subscenario_html = (
        f'<div class="ov-futures-brief-subscenario">{escape(subscenario_text)}</div>'
        if subscenario_text
        else ""
    )
    mixed_reason = str(model.get("mixed_reason") or "").strip()
    mixed_reason_html = (
        f'<div class="ov-futures-brief-mixed-reason">{escape(mixed_reason)}</div>'
        if mixed_reason
        else ""
    )
    st.markdown(
        f"""
        <div class="ov-futures-brief">
          <div class="ov-futures-brief-main">
            <div class="ov-futures-brief-eyebrow">{escape(str(model["eyebrow"]))}</div>
            <div class="ov-futures-brief-scenario">{escape(str(model["scenario"]))}</div>
            {subscenario_html}
            {mixed_reason_html}
            <div class="ov-futures-brief-sentence">{escape(str(model["sentence"]))}</div>
            <div class="ov-futures-brief-evidence">{evidence_html}</div>
          </div>
          <div class="ov-futures-brief-support">{"".join(support_html)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _macro_weekly_value_float(value: Any) -> float:
    try:
        text = str(value or "0").replace("%", "").replace(",", "").strip()
        if text.startswith("+"):
            text = text[1:]
        return float(text)
    except (TypeError, ValueError):
        return 0.0


def _futures_weekly_flow_model(weekly_context: dict[str, Any]) -> dict[str, Any]:
    cards = [dict(card) for card in weekly_context.get("cards") or []]
    ranked = sorted(cards, key=lambda card: abs(_macro_weekly_value_float(card.get("value"))), reverse=True)
    driver = ranked[0] if ranked else {}
    supporting = [card for card in cards if str(card.get("tone") or "neutral") == "positive"]
    tempering = [card for card in cards if str(card.get("tone") or "neutral") in {"danger", "warning"}]
    neutral = [card for card in cards if str(card.get("tone") or "neutral") == "neutral"]
    return {
        "title": "최근 1주 흐름",
        "basis": str(weekly_context.get("basis") or "저장된 1D 선물 OHLCV의 최근 5거래일 변화율"),
        "summary": str(weekly_context.get("summary") or ""),
        "driver": driver,
        "supporting": supporting,
        "tempering": tempering,
        "neutral": neutral,
    }


def _render_futures_signal_strip(items: list[dict[str, Any]], *, class_prefix: str) -> None:
    html_items: list[str] = []
    for item in items:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        html_items.append(
            f'<div class="{class_prefix}-item" style="--ov-signal-tone:{tone_color};">'
            f'<div class="{class_prefix}-label">{escape(str(item.get("label") or "-"))}</div>'
            f'<div class="{class_prefix}-value">{escape(str(item.get("value") or "-"))}</div>'
            f'<div class="{class_prefix}-detail">{escape(str(item.get("detail") or ""))}</div>'
            "</div>"
        )
    st.markdown(
        f'<div class="{class_prefix}-strip">{"".join(html_items)}</div>',
        unsafe_allow_html=True,
    )


def _macro_score_tone(row: pd.Series) -> str:
    tone = str(row.get("Tone") or "").strip()
    if tone and tone != "neutral":
        return tone
    try:
        value = float(row.get("Value"))
    except (TypeError, ValueError):
        return "neutral"
    if value > 0:
        return "positive"
    if value < 0:
        return "danger"
    return "neutral"


def _render_macro_score_lane(scores: Any) -> None:
    badges = _macro_score_badges(scores)
    if isinstance(scores, pd.DataFrame) and not scores.empty:
        score_rows = []
        for badge, (_, row) in zip(badges, scores.iterrows(), strict=False):
            score_rows.append((badge, _macro_score_tone(row)))
    else:
        score_rows = [(badge, str(badge.get("tone") or "neutral")) for badge in badges]
    html_items: list[str] = []
    for badge, tone in score_rows:
        tone_color = _overview_tone_color(tone)
        html_items.append(
            f'<span class="ov-futures-score-chip" style="--ov-chip-tone:{tone_color};">'
            f'<span class="ov-futures-score-label">{escape(str(badge.get("label") or "-"))}</span>'
            f'<span class="ov-futures-score-value">{escape(str(badge.get("value") or "-"))}</span>'
            "</span>"
        )
    st.markdown(
        f'<div class="ov-futures-score-lane">{"".join(html_items)}</div>',
        unsafe_allow_html=True,
    )


def _render_weekly_macro_context(weekly_context: dict[str, Any]) -> None:
    model = _futures_weekly_flow_model(weekly_context)
    if not model["driver"]:
        return
    driver = dict(model["driver"])
    driver_tone = _overview_tone_color(str(driver.get("tone") or "neutral"))

    def _weekly_item_html(item: dict[str, Any]) -> str:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        return (
            f'<div class="ov-futures-week-lane-item" style="--ov-week-tone:{tone_color};">'
            f'<span class="ov-futures-week-lane-label">{escape(str(item.get("label") or "-"))}</span>'
            f'<span class="ov-futures-week-lane-value">{escape(str(item.get("value") or "-"))}</span>'
            f'<span class="ov-futures-week-lane-detail">{escape(str(item.get("detail") or item.get("meaning") or ""))}</span>'
            "</div>"
        )

    supporting_html = "".join(_weekly_item_html(item) for item in model["supporting"][:3])
    tempering_html = "".join(_weekly_item_html(item) for item in model["tempering"][:3])
    if not supporting_html:
        supporting_html = '<div class="ov-futures-week-lane-empty">뚜렷한 지지 흐름 없음</div>'
    if not tempering_html:
        tempering_html = '<div class="ov-futures-week-lane-empty">뚜렷한 완화/충돌 흐름 없음</div>'
    st.markdown(
        f"""
        <div class="ov-futures-week-flow">
          <div class="ov-futures-week-flow-head">
            <div>
              <div class="ov-futures-week-flow-title">{escape(str(model["title"]))}</div>
              <div class="ov-futures-week-flow-basis">{escape(str(model["basis"]))}</div>
            </div>
            <div class="ov-futures-week-driver" style="--ov-week-tone:{driver_tone};">
              <span>{escape(str(driver.get("label") or "-"))}</span>
              <strong>{escape(str(driver.get("value") or "-"))}</strong>
            </div>
          </div>
          <div class="ov-futures-week-summary">{escape(str(model["summary"]))}</div>
          <div class="ov-futures-week-lanes">
            <div class="ov-futures-week-lane">
              <div class="ov-futures-week-lane-title">오늘 해석을 지지</div>
              {supporting_html}
            </div>
            <div class="ov-futures-week-lane">
              <div class="ov-futures-week-lane-title">주의해서 볼 흐름</div>
              {tempering_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_macro_evidence_reading(sections: list[dict[str, Any]]) -> None:
    if not sections:
        st.info("해석 가능한 macro evidence가 아직 없습니다.")
        return
    by_key = {str(section.get("key") or ""): section for section in sections}
    summary = " · ".join(
        [
            f"강한 근거 {int(dict(by_key.get('strong') or {}).get('count') or 0)}개",
            f"약한 근거 {int(dict(by_key.get('weak') or {}).get('count') or 0)}개",
            f"충돌 {int(dict(by_key.get('conflicting') or {}).get('count') or 0)}개",
            f"자료 부족 {int(dict(by_key.get('missing') or {}).get('count') or 0)}개",
        ]
    )
    section_html: list[str] = []
    for section in sections:
        items = list(section.get("items") or [])
        item_html: list[str] = []
        if not items:
            item_html.append(
                f'<div class="ov-futures-evidence-empty">{escape(str(section.get("empty_label") or "해당 항목 없음"))}</div>'
            )
        for item in items[:4]:
            contribution = str(item.get("contribution_z") or "-")
            impact = str(item.get("impact_label") or "")
            meta_parts = []
            if contribution and contribution != "-":
                meta_parts.append(f"기여도 {contribution}")
            if impact:
                meta_parts.append(impact)
            item_html.append(
                '<div class="ov-futures-evidence-item">'
                f'<div class="ov-futures-evidence-item-title">{escape(str(item.get("title") or "-"))}</div>'
                f'<div class="ov-futures-evidence-item-meta">{escape(" · ".join(meta_parts) or str(item.get("detail") or ""))}</div>'
                f'<div class="ov-futures-evidence-item-meaning">{escape(str(item.get("meaning") or ""))}</div>'
                "</div>"
            )
        section_html.append(
            '<div class="ov-futures-evidence-section">'
            f'<div class="ov-futures-evidence-section-head">'
            f'<span>{escape(str(section.get("label") or "-"))}</span>'
            f'<strong>{int(section.get("count") or 0)}개</strong>'
            "</div>"
            f'<div class="ov-futures-evidence-description">{escape(str(section.get("description") or ""))}</div>'
            f'{"".join(item_html)}'
            "</div>"
        )
    st.markdown(
        f"""
        <div class="ov-futures-evidence-state">
          <div class="ov-futures-evidence-title">현재 근거 상태</div>
          <div class="ov-futures-evidence-summary">{escape(summary)}</div>
          <div class="ov-futures-evidence-grid">
            {"".join(section_html)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_macro_evidence_groups(groups: dict[str, Any]) -> None:
    cols = st.columns(4, gap="small")
    sections = [
        ("Strong Evidence", groups.get("strong") or [], "positive"),
        ("Weak Evidence", groups.get("weak") or [], "neutral"),
        ("Conflicting Evidence", groups.get("conflicting") or [], "warning"),
        ("Missing Symbols", groups.get("missing") or [], "danger"),
    ]
    for col, (title, items, tone) in zip(cols, sections):
        with col:
            st.markdown(f"**{title}**")
            if items:
                for item in list(items)[:5]:
                    st.caption(str(item))
            else:
                st.caption("None")


def _render_macro_validation_summary(validation: dict[str, Any], *, confidence_label: str | None = None) -> None:
    summary = build_current_scenario_validation_summary(validation, confidence_label=confidence_label)
    if not summary:
        st.info("현재 시나리오 기준 과거 점검 요약이 아직 없습니다.")
        return
    metric_html = "".join(
        '<div class="ov-futures-validation-metric">'
        f'<span>{escape(str(item.get("label") or "-"))}</span>'
        f'<strong>{escape(str(item.get("value") or "-"))}</strong>'
        "</div>"
        for item in list(summary.get("metrics") or [])[:3]
    )
    occurrence = dict(summary.get("occurrence") or {})
    st.markdown(
        f"""
        <div class="ov-futures-validation-summary">
          <div class="ov-futures-validation-head">
            <div>
              <div class="ov-futures-validation-title">{escape(str(summary.get("title") or "과거 점검 요약"))}</div>
              <div class="ov-futures-validation-scenario">현재 시나리오: {escape(str(summary.get("scenario") or "-"))}</div>
            </div>
            <div class="ov-futures-validation-occurrence">
              <span>{escape(str(occurrence.get("label") or "-"))}</span>
              <strong>{escape(str(occurrence.get("value") or "-"))}</strong>
            </div>
          </div>
          <div class="ov-futures-validation-coverage">점검 범위: {escape(str(summary.get("coverage") or "-"))}</div>
          <div class="ov-futures-validation-metrics">{metric_html}</div>
          <div class="ov-futures-validation-copy">{escape(str(summary.get("interpretation") or ""))}</div>
          <div class="ov-futures-validation-effect">{escape(str(summary.get("confidence_effect") or ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_macro_validation_raw_tables(validation: dict[str, Any]) -> None:
    scenario_summary = validation.get("scenario_summary")
    if isinstance(scenario_summary, pd.DataFrame) and not scenario_summary.empty:
        preferred_cols = [
            "Scenario",
            "Occurrence Count",
            "Target Family",
            "Sample 1D",
            "Mean 1D %",
            "Hit Rate 1D %",
            "False Positive 1D %",
            "Sample 5D",
            "Mean 5D %",
            "Hit Rate 5D %",
            "False Positive 5D %",
            "Sample 20D",
            "Mean 20D %",
            "Hit Rate 20D %",
            "False Positive 20D %",
            "Max Adverse 5D %",
        ]
        with st.expander("전체 시나리오 원본 표", expanded=False):
            st.dataframe(
                scenario_summary[[col for col in preferred_cols if col in scenario_summary.columns]],
                width="stretch",
                hide_index=True,
            )
    relationships = validation.get("relationships")
    threshold_sensitivity = validation.get("threshold_sensitivity")
    if isinstance(relationships, pd.DataFrame) and not relationships.empty:
        with st.expander("점수와 이후 수익률 관계 원본", expanded=False):
            st.dataframe(relationships, width="stretch", hide_index=True)
    if isinstance(threshold_sensitivity, pd.DataFrame) and not threshold_sensitivity.empty:
        with st.expander("점수 기준 민감도 원본", expanded=False):
            st.dataframe(threshold_sensitivity, width="stretch", hide_index=True)


def _render_futures_macro_data_management(macro: dict[str, Any]) -> None:
    coverage = dict(macro.get("coverage") or {})
    coverage_label = _futures_daily_coverage_label(coverage)
    latest_daily = _snapshot_value(coverage.get("latest_daily_date"))
    raw_rows = int(coverage.get("raw_rows") or 0)
    st.markdown(
        f"""
        <div class="ov-futures-data-management">
          <div class="ov-futures-data-management-title">자료 관리</div>
          <div class="ov-futures-data-management-grid">
            <div>
              <span>매크로 일봉 기준일</span>
              <strong>{escape(latest_daily)}</strong>
            </div>
            <div>
              <span>daily coverage</span>
              <strong>{escape(coverage_label)}</strong>
            </div>
            <div>
              <span>저장 row</span>
              <strong>{raw_rows:,}</strong>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_market_job_result("overview_futures_daily_ohlcv_result")


def _render_futures_macro_raw_tables(
    *,
    scores: Any,
    components: Any,
    symbols: Any,
    validation: dict[str, Any],
    cautions: list[str],
) -> None:
    _render_futures_section_header("원본 표", "상세 분석자가 확인할 수 있는 계산 원본")
    if isinstance(scores, pd.DataFrame) and not scores.empty:
        with st.expander("원본 점수 표", expanded=False):
            st.dataframe(
                scores.drop(columns=["Tone"], errors="ignore"),
                width="stretch",
                hide_index=True,
            )
    if isinstance(components, pd.DataFrame) and not components.empty:
        with st.expander("구성 선물별 기여", expanded=False):
            st.dataframe(components, width="stretch", hide_index=True)
    if isinstance(symbols, pd.DataFrame) and not symbols.empty:
        with st.expander("선물별 일봉 변화 원본", expanded=False):
            st.dataframe(symbols, width="stretch", hide_index=True)
    _render_macro_validation_raw_tables(validation)
    if cautions:
        with st.expander("해석 주의점", expanded=False):
            for caution in list(dict.fromkeys(cautions)):
                st.caption(caution)


def _render_futures_macro_refresh_controls(*, section_detail: str) -> None:
    refreshed_at = st.session_state.get("overview_futures_macro_daily_refreshed_at")
    reloaded_at = st.session_state.get("overview_futures_macro_reloaded_at")
    status_text = refreshed_at or reloaded_at
    status_label = "최근 일봉 갱신" if refreshed_at else "최근 다시 읽기"
    status_detail = ""
    if status_text:
        status_detail = (
            f'<div class="ov-futures-macro-action-detail">{escape(status_label)}: {escape(str(status_text))}</div>'
        )
    cols = st.columns([1, 0.16, 0.16], gap="small", vertical_alignment="center")
    cols[0].markdown(
        f"""
        <div class="ov-futures-macro-action-copy">
          <div class="ov-futures-macro-action-title">매크로 컨텍스트</div>
          <div class="ov-futures-macro-action-meta">{escape(section_detail)}</div>
          {status_detail}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cols[1].button(
        "일봉 갱신",
        key="overview_futures_macro_tab_daily_refresh",
        use_container_width=True,
        help="저장된 주요 선물 5년 1D OHLCV를 다시 수집하고 매크로 snapshot cache를 비웁니다.",
    ):
        with st.spinner("선물 5년 일봉을 yfinance에서 수집하는 중입니다..."):
            _store_overview_job_result(
                "overview_futures_daily_ohlcv_result",
                _run_futures_daily_ohlcv_action(),
            )
            clear_overview_futures_macro_snapshot_cache()
            st.session_state["overview_futures_macro_daily_refreshed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    if cols[2].button(
        "다시 읽기",
        key="overview_futures_macro_tab_reload",
        use_container_width=True,
        help="수집 job은 실행하지 않고 현재 DB 기준으로 매크로 snapshot cache만 비운 뒤 다시 읽습니다.",
    ):
        clear_overview_futures_macro_snapshot_cache()
        st.session_state["overview_futures_macro_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    st.markdown('<div class="ov-futures-macro-action-rule"></div>', unsafe_allow_html=True)


def _render_futures_macro_panel(*, detail_expanded: bool = False) -> None:
    macro = load_overview_futures_macro_snapshot()
    coverage = dict(macro.get("coverage") or {})
    scores = macro.get("scores")
    components = macro.get("score_components")
    symbols = macro.get("symbols")
    summary = dict(macro.get("summary") or {})
    confidence = dict(macro.get("confidence") or {})
    validation = dict(macro.get("validation") or {})

    _render_futures_macro_refresh_controls(
        section_detail=(
            f"일봉 {coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}개"
            f" · 기준일 {_snapshot_value(coverage.get('latest_daily_date'))}"
        ),
    )
    _render_futures_market_brief(macro)
    _render_weekly_macro_context(dict(macro.get("weekly_context") or {}))
    _render_macro_score_lane(scores)
    warnings = list(macro.get("warnings") or [])
    warnings.extend(str(item) for item in validation.get("warnings") or [])
    if warnings:
        _render_snapshot_warnings({"warnings": [_futures_warning_label(warning) for warning in warnings]})

    cautions = [_macro_caution_label(item) for item in macro.get("cautions") or [] if str(item).strip()]
    cautions.extend(_macro_caution_label(item) for item in validation.get("caveats") or [] if str(item).strip())
    with st.expander("근거 해석 / 원본 데이터", expanded=detail_expanded):
        _render_macro_evidence_reading(list(macro.get("evidence_reading") or []))
        _render_macro_validation_summary(validation, confidence_label=str(confidence.get("label") or ""))
        _render_futures_macro_data_management(macro)
        _render_futures_macro_raw_tables(
            scores=scores,
            components=components,
            symbols=symbols,
            validation=validation,
            cautions=cautions,
        )


def _render_futures_macro_fragment(*, detail_expanded: bool = False) -> None:
    @st.fragment
    def _futures_macro_context_fragment() -> None:
        _render_futures_macro_panel(detail_expanded=detail_expanded)

    _futures_macro_context_fragment()


def _render_futures_macro_tab() -> None:
    st.markdown("### 선물 매크로")
    st.caption("저장된 선물 일봉으로 현재 macro 상태와 과거 점검 근거를 함께 확인합니다.")
    _render_futures_macro_fragment(detail_expanded=True)


def _render_futures_mini_chart_grid(snapshot: dict[str, Any], *, chart_interval: str, chart_scope: str) -> None:
    all_candles = snapshot.get("all_candles")
    rows = snapshot.get("rows")
    symbols = _futures_chart_symbols(snapshot, chart_scope=chart_scope)
    if not symbols:
        message = (
            "선택한 선물에 저장된 candle이 없습니다."
            if chart_scope == "all_with_data" and _futures_selected_symbols(snapshot)
            else "선택된 선물 심볼이 없습니다."
        )
        st.info(message)
        return

    grid_cols = st.columns(3, gap="small")
    for index, symbol in enumerate(symbols):
        metric = _futures_metric_for_symbol(rows, symbol)
        symbol_candles = (
            all_candles[all_candles["Symbol"] == symbol]
            if isinstance(all_candles, pd.DataFrame) and not all_candles.empty and "Symbol" in all_candles
            else pd.DataFrame()
        )
        display_candles = _resample_futures_candles(symbol_candles, interval=chart_interval)
        with grid_cols[index % 3]:
            with st.container(border=True):
                _render_futures_chart_card_header(metric, symbol)
                if display_candles.empty:
                    st.info("표시할 candle이 없습니다.")
                else:
                    st.altair_chart(
                        _build_futures_candlestick_chart(
                            display_candles,
                            height=220,
                            body_size=3,
                            y_title=None,
                        ),
                        width="stretch",
                    )


def _render_futures_live_panel(
    snapshot: dict[str, Any],
    *,
    chart_interval: str,
    lookback_label: str,
    chart_scope: str,
) -> None:
    rows = snapshot.get("rows")
    state_counts = rows["State"].value_counts().to_dict() if isinstance(rows, pd.DataFrame) and not rows.empty and "State" in rows else {}
    _render_futures_section_header(
        "차트 워크스페이스",
        _futures_live_summary_line(
            snapshot,
            chart_interval=chart_interval,
            lookback_label=lookback_label,
            chart_scope=chart_scope,
        ),
    )
    st.markdown(
        f'<div class="ov-futures-chart-question">이 차트에서 확인할 것: {escape(_futures_chart_workspace_question(snapshot, chart_scope=chart_scope))}</div>',
        unsafe_allow_html=True,
    )
    warnings = list(snapshot.get("warnings") or [])
    if warnings:
        _render_snapshot_warnings({"warnings": [_futures_warning_label(warning) for warning in warnings]})
    if state_counts:
        state_html = "".join(
            _futures_chart_metric_chip(_futures_state_label(state), str(int(count)), _futures_state_tone(str(state)))
            for state, count in state_counts.items()
        )
        st.markdown(f'<div class="ov-futures-chart-metrics">{state_html}</div>', unsafe_allow_html=True)

    _render_futures_mini_chart_grid(snapshot, chart_interval=chart_interval, chart_scope=chart_scope)


def _futures_live_summary_line(
    snapshot: dict[str, Any],
    *,
    chart_interval: str,
    lookback_label: str,
    chart_scope: str,
) -> str:
    selected_count = len([symbol for symbol in snapshot.get("symbols") or [] if str(symbol).strip()])
    return (
        f"선택 {selected_count}개 · {_futures_interval_label(chart_interval)} 봉 · {lookback_label} 범위 · "
        f"{_futures_chart_scope_detail(snapshot, chart_scope=chart_scope)}"
    )


def _futures_chart_workspace_question(snapshot: dict[str, Any], *, chart_scope: str) -> str:
    top_move = dict(snapshot.get("top_move") or {})
    if top_move.get("Symbol"):
        return (
            f"{top_move.get('Symbol')}의 단기 움직임이 다른 선택 선물로 확산되는지, "
            f"{_futures_chart_scope_detail(snapshot, chart_scope=chart_scope)} 기준으로 확인합니다."
        )
    return f"{_futures_chart_scope_detail(snapshot, chart_scope=chart_scope)} 기준으로 선택 선물의 단기 흐름을 확인합니다."


def _render_futures_diagnostics(snapshot: dict[str, Any]) -> None:
    rows = snapshot.get("rows")
    candles = snapshot.get("candles")
    latest_run = snapshot.get("latest_run")
    with st.expander("진단 / Provider 근거", expanded=False):
        st.markdown("#### 급변 상태 원본")
        if isinstance(rows, pd.DataFrame) and not rows.empty:
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.info("저장된 선물 OHLCV row가 아직 없습니다. 먼저 1분봉 데이터 갱신을 실행하세요.")
        st.markdown("#### Provider 수집 결과")
        if isinstance(latest_run, dict) and latest_run:
            metric_cols = st.columns(4)
            metric_cols[0].metric("상태", _futures_run_status_label(latest_run.get("status") or "-"))
            metric_cols[1].metric("저장 행", latest_run.get("rows_written") or 0)
            metric_cols[2].metric("처리", f"{latest_run.get('symbols_processed') or 0} / {latest_run.get('symbols_requested') or 0}")
            metric_cols[3].metric("최신 candle", _snapshot_value(latest_run.get("latest_candle_time_utc")))
            st.caption(str(latest_run.get("message") or snapshot.get("source_note") or ""))
        else:
            st.info("기록된 선물 provider 수집 결과가 없습니다.")
        _render_market_job_result("overview_futures_ohlcv_result")
        if isinstance(candles, pd.DataFrame) and not candles.empty:
            st.markdown("#### 선택 선물 candle 원본")
            st.dataframe(candles.tail(80), width="stretch", hide_index=True)


def _render_futures_live_workspace(
    snapshot: dict[str, Any],
    *,
    group: str,
    selected_symbols: list[str],
    selected_symbol: str,
    lookback_label: str,
    chart_interval: str,
    chart_scope: str,
    refresh_mode: str,
) -> None:
    def _load_live_snapshot() -> dict[str, Any]:
        return load_overview_futures_monitor_snapshot(
            group=group,
            symbols=selected_symbols,
            selected_symbol=selected_symbol,
            lookback_minutes=FUTURES_LOOKBACK_OPTIONS[lookback_label],
        )

    if refresh_mode in {"auto_60s", "fast_20s"}:
        cadence = FUTURES_FAST_AUTO_REFRESH_SECONDS if refresh_mode == "fast_20s" else FUTURES_DEFAULT_AUTO_REFRESH_SECONDS

        @st.fragment(run_every=cadence)
        def _futures_live_auto_panel() -> None:
            with st.spinner("선물 1분봉 자동 확인 중입니다..."):
                _store_overview_job_result(
                    "overview_futures_ohlcv_result",
                    _run_futures_ohlcv_action(symbols=selected_symbols, cadence_mode="browser_auto"),
                )
            refreshed_snapshot = _load_live_snapshot()
            _render_futures_live_panel(
                refreshed_snapshot,
                chart_interval=chart_interval,
                lookback_label=lookback_label,
                chart_scope=chart_scope,
            )
            _render_futures_diagnostics(refreshed_snapshot)

        _futures_live_auto_panel()
        return

    _render_futures_live_panel(
        snapshot,
        chart_interval=chart_interval,
        lookback_label=lookback_label,
        chart_scope=chart_scope,
    )
    _render_futures_diagnostics(snapshot)


def _render_futures_monitor_tab() -> None:
    st.markdown("### 선물 모니터")
    st.caption("미국장 / 한국장 전 주요 선물 OHLCV, 단기 급변 상태, 일봉 기반 매크로 맥락을 read-only로 확인합니다.")

    control_cols = st.columns([1.15, 0.78, 0.78, 1.05], gap="small", vertical_alignment="bottom")
    group = str(
        control_cols[0].selectbox(
            "관찰 그룹",
            FUTURES_GROUP_OPTIONS,
            index=0,
            key="overview_futures_watch_group",
            format_func=_futures_group_label,
        )
    )
    lookback_label = str(
        control_cols[1].selectbox(
            "시간 범위",
            list(FUTURES_LOOKBACK_OPTIONS.keys()),
            index=1,
            key="overview_futures_lookback",
        )
    )
    chart_key = "overview_futures_chart_interval"
    if st.session_state.get(chart_key) == "1h":
        st.session_state[chart_key] = "60m"
    chart_interval = str(
        control_cols[2].selectbox(
            "차트 봉",
            FUTURES_CHART_INTERVAL_OPTIONS,
            index=1,
            key=chart_key,
            format_func=_futures_interval_label,
        )
    )
    chart_scope_key = "overview_futures_chart_scope"
    if st.session_state.get(chart_scope_key) not in FUTURES_CHART_SCOPE_OPTIONS:
        st.session_state[chart_scope_key] = "compact_6"
    chart_scope = str(
        control_cols[3].selectbox(
            "차트 범위",
            FUTURES_CHART_SCOPE_OPTIONS,
            key=chart_scope_key,
            format_func=_futures_chart_scope_label,
            help="핵심 6개는 데이터가 있는 선물 중 첫 6개만, 데이터 있는 전체는 저장 candle이 있는 선택 심볼 전체를 표시합니다.",
        )
    )

    preview = load_overview_futures_monitor_snapshot(
        group=group,
        lookback_minutes=FUTURES_LOOKBACK_OPTIONS[lookback_label],
    )
    symbol_options = list(preview.get("symbols") or [])
    if not symbol_options:
        symbol_options = ["ES=F", "NQ=F", "ZN=F", "CL=F", "GC=F", "6J=F"]
    default_symbols = symbol_options[: min(6, len(symbol_options))]
    symbols_key = f"overview_futures_symbols_{group.replace(' ', '_').lower()}"
    current_symbols = st.session_state.get(symbols_key)
    if isinstance(current_symbols, list):
        retained = [symbol for symbol in current_symbols if symbol in symbol_options]
        if retained:
            migration_key = f"{symbols_key}_v3x2_migrated"
            if (
                group == "Pre-open Core"
                and not st.session_state.get(migration_key)
                and len(retained) < min(6, len(symbol_options))
            ):
                retained.extend(symbol for symbol in default_symbols if symbol not in retained)
                st.session_state[symbols_key] = retained
                st.session_state[migration_key] = True
            default_symbols = retained
    with st.expander("관찰 대상 편집", expanded=False):
        selected_symbols = list(
            st.multiselect(
                "선물 선택",
                options=symbol_options,
                default=default_symbols,
                key=symbols_key,
            )
        )
        st.markdown(
            '<div class="ov-futures-control-note">기본 화면은 선택 심볼을 요약해서 보여줍니다. 관찰 대상을 바꿀 때만 이 영역을 열어 조정하세요.</div>',
            unsafe_allow_html=True,
        )
    if not selected_symbols:
        selected_symbols = default_symbols
    selected_symbol = selected_symbols[0]

    snapshot = load_overview_futures_monitor_snapshot(
        group=group,
        symbols=selected_symbols,
        selected_symbol=selected_symbol,
        lookback_minutes=FUTURES_LOOKBACK_OPTIONS[lookback_label],
    )

    mode_options = ["manual", "auto_60s"]
    mode_key = "overview_futures_refresh_mode"
    if st.session_state.get(mode_key) not in mode_options:
        st.session_state[mode_key] = "manual"
    refresh_mode = str(st.session_state.get(mode_key) or "manual")

    _render_futures_workbench_context_bar(
        snapshot=snapshot,
        group=group,
        selected_symbols=selected_symbols,
        lookback_label=lookback_label,
        chart_interval=chart_interval,
        chart_scope=chart_scope,
        refresh_mode=refresh_mode,
    )
    refresh_mode = _render_futures_refresh_module(
        snapshot=snapshot,
        selected_symbols=selected_symbols,
        refresh_mode=refresh_mode,
    )
    _render_futures_watch_strip(snapshot, selected_symbols)

    _render_futures_macro_fragment(detail_expanded=False)
    st.divider()
    _render_futures_live_workspace(
        snapshot,
        group=group,
        selected_symbols=selected_symbols,
        selected_symbol=selected_symbol,
        lookback_label=lookback_label,
        chart_interval=chart_interval,
        chart_scope=chart_scope,
        refresh_mode=refresh_mode,
    )


def _group_trend_selection_key(group_by: str) -> str:
    normalized = str(group_by or "sector").strip().lower()
    return f"overview_group_leadership_trend_groups_{normalized}"


def _remembered_group_trend_groups(group_by: str) -> tuple[str, ...]:
    values = st.session_state.get(_group_trend_selection_key(group_by), [])
    if isinstance(values, str):
        values = [values]
    return tuple(str(value) for value in values if str(value).strip())


def _select_group_trend_groups(*, group_by: str, group_options: list[str]) -> list[str]:
    key = _group_trend_selection_key(group_by)
    clean_options = [str(option) for option in group_options if str(option).strip()]
    option_set = set(clean_options)
    current = st.session_state.get(key, [])
    if isinstance(current, str):
        current = [current]
    retained = [str(value) for value in current if str(value) in option_set]
    if not retained:
        retained = clean_options[: min(5, len(clean_options))]
    if key in st.session_state:
        if list(current) != retained:
            st.session_state[key] = retained
        return list(st.multiselect("Trend Groups", options=clean_options, key=key))
    return list(st.multiselect("Trend Groups", options=clean_options, default=retained, key=key))


def _render_event_refresh_toolbar() -> str:
    render_overview_toolbar_label("일정 타입")
    controls = st.columns([0.95, 2.9, 0.9], gap="small", vertical_alignment="bottom")
    event_options = list(EVENT_TYPE_LABELS.keys())
    event_filter = str(
        controls[0].selectbox(
            "Type",
            event_options,
            index=_option_index(
                event_options,
                st.session_state.get("overview_events_type_filter", "ALL"),
            ),
            format_func=_event_filter_label,
            key="overview_events_type_filter",
        )
    )
    with controls[2].popover(
        "Refresh",
        icon=":material/sync:",
        use_container_width=True,
    ):
        if st.button("FOMC", key="overview_events_refresh_fomc", use_container_width=True):
            current_year = datetime.now().year
            with st.spinner("Collecting FOMC calendar from the official Fed page..."):
                _store_overview_job_result(
                    "overview_fomc_calendar_result",
                    run_overview_fomc_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
        if st.button(
            "Earnings",
            key="overview_events_refresh_earnings",
            use_container_width=True,
            help="Collects upcoming earnings for the latest S&P 500 market movers snapshot.",
        ):
            with st.spinner("Collecting earnings dates from yfinance calendar for latest S&P 500 movers..."):
                _store_overview_job_result(
                    "overview_earnings_calendar_result",
                    run_overview_earnings_calendar(),
                )
            st.rerun()
        if st.button(
            "Macro",
            key="overview_events_refresh_macro",
            use_container_width=True,
            help="Collects CPI, PPI, Employment Situation, and GDP release dates from official schedules.",
        ):
            current_year = datetime.now().year
            with st.spinner("Collecting macro calendar from official BLS and BEA schedules..."):
                _store_overview_job_result(
                    "overview_macro_calendar_result",
                    run_overview_macro_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
    return event_filter


def _select_market_refresh_mode(container: Any, *, auto_supported: bool) -> str:
    key = "overview_market_movers_refresh_mode"
    options = ["manual", "auto"] if auto_supported else ["manual"]
    if st.session_state.get(key) not in options:
        st.session_state[key] = "manual"
    segmented_control = getattr(container, "segmented_control", None)
    if callable(segmented_control):
        selected = segmented_control(
            "갱신 방식",
            options,
            key=key,
            format_func=_market_refresh_mode_label,
            disabled=not auto_supported,
            help="자동 갱신은 현재 선택한 Daily coverage의 일중 스냅샷만 확인합니다.",
        )
    else:
        selected = container.radio(
            "갱신 방식",
            options,
            key=key,
            format_func=_market_refresh_mode_label,
            horizontal=True,
            disabled=not auto_supported,
            help="자동 갱신은 현재 선택한 Daily coverage의 일중 스냅샷만 확인합니다.",
        )
    return str(selected or "manual")


def _render_market_auto_refresh_summary(*, universe_code: str) -> None:
    summary, checked_at = _get_browser_auto_refresh_state(universe_code)
    if summary:
        _render_browser_auto_refresh_timing(
            summary,
            live_countdown=True,
            auto_reload=True,
            key_suffix=f"{universe_code}-{checked_at or 'new'}",
        )
        message = str(summary.get("message") or _browser_auto_refresh_completion_label(summary))
        if message:
            render_market_auto_message(message)
        with st.expander("자동 갱신 세부 정보", expanded=False):
            jobs_due = summary.get("jobs_due")
            jobs_run = summary.get("jobs_run")
            detail_cols = st.columns(3, gap="small")
            detail_cols[0].metric("상태", _auto_refresh_status_label(summary.get("status")))
            detail_cols[1].metric("마지막 확인", str(checked_at or summary.get("finished_at") or "-"))
            detail_cols[2].metric(
                "실행",
                f"{jobs_due if jobs_due is not None else '-'} / {jobs_run if jobs_run is not None else '-'}",
            )
            config = _browser_auto_refresh_job_config(universe_code)
            st.caption(f"Profile: {summary.get('profile') or config['profile']} · Job: {config['job_id']}")
        return

    render_market_auto_waiting_panel(MARKET_COVERAGE_LABELS.get(universe_code, universe_code))


def _render_market_movers_daily_refresh_bar(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> None:
    universe_label = MARKET_COVERAGE_LABELS.get(universe_code, universe_code)
    intraday_result_key = f"overview_{universe_code.lower()}_intraday_result"
    coverage = dict(snapshot.get("coverage") or {})
    state = _get_market_movers_refresh_state(snapshot, universe_code=universe_code, period=period)
    auto_supported = universe_code in BROWSER_AUTO_REFRESH_JOB_CONFIG and period == "daily"

    refresh_state = dict(coverage.get("refresh_state") or {})
    returnable = coverage.get("returnable_count") or 0
    universe_count = coverage.get("universe_count") or 0
    returnable_pct = coverage.get("returnable_pct")
    next_due = refresh_state.get("next_due_in_minutes")
    next_check_text = "now" if next_due in (None, 0) else f"{int(next_due)}m"

    render_market_refresh_status_bar(
        universe_label=universe_label,
        price_mode=coverage.get("price_mode") or "-",
        returnable=returnable,
        universe_count=universe_count,
        returnable_pct=returnable_pct,
        next_check_text=next_check_text,
        state=state,
    )

    control_cols = st.columns([0.95, 1.1, 0.95, 0.95], gap="small", vertical_alignment="bottom")
    selected_mode = _select_market_refresh_mode(control_cols[0], auto_supported=auto_supported)
    if control_cols[1].button(
        "일중 스냅샷 갱신",
        key=f"overview_{universe_code.lower()}_intraday_refresh",
        use_container_width=True,
        type="primary",
        help="Provider quote를 수집해 DB에 새 일중 스냅샷을 저장합니다.",
    ):
        with st.spinner(f"Updating {universe_label} quote snapshot..."):
            _store_overview_job_result(
                intraday_result_key,
                _run_market_intraday_snapshot_action(
                    universe_code=universe_code,
                    universe_limit=universe_limit,
                ),
            )
        st.rerun()
    if universe_code == "SP500" and control_cols[2].button(
        "유니버스 갱신",
        key="overview_sp500_universe_refresh",
        use_container_width=True,
    ):
        with st.spinner("Refreshing S&P 500 universe..."):
            _store_overview_job_result("overview_sp500_universe_result", run_overview_sp500_universe())
        st.rerun()
    if universe_code == "NASDAQ" and control_cols[2].button(
        "Nasdaq 목록 갱신",
        key="overview_nasdaq_symbol_directory_refresh",
        use_container_width=True,
        help="Nasdaq Symbol Directory current snapshot을 lifecycle evidence table에 저장합니다.",
    ):
        with st.spinner("Refreshing Nasdaq Symbol Directory current snapshot..."):
            _store_overview_job_result(
                "overview_nasdaq_symbol_directory_result",
                _run_nasdaq_symbol_directory_action(),
            )
        st.rerun()
    if universe_code not in {"SP500", "NASDAQ"}:
        control_cols[2].caption("Top universe는 market-cap ranked asset profile 기준입니다.")
    if control_cols[3].button(
        "화면 새로고침",
        key=f"overview_{universe_code.lower()}_market_movers_reload",
        use_container_width=True,
    ):
        st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()

    if selected_mode == "auto" and auto_supported:
        _render_market_auto_refresh_summary(universe_code=universe_code)
    elif refresh_state.get("recommended_action"):
        render_market_auto_message(refresh_state.get("recommended_action"))

    if universe_code == "SP500":
        _render_market_job_result("overview_sp500_universe_result")
    if universe_code == "NASDAQ":
        st.caption(
            "Nasdaq coverage는 Nasdaq Symbol Directory current listing snapshot 기준입니다. "
            "Nasdaq Composite 또는 Nasdaq-100 historical membership proof가 아닙니다."
        )
        _render_market_job_result("overview_nasdaq_symbol_directory_result")
    _render_market_job_result(intraday_result_key)


def _market_movers_eod_refresh_state(snapshot: dict[str, Any], *, period: str) -> dict[str, str | bool]:
    status = str(snapshot.get("status") or "").upper()
    period_label = _market_mover_period_label(period)
    if status == "OK":
        return {
            "dot_color": OVERVIEW_COLOR_POSITIVE,
            "label": "EOD DB",
            "detail": f"{period_label} 가격 이력",
            "refresh_due": False,
        }
    return {
        "dot_color": OVERVIEW_COLOR_WARNING,
        "label": "갱신 필요",
        "detail": f"{period_label} 가격 이력 확인",
        "refresh_due": True,
    }


def _render_market_movers_eod_refresh_bar(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> None:
    period_label = _market_mover_period_label(period)
    universe_label = MARKET_COVERAGE_LABELS.get(universe_code, universe_code)
    eod_result_key = f"overview_{universe_code.lower()}_{period}_eod_history_result"
    coverage = dict(snapshot.get("coverage") or {})
    returnable = coverage.get("returnable_count") or 0
    universe_count = coverage.get("universe_count") or 0
    returnable_pct = coverage.get("returnable_pct")

    render_market_refresh_status_bar(
        universe_label=universe_label,
        price_mode=coverage.get("price_mode") or "EOD DB",
        returnable=returnable,
        universe_count=universe_count,
        returnable_pct=returnable_pct,
        next_check_text="수동",
        state=_market_movers_eod_refresh_state(snapshot, period=period),
    )
    st.caption(
        f"{period_label}는 저장된 EOD 가격 이력을 기준으로 계산합니다. "
        "최신 기간을 보려면 가격 이력을 수동 갱신하세요."
    )
    if universe_code == "NASDAQ":
        st.warning(
            "Nasdaq-listed 가격 이력 갱신은 Nasdaq Symbol Directory current snapshot 기준의 큰 universe를 수집하므로 "
            "provider 호출과 실행 시간이 커질 수 있습니다.",
        )
        st.caption("목록이 비어 있으면 Daily의 `Nasdaq 목록 갱신` 또는 Ingestion의 Nasdaq Symbol Directory 수집을 먼저 실행하세요.")
    elif universe_code != "SP500":
        st.warning(
            f"{universe_label} 가격 이력 갱신은 market-cap ranked asset profile 기준의 큰 universe를 수집하므로 "
            "provider 호출과 실행 시간이 커질 수 있습니다.",
        )

    control_cols = st.columns([1.05, 0.95, 2.3], gap="small", vertical_alignment="bottom")
    if control_cols[0].button(
        "가격 이력 갱신",
        key=f"overview_{universe_code.lower()}_{period}_eod_history_refresh",
        use_container_width=True,
        type="primary",
        help="기존 OHLCV 수집 pipeline으로 finance_price.nyse_price_history의 EOD 1d 가격 이력을 갱신합니다.",
    ):
        with st.spinner(f"{universe_label} {period_label} EOD 가격 이력을 수집하는 중입니다..."):
            _store_overview_job_result(
                eod_result_key,
                _run_market_movers_eod_history_action(
                    universe_code=universe_code,
                    universe_limit=universe_limit,
                    period=period,
                ),
            )
        st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    if control_cols[1].button(
        "화면 새로고침",
        key=f"overview_{universe_code.lower()}_{period}_market_movers_reload",
        use_container_width=True,
    ):
        st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    control_cols[2].caption("자동 분당 갱신은 Daily 일중 스냅샷에만 적용됩니다.")

    _render_market_job_result(eod_result_key)


def _render_market_movers_refresh_bar(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> None:
    if period == "daily":
        _render_market_movers_daily_refresh_bar(
            snapshot,
            universe_code=universe_code,
            universe_limit=universe_limit,
            period=period,
        )
        return
    _render_market_movers_eod_refresh_bar(
        snapshot,
        universe_code=universe_code,
        universe_limit=universe_limit,
        period=period,
    )


def _rank_token(value: Any, fallback: int) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(fallback)
    if pd.isna(numeric):
        return str(fallback)
    if numeric.is_integer():
        return str(int(numeric))
    return str(value)


MARKET_MOVER_UI_LABELS = {
    "Source": "출처",
    "Open": "열기",
    "Search Query": "검색어",
    "Purpose": "용도",
    "Title": "제목",
    "Published At": "게시 시각",
    "Snippet": "단서",
    "Form": "양식",
    "Filing Date": "공시일",
}
MARKET_MOVER_SUMMARY_LABELS = {
    "Symbol": "종목",
    "Name": "회사명",
    "Sector": "섹터",
    "Industry": "산업",
    "Market Cap": "시가총액",
    "Period": "기간",
    "Coverage": "범위",
    "Rank Type": "순위 기준",
    "Rank": "순위",
    "Return %": "수익률",
    "Previous Return %": "직전 수익률",
    "Momentum Delta": "모멘텀 변화",
    "Volume": "거래량",
    "Dollar Volume": "거래대금",
}
MARKET_MOVER_CONTEXT_VALUE_LABELS = {
    "Daily": "일간",
    "Weekly": "주간",
    "Monthly": "월간",
    "Yearly": "연간",
    "Return Rank": "수익률 순위",
    "Volume Rank": "거래량 순위",
    "Unknown": "미확인",
}


def _market_mover_display_value(value: Any) -> Any:
    if isinstance(value, str):
        return MARKET_MOVER_CONTEXT_VALUE_LABELS.get(value, value)
    return value


def _market_mover_catalyst_candidates(rows: pd.DataFrame, volume_rows: pd.DataFrame) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    def append_from_frame(frame: pd.DataFrame, *, rank_source: str, id_prefix: str, label_prefix: str) -> None:
        if not isinstance(frame, pd.DataFrame) or frame.empty:
            return
        for offset, (_, row) in enumerate(frame.iterrows(), start=1):
            symbol = str(row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            rank = _rank_token(row.get("Rank"), offset)
            candidate_id = f"{id_prefix}:{rank}:{symbol}"
            if candidate_id in seen:
                continue
            seen.add(candidate_id)
            name = str(row.get("Name") or "").strip() or symbol
            candidates.append(
                {
                    "id": candidate_id,
                    "symbol": symbol,
                    "name": name,
                    "rank": rank,
                    "rank_source": rank_source,
                    "mover": row.to_dict(),
                    "label": f"{label_prefix} #{rank} · {symbol} · {name}",
                }
            )

    append_from_frame(rows, rank_source="Return Rank", id_prefix="return", label_prefix="수익률")
    append_from_frame(volume_rows, rank_source="Volume Rank", id_prefix="volume", label_prefix="거래량")
    return candidates


def _market_mover_open_link_column_config(column_name: str = "열기") -> dict[str, Any]:
    return {column_name: st.column_config.LinkColumn(column_name, display_text="열기")}


def _market_mover_metadata_column_config() -> dict[str, Any]:
    return _market_mover_open_link_column_config("열기")


def _market_mover_research_link_column_config() -> dict[str, Any]:
    return _market_mover_open_link_column_config("열기")


def _market_mover_open_link_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return pd.DataFrame(columns=[MARKET_MOVER_UI_LABELS.get(column, column) for column in columns])
    display = frame.copy()
    if "Open" not in display.columns:
        display["Open"] = display["URL"] if "URL" in display.columns else ""
    out = pd.DataFrame(index=display.index)
    for column in columns:
        display_label = MARKET_MOVER_UI_LABELS.get(column, column)
        out[display_label] = display[column] if column in display.columns else ""
    return out.reset_index(drop=True)


def _market_mover_external_search_table_model(links: pd.DataFrame) -> dict[str, Any]:
    return {
        "label": "외부 검색",
        "expanded": False,
        "rows": _market_mover_open_link_frame(links, ["Source", "Open", "Search Query", "Purpose"]),
        "column_config": _market_mover_research_link_column_config(),
    }


def _market_mover_tone_style(tone: str) -> tuple[str, str, str]:
    if tone == "success":
        return OVERVIEW_COLOR_POSITIVE, "rgba(24, 130, 84, 0.10)", "rgba(24, 130, 84, 0.28)"
    if tone == "warning":
        return OVERVIEW_COLOR_WARNING, "rgba(214, 137, 16, 0.10)", "rgba(214, 137, 16, 0.30)"
    if tone == "error":
        return OVERVIEW_COLOR_DANGER, "rgba(197, 48, 48, 0.10)", "rgba(197, 48, 48, 0.30)"
    return OVERVIEW_COLOR_TEXT, OVERVIEW_COLOR_SURFACE_SUBTLE, OVERVIEW_COLOR_BORDER


def _market_mover_summary_group_html(title: str, items: list[tuple[str, Any]]) -> str:
    facts: list[str] = []
    for label, value in items:
        display_label = MARKET_MOVER_SUMMARY_LABELS.get(str(label), str(label))
        display_value = str(_market_mover_display_value(value) if value not in (None, "") else "-")
        facts.append(
            (
                '<div style="min-width:0;">'
                f'<div style="font-size:0.72rem;color:{OVERVIEW_COLOR_TEXT_MUTED};font-weight:700;margin-bottom:0.15rem;">'
                f'{escape(display_label)}'
                "</div>"
                '<div style="font-size:0.95rem;font-weight:750;line-height:1.22;overflow-wrap:anywhere;">'
                f'{escape(display_value)}'
                "</div>"
                "</div>"
            )
        )
    return (
        '<div style="min-width:0;">'
        f'<div style="font-size:0.75rem;color:{OVERVIEW_COLOR_PRIMARY};font-weight:800;'
        'text-transform:uppercase;margin-bottom:0.55rem;">'
        f'{escape(title)}</div>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));'
        f'gap:0.7rem 0.9rem;">{"".join(facts)}</div>'
        "</div>"
    )


def _render_market_mover_movement_summary_header(
    identity: dict[str, Any],
    context: dict[str, Any],
    movement: dict[str, Any],
) -> None:
    groups = [
        _market_mover_summary_group_html(
            "기본 정보",
            [
                ("Symbol", identity.get("Symbol")),
                ("Name", identity.get("Name")),
                ("Sector", identity.get("Sector")),
                ("Industry", identity.get("Industry")),
                ("Market Cap", _compact_number(identity.get("Market Cap"), prefix="$")),
            ],
        ),
        _market_mover_summary_group_html(
            "순위 맥락",
            [
                ("Period", context.get("Period")),
                ("Coverage", context.get("Coverage")),
                ("Rank Type", context.get("Rank Type")),
                ("Rank", context.get("Rank")),
            ],
        ),
        _market_mover_summary_group_html(
            "움직임",
            [
                ("Return %", _format_signed(movement.get("Return %"))),
                ("Previous Return %", _format_signed(movement.get("Previous Return %"))),
                ("Momentum Delta", _format_signed(movement.get("Momentum Delta pp"), suffix=" pp")),
                ("Volume", _compact_number(movement.get("Volume"))),
                ("Dollar Volume", _compact_number(movement.get("Dollar Volume"), prefix="$")),
            ],
        ),
    ]
    st.markdown(
        (
            f'<div style="border:1px solid {OVERVIEW_COLOR_BORDER};border-radius:8px;'
            f'background:{OVERVIEW_COLOR_SURFACE};padding:1rem;margin:0.55rem 0 0.85rem;">'
            '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));'
            f'gap:1.1rem 1.25rem;">{"".join(groups)}</div></div>'
        ),
        unsafe_allow_html=True,
    )


def _render_market_mover_metadata_status_strip(metadata: dict[str, Any]) -> None:
    strip = build_market_mover_metadata_status_strip(metadata)
    blocks: list[str] = []
    for item in strip.get("items") or []:
        tone = str(item.get("tone") or "neutral")
        color, background, border = _market_mover_tone_style(tone)
        blocks.append(
            (
                f'<div style="border:1px solid {border};background:{background};border-radius:8px;'
                'padding:0.7rem 0.8rem;min-width:0;">'
                f'<div style="font-size:0.72rem;color:{OVERVIEW_COLOR_TEXT_MUTED};font-weight:800;'
                f'margin-bottom:0.25rem;">{escape(str(item.get("label") or ""))}</div>'
                f'<div style="font-size:0.92rem;color:{color};font-weight:800;line-height:1.2;'
                f'overflow-wrap:anywhere;">{escape(str(item.get("value") or "-"))}</div>'
                "</div>"
            )
        )
    st.markdown(
        (
            '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));'
            f'gap:0.65rem;margin:0.1rem 0 0.8rem;">{"".join(blocks)}</div>'
        ),
        unsafe_allow_html=True,
    )


def _market_mover_metadata_messages(metadata: dict[str, Any]) -> list[str]:
    return [str(message).strip() for message in metadata.get("messages") or [] if str(message).strip()]


def _market_mover_lane_failed(messages: list[str], provider: str) -> bool:
    normalized = str(provider or "").strip().lower()
    prefixes = {
        "news": ("news metadata lookup failed:", "뉴스 메타데이터 조회 실패:"),
        "korean news": ("korean news metadata lookup failed:", "한국어 뉴스 메타데이터 조회 실패:"),
        "korean_news": ("korean news metadata lookup failed:", "한국어 뉴스 메타데이터 조회 실패:"),
        "sec": ("sec metadata lookup failed:", "sec 메타데이터 조회 실패:"),
    }.get(normalized, (f"{normalized} metadata lookup failed:",))
    return any(message.lower().startswith(prefix) for message in messages for prefix in prefixes)


def _render_market_mover_metadata_lane(
    title: str,
    caption: str,
    frame: pd.DataFrame,
    columns: list[str],
    *,
    failed: bool,
    empty_message: str,
) -> None:
    st.markdown(f"###### {title}")
    st.caption(caption)
    display = _market_mover_open_link_frame(frame, columns)
    if failed:
        st.error(f"{title} 조회가 실패했습니다. 상태 메시지를 참고하세요.")
    if not display.empty:
        st.dataframe(
            display,
            width="stretch",
            hide_index=True,
            column_config=_market_mover_metadata_column_config(),
        )
    elif not failed:
        st.info(empty_message)


def _render_market_mover_investigation_leads(metadata: dict[str, Any], links: pd.DataFrame, *, metadata_key: str) -> None:
    status = str(metadata.get("status") or "NOT_REQUESTED").strip().upper()
    messages = _market_mover_metadata_messages(metadata)
    if messages:
        for message in messages:
            st.caption(message)

    news = metadata.get("news")
    if not isinstance(news, pd.DataFrame):
        news = pd.DataFrame(columns=["Title", "Source", "Published At", "URL"])
    korean_news = metadata.get("korean_news")
    if not isinstance(korean_news, pd.DataFrame):
        korean_news = pd.DataFrame(columns=["Title", "Source", "Published At", "Snippet", "URL"])
    sec_filings = metadata.get("sec_filings")
    if isinstance(sec_filings, pd.DataFrame):
        sec_filings = sort_market_mover_sec_filings_by_form_priority(sec_filings)
    else:
        sec_filings = pd.DataFrame(columns=["Form", "Filing Date", "Title", "URL"])

    not_requested_message = "간단 메타데이터 조회를 실행하면 이번 세션에만 이 영역이 채워집니다."
    _render_market_mover_metadata_lane(
        "뉴스 메타데이터",
        "헤드라인 메타데이터만 표시합니다. 기사 본문, AI 요약, 감성 점수, 원인 판정은 수집하지 않습니다.",
        news,
        ["Title", "Source", "Published At", "Open"],
        failed=_market_mover_lane_failed(messages, "News"),
        empty_message=not_requested_message if status == "NOT_REQUESTED" else "간단 뉴스 메타데이터가 반환되지 않았습니다.",
    )
    _render_market_mover_metadata_lane(
        "한국어 뉴스",
        "Google News KR RSS metadata/snippet만 표시합니다. 기사 본문, AI 요약, 감성 점수, 원인 판정은 수집하지 않습니다.",
        korean_news,
        ["Title", "Source", "Published At", "Snippet", "Open"],
        failed=_market_mover_lane_failed(messages, "Korean News"),
        empty_message=not_requested_message if status == "NOT_REQUESTED" else "Google News KR RSS 한국어 뉴스 메타데이터가 반환되지 않았습니다.",
    )
    _render_market_mover_metadata_lane(
        "SEC 공시",
        "공식 공시 메타데이터 단서입니다. 양식 우선순위는 표시 순서에만 쓰이며 공시 본문은 파싱하지 않습니다.",
        sec_filings,
        ["Form", "Filing Date", "Title", "Open"],
        failed=_market_mover_lane_failed(messages, "SEC"),
        empty_message=not_requested_message if status == "NOT_REQUESTED" else "간단 SEC 공시 메타데이터가 반환되지 않았습니다.",
    )

    table_model = _market_mover_external_search_table_model(links)
    if isinstance(table_model.get("rows"), pd.DataFrame) and not table_model["rows"].empty:
        with st.expander(str(table_model["label"]), expanded=bool(table_model["expanded"])):
            st.caption("외부 검색 시작점입니다. 링크를 열어도 앱이 원문을 조회, 파싱, 저장하지 않습니다.")
            st.dataframe(
                table_model["rows"],
                width="stretch",
                hide_index=True,
                column_config=table_model["column_config"],
            )


def _render_market_mover_why_it_moved_panel(
    rows: pd.DataFrame,
    volume_rows: pd.DataFrame,
    *,
    universe_code: str,
    period: str,
) -> None:
    candidates = _market_mover_catalyst_candidates(rows, volume_rows)
    if not candidates:
        return

    st.markdown("#### Why It Moved")
    st.caption("수동 조사 패널입니다. 자동 원인 판정, AI 요약, 원문 수집, DB 저장은 실행하지 않습니다.")
    candidate_by_id = {item["id"]: item for item in candidates}
    option_ids = list(candidate_by_id)
    selection_key = "overview_market_mover_why_it_moved_selection"
    if st.session_state.get(selection_key) not in candidate_by_id:
        st.session_state[selection_key] = option_ids[0]
    selected_id = str(
        st.selectbox(
            "종목",
            option_ids,
            format_func=lambda value: candidate_by_id.get(str(value), {}).get("label", str(value)),
            key=selection_key,
        )
    )
    selected = candidate_by_id[selected_id]
    mover = dict(selected.get("mover") or {})
    mover["Rank"] = selected.get("rank")
    mover["Symbol"] = selected.get("symbol")
    mover["Name"] = selected.get("name")
    model = build_market_mover_why_it_moved_read_model(
        mover=mover,
        period=period,
        coverage=universe_code,
        rank_source=str(selected["rank_source"]),
    )
    identity = model.get("identity") or {}
    context = model.get("context") or {}
    movement = model.get("movement") or {}

    links = model.get("links")
    if not isinstance(links, pd.DataFrame):
        links = pd.DataFrame(columns=["Source", "URL", "Search Query", "Purpose"])

    _render_market_mover_movement_summary_header(identity, context, movement)

    metadata_store_key = "overview_market_mover_why_it_moved_metadata"
    metadata_store = st.session_state.get(metadata_store_key)
    if not isinstance(metadata_store, dict):
        metadata_store = {}
        st.session_state[metadata_store_key] = metadata_store
    metadata_key = f"{universe_code}:{period}:{selected_id}"
    current_metadata = metadata_store.get(metadata_key) or model.get("metadata") or {}

    status_container = st.container()
    if st.button("간단 메타데이터 조회", key=f"overview_market_mover_why_it_moved_fetch_{metadata_key}"):
        with st.spinner(f"{identity.get('Symbol') or selected.get('symbol')} 간단 메타데이터를 조회하는 중..."):
            current_metadata = fetch_market_mover_compact_metadata(
                str(identity.get("Symbol") or selected.get("symbol") or ""),
                name=str(identity.get("Name") or selected.get("name") or ""),
            )
            metadata_store[metadata_key] = current_metadata
            st.session_state[metadata_store_key] = metadata_store
    with status_container:
        _render_market_mover_metadata_status_strip(dict(current_metadata))

    st.markdown("##### 조사 단서")
    _render_market_mover_investigation_leads(dict(current_metadata), links, metadata_key=metadata_key)


def _render_market_movers_snapshot_panel(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> None:
    render_market_snapshot_meta_strip(_snapshot_status_items(snapshot))
    _render_snapshot_warnings(snapshot)
    _render_missing_diagnostics(snapshot, universe_code=universe_code, period=period)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed market mover rows are not available for the selected controls.")
        st.markdown("#### Why It Moved")
        st.info("Market mover rows are needed before Why It Moved can be shown.")
        st.caption("선택한 coverage에 ranking row가 생기면 조사 패널을 사용할 수 있습니다.")
        return
    volume_rows = snapshot.get("volume_rows")
    if not isinstance(volume_rows, pd.DataFrame) or volume_rows.empty:
        volume_rows = rows

    left, right = st.columns([0.95, 1.25], gap="medium")
    with left:
        return_tab, volume_tab, sector_tab = st.tabs(["Return Rank", "Volume Rank", "Sector Pulse"])
        with return_tab:
            st.altair_chart(_build_return_bar_chart(rows), width="stretch")
        with volume_tab:
            st.altair_chart(_build_volume_bar_chart(volume_rows), width="stretch")
        with sector_tab:
            st.altair_chart(_build_market_mover_sector_chart(rows), width="stretch")
    with right:
        return_table_tab, volume_table_tab = st.tabs(["Return Table", "Volume Table"])
        with return_table_tab:
            st.dataframe(
                rows,
                width="stretch",
                height=_market_mover_chart_height(len(rows)) + MARKET_MOVER_TABLE_CHROME_HEIGHT,
                hide_index=True,
            )
        with volume_table_tab:
            st.dataframe(
                volume_rows,
                width="stretch",
                height=_market_mover_chart_height(len(volume_rows)) + MARKET_MOVER_TABLE_CHROME_HEIGHT,
                hide_index=True,
            )
    _render_market_mover_why_it_moved_panel(
        rows,
        volume_rows,
        universe_code=universe_code,
        period=period,
    )


def _render_market_movers_tab() -> None:
    st.markdown("### Market Movers")
    controls = _render_market_movers_controls()

    reloaded_at = st.session_state.get("overview_market_movers_reloaded_at")
    if reloaded_at:
        st.caption(f"Last DB snapshot reload request: {reloaded_at}")
    if controls.period == "daily":
        st.caption(
            "Daily는 저장된 quote snapshot을 previous close와 비교합니다. 갱신 방식은 아래 데이터 갱신 영역에서 선택합니다."
        )

    if controls.coverage not in BROWSER_AUTO_REFRESH_JOB_CONFIG or controls.period != "daily":
        st.session_state["overview_market_movers_refresh_mode"] = "manual"
    auto_refresh_enabled = (
        controls.coverage in BROWSER_AUTO_REFRESH_JOB_CONFIG
        and controls.period == "daily"
        and st.session_state.get("overview_market_movers_refresh_mode") == "auto"
    )

    if auto_refresh_enabled:
        @st.fragment(run_every=BROWSER_AUTO_REFRESH_SECONDS)
        def _market_movers_auto_refresh_panel() -> None:
            summary, checked_at = _get_browser_auto_refresh_state(controls.coverage)
            if _should_run_browser_auto_refresh_check(summary, checked_at=str(checked_at or "")):
                coverage_label = MARKET_COVERAGE_LABELS.get(controls.coverage, controls.coverage)
                with st.spinner(f"{coverage_label} 자동 갱신 조건을 확인하는 중입니다..."):
                    _run_browser_auto_refresh_check(universe_code=controls.coverage)
            snapshot = _load_market_movers_snapshot(
                universe_code=controls.coverage,
                universe_limit=controls.universe_limit,
                period=controls.period,
                top_n=controls.top_n,
                sector=controls.sector,
            )
            _render_market_movers_refresh_bar(
                snapshot,
                universe_code=controls.coverage,
                universe_limit=controls.universe_limit,
                period=controls.period,
            )
            _render_market_movers_snapshot_panel(
                snapshot,
                universe_code=controls.coverage,
                period=controls.period,
            )

        _market_movers_auto_refresh_panel()
    else:
        snapshot = _load_market_movers_snapshot(
            universe_code=controls.coverage,
            universe_limit=controls.universe_limit,
            period=controls.period,
            top_n=controls.top_n,
            sector=controls.sector,
        )
        _render_market_movers_refresh_bar(
            snapshot,
            universe_code=controls.coverage,
            universe_limit=controls.universe_limit,
            period=controls.period,
        )
        _render_market_movers_snapshot_panel(
            snapshot,
            universe_code=controls.coverage,
            period=controls.period,
        )


def _render_sector_industry_tab() -> None:
    st.markdown("### Sector / Industry")
    st.caption("시장 맥락의 섹터 / 업종 확산, 리더십, 집중도를 확인하는 상세 근거입니다.")
    controls = _render_group_leadership_controls()

    loading_label = (
        "Sector / Industry leadership 계산 중..."
        if controls.group_by == "sector"
        else "Industry leadership 계산 중..."
    )
    with st.spinner(f"{loading_label} DB 가격, 그룹 랭킹, 트렌드, 티커 리더를 계산하고 있습니다."):
        snapshot = load_overview_group_leadership_snapshot(
            universe_limit=controls.universe_limit,
            universe_code=controls.coverage,
            group_by=controls.group_by,
            period=controls.period,
            top_n=controls.top_n,
            min_group_size=controls.min_group_size,
            trend_groups=_remembered_group_trend_groups(controls.group_by),
        )
    _render_snapshot_status_cards(snapshot)
    _render_snapshot_warnings(snapshot)
    coverage = dict(snapshot.get("coverage") or {})
    date_window = dict(snapshot.get("date_window") or {})
    price_mode = coverage.get("price_mode") or "EOD DB"
    start_value = date_window.get("start_date") or "-"
    end_value = coverage.get("snapshot_time_utc") or date_window.get("effective_end_date") or date_window.get("end_date") or "-"
    st.caption(f"Return Window: {start_value} -> {end_value} · Price Mode: {price_mode}")
    render_breadth_heatmap_summary(load_overview_breadth_heatmap_summary(snapshot))

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed group leadership rows are not available for the selected controls.")
        return
    trend_rows = snapshot.get("trend_rows")
    ticker_leader_rows = snapshot.get("ticker_leader_rows")
    st.markdown("#### Latest Breadth Heatmap")
    st.altair_chart(_build_group_leadership_heatmap(rows), width="stretch")
    st.markdown("#### Latest Ranking")
    insight_cards = _group_leadership_insight_cards(
        rows,
        trend_rows if isinstance(trend_rows, pd.DataFrame) else None,
    )
    if insight_cards:
        render_status_card_grid(insight_cards)
    st.altair_chart(_build_group_leadership_rank_chart(rows), width="stretch")
    if isinstance(trend_rows, pd.DataFrame) and not trend_rows.empty:
        st.markdown("#### Trend")
        group_options = (
            pd.concat(
                [
                    rows["Group"].dropna().astype(str),
                    trend_rows["Group"].dropna().astype(str),
                ],
                ignore_index=True,
            )
            .drop_duplicates()
            .tolist()
        )
        selected_groups = _select_group_trend_groups(
            group_by=controls.group_by,
            group_options=group_options,
        )
        visible_trend_rows = (
            trend_rows[trend_rows["Group"].astype(str).isin(selected_groups)]
            if selected_groups
            else trend_rows.iloc[0:0]
        )
        heatmap_tab, line_tab, delta_tab = st.tabs(["Heatmap", "Line", "Latest Delta"])
        with heatmap_tab:
            st.altair_chart(_build_group_leadership_trend_heatmap(visible_trend_rows), width="stretch")
        with line_tab:
            st.altair_chart(_build_group_leadership_trend_chart(visible_trend_rows), width="stretch")
        with delta_tab:
            st.altair_chart(_build_group_leadership_delta_chart(visible_trend_rows), width="stretch")
    if isinstance(ticker_leader_rows, pd.DataFrame) and not ticker_leader_rows.empty:
        st.markdown("#### Positive Group Detail")
        positive_group_set = set(ticker_leader_rows["Group"].dropna().astype(str).tolist())
        positive_groups = [
            group_name
            for group_name in rows["Group"].dropna().astype(str).drop_duplicates().tolist()
            if group_name in positive_group_set
        ]
        if not positive_groups:
            positive_groups = ticker_leader_rows["Group"].dropna().astype(str).drop_duplicates().tolist()
        detail_controls = st.columns([1.4, 0.7], gap="small", vertical_alignment="bottom")
        selected_detail_group = str(
            detail_controls[0].selectbox(
                "Positive Group",
                positive_groups,
                index=0,
                key=(
                    "overview_group_leadership_positive_group_"
                    f"{controls.coverage}_{controls.group_by}_{controls.period}_{controls.top_n}_{controls.min_group_size}"
                ),
            )
        )
        ticker_top_n = int(
            detail_controls[1].selectbox(
                "Ticker Top N",
                [5, 10, 15, 20],
                index=1,
                key=(
                    "overview_group_leadership_ticker_top_n_"
                    f"{controls.coverage}_{controls.group_by}_{controls.period}_{controls.top_n}_{controls.min_group_size}"
                ),
            )
        )
        detail_rows = ticker_leader_rows[
            ticker_leader_rows["Group"].astype(str) == selected_detail_group
        ].copy()
        detail_rows = detail_rows.sort_values("Rank").head(ticker_top_n)
        detail_bar, detail_share = st.columns([1.25, 0.75], gap="medium")
        with detail_bar:
            st.altair_chart(_build_group_ticker_leader_bar_chart(detail_rows), width="stretch")
        with detail_share:
            st.altair_chart(
                _build_group_ticker_contribution_donut(
                    ticker_leader_rows[
                        ticker_leader_rows["Group"].astype(str) == selected_detail_group
                    ],
                    top_n=ticker_top_n,
                ),
                width="stretch",
            )
    with st.expander("상세 표", expanded=False):
        st.dataframe(rows, width="stretch", hide_index=True)
        if isinstance(trend_rows, pd.DataFrame) and not trend_rows.empty:
            st.dataframe(trend_rows, width="stretch", hide_index=True)
        if isinstance(ticker_leader_rows, pd.DataFrame) and not ticker_leader_rows.empty:
            st.dataframe(ticker_leader_rows, width="stretch", hide_index=True)


def _sentiment_status_tone(status: Any) -> str:
    normalized = str(status or "").upper()
    if normalized == "OK":
        return "positive"
    if normalized in {"REVIEW", "DUE"}:
        return "warning"
    if normalized in {"MISSING", "ERROR", "STALE"}:
        return "danger"
    return "neutral"


def _sentiment_tone(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"positive", "warning", "danger", "neutral"}:
        return normalized
    return _sentiment_status_tone(value)


def _sentiment_trend_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        rows = pd.DataFrame([{"Date": date.today().isoformat(), "Series": "No Data", "Value": 0.0, "Source": "-"}])
    chart_rows = rows.copy()
    chart_rows["Date Parsed"] = pd.to_datetime(chart_rows.get("Date"), errors="coerce")
    chart_rows["Value"] = pd.to_numeric(chart_rows.get("Value"), errors="coerce")
    chart_rows = chart_rows.dropna(subset=["Date Parsed", "Value"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Date Parsed": pd.Timestamp(date.today()), "Series": "No Data", "Value": 0.0, "Source": "-"}])
    return (
        alt.Chart(chart_rows)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("Date Parsed:T", title=None, axis=alt.Axis(format="%b %d", labelAngle=-35)),
            y=alt.Y("Value:Q", title=None),
            color=alt.Color(
                "Series:N",
                title=None,
                legend=alt.Legend(orient="bottom"),
                scale=alt.Scale(range=OVERVIEW_SERIES_COLORS),
            ),
            tooltip=["Date Parsed:T", "Series:N", "Value:Q", "Source:N"],
        )
        .properties(height=260)
    )


def _sentiment_component_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        rows = pd.DataFrame([{"Series": "No Data", "Score": 0.0, "Rating": "-", "Status": "-"}])
    chart_rows = rows.copy()
    chart_rows["Score"] = pd.to_numeric(chart_rows.get("Score"), errors="coerce").fillna(0.0)
    chart_rows["Bar Color"] = chart_rows["Score"].map(
        lambda value: OVERVIEW_COLOR_DANGER
        if value < 25
        else OVERVIEW_COLOR_WARNING
        if value < 45
        else OVERVIEW_COLOR_NEUTRAL
        if value < 55
        else OVERVIEW_COLOR_POSITIVE
        if value < 75
        else OVERVIEW_COLOR_PRIMARY
    )
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Score:Q", title=None, scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Series:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180)),
            color=alt.Color("Bar Color:N", scale=None, legend=None),
            tooltip=["Series:N", "Score:Q", "Rating:N", "Status:N"],
        )
        .properties(height=max(220, min(390, len(chart_rows) * 38)))
    )


def _render_sentiment_analysis_panel(analysis: dict[str, Any]) -> None:
    phase_label = escape(str(analysis.get("phase_label") or "-"))
    headline = escape(str(analysis.get("headline") or "-"))
    summary = escape(str(analysis.get("summary") or ""))
    tone = escape(_sentiment_tone(analysis.get("tone") or "neutral"))
    data_confidence = dict(analysis.get("data_confidence") or {})
    confidence_status = escape(str(data_confidence.get("status") or "-"))
    confidence_detail = escape(str(data_confidence.get("detail") or ""))

    st.markdown(
        """
        <style>
          .ov-sentiment-brief {
            margin: 0.45rem 0 0.8rem 0;
            padding: 0.92rem 1rem;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-left: 4px solid var(--ov-sentiment-tone, #64748b);
            border-radius: 8px;
            background: linear-gradient(135deg, color-mix(in srgb, var(--ov-sentiment-tone, #64748b) 8%, transparent), rgba(255,255,255,0.96));
          }
          .ov-sentiment-eyebrow {
            color: #475569;
            font-size: 0.75rem;
            font-weight: 760;
            letter-spacing: 0;
            text-transform: uppercase;
          }
          .ov-sentiment-headline {
            margin-top: 0.34rem;
            color: #111827;
            font-size: 1.08rem;
            line-height: 1.26;
            font-weight: 820;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-summary {
            margin-top: 0.35rem;
            max-width: 76rem;
            color: #334155;
            font-size: 0.88rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-meta {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.58rem;
          }
          .ov-sentiment-pill {
            display: inline-flex;
            align-items: center;
            min-height: 1.38rem;
            padding: 0.16rem 0.52rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--ov-sentiment-tone, #64748b) 13%, transparent);
            color: #111827;
            font-size: 0.76rem;
            font-weight: 760;
            line-height: 1.15;
          }
          .ov-sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap: 0.58rem;
            margin: 0.35rem 0 0.85rem 0;
          }
          .ov-sentiment-step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 0.72rem;
            margin: 0.4rem 0 0.95rem 0;
          }
          .ov-sentiment-step {
            min-height: 148px;
            padding: 0.86rem 0.92rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-left: 4px solid var(--ov-step-tone, #64748b);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.94);
          }
          .ov-sentiment-step-num {
            display: inline-flex;
            align-items: center;
            min-height: 1.32rem;
            padding: 0.12rem 0.42rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--ov-step-tone, #64748b) 11%, transparent);
            color: var(--ov-step-tone, #64748b);
            font-size: 0.72rem;
            font-weight: 820;
          }
          .ov-sentiment-step-title {
            margin-top: 0.42rem;
            color: #111827;
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 800;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-step-status {
            margin-top: 0.34rem;
            color: #111827;
            font-size: 0.82rem;
            line-height: 1.2;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-step-detail {
            margin-top: 0.34rem;
            color: #334155;
            font-size: 0.8rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-driver {
            min-height: 92px;
            padding: 0.62rem 0.7rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-left: 3px solid var(--ov-driver-tone, #64748b);
            border-radius: 8px;
            background: rgba(255,255,255,0.92);
          }
          .ov-sentiment-driver-title {
            color: #111827;
            font-size: 0.82rem;
            line-height: 1.25;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-driver-detail {
            margin-top: 0.22rem;
            color: #334155;
            font-size: 0.75rem;
            line-height: 1.32;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning {
            min-height: 184px;
            padding: 0.78rem 0.82rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-top: 4px solid var(--ov-learning-tone, #64748b);
            border-radius: 8px;
            background: rgba(255,255,255,0.94);
          }
          .ov-sentiment-learning-title {
            color: #111827;
            font-size: 0.92rem;
            line-height: 1.25;
            font-weight: 820;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning-score {
            margin-top: 0.3rem;
            color: var(--ov-learning-tone, #64748b);
            font-size: 0.82rem;
            line-height: 1.24;
            font-weight: 800;
          }
          .ov-sentiment-learning-body {
            margin-top: 0.34rem;
            color: #334155;
            font-size: 0.76rem;
            line-height: 1.38;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning-body strong {
            color: #111827;
            font-weight: 780;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    tone_color = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
        "neutral": OVERVIEW_COLOR_NEUTRAL,
    }.get(tone, OVERVIEW_COLOR_NEUTRAL)
    st.markdown(
        f"""
        <section class="ov-sentiment-brief" style="--ov-sentiment-tone:{tone_color};">
          <div class="ov-sentiment-eyebrow">시장 심리 컨텍스트</div>
          <div class="ov-sentiment-headline">{headline}</div>
          <div class="ov-sentiment-summary">{summary}</div>
          <div class="ov-sentiment-meta">
            <span class="ov-sentiment-pill">{phase_label}</span>
            <span class="ov-sentiment-pill">데이터 신뢰도: {confidence_status}</span>
            <span class="ov-sentiment-pill">{confidence_detail}</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_sentiment_analysis_steps(analysis: dict[str, Any]) -> None:
    steps = list(analysis.get("analysis_steps") or [])
    if not steps:
        return
    html_steps: list[str] = []
    for index, step in enumerate(steps, start=1):
        tone = _sentiment_tone(step.get("tone") or "neutral")
        tone_color = {
            "positive": OVERVIEW_COLOR_POSITIVE,
            "warning": OVERVIEW_COLOR_WARNING,
            "danger": OVERVIEW_COLOR_DANGER,
            "neutral": OVERVIEW_COLOR_NEUTRAL,
        }.get(tone, OVERVIEW_COLOR_NEUTRAL)
        html_steps.append(
            f'<div class="ov-sentiment-step" style="--ov-step-tone:{tone_color};">'
            f'<div class="ov-sentiment-step-num">STEP {index}</div>'
            f'<div class="ov-sentiment-step-title">{escape(str(step.get("title") or "-"))}</div>'
            f'<div class="ov-sentiment-step-status">{escape(str(step.get("status") or "-"))}</div>'
            f'<div class="ov-sentiment-step-detail">{escape(str(step.get("detail") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### 시장 심리 읽기 - 6단계")
    st.markdown(f'<div class="ov-sentiment-step-grid">{"".join(html_steps)}</div>', unsafe_allow_html=True)


def _render_sentiment_driver_groups(analysis: dict[str, Any]) -> None:
    groups = dict(analysis.get("driver_groups") or {})
    labels = [
        ("greed", "탐욕 드라이버", OVERVIEW_COLOR_POSITIVE),
        ("fear", "공포 드라이버", OVERVIEW_COLOR_WARNING),
        ("neutral", "중립 드라이버", OVERVIEW_COLOR_NEUTRAL),
    ]
    html_cards: list[str] = []
    for key, title, color in labels:
        rows = list(groups.get(key) or [])
        if rows:
            detail = " / ".join(
                f"{row.get('label_ko') or row.get('series')}: {row.get('score')} ({row.get('rating_label_ko') or row.get('rating')})"
                for row in rows[:4]
            )
        else:
            detail = "이 구간의 활성 드라이버가 없습니다."
        html_cards.append(
            f'<div class="ov-sentiment-driver" style="--ov-driver-tone:{color};">'
            f'<div class="ov-sentiment-driver-title">{escape(title)} · {len(rows)}</div>'
            f'<div class="ov-sentiment-driver-detail">{escape(detail)}</div>'
            "</div>"
        )
    st.markdown("#### 드라이버 분해")
    st.markdown(f'<div class="ov-sentiment-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_sentiment_component_learning_cards(analysis: dict[str, Any]) -> None:
    explanations = list(analysis.get("component_explanations") or [])
    if not explanations:
        return
    tone_colors = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
        "neutral": OVERVIEW_COLOR_NEUTRAL,
    }
    html_cards: list[str] = []
    for item in explanations:
        tone_color = tone_colors.get(_sentiment_tone(item.get("tone") or "neutral"), OVERVIEW_COLOR_NEUTRAL)
        score = "-" if item.get("score") is None else f"{float(item.get('score')):.1f}"
        title = f"{item.get('label_ko') or '-'} · {item.get('series') or '-'}"
        html_cards.append(
            f'<div class="ov-sentiment-learning" style="--ov-learning-tone:{tone_color};">'
            f'<div class="ov-sentiment-learning-title">{escape(str(title))}</div>'
            f'<div class="ov-sentiment-learning-score">현재 {score} · {escape(str(item.get("rating_label_ko") or item.get("rating") or "-"))}</div>'
            f'<div class="ov-sentiment-learning-body"><strong>보는 것</strong><br>{escape(str(item.get("what_it_checks") or ""))}</div>'
            f'<div class="ov-sentiment-learning-body"><strong>현재 읽기</strong><br>{escape(str(item.get("current_reading") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### CNN 구성요소 학습 노트")
    st.markdown(f'<div class="ov-sentiment-step-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_sentiment_next_checks(analysis: dict[str, Any]) -> None:
    checks = list(analysis.get("next_checks") or [])
    if not checks:
        return
    html_cards: list[str] = []
    for check in checks:
        html_cards.append(
            f'<div class="ov-sentiment-driver" style="--ov-driver-tone:{OVERVIEW_COLOR_PRIMARY};">'
            f'<div class="ov-sentiment-driver-title">{escape(str(check.get("target") or "-"))}</div>'
            f'<div class="ov-sentiment-driver-detail"><strong>왜</strong> {escape(str(check.get("reason") or ""))}</div>'
            f'<div class="ov-sentiment-driver-detail"><strong>볼 것</strong> {escape(str(check.get("watch_for") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### 다음 확인")
    st.markdown(f'<div class="ov-sentiment-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_market_sentiment_tab() -> None:
    st.markdown("### 시장 심리 컨텍스트")
    control_cols = st.columns([1.1, 1, 1], gap="small", vertical_alignment="bottom")
    if control_cols[0].button(
        "시장 심리 갱신",
        key="overview_market_sentiment_refresh",
        use_container_width=True,
        type="primary",
    ):
        with st.spinner("Refreshing CNN Fear & Greed / AAII sentiment..."):
            _store_overview_job_result("overview_market_sentiment_result", run_overview_market_sentiment())
            load_overview_market_sentiment_snapshot.clear()
        st.rerun()
    if control_cols[1].button(
        "화면 새로고침",
        key="overview_market_sentiment_reload",
        use_container_width=True,
    ):
        load_overview_market_sentiment_snapshot.clear()
        st.rerun()
    control_cols[2].caption("CNN / AAII 저장 데이터 기준")

    _render_market_job_result("overview_market_sentiment_result")
    snapshot = load_overview_market_sentiment_snapshot()
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    _render_sentiment_analysis_panel(analysis)
    _render_sentiment_analysis_steps(analysis)
    render_status_card_grid(
        [
            {
                "title": "데이터 신뢰도",
                "value": dict(analysis.get("data_confidence") or {}).get("status") or snapshot.get("status") or "-",
                "detail": f"{coverage.get('missing_count') or 0} missing · {coverage.get('stale_count') or 0} stale",
                "tone": _sentiment_tone(dict(analysis.get("data_confidence") or {}).get("tone") or snapshot.get("status")),
            },
            {
                "title": "CNN Fear & Greed",
                "value": "-" if coverage.get("cnn_score") is None else f"{float(coverage['cnn_score']):.1f}",
                "detail": str(coverage.get("cnn_rating") or "-"),
                "tone": "positive"
                if _safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) >= 55
                else "warning"
                if _safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) < 45
                else "neutral",
            },
            {
                "title": "AAII Bearish",
                "value": "-" if coverage.get("aaii_bearish") is None else f"{float(coverage['aaii_bearish']):.1f}%",
                "detail": "weekly bearish sentiment",
                "tone": "warning"
                if _safe_float(coverage.get("aaii_bearish")) is not None and float(coverage["aaii_bearish"]) >= 40
                else "neutral",
            },
            {
                "title": "Bull-Bear Spread",
                "value": "-"
                if coverage.get("aaii_bull_bear_spread") is None
                else f"{float(coverage['aaii_bull_bear_spread']):+.1f} pp",
                "detail": "AAII bullish minus bearish",
                "tone": "positive"
                if _safe_float(coverage.get("aaii_bull_bear_spread")) is not None
                and float(coverage["aaii_bull_bear_spread"]) > 0
                else "warning"
                if _safe_float(coverage.get("aaii_bull_bear_spread")) is not None
                else "neutral",
            },
        ]
    )
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))

    rows = snapshot.get("rows")
    component_rows = snapshot.get("component_rows")
    history_rows = snapshot.get("history_rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("Stored sentiment rows are not available yet. Run Market Sentiment refresh first.")
        return

    _render_sentiment_driver_groups(analysis)
    _render_sentiment_component_learning_cards(analysis)
    _render_sentiment_next_checks(analysis)

    trend_tab, components_tab, table_tab = st.tabs(["추세 근거", "CNN 구성 상세", "원천 테이블"])
    with trend_tab:
        st.altair_chart(_sentiment_trend_chart(history_rows if isinstance(history_rows, pd.DataFrame) else pd.DataFrame()), width="stretch")
    with components_tab:
        st.altair_chart(_sentiment_component_chart(component_rows if isinstance(component_rows, pd.DataFrame) else pd.DataFrame()), width="stretch")
        if isinstance(component_rows, pd.DataFrame) and not component_rows.empty:
            st.dataframe(component_rows, width="stretch", hide_index=True)
    with table_tab:
        st.dataframe(rows, width="stretch", hide_index=True)


def _event_type_label(value: Any) -> str:
    labels = {
        "FOMC_MEETING": "FOMC",
        "EARNINGS": "Earnings",
        "MACRO": "Macro",
        "MACRO_CPI": "CPI",
        "MACRO_PPI": "PPI",
        "MACRO_EMPLOYMENT": "Jobs",
        "MACRO_GDP": "GDP",
    }
    return labels.get(str(value or ""), str(value or "-").replace("_", " ").title())


def _event_importance_from_type(value: Any) -> str:
    event_type = str(value or "").upper()
    if event_type == "FOMC_MEETING" or event_type == "MACRO" or event_type.startswith("MACRO_"):
        return "High"
    if event_type == "EARNINGS":
        return "Medium"
    return "Low"


def _event_focus_from_row(row: pd.Series) -> str:
    quality_action = str(row.get("Quality Action") or "")
    if quality_action and quality_action != "No action":
        return "Needs Review"
    days_until = row.get("Days Until")
    if pd.isna(days_until):
        return "Unknown"
    day_number = int(days_until)
    if day_number < 0:
        return "Past"
    if day_number == 0:
        return "Today"
    if day_number <= 7:
        return "This Week"
    if day_number <= 30:
        return "Next 30D"
    return "Later"


def _prepare_event_calendar_frame(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["Date Parsed"] = pd.to_datetime(out.get("Date"), errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    calculated_days = (out["Date Parsed"] - today).dt.days
    if "Days Until" in out:
        out["Days Until"] = pd.to_numeric(out["Days Until"], errors="coerce")
        out["Days Until"] = out["Days Until"].where(out["Days Until"].notna(), calculated_days)
    else:
        out["Days Until"] = calculated_days
    out["Month"] = out["Date Parsed"].dt.strftime("%Y-%m")
    out["Week"] = out["Date Parsed"].dt.to_period("W").astype(str)
    out["Type Label"] = out.get("Type", pd.Series(dtype=str)).map(_event_type_label)
    if "Importance" not in out:
        out["Importance"] = out.get("Type", pd.Series(dtype=str)).map(_event_importance_from_type)
    else:
        fallback_importance = out.get("Type", pd.Series(dtype=str)).map(_event_importance_from_type)
        out["Importance"] = out["Importance"].where(out["Importance"].notna() & (out["Importance"] != ""), fallback_importance)
    if "Focus" not in out:
        out["Focus"] = out.apply(_event_focus_from_row, axis=1)
    else:
        fallback_focus = out.apply(_event_focus_from_row, axis=1)
        out["Focus"] = out["Focus"].where(out["Focus"].notna() & (out["Focus"] != ""), fallback_focus)
    out["Symbol Label"] = out.get("Symbol", pd.Series(dtype=str)).replace({"-": ""})
    out["Summary"] = out.apply(
        lambda row: f"{row.get('Type Label')}: {row.get('Symbol Label') or row.get('Title') or '-'}",
        axis=1,
    )
    return out


def _filter_event_rows_for_calendar(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    render_overview_toolbar_label("보기 조건")
    filter_cols = st.columns([1, 1, 1, 1], gap="small")
    source_options = ["All"] + sorted(
        value for value in rows.get("Source Type", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    validation_options = ["All"] + sorted(
        value for value in rows.get("Validation", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    importance_values = rows.get("Importance", pd.Series(dtype=str)).dropna().unique().tolist()
    importance_options = ["All"] + [
        value for value in ["High", "Medium", "Low"] if value in importance_values
    ]
    window = str(
        filter_cols[0].selectbox(
            "Window",
            ["30D", "90D", "All"],
            index=_option_index(
                ["30D", "90D", "All"],
                st.session_state.get("overview_events_window_filter", "90D"),
                default=1,
            ),
            key="overview_events_window_filter",
        )
    )
    source_filter = str(
        filter_cols[1].selectbox(
            "Source Type",
            source_options,
            index=0,
            key="overview_events_source_filter",
        )
    )
    validation_filter = str(
        filter_cols[2].selectbox(
            "Validation",
            validation_options,
            index=0,
            key="overview_events_validation_filter",
        )
    )
    importance_filter = str(
        filter_cols[3].selectbox(
            "Importance",
            importance_options,
            index=0,
            key="overview_events_importance_filter",
        )
    )

    filtered = rows.copy()
    if window != "All":
        days = 30 if window == "30D" else 90
        filtered = filtered[(filtered["Days Until"].isna()) | ((filtered["Days Until"] >= 0) & (filtered["Days Until"] <= days))]
    if source_filter != "All" and "Source Type" in filtered:
        filtered = filtered[filtered["Source Type"] == source_filter]
    if validation_filter != "All" and "Validation" in filtered:
        filtered = filtered[filtered["Validation"] == validation_filter]
    if importance_filter != "All" and "Importance" in filtered:
        filtered = filtered[filtered["Importance"] == importance_filter]
    return filtered


def _event_tone(value: Any) -> str:
    text = str(value or "").lower()
    if text in {"fomc", "fomc_meeting"}:
        return "fomc"
    if text in {"macro", "cpi", "ppi", "jobs", "gdp"} or text.startswith("macro"):
        return "macro"
    if text == "earnings":
        return "earnings"
    if text in {"high", "needs review", "not confirmed", "conflict", "stale estimate"}:
        return "review"
    if text in {"official", "cross-checked", "no action"}:
        return "official"
    if text in {"estimate only", "provider estimate", "medium", "current estimate"}:
        return "estimate"
    return "neutral"


def _event_days_text(value: Any) -> str:
    if value in (None, "") or pd.isna(value):
        return "date pending"
    day_number = int(value)
    if day_number < 0:
        return f"{abs(day_number)}d ago"
    if day_number == 0:
        return "today"
    if day_number == 1:
        return "tomorrow"
    return f"in {day_number}d"


def _event_main_title(row: pd.Series) -> str:
    symbol = str(row.get("Symbol Label") or row.get("Symbol") or "").strip()
    if symbol == "-":
        symbol = ""
    title = str(row.get("Title") or "-")
    return f"{symbol} · {title}" if symbol else title


def _event_subtitle(row: pd.Series) -> str:
    parts = [
        str(row.get("Type Label") or row.get("Type") or "-"),
        str(row.get("Source Type") or "-"),
        str(row.get("Freshness") or "-"),
    ]
    action = str(row.get("Quality Action") or "")
    if action and action != "No action":
        parts.append(action)
    return " · ".join(part for part in parts if part and part != "-")


def _event_agenda_item(row: pd.Series) -> dict[str, Any]:
    return {
        "date": str(row.get("Date") or "-"),
        "countdown": _event_days_text(row.get("Days Until")),
        "title": _event_main_title(row),
        "subtitle": _event_subtitle(row),
        "badges": [
            {"label": row.get("Type Label") or row.get("Type") or "-", "tone": _event_tone(row.get("Type Label"))},
            {"label": row.get("Importance") or "-", "tone": _event_tone(row.get("Importance"))},
            {"label": row.get("Validation") or "-", "tone": _event_tone(row.get("Validation"))},
            {"label": row.get("Focus") or "-", "tone": _event_tone(row.get("Focus"))},
        ],
    }


def _event_agenda_sections(rows: pd.DataFrame) -> list[dict[str, Any]]:
    if rows.empty:
        return []
    focus_rows = rows.copy()
    focus_rows["Days Until"] = pd.to_numeric(focus_rows.get("Days Until"), errors="coerce")
    recent_major_rows = focus_rows[
        (focus_rows["Days Until"] < 0)
        & (focus_rows["Days Until"] >= -7)
        & (focus_rows.get("Importance") == "High")
    ].sort_values(
        ["Date Parsed", "Type Label", "Symbol"],
        ascending=[False, True, True],
    )
    future_rows = focus_rows[focus_rows["Days Until"].isna() | (focus_rows["Days Until"] >= 0)].sort_values(
        ["Date Parsed", "Importance", "Type Label", "Symbol"],
        ascending=[True, True, True, True],
    )
    sections: list[dict[str, Any]] = []
    if not recent_major_rows.empty:
        recent_rows = recent_major_rows.head(8)
        sections.append(
            {
                "title": "Recent Major",
                "meta": f"{len(recent_rows)} shown",
                "rows": [_event_agenda_item(row) for _, row in recent_rows.iterrows()],
            }
        )
    section_specs = [
        ("Today", future_rows["Days Until"] == 0, 8),
        ("This Week", (future_rows["Days Until"] > 0) & (future_rows["Days Until"] <= 7), 10),
        ("Next 30D", (future_rows["Days Until"] > 7) & (future_rows["Days Until"] <= 30), 12),
        ("Later", future_rows["Days Until"] > 30, 12),
    ]
    for title, mask, limit in section_specs:
        section_rows = future_rows[mask].head(limit)
        if section_rows.empty:
            continue
        sections.append(
            {
                "title": title,
                "meta": f"{len(section_rows)} shown",
                "rows": [_event_agenda_item(row) for _, row in section_rows.iterrows()],
            }
        )
    unknown_rows = future_rows[future_rows["Days Until"].isna()].head(6)
    if not unknown_rows.empty:
        sections.append(
            {
                "title": "Date Pending",
                "meta": f"{len(unknown_rows)} shown",
                "rows": [_event_agenda_item(row) for _, row in unknown_rows.iterrows()],
            }
        )
    return sections


def _event_quality_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    return rows[
        (rows.get("Focus") == "Needs Review")
        | ((rows.get("Quality Action") != "No action") & rows.get("Quality Action").notna())
        | (rows.get("Validation").isin(["Estimate only", "Not confirmed", "Conflict"]))
        | (rows.get("Freshness").isin(["Stale estimate", "Stale source"]))
    ].sort_values(["Date Parsed", "Type Label", "Symbol"])


def _event_quality_sections(rows: pd.DataFrame) -> list[dict[str, Any]]:
    quality_rows = _event_quality_rows(rows)
    if quality_rows.empty:
        return []
    review_mask = (quality_rows.get("Focus") == "Needs Review") | (
        (quality_rows.get("Quality Action") != "No action") & quality_rows.get("Quality Action").notna()
    )
    estimate_mask = quality_rows.get("Validation").isin(["Estimate only", "Not confirmed", "Conflict"])
    freshness_mask = quality_rows.get("Freshness").isin(["Stale estimate", "Stale source"])
    section_specs = [
        ("Action Required", quality_rows[review_mask].head(18)),
        ("Estimate Validation", quality_rows[estimate_mask].head(18)),
        ("Freshness", quality_rows[freshness_mask].head(18)),
    ]
    sections: list[dict[str, Any]] = []
    seen_keys: set[tuple[Any, Any, Any]] = set()
    for title, section_rows in section_specs:
        if section_rows.empty:
            continue
        deduped_rows = []
        for _, row in section_rows.iterrows():
            key = (row.get("Date"), row.get("Type"), row.get("Symbol"), row.get("Title"))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped_rows.append(_event_agenda_item(row))
        if deduped_rows:
            sections.append({"title": title, "meta": f"{len(deduped_rows)} shown", "rows": deduped_rows})
    return sections


def _event_summary_items(rows: pd.DataFrame, coverage: dict[str, Any], *, event_type: Any) -> list[dict[str, Any]]:
    if rows.empty:
        next_value = _snapshot_value(coverage.get("next_event_date"))
        next_detail = f"filter: {event_type or 'All'}"
    else:
        rows_with_days = rows.copy()
        rows_with_days["Days Until"] = pd.to_numeric(rows_with_days.get("Days Until"), errors="coerce")
        upcoming = rows_with_days[rows_with_days["Days Until"].isna() | (rows_with_days["Days Until"] >= 0)].sort_values(
            ["Date Parsed", "Type Label", "Symbol"],
            ascending=[True, True, True],
        )
        next_row = upcoming.iloc[0] if not upcoming.empty else rows_with_days.sort_values("Date Parsed").iloc[0]
        next_value = str(next_row.get("Date") or _snapshot_value(coverage.get("next_event_date")))
        next_detail = f"{_event_days_text(next_row.get('Days Until'))} · {_event_main_title(next_row)}"
    needs_review_count = int(len(_event_quality_rows(rows))) if not rows.empty else int(coverage.get("needs_review_count") or 0)
    return [
        {"label": "Next Event", "value": next_value, "detail": next_detail, "tone": "primary"},
        {
            "label": "This Week",
            "value": coverage.get("this_week_count") or 0,
            "detail": "today through 7D",
            "tone": "positive",
        },
        {
            "label": "Next 30D",
            "value": coverage.get("next_30d_count") or 0,
            "detail": f"stored rows: {coverage.get('event_count') or 0}",
            "tone": "neutral",
        },
        {
            "label": "Needs Review",
            "value": needs_review_count,
            "detail": f"latest: {_snapshot_value(coverage.get('latest_collected_at'))}",
            "tone": "danger" if needs_review_count else "positive",
        },
    ]


def _latest_collected_at(rows: pd.DataFrame) -> str:
    if rows.empty or "Collected At" not in rows:
        return "-"
    values = rows["Collected At"].replace("-", pd.NA).dropna().astype(str)
    return values.max() if not values.empty else "-"


def _compact_event_timestamp(value: str) -> str:
    if len(value) >= 16 and value[:4].isdigit():
        return value[5:16]
    return value


def _event_source_items(rows: pd.DataFrame, *, event_filter: str) -> list[dict[str, Any]]:
    source_specs = [
        ("FOMC", "FOMC_MEETING", lambda frame: frame["Type"].astype(str).str.upper() == "FOMC_MEETING", "fomc"),
        ("Earnings", "EARNINGS", lambda frame: frame["Type"].astype(str).str.upper() == "EARNINGS", "earnings"),
        ("Macro", "MACRO", lambda frame: frame["Type"].astype(str).str.upper().str.startswith("MACRO"), "macro"),
    ]
    selected_filter = str(event_filter or "ALL").upper()
    items: list[dict[str, Any]] = []
    for title, source_filter, mask_fn, base_tone in source_specs:
        if selected_filter != "ALL" and source_filter != selected_filter:
            continue
        subset = rows[mask_fn(rows)] if not rows.empty and "Type" in rows else pd.DataFrame()
        review_count = len(_event_quality_rows(subset)) if not subset.empty else 0
        if subset.empty:
            status = "Missing"
            tone = "danger"
        elif review_count:
            status = "Review"
            tone = "review"
        else:
            status = "OK"
            tone = base_tone
        latest = _latest_collected_at(subset)
        items.append(
            {
                "title": title,
                "status": status,
                "detail": f"{len(subset)} rows · latest {latest} · review {review_count}",
                "rows": len(subset),
                "latest": _compact_event_timestamp(latest),
                "review_count": review_count,
                "tone": tone,
            }
        )
    return items


def _build_event_calendar_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        chart_rows = pd.DataFrame(
            [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Type Label": "No Data", "Count": 0}]
        )
    else:
        valid_rows = rows.dropna(subset=["Date Parsed"])
        if valid_rows.empty:
            chart_rows = pd.DataFrame(
                [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Type Label": "No Data", "Count": 0}]
            )
        else:
            chart_rows = (
                valid_rows
                .groupby(["Date Parsed", "Type Label"], as_index=False)
                .size()
                .rename(columns={"size": "Count"})
            )
    date_min = chart_rows["Date Parsed"].min()
    date_max = chart_rows["Date Parsed"].max()
    if pd.isna(date_min) or pd.isna(date_max):
        date_min = pd.Timestamp(datetime.now().date())
        date_max = date_min + pd.Timedelta(days=1)
    elif date_min == date_max:
        date_max = date_min + pd.Timedelta(days=1)
    max_count = max(1, int(chart_rows.groupby("Date Parsed")["Count"].sum().max() or 0))
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(
                "Date Parsed:T",
                title=None,
                axis=alt.Axis(format="%b %d", labelAngle=-35),
                scale=alt.Scale(domain=[date_min, date_max]),
            ),
            y=alt.Y("Count:Q", title="Events", stack="zero", scale=alt.Scale(domain=[0, max_count])),
            color=alt.Color(
                "Type Label:N",
                title=None,
                legend=alt.Legend(orient="bottom"),
                scale=alt.Scale(
                    range=[
                        OVERVIEW_COLOR_PRIMARY,
                        OVERVIEW_COLOR_POSITIVE,
                        OVERVIEW_COLOR_WARNING,
                        OVERVIEW_COLOR_PURPLE,
                        OVERVIEW_COLOR_NEUTRAL,
                        OVERVIEW_COLOR_SOFT,
                    ]
                ),
            ),
            tooltip=["Date Parsed:T", "Type Label:N", "Count:Q"],
        )
        .properties(height=240)
    )


def _event_month_options(rows: pd.DataFrame) -> list[str]:
    if rows.empty or "Month" not in rows:
        return []
    return sorted(value for value in rows["Month"].dropna().astype(str).unique().tolist() if value)


def _default_event_month_index(month_options: list[str]) -> int:
    if not month_options:
        return 0
    current_month = datetime.now().strftime("%Y-%m")
    if current_month in month_options:
        return month_options.index(current_month)
    future_months = [month for month in month_options if month >= current_month]
    if future_months:
        return month_options.index(future_months[0])
    return 0


def _event_month_label(month_value: str) -> str:
    try:
        month_date = pd.Timestamp(f"{month_value}-01")
    except ValueError:
        return month_value
    if pd.isna(month_date):
        return month_value
    return month_date.strftime("%B %Y")


def _event_calendar_tone_class(row: pd.Series) -> str:
    event_type = str(row.get("Type") or "").upper()
    type_label = str(row.get("Type Label") or "").lower()
    if event_type == "FOMC_MEETING" or type_label == "fomc":
        return "fomc"
    if event_type == "EARNINGS" or type_label == "earnings":
        return "earnings"
    if event_type == "MACRO" or event_type.startswith("MACRO_") or type_label in {"cpi", "ppi", "jobs", "gdp", "macro"}:
        return "macro"
    return "other"


def _event_calendar_item_html(row: pd.Series) -> str:
    type_label = str(row.get("Type Label") or row.get("Type") or "-")
    symbol = str(row.get("Symbol Label") or row.get("Symbol") or "").strip()
    if symbol == "-":
        symbol = ""
    title = str(row.get("Title") or "-")
    importance = str(row.get("Importance") or "Low").lower()
    tone = _event_calendar_tone_class(row)
    detail = symbol or title
    full_text = f"{type_label}: {symbol or title}"
    return (
        f'<div class="event-calendar-item event-calendar-{tone} '
        f'event-calendar-importance-{escape(importance)}" title="{escape(full_text)}">'
        f'<span class="event-calendar-type event-calendar-type-{tone}">{escape(type_label)}</span>'
        f'<span class="event-calendar-text">{escape(detail)}</span>'
        "</div>"
    )


def _event_calendar_legend_html(rows: pd.DataFrame) -> str:
    counts = {"fomc": 0, "earnings": 0, "macro": 0, "other": 0}
    if not rows.empty:
        for _, row in rows.iterrows():
            counts[_event_calendar_tone_class(row)] += 1
    labels = [
        ("FOMC", "fomc"),
        ("Earnings", "earnings"),
        ("Macro", "macro"),
        ("Other", "other"),
    ]
    return "".join(
        '<span class="event-calendar-legend-item">'
        f'<span class="event-calendar-legend-dot event-calendar-legend-{tone}"></span>'
        f"{escape(label)} {counts[tone]}"
        "</span>"
        for label, tone in labels
        if counts[tone] or tone != "other"
    )


def _render_event_month_grid(rows: pd.DataFrame) -> None:
    valid_rows = rows.dropna(subset=["Date Parsed"]) if "Date Parsed" in rows else pd.DataFrame()
    month_options = _event_month_options(valid_rows)
    if not month_options:
        st.info("No dated event rows match the selected calendar filters.")
        return

    selected_month = str(
        st.selectbox(
            "Month",
            month_options,
            index=_default_event_month_index(month_options),
            format_func=_event_month_label,
            key="overview_events_calendar_month",
        )
    )
    month_start = pd.Timestamp(f"{selected_month}-01")
    if pd.isna(month_start):
        st.info("No dated event rows match the selected calendar filters.")
        return

    month_rows = valid_rows[valid_rows["Month"] == selected_month].copy()
    month_rows["Date Key"] = month_rows["Date Parsed"].dt.strftime("%Y-%m-%d")
    importance_rank = {"High": 0, "Medium": 1, "Low": 2}
    month_rows["Importance Rank"] = month_rows.get("Importance", pd.Series(dtype=str)).map(importance_rank).fillna(3)
    grouped_rows = {
        date_key: day_rows.sort_values(["Importance Rank", "Type Label", "Symbol"]).reset_index(drop=True)
        for date_key, day_rows in month_rows.groupby("Date Key", sort=True)
    }

    today_value = datetime.now().date()
    calendar_weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(int(month_start.year), int(month_start.month))
    weekday_html = "".join(f'<div class="event-calendar-weekday">{label}</div>' for label in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    day_cells: list[str] = []
    for week in calendar_weeks:
        for day_value in week:
            date_key = day_value.isoformat()
            day_rows = grouped_rows.get(date_key, pd.DataFrame())
            muted_class = " event-calendar-muted" if day_value.month != int(month_start.month) else ""
            today_class = " event-calendar-today" if day_value == today_value else ""
            event_class = " event-calendar-has-events" if not day_rows.empty else ""
            high_class = (
                " event-calendar-has-high"
                if not day_rows.empty and (day_rows.get("Importance", pd.Series(dtype=str)) == "High").any()
                else ""
            )
            visible_rows = day_rows.head(3) if not day_rows.empty else pd.DataFrame()
            event_html = "".join(_event_calendar_item_html(row) for _, row in visible_rows.iterrows())
            extra_count = max(0, len(day_rows) - len(visible_rows))
            if extra_count:
                event_html += f'<div class="event-calendar-more">+{extra_count} more</div>'
            count_html = f'<span class="event-calendar-count">{len(day_rows)}</span>' if not day_rows.empty else ""
            day_cells.append(
                f'<div class="event-calendar-day{muted_class}{today_class}{event_class}{high_class}">'
                '<div class="event-calendar-day-head">'
                f'<div class="event-calendar-date">{day_value.day}</div>'
                f"{count_html}"
                "</div>"
                f'<div class="event-calendar-items">{event_html}</div>'
                "</div>"
            )

    event_count = len(month_rows)
    high_impact_count = int((month_rows.get("Importance", pd.Series(dtype=str)) == "High").sum())
    legend_html = _event_calendar_legend_html(month_rows)
    month_label = _event_month_label(selected_month)
    st.markdown(
        f"""
        <style>
          .event-calendar-shell {{
            border: 1px solid {OVERVIEW_COLOR_BORDER};
            border-radius: 8px;
            overflow: hidden;
            background: {OVERVIEW_COLOR_SURFACE};
          }}
          .event-calendar-topbar {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 14px;
            padding: 12px 14px;
            border-bottom: 1px solid {OVERVIEW_COLOR_BORDER};
            background:
              linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(15, 118, 110, 0.05)),
              {OVERVIEW_COLOR_SURFACE_SUBTLE};
          }}
          .event-calendar-title {{
            color: {OVERVIEW_COLOR_TEXT};
            font-size: 16px;
            font-weight: 780;
            line-height: 1.2;
          }}
          .event-calendar-subtitle {{
            color: {OVERVIEW_COLOR_TEXT_SUBTLE};
            font-size: 12px;
            font-weight: 650;
            margin-top: 3px;
          }}
          .event-calendar-legend {{
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            flex-wrap: wrap;
            max-width: 58%;
          }}
          .event-calendar-legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            min-height: 24px;
            padding: 3px 8px;
            border: 1px solid {OVERVIEW_COLOR_BORDER};
            border-radius: 999px;
            background: {OVERVIEW_COLOR_SURFACE};
            color: {OVERVIEW_COLOR_TEXT_SUBTLE};
            font-size: 11px;
            font-weight: 720;
          }}
          .event-calendar-legend-dot {{
            width: 8px;
            height: 8px;
            border-radius: 999px;
            flex: 0 0 auto;
          }}
          .event-calendar-legend-fomc {{ background: {OVERVIEW_COLOR_PRIMARY}; }}
          .event-calendar-legend-macro {{ background: {OVERVIEW_COLOR_POSITIVE}; }}
          .event-calendar-legend-earnings {{ background: {OVERVIEW_COLOR_WARNING}; }}
          .event-calendar-legend-other {{ background: {OVERVIEW_COLOR_NEUTRAL}; }}
          .event-calendar-grid {{
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
          }}
          .event-calendar-weekday {{
            padding: 8px 10px;
            background: {OVERVIEW_COLOR_SURFACE_SUBTLE};
            border-bottom: 1px solid {OVERVIEW_COLOR_BORDER};
            color: {OVERVIEW_COLOR_NEUTRAL};
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
          }}
          .event-calendar-day {{
            min-height: 126px;
            padding: 8px;
            border-right: 1px solid {OVERVIEW_COLOR_BORDER};
            border-bottom: 1px solid {OVERVIEW_COLOR_BORDER};
            background: {OVERVIEW_COLOR_SURFACE};
          }}
          .event-calendar-day:nth-child(7n) {{
            border-right: 0;
          }}
          .event-calendar-muted {{
            background: {OVERVIEW_COLOR_SURFACE_SUBTLE};
            color: {OVERVIEW_COLOR_TEXT_MUTED};
          }}
          .event-calendar-has-events {{
            background:
              linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(255, 255, 255, 0.98)),
              {OVERVIEW_COLOR_SURFACE_ALT};
          }}
          .event-calendar-has-high {{
            background:
              linear-gradient(180deg, rgba(180, 83, 9, 0.07), rgba(255, 255, 255, 0.98)),
              {OVERVIEW_COLOR_SURFACE_ALT};
          }}
          .event-calendar-today {{
            box-shadow: inset 0 0 0 2px {OVERVIEW_COLOR_PRIMARY};
          }}
          .event-calendar-day-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            margin-bottom: 8px;
          }}
          .event-calendar-date {{
            color: {OVERVIEW_COLOR_TEXT};
            font-size: 13px;
            font-weight: 700;
            line-height: 1;
          }}
          .event-calendar-count {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 20px;
            height: 20px;
            border-radius: 999px;
            background: rgba(37, 99, 235, 0.10);
            color: {OVERVIEW_COLOR_PRIMARY};
            font-size: 10px;
            font-weight: 800;
          }}
          .event-calendar-items {{
            display: flex;
            flex-direction: column;
            gap: 5px;
          }}
          .event-calendar-item {{
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            gap: 5px;
            align-items: center;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-radius: 6px;
            background: {OVERVIEW_COLOR_SURFACE};
            padding: 4px 5px;
            min-width: 0;
          }}
          .event-calendar-type {{
            color: {OVERVIEW_COLOR_TEXT_INVERSE};
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            white-space: nowrap;
            border-radius: 999px;
            padding: 2px 5px;
          }}
          .event-calendar-type-fomc {{ background: {OVERVIEW_COLOR_PRIMARY}; }}
          .event-calendar-type-macro {{ background: {OVERVIEW_COLOR_POSITIVE}; }}
          .event-calendar-type-earnings {{ background: {OVERVIEW_COLOR_WARNING}; }}
          .event-calendar-type-other {{ background: {OVERVIEW_COLOR_NEUTRAL}; }}
          .event-calendar-text {{
            color: {OVERVIEW_COLOR_TEXT};
            font-size: 11px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            min-width: 0;
          }}
          .event-calendar-importance-high {{
            border-color: rgba(180, 83, 9, 0.35);
          }}
          .event-calendar-more {{
            color: {OVERVIEW_COLOR_NEUTRAL};
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
          }}
          @media (max-width: 760px) {{
            .event-calendar-topbar {{ flex-direction: column; }}
            .event-calendar-legend {{ justify-content: flex-start; max-width: 100%; }}
            .event-calendar-weekday {{ padding: 6px 4px; font-size: 10px; }}
            .event-calendar-day {{ min-height: 92px; padding: 5px; }}
            .event-calendar-item {{ display: block; padding: 3px 4px; }}
            .event-calendar-type {{ display: block; font-size: 9px; }}
            .event-calendar-text {{ display: block; font-size: 10px; }}
          }}
        </style>
        <div class="event-calendar-shell">
          <div class="event-calendar-topbar">
            <div>
              <div class="event-calendar-title">{escape(month_label)}</div>
              <div class="event-calendar-subtitle">{event_count} events · {high_impact_count} high impact</div>
            </div>
            <div class="event-calendar-legend">{legend_html}</div>
          </div>
          <div class="event-calendar-grid">
            {weekday_html}
            {"".join(day_cells)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _event_focus_display_columns(rows: pd.DataFrame) -> list[str]:
    return [
        column
        for column in [
            "Date",
            "Days Until",
            "Type Label",
            "Symbol",
            "Title",
            "Importance",
            "Focus",
            "Validation",
            "Quality Action",
            "Freshness",
        ]
        if column in rows.columns
    ]


def _has_event_refresh_result() -> bool:
    return any(
        isinstance(st.session_state.get(key), dict)
        for key in [
            "overview_fomc_calendar_result",
            "overview_earnings_calendar_result",
            "overview_macro_calendar_result",
        ]
    )


def _render_events_tab() -> None:
    st.markdown("### Events")
    event_filter = _render_event_refresh_toolbar()

    selected_event_type = None if event_filter == "ALL" else event_filter
    snapshot = load_overview_market_events_snapshot(event_type=selected_event_type, horizon_days=540)
    coverage = dict(snapshot.get("coverage") or {})
    rows = snapshot.get("rows")
    calendar_rows = _prepare_event_calendar_frame(rows) if isinstance(rows, pd.DataFrame) else pd.DataFrame()
    if _has_event_refresh_result():
        with st.expander("Refresh Results", expanded=False):
            _render_market_job_result("overview_fomc_calendar_result")
            _render_market_job_result("overview_earnings_calendar_result")
            _render_market_job_result("overview_macro_calendar_result")
    render_events_summary_strip(_event_summary_items(calendar_rows, coverage, event_type=snapshot.get("event_type")))
    render_event_source_lane(_event_source_items(calendar_rows, event_filter=event_filter))
    render_event_warning_strip(list(snapshot.get("warnings") or []))
    render_macro_week_lane(load_overview_macro_week_lane(snapshot))

    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("Stored market event rows are not available for the selected filter. Run the matching refresh here or from Ingestion.")
        return

    filtered_rows = _filter_event_rows_for_calendar(calendar_rows)

    agenda_tab, calendar_tab, quality_tab, raw_tab = st.tabs(["Agenda", "Calendar", "Quality", "Raw"])
    with agenda_tab:
        render_event_agenda_sections(
            _event_agenda_sections(filtered_rows),
            empty_message="No upcoming event rows match the selected filters.",
        )
    with calendar_tab:
        _render_event_month_grid(filtered_rows)
        st.altair_chart(_build_event_calendar_chart(filtered_rows), width="stretch")
    with quality_tab:
        render_event_agenda_sections(
            _event_quality_sections(filtered_rows),
            empty_message="No event rows currently need source or validation review.",
        )
        quality_rows = _event_quality_rows(filtered_rows)
        if not quality_rows.empty:
            st.dataframe(
                quality_rows[_event_focus_display_columns(quality_rows)],
                width="stretch",
                hide_index=True,
            )
    with raw_tab:
        st.dataframe(filtered_rows.drop(columns=["Date Parsed"], errors="ignore"), width="stretch", hide_index=True)


def _overview_active_tab_label(value: str | None) -> str:
    label = str(value or "").strip()
    if label in OVERVIEW_DEEP_TAB_OPTIONS:
        return label
    return OVERVIEW_DEEP_TAB_OPTIONS[0]


def _overview_tab_label_from_slug(value: Any) -> str | None:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    for label, slug in OVERVIEW_DEEP_TAB_SLUGS.items():
        if normalized == slug:
            return label
    return None


def _overview_query_tab_label() -> str | None:
    query_params = getattr(st, "query_params", None)
    if query_params is None:
        return None
    try:
        raw_value = query_params.get(OVERVIEW_DEEP_TAB_QUERY_PARAM)
    except Exception:
        return None
    if isinstance(raw_value, list):
        raw_value = raw_value[-1] if raw_value else None
    return _overview_tab_label_from_slug(raw_value)


def _overview_tab_display_label(label: str) -> str:
    active_label = _overview_active_tab_label(label)
    primary, secondary = OVERVIEW_DEEP_TAB_DISPLAY[active_label]
    return f"{primary} · {secondary}"


def _overview_tab_seed_label(
    *,
    query_label: str | None,
    widget_value: str | None,
    session_value: str | None,
) -> str:
    if widget_value in OVERVIEW_DEEP_TAB_OPTIONS:
        return _overview_active_tab_label(widget_value)
    if query_label in OVERVIEW_DEEP_TAB_OPTIONS:
        return _overview_active_tab_label(query_label)
    return _overview_active_tab_label(session_value)


def _overview_tab_nav_css() -> str:
    return (
        """
<style>
/* ov-primary-nav: scoped override for the Overview st.pills selector. */
.st-key-overview_active_deep_tab_widget [data-testid="stButtonGroup"] {
  margin: 0.42rem 0 1.08rem 0;
  padding: 0;
  border-bottom: 1px solid rgba(100, 116, 139, 0.24);
}
.st-key-overview_active_deep_tab_widget div[data-baseweb="button-group"] {
  gap: 1.45rem;
  align-items: flex-end;
}
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pills"],
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pillsActive"] {
  min-height: 2.15rem;
  padding: 0 0 0.62rem 0;
  border: 0 !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0;
  background: transparent !important;
  color: rgba(100, 116, 139, 0.95);
  color: color-mix(in srgb, var(--text-color) 70%, transparent);
  box-shadow: none !important;
  font-weight: 650;
  letter-spacing: 0;
}
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pillsActive"] {
  border-bottom-color: #ff4b4b !important;
  background: transparent !important;
  color: #ff4b4b !important;
  box-shadow: none !important;
}
.st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pills"]:hover {
  color: #ff4b4b;
  background: transparent !important;
}
@media (max-width: 760px) {
  .st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pills"],
  .st-key-overview_active_deep_tab_widget [data-testid="stBaseButton-pillsActive"] {
    min-height: 2.1rem;
    padding-bottom: 0.55rem;
  }
}
</style>
"""
    )


def _render_overview_tab_selector() -> str:
    current = _overview_tab_seed_label(
        query_label=_overview_query_tab_label(),
        widget_value=st.session_state.get(OVERVIEW_DEEP_TAB_WIDGET_KEY),
        session_value=st.session_state.get(OVERVIEW_DEEP_TAB_KEY),
    )

    st.markdown(_overview_tab_nav_css(), unsafe_allow_html=True)
    selected = st.pills(
        "Overview 영역",
        OVERVIEW_DEEP_TAB_OPTIONS,
        selection_mode="single",
        default=current,
        required=True,
        format_func=_overview_tab_display_label,
        key=OVERVIEW_DEEP_TAB_WIDGET_KEY,
        label_visibility="collapsed",
        width="stretch",
    )
    selected_label = _overview_active_tab_label(str(selected or current))
    st.session_state[OVERVIEW_DEEP_TAB_KEY] = selected_label
    return selected_label


def _render_selected_overview_tab(
    selected_label: str | None,
    *,
    renderers: dict[str, Callable[[], None]],
) -> None:
    active_label = _overview_active_tab_label(selected_label)
    renderer = renderers.get(active_label) or renderers.get(OVERVIEW_DEEP_TAB_OPTIONS[0])
    if callable(renderer):
        renderer()


# Render the top-level product dashboard for Workspace > Overview.
def render_overview_dashboard(
    *,
    runtime_marker: str,
    loaded_at: datetime,
    git_sha: str | None,
    latest_result: dict[str, Any] | None = None,
    recent_results: list[dict[str, Any]] | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    st.title("Overview")
    st.caption("저장된 시장 자료를 브리프처럼 읽고, 필요한 세부 근거는 각 탭에서 이어서 확인합니다.")
    render_market_session_banner(_market_session_banner_model())

    active_tab = _render_overview_tab_selector()
    _render_selected_overview_tab(
        active_tab,
        renderers={
            "Market Context": _render_overview_market_context_tab,
            "Market Movers": _render_market_movers_tab,
            "Futures Macro": _render_futures_macro_tab,
            "Sentiment": _render_market_sentiment_tab,
            "Events": _render_events_tab,
        },
    )
