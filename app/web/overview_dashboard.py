from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from html import escape
from inspect import signature
from typing import Any, Callable
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.run_history import append_run_history
from app.jobs.overview_automation import run_overview_automation
from app.jobs.ingestion_jobs import (
    run_diagnose_market_quote_gaps,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_futures_ohlcv,
    run_collect_macro_calendar,
    run_collect_market_sentiment,
    run_collect_market_intraday_snapshot,
    run_collect_sp500_universe,
)
from app.services.futures_macro_thermometer import (
    clear_overview_futures_macro_snapshot_cache,
    load_overview_futures_macro_snapshot,
)
from app.services.futures_market_monitoring import load_overview_futures_monitor_snapshot
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.overview_dashboard_helpers import (
    load_overview_collection_ops_snapshot,
    load_overview_dashboard_snapshot,
    load_overview_group_leadership_snapshot,
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
    render_event_agenda_sections,
    render_event_source_lane,
    render_event_warning_strip,
    render_events_summary_strip,
    render_market_session_banner,
    render_market_auto_message,
    render_market_auto_waiting_panel,
    render_overview_toolbar_label,
    render_market_refresh_status_bar,
    render_market_snapshot_meta_strip,
)
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS


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
}
MARKET_COVERAGE_OPTIONS = tuple(MARKET_COVERAGE_LABELS.keys())
MARKET_UNIVERSE_LIMITS = {
    "SP500": 500,
    "TOP1000": 1000,
    "TOP2000": 2000,
}
MARKET_MOVER_PERIOD_LABELS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "yearly": "Yearly",
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
    "Optional Micro",
    "Optional Crypto",
    "All",
)
FUTURES_LOOKBACK_OPTIONS = {
    "2H": 120,
    "6H": 360,
    "12H": 720,
    "1D": 1440,
}
FUTURES_CHART_INTERVAL_OPTIONS = ("1m", "5m", "15m", "60m")
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
        "auto_60s": "60초 자동",
        "fast_20s": "20초 Fast",
    }.get(value, value)


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


def _option_index(options: list[str], current: Any, *, default: int = 0) -> int:
    try:
        return options.index(str(current))
    except ValueError:
        return default


# Render one ranked candidate card in the Overview priority section.
def _render_priority_candidate_card(candidate: dict[str, Any], rank: int) -> None:
    cagr = candidate.get("cagr")
    mdd = candidate.get("mdd")
    cagr_text = f"{float(cagr):.2f}%" if cagr is not None else "-"
    mdd_text = f"{float(mdd):.2f}%" if mdd is not None else "-"
    st.markdown(f"##### #{rank} {candidate.get('title') or '-'}")
    render_badge_strip(
        [
            {"label": "Score", "value": f"{candidate.get('score')} / 10", "tone": "positive"},
            {"label": "Family", "value": candidate.get("family") or "-", "tone": "neutral"},
            {"label": "Pre-Live", "value": candidate.get("pre_live_status") or "-", "tone": "positive"},
        ]
    )
    render_status_card_grid(
        [
            {"title": "CAGR", "value": cagr_text, "tone": "positive"},
            {"title": "MDD", "value": mdd_text, "tone": "warning"},
            {"title": "Promotion", "value": candidate.get("promotion") or "-", "tone": "neutral"},
        ]
    )
    st.caption(str(candidate.get("next_action") or ""))


