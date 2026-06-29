from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_browser_auto_refresh,
    run_overview_market_intraday_snapshot,
    run_overview_market_movers_eod_history,
    run_overview_nasdaq_symbol_directory,
    run_overview_quote_gap_diagnostics,
    run_overview_sp500_universe,
)
from app.web.overview.session_helpers import _snapshot_status_items, _snapshot_value
from app.web.overview_dashboard_helpers import (
    load_overview_market_mover_sectors,
    load_overview_market_movers_snapshot,
)
from app.web.overview_ui_components import (
    OVERVIEW_COLOR_BORDER,
    OVERVIEW_COLOR_DANGER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_PRIMARY,
    OVERVIEW_COLOR_SURFACE,
    OVERVIEW_COLOR_SURFACE_SUBTLE,
    OVERVIEW_COLOR_TEXT,
    OVERVIEW_COLOR_TEXT_MUTED,
    OVERVIEW_COLOR_WARNING,
    OVERVIEW_SECTOR_COLOR_MAP,
    OVERVIEW_SERIES_COLORS,
    render_auto_refresh_countdown,
    render_auto_refresh_timing_static,
    render_market_auto_message,
    render_market_auto_waiting_panel,
    render_market_refresh_status_bar,
    render_market_snapshot_meta_strip,
    render_overview_toolbar_label,
)


MARKET_INTRADAY_REFRESH_MINUTES = 5
BROWSER_AUTO_REFRESH_SECONDS = 300
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


@dataclass(frozen=True)
class MarketMoverControls:
    coverage: str
    universe_limit: int
    period: str
    sector: str
    top_n: int


def _coverage_label(value: str) -> str:
    return MARKET_COVERAGE_LABELS.get(value, value)


def _universe_limit(value: str) -> int:
    return MARKET_UNIVERSE_LIMITS.get(value, 500)


def _market_mover_period_label(value: str) -> str:
    return MARKET_MOVER_PERIOD_LABELS.get(value, value.title())


def _market_refresh_mode_label(value: str) -> str:
    return {"manual": "수동 갱신", "auto": "자동 갱신"}.get(value, value)


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


def _format_signed(value: Any, *, suffix: str = "%") -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):+.2f}{suffix}"


def _sector_bar_color(sector: Any, return_pct: Any | None = None) -> str:
    numeric_return = pd.to_numeric(return_pct, errors="coerce") if return_pct is not None else None
    if numeric_return is not None and pd.notna(numeric_return) and float(numeric_return) < 0:
        return OVERVIEW_COLOR_DANGER
    return OVERVIEW_SECTOR_COLOR_MAP.get(str(sector or "Unknown"), OVERVIEW_SECTOR_COLOR_MAP["Unknown"])


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


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
    details = dict(result.get("details") or {})
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


def _summarize_auto_refresh_plan(summary: dict[str, Any]) -> str:
    plan = summary.get("plan")
    if not isinstance(plan, list) or not plan:
        return "-"
    row = dict(plan[0] or {})
    label = _auto_refresh_job_label(row.get("label") or row.get("job_id") or "-")
    reason = _auto_refresh_reason_label(row.get("reason") or "-")
    return f"{label}: {reason}"


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
    summary = run_overview_browser_auto_refresh(
        profile=config["profile"],
        job_id=config["job_id"],
        universe_code=universe_code,
        checked_at=checked_at,
    )
    _store_browser_auto_refresh_state(universe_code, summary, checked_at)
    return summary


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