# Build an Altair donut chart for the candidate/proposal funnel.
def _build_funnel_chart(funnel_rows: pd.DataFrame) -> alt.Chart:
    chart_rows = funnel_rows.copy()
    if chart_rows.empty or int(chart_rows["Count"].sum()) <= 0:
        chart_rows = pd.DataFrame([{"Stage": "No Data", "Count": 1}])
    total_count = max(1, int(chart_rows["Count"].sum()))
    return (
        alt.Chart(chart_rows)
        .mark_arc(innerRadius=58, outerRadius=96, stroke=OVERVIEW_COLOR_TEXT_INVERSE)
        .encode(
            theta=alt.Theta("Count:Q", stack=True, scale=alt.Scale(domain=[0, total_count])),
            color=alt.Color(
                "Stage:N",
                scale=alt.Scale(
                    range=[
                        OVERVIEW_COLOR_POSITIVE,
                        OVERVIEW_COLOR_PRIMARY,
                        OVERVIEW_COLOR_WARNING,
                        OVERVIEW_COLOR_NEUTRAL,
                        OVERVIEW_COLOR_SOFT,
                    ]
                ),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=["Stage:N", "Count:Q"],
        )
        .properties(height=260)
    )


# Render the next-action list as compact operator cards.
def _render_next_actions(actions: list[dict[str, Any]]) -> None:
    for action in actions:
        priority = str(action.get("priority") or "Low")
        tone = "danger" if priority == "High" else "warning" if priority == "Medium" else "neutral"
        with st.container(border=True):
            render_badge_strip(
                [
                    {"label": "Priority", "value": priority, "tone": tone},
                    {"label": "Target", "value": action.get("target") or "-", "tone": "neutral"},
                ]
            )
            st.markdown(f"**{escape(str(action.get('title') or '-'))}**")
            st.caption(str(action.get("detail") or ""))


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
                        run_diagnose_market_quote_gaps(
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
        append_run_history(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _status_tone(status: Any) -> str:
    normalized = str(status or "").lower()
    if normalized in {"success", "dry_run"}:
        return "positive"
    if normalized in {"partial_success", "skipped", "locked"}:
        return "warning"
    if normalized in {"failed", "error"}:
        return "danger"
    return "neutral"


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
    try:
        summary = run_overview_automation(
            profile=profile,
            job_ids=[job_id],
            execution_mode="browser_auto",
        )
    except RuntimeError as exc:
        summary = {
            "job_name": "overview_automation",
            "status": "locked",
            "profile": profile,
            "execution_mode": "browser_auto",
            "started_at": checked_at,
            "finished_at": checked_at,
            "jobs_due": 1,
            "jobs_run": 0,
            "plan": [],
            "results": [],
            "message": str(exc),
        }
    except Exception as exc:  # pragma: no cover - UI resilience only
        summary = {
            "job_name": "overview_automation",
            "status": "failed",
            "profile": profile,
            "execution_mode": "browser_auto",
            "started_at": checked_at,
            "finished_at": checked_at,
            "jobs_due": None,
            "jobs_run": 0,
            "plan": [],
            "results": [],
            "message": str(exc),
        }
    summary["selected_universe_code"] = str(universe_code or "SP500").strip().upper()
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


def _run_collect_market_intraday_snapshot_compat(
    *,
    universe_code: str,
    universe_limit: int,
) -> dict[str, Any]:
    refresh_kwargs: dict[str, Any] = {
        "universe_code": universe_code,
        "universe_limit": universe_limit,
        "interval": "5m",
        "chunk_size": 100,
        "quote_batch_size": 200,
        "method": "quote_fast",
        "fallback_to_yfinance": universe_code == "SP500",
    }
    supported_params = signature(run_collect_market_intraday_snapshot).parameters
    supported_kwargs = {key: value for key, value in refresh_kwargs.items() if key in supported_params}
    return run_collect_market_intraday_snapshot(**supported_kwargs)


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


def _run_collect_futures_ohlcv_compat(
    *,
    symbols: list[str],
    cadence_mode: str,
) -> dict[str, Any]:
    refresh_kwargs: dict[str, Any] = {
        "symbols": symbols,
        "period": "1d",
        "interval": "1m",
        "cadence_mode": cadence_mode,
        "max_symbols": max(1, min(24, len(symbols))),
        "batch_size": 6,
        "sleep_sec": 0.1,
    }
    supported_params = signature(run_collect_futures_ohlcv).parameters
    supported_kwargs = {key: value for key, value in refresh_kwargs.items() if key in supported_params}
    return run_collect_futures_ohlcv(**supported_kwargs)


def _run_collect_futures_daily_ohlcv_compat() -> dict[str, Any]:
    refresh_kwargs: dict[str, Any] = {
        "symbols": list(DEFAULT_CORE_FUTURES_SYMBOLS),
        "period": "5y",
        "interval": "1d",
        "cadence_mode": "manual_macro_daily",
        "max_symbols": len(DEFAULT_CORE_FUTURES_SYMBOLS),
        "batch_size": 6,
        "sleep_sec": 0.1,
    }
    supported_params = signature(run_collect_futures_ohlcv).parameters
    supported_kwargs = {key: value for key, value in refresh_kwargs.items() if key in supported_params}
    return run_collect_futures_ohlcv(**supported_kwargs)


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


def _futures_chart_symbols(snapshot: dict[str, Any]) -> list[str]:
    symbols = [str(symbol) for symbol in snapshot.get("symbols") or [] if str(symbol).strip()]
    ordered: list[str] = []
    for symbol in symbols:
        if symbol and symbol not in ordered:
            ordered.append(symbol)
        if len(ordered) >= 6:
            break
    return ordered


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
        return f"{float(value):.0f}m"
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
                "60m",
                _format_futures_percent(metric.get("60m %")),
                _futures_value_tone(metric.get("60m %")),
            ),
            _futures_chart_metric_chip(
                "15m",
                _format_futures_percent(metric.get("15m %")),
                _futures_value_tone(metric.get("15m %")),
            ),
            _futures_chart_metric_chip("Age", _format_futures_age(metric.get("Age Min")), state_tone),
        ]
    )
    st.markdown(
        f"""
        <div class="ov-futures-chart-head">
          <div>
            <div class="ov-futures-chart-title">{escape(symbol)}</div>
            <div class="ov-futures-chart-subtitle">{escape(_futures_contract_title(metric, symbol))}</div>
          </div>
          <span class="ov-futures-chart-state" style="--ov-chart-tone:{_overview_tone_color(state_tone)};">{escape(state)} · {_format_futures_age(metric.get("Age Min"))}</span>
        </div>
        <div class="ov-futures-chart-metrics">{metric_html}</div>
        """,
        unsafe_allow_html=True,
    )