def _get_market_movers_refresh_state(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> dict[str, str | bool] | None:
    del universe_code
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


def render_market_movers_header() -> None:
    st.markdown("### Market Movers")


def render_market_movers_controls() -> MarketMoverControls:
    return _render_market_movers_controls()


def render_market_movers_context_captions(controls: MarketMoverControls) -> None:
    reloaded_at = st.session_state.get("overview_market_movers_reloaded_at")
    if reloaded_at:
        st.caption(f"Last DB snapshot reload request: {reloaded_at}")
    if controls.period == "daily":
        st.caption(
            "Daily는 저장된 quote snapshot을 previous close와 비교합니다. 갱신 방식은 아래 데이터 갱신 영역에서 선택합니다."
        )


def normalize_market_movers_refresh_mode(controls: MarketMoverControls) -> None:
    if controls.coverage not in BROWSER_AUTO_REFRESH_JOB_CONFIG or controls.period != "daily":
        st.session_state["overview_market_movers_refresh_mode"] = "manual"


def is_market_movers_auto_refresh_enabled(controls: MarketMoverControls) -> bool:
    return (
        controls.coverage in BROWSER_AUTO_REFRESH_JOB_CONFIG
        and controls.period == "daily"
        and st.session_state.get("overview_market_movers_refresh_mode") == "auto"
    )


def render_market_movers_auto_refresh_panel(controls: MarketMoverControls) -> None:
    @st.fragment(run_every=BROWSER_AUTO_REFRESH_SECONDS)
    def _market_movers_auto_refresh_panel() -> None:
        summary, checked_at = _get_browser_auto_refresh_state(controls.coverage)
        if _should_run_browser_auto_refresh_check(summary, checked_at=str(checked_at or "")):
            coverage_label = MARKET_COVERAGE_LABELS.get(controls.coverage, controls.coverage)
            with st.spinner(f"{coverage_label} 자동 갱신 조건을 확인하는 중입니다..."):
                _run_browser_auto_refresh_check(universe_code=controls.coverage)
        render_market_movers_snapshot(controls)

    _market_movers_auto_refresh_panel()


def _render_snapshot_warnings(snapshot: dict[str, Any]) -> None:
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))


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
        tooltip=["Rank:O", "Symbol:N", "Name:N", "Return Label:N", "Sector:N", "Industry:N"],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    labels = base.mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT).encode(
        text=alt.Text("Return Label:N"),
    )
    return (bars + labels).properties(height=_market_mover_chart_height(len(chart_rows)))


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
            [{"Symbol": "No Data", "Name": "-", "Volume Metric": 0.0, "Volume Basis": "Volume"}]
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
    if "Sector" not in chart_rows:
        chart_rows["Sector"] = "Unknown"
    chart_rows["Bar Color"] = chart_rows["Sector"].map(lambda value: _sector_bar_color(value))
    symbol_order = chart_rows["Symbol"].drop_duplicates().tolist()
    max_volume = max(1.0, float(chart_rows["Volume Metric"].max()) if not chart_rows.empty else 1.0)
    base = alt.Chart(chart_rows).encode(
        x=alt.X("Volume Metric:Q", title="Volume Metric", scale=alt.Scale(domain=[0, max_volume * 1.12])),
        y=alt.Y("Symbol:N", sort=symbol_order, title=None, axis=alt.Axis(labelLimit=80)),
        tooltip=["Volume Rank:O", "Symbol:N", "Name:N", "Volume Basis:N", "Volume Metric Label:N", "Sector:N"],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    labels = base.mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT).encode(
        text=alt.Text("Volume Metric Label:N")
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
        tooltip=["Sector:N", "Count:Q", "Average Return Label:N"],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    labels = base.mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT).encode(
        text=alt.Text("Average Return Label:N"),
    )
    return (bars + labels).properties(height=_market_mover_chart_height(source_row_count))


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
                run_overview_market_intraday_snapshot(universe_code=universe_code, universe_limit=universe_limit),
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
            _store_overview_job_result("overview_nasdaq_symbol_directory_result", run_overview_nasdaq_symbol_directory())
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
                run_overview_market_movers_eod_history(
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
    symbol = str(selected.get("symbol") or mover.get("Symbol") or "").upper()
    name = str(selected.get("name") or mover.get("Name") or symbol)
    search_query = f"{symbol} {name} stock news"
    links = pd.DataFrame(
        [
            {
                "Source": "Google News",
                "URL": f"https://news.google.com/search?q={search_query.replace(' ', '+')}",
                "Search Query": search_query,
                "Purpose": "최근 뉴스 헤드라인 확인",
            },
            {
                "Source": "SEC",
                "URL": f"https://www.sec.gov/edgar/search/#/q={symbol}",
                "Search Query": symbol,
                "Purpose": "최근 공시 단서 확인",
            },
        ]
    )
    summary_rows = [
        {"항목": "종목", "값": symbol},
        {"항목": "회사", "값": name},
        {"항목": "순위 기준", "값": selected.get("rank_source")},
        {"항목": "수익률", "값": _format_signed(mover.get("Return %"))},
        {"항목": "섹터", "값": mover.get("Sector") or "-"},
    ]
    st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
    table_model = _market_mover_external_search_table_model(links)
    with st.expander(str(table_model["label"]), expanded=False):
        st.caption("외부 검색 시작점입니다. 링크를 열어도 앱이 원문을 조회, 파싱, 저장하지 않습니다.")
        st.dataframe(
            table_model["rows"],
            width="stretch",
            hide_index=True,
            column_config=table_model["column_config"],
        )


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


def render_market_movers_snapshot(controls: MarketMoverControls) -> None:
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