def _futures_live_signal_cards(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    coverage = dict(snapshot.get("coverage") or {})
    top_move = dict(snapshot.get("top_move") or {})
    latest_run = dict(snapshot.get("latest_run") or {})
    latest_age = coverage.get("latest_age_minutes")
    latest_run_status = latest_run.get("status") or "-"
    return [
        {
            "label": "Status",
            "value": snapshot.get("status") or "-",
            "detail": f"{coverage.get('returnable_count') or 0}/{coverage.get('symbol_count') or 0} symbols",
            "tone": "positive" if snapshot.get("status") == "OK" else "warning",
        },
        {
            "label": "Top Move",
            "value": top_move.get("Symbol") or "-",
            "detail": (
                f"15m {_format_futures_percent(top_move.get('15m %'))} · 60m {_format_futures_percent(top_move.get('60m %'))}"
                if top_move.get("Symbol")
                else "waiting for candles"
            ),
            "tone": _futures_state_tone(str(top_move.get("State") or "")),
        },
        {
            "label": "Freshness",
            "value": _format_futures_age(latest_age),
            "detail": f"oldest {_format_futures_age(coverage.get('oldest_age_minutes'))}",
            "tone": (
                "positive"
                if latest_age is not None and not pd.isna(latest_age) and int(latest_age or 0) <= 2
                else "warning"
            ),
        },
        {
            "label": "Provider Run",
            "value": latest_run_status,
            "detail": f"{latest_run.get('rows_written') or 0} rows · yfinance",
            "tone": _status_tone(latest_run_status),
        },
    ]


def _futures_contract_title(metric: dict[str, Any], symbol: str) -> str:
    name = str(metric.get("Name") or "").strip()
    group = str(metric.get("Group") or "").strip()
    if name and group:
        return f"{name} · {group}"
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
        label = "Missing"
        detail = "no stored candles"
        tone = "danger"
    else:
        age_value = int(latest_age or 0)
        if age_value <= 2 and status == "OK":
            label = "Fresh"
            detail = f"latest {age_value}m"
            tone = "positive"
        elif age_value <= 10:
            label = "Review"
            detail = f"latest {age_value}m"
            tone = "warning"
        else:
            label = "Stale"
            detail = f"latest {age_value}m"
            tone = "danger"
    cadence = "manual"
    if refresh_mode == "auto_60s":
        cadence = "60s browser auto"
    elif refresh_mode == "fast_20s":
        cadence = "20s browser auto"
    return {
        "label": label,
        "detail": detail,
        "tone": tone,
        "cadence": cadence,
        "latest_age": latest_age,
        "oldest_age": oldest_age,
    }


def _render_futures_command_center(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    refresh_mode: str,
) -> None:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    coverage = dict(snapshot.get("coverage") or {})
    top_move = dict(snapshot.get("top_move") or {})
    latest_run = dict(snapshot.get("latest_run") or {})
    tone_color = _overview_tone_color(str(feed.get("tone") or "neutral"))
    symbols_label = ", ".join(selected_symbols[:6]) if selected_symbols else "-"
    if len(selected_symbols) > 6:
        symbols_label = f"{symbols_label} +{len(selected_symbols) - 6}"
    latest_run_label = str(latest_run.get("status") or "-")
    latest_run_detail = (
        f"{latest_run.get('rows_written') or 0} rows · {_snapshot_value(latest_run.get('latest_candle_time_utc'))}"
        if latest_run
        else "no provider run"
    )
    st.markdown(
        f"""
        <div class="ov-futures-command">
          <div class="ov-futures-command-cell">
            <div class="ov-futures-kicker">Futures Workspace</div>
            <div class="ov-futures-title">{escape(group)} · {len(selected_symbols)} selected</div>
            <div class="ov-futures-detail">{escape(symbols_label)}</div>
            <div class="ov-futures-feed-row">
              <span class="ov-futures-feed-pill" style="--ov-feed-tone: {tone_color};">{escape(str(feed.get("label") or "-"))}</span>
              <span class="ov-futures-feed-pill" style="--ov-feed-tone: {OVERVIEW_COLOR_NEUTRAL};">{escape(str(feed.get("cadence") or "-"))}</span>
            </div>
          </div>
          <div class="ov-futures-command-cell">
            <div class="ov-futures-kicker">Market Pulse</div>
            <div class="ov-futures-title">{escape(str(top_move.get("Symbol") or "-"))}</div>
            <div class="ov-futures-detail">15m {_format_futures_percent(top_move.get("15m %"))} · 60m {_format_futures_percent(top_move.get("60m %"))}</div>
            <div class="ov-futures-feed-row">
              <span class="ov-futures-feed-pill" style="--ov-feed-tone: {_overview_tone_color(_futures_state_tone(str(top_move.get("State") or "")))};">{escape(str(top_move.get("State") or "Waiting"))}</span>
              <span class="ov-futures-feed-pill" style="--ov-feed-tone: {OVERVIEW_COLOR_NEUTRAL};">{escape(lookback_label)} · {escape(chart_interval)} candles</span>
            </div>
          </div>
          <div class="ov-futures-command-cell">
            <div class="ov-futures-kicker">Data Feed</div>
            <div class="ov-futures-title">{escape(str(feed.get("detail") or "-"))}</div>
            <div class="ov-futures-detail">{coverage.get("returnable_count") or 0} / {coverage.get("symbol_count") or 0} symbols · oldest {_format_futures_age(feed.get("oldest_age"))}</div>
            <div class="ov-futures-feed-row">
              <span class="ov-futures-feed-pill" style="--ov-feed-tone: {_overview_tone_color(_status_tone(latest_run_label))};">{escape(latest_run_label)}</span>
              <span class="ov-futures-feed-pill" style="--ov-feed-tone: {OVERVIEW_COLOR_NEUTRAL};">{escape(latest_run_detail)}</span>
            </div>
          </div>
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
    labels = {
        "Risk-On Score": "Risk-On",
        "Growth Score": "Growth",
        "Rate Pressure Score": "Rates",
        "Dollar Pressure Score": "Dollar",
        "Safe Haven Score": "Safe Haven",
        "Inflation Pressure Score": "Inflation",
    }
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return [{"label": "Macro", "value": "-", "tone": "neutral"}]
    badges: list[dict[str, Any]] = []
    for _, row in scores.iterrows():
        score_name = str(row.get("Score") or "-")
        badges.append(
            {
                "label": labels.get(score_name, score_name.replace(" Score", "")),
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


def _macro_signal_cards(macro: dict[str, Any]) -> list[dict[str, Any]]:
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
    scenario = dict(macro.get("summary") or {}).get("scenario") or "해석 대기"
    return [
        {
            "label": "Scenario",
            "value": scenario,
            "detail": "mixed는 억지 분류하지 않음",
            "tone": "primary",
        },
        {
            "label": "Confidence",
            "value": confidence.get("label") or "Not Enough History",
            "detail": ", ".join(list(confidence.get("reasons") or [])[:1]) or "validation pending",
            "tone": confidence.get("tone") or "warning",
        },
        {
            "label": "Validation",
            "value": validation.get("status") or "MISSING",
            "detail": f"{validation_dates} PIT dates · {span or '-'}y",
            "tone": "positive" if validation.get("status") == "OK" else "warning",
        },
        {
            "label": "History",
            "value": sample or occurrence_count or 0,
            "detail": (
                f"5D hit {_format_macro_percent(hit_rate)}"
                if hit_applicable
                else "occurrences, hit n/a"
            ),
            "tone": "positive" if int(sample or occurrence_count or 0) >= 60 else "warning",
        },
    ]


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


def _render_macro_validation_detail(validation: dict[str, Any]) -> None:
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    if current_metrics:
        hit_applicable = bool(current_metrics.get("Directional Hit Applicable"))
        render_badge_strip(
            [
                {
                    "label": "Current Scenario",
                    "value": current_metrics.get("Scenario") or "-",
                    "tone": "primary",
                },
                {
                    "label": "5D Sample" if hit_applicable else "Occurrences",
                    "value": current_metrics.get("Sample 5D") if hit_applicable else current_metrics.get("Occurrence Count") or 0,
                    "tone": "neutral",
                },
                {
                    "label": "5D Hit",
                    "value": _format_macro_percent(current_metrics.get("Hit Rate 5D %")) if hit_applicable else "N/A",
                    "tone": "positive" if hit_applicable and (current_metrics.get("Hit Rate 5D %") or 0) >= 55 else "warning",
                },
                {
                    "label": "5D False Positive",
                    "value": _format_macro_percent(current_metrics.get("False Positive 5D %")) if hit_applicable else "N/A",
                    "tone": "warning",
                },
                {
                    "label": "5D Max Adverse",
                    "value": _format_macro_percent(current_metrics.get("Max Adverse 5D %"), digits=2) if hit_applicable else "N/A",
                    "tone": "warning",
                },
            ]
        )
    scenario_summary = validation.get("scenario_summary")
    if isinstance(scenario_summary, pd.DataFrame) and not scenario_summary.empty:
        st.markdown("#### Historical Validation Summary")
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
        st.dataframe(
            scenario_summary[[col for col in preferred_cols if col in scenario_summary.columns]],
            width="stretch",
            hide_index=True,
        )
    relationships = validation.get("relationships")
    threshold_sensitivity = validation.get("threshold_sensitivity")
    if isinstance(relationships, pd.DataFrame) and not relationships.empty:
        with st.expander("Score / Forward Return Relationships", expanded=False):
            st.dataframe(relationships, width="stretch", hide_index=True)
    if isinstance(threshold_sensitivity, pd.DataFrame) and not threshold_sensitivity.empty:
        with st.expander("Score Threshold Sensitivity", expanded=False):
            st.dataframe(threshold_sensitivity, width="stretch", hide_index=True)


def _render_futures_macro_panel(*, detail_expanded: bool = False) -> None:
    macro = load_overview_futures_macro_snapshot()
    coverage = dict(macro.get("coverage") or {})
    scores = macro.get("scores")
    components = macro.get("score_components")
    symbols = macro.get("symbols")
    summary = dict(macro.get("summary") or {})
    confidence = dict(macro.get("confidence") or {})
    validation = dict(macro.get("validation") or {})

    _render_futures_section_header(
        "Macro Context",
        f"{coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0} daily symbols · {_snapshot_value(coverage.get('latest_daily_date'))}",
    )
    _render_futures_signal_strip(_macro_signal_cards(macro), class_prefix="ov-futures-macro")
    sentences = [str(sentence) for sentence in macro.get("summary_sentences") or [] if str(sentence).strip()]
    evidence = [str(item) for item in macro.get("evidence") or [] if str(item).strip()]
    st.markdown(
        f"""
        <div class="ov-futures-macro-hero">
          <div class="ov-futures-macro-scenario">{escape(str(summary.get('scenario') or '시장 해석 대기'))}</div>
          <div class="ov-futures-macro-sentence">{escape(sentences[0] if sentences else '저장된 일봉 선물 데이터로 시장 흐름을 해석합니다.')}</div>
          <div class="ov-futures-macro-evidence">{escape(' · '.join(evidence[:2]) if evidence else '주요 근거는 상세 영역에서 확인합니다.')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_macro_score_lane(scores)
    warnings = list(macro.get("warnings") or [])
    warnings.extend(str(item) for item in validation.get("warnings") or [])
    if warnings:
        _render_snapshot_warnings({"warnings": warnings})

    cautions = [str(item) for item in macro.get("cautions") or [] if str(item).strip()]
    cautions.extend(str(item) for item in validation.get("caveats") or [] if str(item).strip())
    with st.expander("Macro Evidence & Data", expanded=detail_expanded):
        _render_futures_section_header("Daily Data", "stored 1D futures OHLCV for macro scoring")
        data_cols = st.columns([1, 1.6], gap="medium", vertical_alignment="top")
        with data_cols[0]:
            if st.button(
                "Refresh Daily Macro OHLCV",
                key="overview_futures_macro_daily_refresh",
                use_container_width=True,
            ):
                with st.spinner("Collecting futures 5y daily OHLCV from yfinance..."):
                    _store_overview_job_result(
                        "overview_futures_daily_ohlcv_result",
                        _run_collect_futures_daily_ohlcv_compat(),
                    )
                    clear_overview_futures_macro_snapshot_cache()
                    st.session_state["overview_futures_macro_daily_refreshed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.rerun(scope="fragment")
        with data_cols[1]:
            _render_market_job_result("overview_futures_daily_ohlcv_result")

        _render_futures_section_header("Evidence Groups", "strong / weak / conflicting / missing symbols")
        _render_macro_evidence_groups(dict(macro.get("evidence_groups") or {}))
        _render_futures_section_header("Historical Validation", "past scenario consistency, thresholds, and relationships")
        _render_macro_validation_detail(validation)
        if isinstance(scores, pd.DataFrame) and not scores.empty:
            _render_futures_section_header("Score Table", "direction, coverage, and standardized move summary")
            st.dataframe(
                scores.drop(columns=["Tone"], errors="ignore"),
                width="stretch",
                hide_index=True,
            )
        if isinstance(components, pd.DataFrame) and not components.empty:
            _render_futures_section_header("Score Components", "ticker-level contribution by macro score")
            st.dataframe(components, width="stretch", hide_index=True)
        if isinstance(symbols, pd.DataFrame) and not symbols.empty:
            _render_futures_section_header("Symbol Standardized Moves", "daily standardized move per futures symbol")
            st.dataframe(symbols, width="stretch", hide_index=True)
        if cautions:
            _render_futures_section_header("Caveats", "interpretation limits and provider caveats")
            for caution in list(dict.fromkeys(cautions)):
                st.caption(caution)


def _render_futures_macro_fragment(*, detail_expanded: bool = False) -> None:
    @st.fragment
    def _futures_macro_context_fragment() -> None:
        _render_futures_macro_panel(detail_expanded=detail_expanded)

    _futures_macro_context_fragment()


def _render_futures_macro_tab() -> None:
    _render_futures_macro_fragment(detail_expanded=True)


def _render_futures_mini_chart_grid(snapshot: dict[str, Any], *, chart_interval: str) -> None:
    all_candles = snapshot.get("all_candles")
    rows = snapshot.get("rows")
    symbols = _futures_chart_symbols(snapshot)
    if not symbols:
        st.info("No futures symbols are selected.")
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
                    st.info("No candles.")
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


def _render_futures_live_panel(snapshot: dict[str, Any], *, chart_interval: str, lookback_label: str) -> None:
    rows = snapshot.get("rows")
    state_counts = rows["State"].value_counts().to_dict() if isinstance(rows, pd.DataFrame) and not rows.empty and "State" in rows else {}
    selected_count = len([symbol for symbol in snapshot.get("symbols") or [] if str(symbol).strip()])
    _render_futures_section_header(
        "Live Futures Charts",
        f"{selected_count} selected futures · {chart_interval} candles · {lookback_label} window",
    )
    _render_futures_signal_strip(_futures_live_signal_cards(snapshot), class_prefix="ov-futures-live")
    warnings = list(snapshot.get("warnings") or [])
    if warnings:
        _render_snapshot_warnings({"warnings": warnings})
    if state_counts:
        state_html = "".join(
            _futures_chart_metric_chip(str(state), str(int(count)), _futures_state_tone(str(state)))
            for state, count in state_counts.items()
        )
        st.markdown(f'<div class="ov-futures-chart-metrics">{state_html}</div>', unsafe_allow_html=True)

    _render_futures_mini_chart_grid(snapshot, chart_interval=chart_interval)


def _render_futures_diagnostics(snapshot: dict[str, Any]) -> None:
    rows = snapshot.get("rows")
    candles = snapshot.get("candles")
    latest_run = snapshot.get("latest_run")
    with st.expander("Diagnostics & Provider Evidence", expanded=False):
        st.markdown("#### Shock Board")
        if isinstance(rows, pd.DataFrame) and not rows.empty:
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.info("Stored futures OHLCV rows are not available yet. Run Refresh Futures OHLCV first.")
        st.markdown("#### Provider Run")
        if isinstance(latest_run, dict) and latest_run:
            metric_cols = st.columns(4)
            metric_cols[0].metric("Status", latest_run.get("status") or "-")
            metric_cols[1].metric("Rows", latest_run.get("rows_written") or 0)
            metric_cols[2].metric("Processed", f"{latest_run.get('symbols_processed') or 0} / {latest_run.get('symbols_requested') or 0}")
            metric_cols[3].metric("Latest Candle", _snapshot_value(latest_run.get("latest_candle_time_utc")))
            st.caption(str(latest_run.get("message") or snapshot.get("source_note") or ""))
        else:
            st.info("No futures provider run has been recorded yet.")
        _render_market_job_result("overview_futures_ohlcv_result")
        if isinstance(candles, pd.DataFrame) and not candles.empty:
            st.markdown("#### Selected Candle Rows")
            st.dataframe(candles.tail(80), width="stretch", hide_index=True)


def _render_futures_live_workspace(
    snapshot: dict[str, Any],
    *,
    group: str,
    selected_symbols: list[str],
    selected_symbol: str,
    lookback_label: str,
    chart_interval: str,
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
            with st.spinner("Checking futures auto refresh..."):
                _store_overview_job_result(
                    "overview_futures_ohlcv_result",
                    _run_collect_futures_ohlcv_compat(symbols=selected_symbols, cadence_mode="browser_auto"),
                )
            refreshed_snapshot = _load_live_snapshot()
            _render_futures_live_panel(refreshed_snapshot, chart_interval=chart_interval, lookback_label=lookback_label)
            _render_futures_diagnostics(refreshed_snapshot)

        _futures_live_auto_panel()
        return

    _render_futures_live_panel(snapshot, chart_interval=chart_interval, lookback_label=lookback_label)
    _render_futures_diagnostics(snapshot)


def _render_futures_monitor_tab() -> None:
    st.markdown("### Futures Monitor")
    st.caption("미국장 / 한국장 전 주요 선물 OHLCV와 급변 상태를 read-only로 확인합니다.")

    control_cols = st.columns([0.95, 2.45, 0.75, 0.75, 0.8], gap="small", vertical_alignment="bottom")
    group = str(
        control_cols[0].selectbox(
            "Watch Group",
            FUTURES_GROUP_OPTIONS,
            index=0,
            key="overview_futures_watch_group",
        )
    )
    lookback_label = str(
        control_cols[2].selectbox(
            "Window",
            list(FUTURES_LOOKBACK_OPTIONS.keys()),
            index=1,
            key="overview_futures_lookback",
        )
    )
    chart_key = "overview_futures_chart_interval"
    if st.session_state.get(chart_key) == "1h":
        st.session_state[chart_key] = "60m"
    chart_interval = str(
        control_cols[3].selectbox(
            "Chart",
            FUTURES_CHART_INTERVAL_OPTIONS,
            index=1,
            key=chart_key,
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
    selected_symbols = list(
        control_cols[1].multiselect(
            "Symbols",
            options=symbol_options,
            default=default_symbols,
            key=symbols_key,
        )
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
    if len(selected_symbols) <= 4:
        mode_options.append("fast_20s")
    mode_key = "overview_futures_refresh_mode"
    if st.session_state.get(mode_key) not in mode_options:
        st.session_state[mode_key] = "manual"
    refresh_mode = str(st.session_state.get(mode_key) or "manual")
    with control_cols[4].popover("Data Actions", use_container_width=True):
        segmented_control = getattr(st, "segmented_control", None)
        if callable(segmented_control):
            refresh_mode = str(
                segmented_control(
                    "Refresh",
                    mode_options,
                    key=mode_key,
                    format_func=_futures_refresh_mode_label,
                    help="20초 Fast는 선택 심볼 4개 이하일 때만 사용합니다.",
                )
            )
        else:
            refresh_mode = str(
                st.radio(
                    "Refresh",
                    mode_options,
                    key=mode_key,
                    format_func=_futures_refresh_mode_label,
                    horizontal=True,
                    help="20초 Fast는 선택 심볼 4개 이하일 때만 사용합니다.",
                )
            )
        if st.button(
            "Refresh Futures OHLCV",
            key="overview_futures_manual_refresh",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("Collecting futures 1m OHLCV from yfinance..."):
                _store_overview_job_result(
                    "overview_futures_ohlcv_result",
                    _run_collect_futures_ohlcv_compat(symbols=selected_symbols, cadence_mode="manual"),
                )
            snapshot = load_overview_futures_monitor_snapshot(
                group=group,
                symbols=selected_symbols,
                selected_symbol=selected_symbol,
                lookback_minutes=FUTURES_LOOKBACK_OPTIONS[lookback_label],
            )
        if st.button("화면 새로고침", key="overview_futures_reload", use_container_width=True):
            st.session_state["overview_futures_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
        st.markdown(
            '<div class="ov-futures-control-note">Provider fetch는 기본 60초 단위입니다. 현재 브라우저 세션이 열려 있을 때만 auto fragment가 확인합니다.</div>',
            unsafe_allow_html=True,
        )

    _render_futures_command_center(
        snapshot=snapshot,
        group=group,
        selected_symbols=selected_symbols,
        lookback_label=lookback_label,
        chart_interval=chart_interval,
        refresh_mode=refresh_mode,
    )
    _render_futures_macro_fragment(detail_expanded=False)
    st.divider()
    _render_futures_live_workspace(
        snapshot,
        group=group,
        selected_symbols=selected_symbols,
        selected_symbol=selected_symbol,
        lookback_label=lookback_label,
        chart_interval=chart_interval,
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
                    run_collect_fomc_calendar(years=(current_year, current_year + 1)),
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
                    run_collect_earnings_calendar(
                        symbol_source="latest_movers",
                        universe_code="SP500",
                        top_movers_limit=20,
                        lookahead_days=120,
                        max_symbols=50,
                        validate_with_nasdaq=True,
                    ),
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
                    run_collect_macro_calendar(years=(current_year, current_year + 1)),
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


def _render_market_movers_refresh_bar(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> None:
    if period != "daily":
        return

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
                _run_collect_market_intraday_snapshot_compat(
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
            _store_overview_job_result("overview_sp500_universe_result", run_collect_sp500_universe())
        st.rerun()
    if universe_code != "SP500":
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
    _render_market_job_result(intraday_result_key)


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
    st.markdown("### Sector / Industry Leadership")
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

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed group leadership rows are not available for the selected controls.")
        return
    trend_rows = snapshot.get("trend_rows")
    ticker_leader_rows = snapshot.get("ticker_leader_rows")
    chart_tab, table_tab = st.tabs(["Trend", "Table"])
    with chart_tab:
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
    with table_tab:
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


def _render_market_sentiment_tab() -> None:
    st.markdown("### Sentiment")
    control_cols = st.columns([1.1, 1, 1], gap="small", vertical_alignment="bottom")
    if control_cols[0].button(
        "시장 심리 갱신",
        key="overview_market_sentiment_refresh",
        use_container_width=True,
        type="primary",
    ):
        with st.spinner("Refreshing CNN Fear & Greed / AAII sentiment..."):
            _store_overview_job_result("overview_market_sentiment_result", run_collect_market_sentiment())
            load_overview_market_sentiment_snapshot.clear()
        st.rerun()
    if control_cols[1].button(
        "화면 새로고침",
        key="overview_market_sentiment_reload",
        use_container_width=True,
    ):
        load_overview_market_sentiment_snapshot.clear()
        st.rerun()
    control_cols[2].caption("CNN / AAII stored observations")

    _render_market_job_result("overview_market_sentiment_result")
    snapshot = load_overview_market_sentiment_snapshot()
    coverage = dict(snapshot.get("coverage") or {})
    render_status_card_grid(
        [
            {
                "title": "Sentiment Status",
                "value": snapshot.get("status") or "-",
                "detail": f"{coverage.get('missing_count') or 0} missing · {coverage.get('stale_count') or 0} stale",
                "tone": _sentiment_status_tone(snapshot.get("status")),
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

    trend_tab, components_tab, table_tab = st.tabs(["Trend", "CNN Components", "Table"])
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
    future_rows = focus_rows[focus_rows["Days Until"].isna() | (focus_rows["Days Until"] >= 0)].sort_values(
        ["Date Parsed", "Importance", "Type Label", "Symbol"],
        ascending=[True, True, True, True],
    )
    section_specs = [
        ("Today", future_rows["Days Until"] == 0, 8),
        ("This Week", (future_rows["Days Until"] > 0) & (future_rows["Days Until"] <= 7), 10),
        ("Next 30D", (future_rows["Days Until"] > 7) & (future_rows["Days Until"] <= 30), 12),
        ("Later", future_rows["Days Until"] > 30, 12),
    ]
    sections: list[dict[str, Any]] = []
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


def _ops_tone(status: str) -> str:
    normalized = str(status or "").lower()
    if normalized == "ok":
        return "positive"
    if normalized in {"due", "partial"}:
        return "warning"
    if normalized in {"failed", "stale", "missing"}:
        return "danger"
    return "neutral"


def _render_collection_ops_tab() -> None:
    st.markdown("### Data Health")
    st.caption("Stored DB freshness and local collection run history for Overview market intelligence.")
    warning = st.session_state.get("overview_run_history_warning")
    if warning:
        st.warning(str(warning))

    snapshot = load_overview_collection_ops_snapshot()
    coverage = dict(snapshot.get("coverage") or {})
    review_count = sum(
        int(coverage.get(key) or 0)
        for key in ("due_count", "stale_count", "missing_count", "failed_count", "partial_count")
    )
    render_status_card_grid(
        [
            {
                "title": "Ops Status",
                "value": snapshot.get("status") or "-",
                "detail": f"{review_count} item(s) need review",
                "tone": "positive" if snapshot.get("status") == "OK" else "warning",
            },
            {
                "title": "Healthy",
                "value": f"{coverage.get('ok_count') or 0} / {coverage.get('job_count') or 0}",
                "detail": "collection targets",
                "tone": "positive" if coverage.get("ok_count") else "neutral",
            },
            {
                "title": "Latest Success",
                "value": _snapshot_value(coverage.get("latest_success_at")),
                "detail": "from local run history",
                "tone": "positive" if coverage.get("latest_success_at") else "neutral",
            },
            {
                "title": "Latest Auto",
                "value": _snapshot_value(coverage.get("latest_auto_at")),
                "detail": "scheduled or browser auto",
                "tone": "positive" if coverage.get("latest_auto_at") else "neutral",
            },
            {
                "title": "Latest Issue",
                "value": _snapshot_value(coverage.get("latest_issue_at")),
                "detail": "failed or partial run",
                "tone": "danger" if coverage.get("latest_issue_at") else "neutral",
            },
            {
                "title": "Failure Streak",
                "value": coverage.get("max_failure_streak") or 0,
                "detail": "max consecutive issues",
                "tone": "danger" if int(coverage.get("max_failure_streak") or 0) else "positive",
            },
        ]
    )
    _render_snapshot_warnings(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("No collection ops status is available yet.")
        return

    status_counts = rows["Status"].value_counts().to_dict() if "Status" in rows else {}
    render_badge_strip(
        [
            {"label": str(status), "value": count, "tone": _ops_tone(str(status))}
            for status, count in status_counts.items()
        ]
    )
    st.dataframe(rows, width="stretch", hide_index=True)


def _render_candidate_ops_tab(
    *,
    snapshot: dict[str, Any],
    latest_result: dict[str, Any] | None,
    recent_results: list[dict[str, Any]],
    runtime_marker: str,
    loaded_at: datetime,
    git_sha: str | None,
    render_runtime_snapshot: Callable[[], None] | None,
) -> None:
    kpis = dict(snapshot["kpis"])

    render_status_card_grid(
        [
            {
                "title": "Current Candidates",
                "value": kpis["current_candidates"],
                "detail": "registry에 남은 활성 후보",
                "tone": "positive" if kpis["current_candidates"] else "neutral",
            },
            {
                "title": "Paper Tracking",
                "value": kpis["paper_tracking"],
                "detail": "실전 전 관찰 중",
                "tone": "positive" if kpis["paper_tracking"] else "neutral",
            },
            {
                "title": "Proposal Drafts",
                "value": kpis["proposal_drafts"],
                "detail": "저장된 구성 초안",
                "tone": "positive" if kpis["proposal_drafts"] else "neutral",
            },
            {
                "title": "Recent Runs",
                "value": kpis["recent_runs"],
                "detail": "persistent backtest history",
                "tone": "positive" if kpis["recent_runs"] else "warning",
            },
        ]
    )

    st.markdown("### 검토 우선 후보 Top 3")
    st.caption("성과 순위가 아니라 Real-Money 신호, Pre-Live 상태, 배포 blocker, CAGR/MDD를 함께 본 운영 검토 우선순위입니다.")
    top_candidates = list(snapshot["top_candidates"])
    if top_candidates:
        candidate_cols = st.columns(len(top_candidates), gap="small")
        for index, candidate in enumerate(top_candidates, start=1):
            with candidate_cols[index - 1].container(border=True):
                _render_priority_candidate_card(candidate, index)
    else:
        st.info("아직 Overview에 표시할 current candidate가 없습니다.")

    left, right = st.columns([1.05, 1.15], gap="medium")
    with left:
        st.markdown("### Candidate Funnel")
        st.caption("현재 후보가 어느 운영 단계에 쌓여 있는지 한눈에 봅니다.")
        st.altair_chart(_build_funnel_chart(snapshot["funnel_rows"]), width="stretch")
        st.dataframe(snapshot["funnel_rows"], width="stretch", hide_index=True)

    with right:
        st.markdown("### Next Actions")
        st.caption("다음에 눌러야 할 탭을 설명하는 운영 체크리스트입니다.")
        _render_next_actions(list(snapshot["next_actions"]))

    st.markdown("### Recent Activity")
    st.caption("최근 candidate, pre-live, proposal, backtest history 이벤트를 한 줄 피드로 확인합니다.")
    activity_rows = snapshot["activity_rows"]
    if activity_rows.empty:
        st.info("표시할 최근 활동이 없습니다.")
    else:
        st.dataframe(activity_rows, width="stretch", hide_index=True)

    latest_status = str((latest_result or {}).get("status") or "").upper()
    if latest_result:
        with st.expander("Session Latest Completed Run", expanded=False):
            label = str(latest_result.get("label") or latest_result.get("job_name") or "latest_run")
            run_time = latest_result.get("finished_at") or latest_result.get("started_at") or "-"
            render_status_card_grid(
                [
                    {"title": "Label", "value": label, "tone": "neutral"},
                    {"title": "Status", "value": latest_status or "-", "tone": "positive" if latest_status == "SUCCESS" else "warning"},
                    {"title": "Finished At", "value": str(run_time), "tone": "neutral"},
                ]
            )
    elif not snapshot["history_rows"] and not recent_results:
        st.info("아직 완료된 실행 기록이 없습니다. 먼저 `Ingestion`이나 `Backtest`에서 작업을 실행하면 Overview에도 요약이 보입니다.")

    with st.expander("System Snapshot", expanded=False):
        if render_runtime_snapshot:
            render_runtime_snapshot()
        else:
            render_status_card_grid(
                [
                    {"title": "Runtime Marker", "value": runtime_marker, "tone": "neutral"},
                    {"title": "Loaded At", "value": loaded_at.strftime("%Y-%m-%d %H:%M:%S"), "tone": "neutral"},
                    {"title": "Git SHA", "value": git_sha or "unknown", "tone": "neutral"},
                ]
            )


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
    snapshot = load_overview_dashboard_snapshot()
    recent_results = recent_results or []

    st.title("Finance Console")
    st.caption("시장 스캔, 후보 운영, Portfolio Proposal, 다음 행동을 한 화면에서 읽는 퀀트 워크벤치 대시보드입니다.")
    render_market_session_banner(_market_session_banner_model())

    market_tab, futures_tab, sentiment_tab, group_tab, events_tab, ops_tab, candidate_tab = st.tabs(
        ["Market Movers", "Futures Monitor", "Sentiment", "Sector / Industry", "Events", "Data Health", "Candidate Ops"]
    )
    with market_tab:
        _render_market_movers_tab()
    with futures_tab:
        _render_futures_monitor_tab()
    with sentiment_tab:
        _render_market_sentiment_tab()
    with group_tab:
        _render_sector_industry_tab()
    with events_tab:
        _render_events_tab()
    with ops_tab:
        _render_collection_ops_tab()
    with candidate_tab:
        _render_candidate_ops_tab(
            snapshot=snapshot,
            latest_result=latest_result,
            recent_results=recent_results,
            runtime_marker=runtime_marker,
            loaded_at=loaded_at,
            git_sha=git_sha,
            render_runtime_snapshot=render_runtime_snapshot,
        )
