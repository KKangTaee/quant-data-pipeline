from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
from time import perf_counter
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_browser_auto_refresh,
    run_overview_market_intraday_snapshot,
    run_overview_market_movers_eod_history,
    run_overview_market_mover_statement_refresh,
    run_overview_nasdaq_symbol_directory,
    run_overview_quote_gap_diagnostics,
    run_overview_sp500_universe,
)
from app.services.overview.market_movers import build_market_movers_coverage_trust_model
from app.services.overview.why_it_moved import (
    build_market_mover_metadata_status_strip,
    build_market_mover_research_snapshot,
    build_market_mover_why_it_moved_read_model,
    fetch_market_mover_news_metadata,
    fetch_market_mover_sec_metadata,
    merge_market_mover_metadata,
)
from app.web.overview.session_helpers import _snapshot_value
from app.web.overview_dashboard_helpers import (
    load_overview_market_mover_sectors,
    load_overview_market_movers_snapshot,
)
from app.web.overview.components.common import (
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
    render_overview_toolbar_label,
)
from app.web.overview.components.market_movers import (
    render_auto_refresh_countdown,
    render_auto_refresh_timing_static,
    render_breadth_heatmap_summary,
    render_market_auto_message,
    render_market_auto_waiting_panel,
    render_market_mover_board,
    render_market_mover_chart_workspace,
    render_market_mover_investigation_pane,
    render_market_mover_research_snapshot,
    render_market_movers_data_trust_strip,
    render_market_movers_coverage_trust,
    render_market_movers_command_strip,
    render_market_movers_empty_state,
    render_market_movers_section_divider,
    render_market_movers_unified_summary,
    render_market_refresh_status_bar,
    render_sector_breadth_market_map,
)
from app.web.overview.market_movers_react_component import render_market_movers_react_workbench


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
MARKET_MOVER_MODE_LABELS = {
    "top_gainers": "상승",
    "top_losers": "하락",
    "volume_leaders": "거래량",
    "unusual_volume": "이상 거래량",
    "sector_leaders": "섹터",
}
MARKET_MOVER_MODE_ORDER = tuple(MARKET_MOVER_MODE_LABELS)
MARKET_MOVER_TOP_N_OPTIONS = (10, 20, 30, 50, 100)
MARKET_MOVER_RANK_SOURCE_LABELS = {
    "Top Gainers": "상승",
    "Top Losers": "하락",
    "Volume Leaders": "거래량",
    "Unusual Volume": "이상 거래량",
    "Sector Leaders": "섹터",
    "Return Rank": "수익률",
    "Volume Rank": "거래량",
    "Selected Rank": "선택 종목",
}
MARKET_MOVER_BOARD_TITLES = {
    "top_gainers": "상승 상위 종목",
    "top_losers": "하락 상위 종목",
    "volume_leaders": "거래량 상위 종목",
    "unusual_volume": "이상 거래량 상위 종목",
    "sector_leaders": "섹터 상위 종목",
}
MARKET_MOVER_CHART_WORKSPACE_KICKER = "가격 / 거래량 워크스페이스"
MARKET_MOVER_CHART_TITLES = {
    "top_gainers": "상승 수익률 차트",
    "top_losers": "하락 수익률 차트",
    "volume_leaders": "거래량 차트",
    "unusual_volume": "이상 거래량 차트",
    "sector_leaders": "섹터 수익률 차트",
}


@dataclass(frozen=True)
class MarketMoverControls:
    coverage: str
    universe_limit: int
    period: str
    sector: str
    top_n: int
    mode: str = "top_gainers"


def _coverage_label(value: str) -> str:
    return MARKET_COVERAGE_LABELS.get(value, value)


def _universe_limit(value: str) -> int:
    return MARKET_UNIVERSE_LIMITS.get(value, 500)


def _market_mover_period_label(value: str) -> str:
    return MARKET_MOVER_PERIOD_LABELS.get(value, value.title())


def _market_mover_mode_label(value: str) -> str:
    return MARKET_MOVER_MODE_LABELS.get(value, str(value).replace("_", " ").title())


def _market_mover_rank_source_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "선택 종목"
    return MARKET_MOVER_RANK_SOURCE_LABELS.get(text, text)


def _normalize_market_mover_mode(value: Any) -> str:
    normalized = str(value or "top_gainers").strip().lower()
    if normalized in MARKET_MOVER_MODE_LABELS:
        return normalized
    return "top_gainers"


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


def _format_count(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{int(numeric):,}"


def _safe_int(value: Any, default: int = 0) -> int:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return default
    return int(numeric)


def _format_pct_detail(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):.1f}% of universe"


def _freshness_label(snapshot: dict[str, Any], coverage: dict[str, Any]) -> str:
    refresh_state = dict(coverage.get("refresh_state") or {})
    label = refresh_state.get("label") or refresh_state.get("status")
    if label:
        return str(label).title() if str(label).islower() else str(label)
    status = str(snapshot.get("status") or "").upper()
    mapping = {
        "OK": "Fresh",
        "NO_UNIVERSE": "No Universe",
        "INSUFFICIENT_DATA": "Needs Refresh",
        "ERROR": "Failed",
    }
    return mapping.get(status, status.title() if status else "-")


def _freshness_detail(coverage: dict[str, Any]) -> str:
    refresh_state = dict(coverage.get("refresh_state") or {})
    detail = refresh_state.get("detail")
    if detail:
        return str(detail)
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is not None:
        return f"{stale_minutes}m old"
    stale_days = coverage.get("stale_days")
    if stale_days is not None:
        return f"{stale_days}D old"
    return str(coverage.get("price_mode") or "-")


def _effective_timestamp(coverage: dict[str, Any]) -> str:
    return str(
        coverage.get("snapshot_time_utc")
        or coverage.get("effective_end_date")
        or coverage.get("latest_raw_date")
        or "-"
    )


def _command_strip_tone(snapshot: dict[str, Any], coverage: dict[str, Any]) -> str:
    status = str(snapshot.get("status") or "").strip().upper()
    refresh_status = str(dict(coverage.get("refresh_state") or {}).get("status") or "").strip().lower()
    missing_count = _safe_int(coverage.get("missing_count"))
    if status in {"ERROR"} or refresh_status in {"failed", "stale"}:
        return "danger"
    if status in {"NO_UNIVERSE", "INSUFFICIENT_DATA"} or refresh_status in {"partial", "due"} or missing_count:
        return "warning"
    if status == "OK":
        return "positive"
    return "neutral"


def build_market_movers_command_strip_model(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
    exploration_mode: str,
) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    coverage_label = _coverage_label(controls.coverage)
    period_label = _market_mover_period_label(controls.period)
    sector_label = controls.sector if controls.sector and controls.sector != "All" else "All sectors"
    freshness = _freshness_label(snapshot, coverage)
    returnable_pct = coverage.get("returnable_pct")
    return {
        "schema_version": "market_movers_command_strip_v1",
        "headline": "변동 종목",
        "context": f"{coverage_label} · {period_label} · {sector_label}",
        "status_label": freshness,
        "tone": _command_strip_tone(snapshot, coverage),
        "items": [
            {"label": "Coverage", "value": coverage_label, "detail": str(coverage.get("coverage_basis") or "")},
            {"label": "Period", "value": period_label, "detail": str(coverage.get("price_mode") or "-")},
            {"label": "Effective timestamp", "value": _effective_timestamp(coverage), "detail": "DB snapshot/read model"},
            {"label": "Freshness", "value": freshness, "detail": _freshness_detail(coverage)},
            {"label": "Universe", "value": _format_count(coverage.get("universe_count"))},
            {
                "label": "Returnable",
                "value": _format_count(coverage.get("returnable_count")),
                "detail": _format_pct_detail(returnable_pct),
            },
            {"label": "Missing", "value": _format_count(coverage.get("missing_count"))},
            {"label": "보기", "value": exploration_mode, "detail": f"Top {controls.top_n}"},
        ],
    }


def build_market_movers_unified_summary_model(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
    exploration_mode: str,
) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    coverage_label = _coverage_label(controls.coverage)
    period_label = _market_mover_period_label(controls.period)
    sector_label = controls.sector if controls.sector and controls.sector != "All" else "All sectors"
    freshness = _freshness_label(snapshot, coverage)
    returnable_pct = coverage.get("returnable_pct")
    action_label = "정상" if _command_strip_tone(snapshot, coverage) == "positive" else "갱신 확인"
    return {
        "schema_version": "market_movers_unified_summary_v1",
        "title": "변동 종목",
        "context": f"{coverage_label} · {period_label} · {sector_label}",
        "trust_state": freshness,
        "trust_detail": _freshness_detail(coverage),
        "tone": _command_strip_tone(snapshot, coverage),
        "action_label": action_label,
        "items": [
            {"label": "기준", "value": _effective_timestamp(coverage), "detail": str(coverage.get("price_mode") or "-")},
            {"label": "Universe", "value": _format_count(coverage.get("universe_count"))},
            {
                "label": "Returnable",
                "value": _format_count(coverage.get("returnable_count")),
                "detail": _format_pct_detail(returnable_pct),
            },
            {"label": "Missing", "value": _format_count(coverage.get("missing_count"))},
            {"label": "보기", "value": exploration_mode, "detail": f"Top {controls.top_n}"},
        ],
    }


def _market_movers_react_actions(*, controls: MarketMoverControls) -> list[dict[str, Any]]:
    if controls.period == "daily":
        actions: list[dict[str, Any]] = [
            {"id": "refresh_intraday", "label": "일중 스냅샷 갱신", "kind": "primary"},
        ]
        if controls.coverage == "SP500":
            actions.append({"id": "refresh_universe", "label": "유니버스 갱신", "kind": "secondary"})
        elif controls.coverage == "NASDAQ":
            actions.append({"id": "refresh_nasdaq_directory", "label": "Nasdaq 목록 갱신", "kind": "secondary"})
        else:
            actions.append({"id": "universe_static", "label": "유니버스 기준", "kind": "disabled"})
        actions.append({"id": "reload", "label": "화면 새로고침", "kind": "secondary"})
        return actions

    return [
        {"id": "refresh_eod_history", "label": "가격 이력 갱신", "kind": "primary"},
        {"id": "reload", "label": "화면 새로고침", "kind": "secondary"},
    ]


def build_market_movers_react_workbench_payload(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
    exploration_mode: str,
) -> dict[str, Any]:
    return {
        "schema_version": "market_movers_react_workbench_v1",
        "component": "MarketMoversWorkbench",
        "summary": build_market_movers_unified_summary_model(
            snapshot,
            controls=controls,
            exploration_mode=exploration_mode,
        ),
        "controls": {
            "coverage": controls.coverage,
            "universe_limit": controls.universe_limit,
            "period": controls.period,
            "sector": controls.sector,
            "top_n": controls.top_n,
            "mode": controls.mode,
        },
        "control_ownership": {
            "mode": "streamlit_owned",
            "migrated_controls": ["summary_actions"],
            "deferred_controls": ["coverage", "period", "sector", "top_n", "mode", "refresh_mode"],
        },
        "actions": _market_movers_react_actions(controls=controls),
    }


def market_movers_react_action_plan(action_id: str, *, controls: MarketMoverControls) -> dict[str, Any]:
    if action_id == "refresh_intraday":
        return {
            "handler": "run_overview_market_intraday_snapshot",
            "universe_code": controls.coverage,
            "universe_limit": controls.universe_limit,
        }
    if action_id == "refresh_universe":
        return {"handler": "run_overview_sp500_universe", "universe_code": controls.coverage}
    if action_id == "refresh_nasdaq_directory":
        return {"handler": "run_overview_nasdaq_symbol_directory", "universe_code": controls.coverage}
    if action_id == "refresh_eod_history":
        return {
            "handler": "run_overview_market_movers_eod_history",
            "universe_code": controls.coverage,
            "universe_limit": controls.universe_limit,
            "period": controls.period,
        }
    if action_id == "reload":
        return {"handler": "reload_market_movers"}
    return {"handler": "noop", "action_id": action_id}


def _market_movers_react_event_payload(event: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    nested = event.get("event")
    if isinstance(nested, dict):
        return nested
    return event


def _market_movers_react_event_action_id(event: dict[str, Any] | None) -> str | None:
    payload = _market_movers_react_event_payload(event)
    action_id = payload.get("id") or payload.get("action_id")
    normalized = str(action_id or "").strip()
    return normalized or None


def _market_movers_react_event_token(event: dict[str, Any] | None) -> str | None:
    action_id = _market_movers_react_event_action_id(event)
    if not action_id:
        return None
    payload = _market_movers_react_event_payload(event)
    nonce = payload.get("nonce") or payload.get("token") or action_id
    return f"{action_id}:{nonce}"


def _consume_market_movers_react_event(event: dict[str, Any] | None) -> bool:
    token = _market_movers_react_event_token(event)
    if not token:
        return False
    state_key = "overview_market_movers_last_react_event_token"
    if st.session_state.get(state_key) == token:
        return False
    st.session_state[state_key] = token
    return True


def _dispatch_market_movers_react_event(event: dict[str, Any] | None, *, controls: MarketMoverControls) -> bool:
    action_id = _market_movers_react_event_action_id(event)
    if not action_id:
        return False
    plan = market_movers_react_action_plan(action_id, controls=controls)
    handler = str(plan.get("handler") or "noop")
    if handler == "noop" or not _consume_market_movers_react_event(event):
        return False

    universe_code = str(plan.get("universe_code") or controls.coverage)
    universe_label = MARKET_COVERAGE_LABELS.get(universe_code, universe_code)
    if handler == "run_overview_market_intraday_snapshot":
        result_key = f"overview_{universe_code.lower()}_intraday_result"
        with st.spinner(f"Updating {universe_label} quote snapshot..."):
            _store_overview_job_result(
                result_key,
                run_overview_market_intraday_snapshot(
                    universe_code=universe_code,
                    universe_limit=int(plan.get("universe_limit") or controls.universe_limit),
                ),
            )
        st.rerun()
        return True

    if handler == "run_overview_sp500_universe":
        with st.spinner("Refreshing S&P 500 universe..."):
            _store_overview_job_result("overview_sp500_universe_result", run_overview_sp500_universe())
        st.rerun()
        return True

    if handler == "run_overview_nasdaq_symbol_directory":
        with st.spinner("Refreshing Nasdaq Symbol Directory current snapshot..."):
            _store_overview_job_result(
                "overview_nasdaq_symbol_directory_result",
                run_overview_nasdaq_symbol_directory(),
            )
        st.rerun()
        return True

    if handler == "run_overview_market_movers_eod_history":
        period = str(plan.get("period") or controls.period)
        period_label = _market_mover_period_label(period)
        result_key = f"overview_{universe_code.lower()}_{period}_eod_history_result"
        with st.spinner(f"{universe_label} {period_label} EOD 가격 이력을 수집하는 중입니다..."):
            _store_overview_job_result(
                result_key,
                run_overview_market_movers_eod_history(
                    universe_code=universe_code,
                    universe_limit=int(plan.get("universe_limit") or controls.universe_limit),
                    period=period,
                ),
            )
        st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
        return True

    if handler == "reload_market_movers":
        st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
        return True

    return False


def _render_market_movers_react_summary(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
) -> dict[str, Any] | None:
    payload = build_market_movers_react_workbench_payload(
        snapshot,
        controls=controls,
        exploration_mode=_market_mover_mode_label(controls.mode),
    )
    event = render_market_movers_react_workbench(
        payload,
        key=f"overview_{controls.coverage.lower()}_{controls.period}_market_movers_workbench",
    )
    if event is None:
        render_market_movers_unified_summary(payload["summary"])
    return event


def build_market_movers_empty_state_model(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
) -> dict[str, Any]:
    coverage_label = _coverage_label(controls.coverage)
    period_label = _market_mover_period_label(controls.period)
    status = str(snapshot.get("status") or "").upper()
    message = str(snapshot.get("message") or "DB-backed market mover rows are not available for the selected controls.")
    if controls.coverage == "NASDAQ" and status == "NO_UNIVERSE":
        title = f"{coverage_label} universe가 아직 비어 있습니다."
        primary_action = "Nasdaq 목록 갱신"
        tone = "warning"
    elif controls.period == "daily":
        title = f"{coverage_label} {period_label} ranking row가 아직 없습니다."
        primary_action = "일중 스냅샷 갱신"
        tone = "warning" if status != "OK" else "neutral"
    else:
        title = f"{coverage_label} {period_label} ranking row가 아직 없습니다."
        primary_action = "가격 이력 갱신"
        tone = "warning" if status != "OK" else "neutral"
    return {
        "schema_version": "market_movers_empty_state_v1",
        "tone": tone,
        "title": title,
        "detail": message,
        "primary_action": primary_action,
        "show_why_it_moved": False,
        "investigation_note": "선택한 coverage에 ranking row가 생기면 선택 종목 조사 패널을 사용할 수 있습니다.",
        "trust_hint": {
            "label": "현재 결과 신뢰도",
            "value": _freshness_label(snapshot, dict(snapshot.get("coverage") or {})),
            "detail": "Coverage trust detail에서 grouped diagnostics를 확인합니다.",
        },
    }


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
    selected = container.selectbox(
        "방식",
        options,
        key=key,
        format_func=_market_refresh_mode_label,
        disabled=not auto_supported,
        help="자동 갱신은 현재 선택한 Daily coverage의 일중 스냅샷만 확인합니다.",
    )
    return str(selected or "manual")


def _select_market_mover_mode(container: Any) -> str:
    key = "overview_market_movers_mode"
    if st.session_state.get(key) not in MARKET_MOVER_MODE_ORDER:
        st.session_state[key] = "top_gainers"
    segmented_control = getattr(container, "segmented_control", None)
    if callable(segmented_control):
        selected = segmented_control(
            "랭킹 기준",
            list(MARKET_MOVER_MODE_ORDER),
            key=key,
            format_func=_market_mover_mode_label,
            help="저장된 read model 안에서 상승, 하락, 거래량, 이상 거래량, 섹터 흐름을 전환합니다.",
        )
    else:
        selected = container.radio(
            "랭킹 기준",
            list(MARKET_MOVER_MODE_ORDER),
            key=key,
            format_func=_market_mover_mode_label,
            horizontal=True,
            help="저장된 read model 안에서 상승, 하락, 거래량, 이상 거래량, 섹터 흐름을 전환합니다.",
        )
    return _normalize_market_mover_mode(selected)


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
    render_overview_toolbar_label("조건")
    controls = st.columns([1.0, 0.92, 1.0, 0.78, 1.0], gap="small", vertical_alignment="bottom")
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
    top_n_key = "overview_market_movers_top_n"
    if st.session_state.get(top_n_key) not in MARKET_MOVER_TOP_N_OPTIONS:
        st.session_state[top_n_key] = 20
    top_n = int(
        controls[3].selectbox(
            "Top N",
            list(MARKET_MOVER_TOP_N_OPTIONS),
            key=top_n_key,
            format_func=lambda value: f"Top {value}",
        )
    )
    mode_key = "overview_market_movers_mode"
    if st.session_state.get(mode_key) not in MARKET_MOVER_MODE_ORDER:
        st.session_state[mode_key] = "top_gainers"
    mode = _normalize_market_mover_mode(
        controls[4].selectbox(
            "랭킹 기준",
            list(MARKET_MOVER_MODE_ORDER),
            key=mode_key,
            format_func=_market_mover_mode_label,
            help="저장된 read model 안에서 상승, 하락, 거래량, 이상 거래량, 섹터 흐름을 전환합니다.",
        )
    )
    return MarketMoverControls(
        coverage=coverage,
        universe_limit=universe_limit,
        period=period,
        sector=sector,
        top_n=top_n,
        mode=mode,
    )


def render_market_movers_header() -> None:
    st.markdown("### 변동 종목")


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


def build_market_movers_data_trust_strip_model(trust_model: dict[str, Any]) -> dict[str, Any]:
    preferred_labels = {"Freshness", "Returnable", "Missing"}
    items = [
        dict(item)
        for item in list(trust_model.get("items") or [])
        if str(dict(item).get("label") or "") in preferred_labels
    ]
    action = dict(trust_model.get("suggested_action") or {})
    return {
        "schema_version": "market_movers_data_trust_strip_v1",
        "state": str(trust_model.get("state") or "-"),
        "tone": str(trust_model.get("tone") or "neutral"),
        "headline": str(trust_model.get("headline") or "-"),
        "detail": str(trust_model.get("detail") or "-"),
        "items": items,
        "action_label": str(action.get("label") or "No action needed"),
        "action_detail": str(action.get("detail") or ""),
        "boundary_note": str(
            trust_model.get("boundary_note")
            or "Coverage trust is context-only data-quality evidence for the current Market Movers view."
        ),
    }


def _render_market_movers_coverage_trust(snapshot: dict[str, Any], *, controls: MarketMoverControls) -> None:
    model = build_market_movers_coverage_trust_model(snapshot)
    grouped_rows = model.get("grouped_missing_rows")
    if not isinstance(grouped_rows, pd.DataFrame):
        grouped_rows = pd.DataFrame()
    action = dict(model.get("suggested_action") or {})
    expanded = str(model.get("state") or "") not in {"Good"}
    with st.expander("Coverage trust detail", expanded=expanded):
        st.caption("Grouped missing diagnostics")
        if grouped_rows.empty:
            st.caption("현재 선택 조건에서 grouped missing diagnostics로 묶을 row가 없습니다.")
        else:
            st.dataframe(grouped_rows, width="stretch", hide_index=True)
        st.caption(action.get("detail") or "Coverage trust는 현재 read model의 보조 설명입니다.")
        if action.get("action_id") == "overview_nasdaq_symbol_directory":
            cols = st.columns([1, 2], gap="small", vertical_alignment="center")
            if cols[0].button(
                "Nasdaq 목록 갱신",
                key="overview_nasdaq_symbol_directory_refresh_trust",
                use_container_width=True,
                help="Nasdaq Symbol Directory current snapshot을 기존 Overview action facade를 통해 DB에 저장합니다.",
            ):
                with st.spinner("Refreshing Nasdaq Symbol Directory current snapshot..."):
                    _store_overview_job_result(
                        "overview_nasdaq_symbol_directory_result",
                        run_overview_nasdaq_symbol_directory(),
                    )
                st.rerun()
            cols[1].caption("새 provider 경로 없이 Ingestion/DB/action facade 경계를 사용합니다.")
            _render_market_job_result("overview_nasdaq_symbol_directory_result")


def _render_missing_diagnostics(snapshot: dict[str, Any], *, universe_code: str, period: str) -> None:
    missing_rows = snapshot.get("missing_rows")
    if not isinstance(missing_rows, pd.DataFrame) or missing_rows.empty:
        return
    with st.expander(f"Raw diagnostics ({len(missing_rows)} missing rows)", expanded=False):
        st.caption(
            "Grouped missing diagnostics를 먼저 확인하고, symbol-level evidence가 필요할 때만 raw rows를 엽니다."
        )
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


def _market_mover_view_model(snapshot: dict[str, Any], mode: Any) -> dict[str, Any]:
    normalized_mode = _normalize_market_mover_mode(mode)
    views = snapshot.get("mover_views")
    model: dict[str, Any] = {}
    if isinstance(views, dict):
        model = dict(views.get(normalized_mode) or {})
    if not model:
        fallback_rows = snapshot.get("volume_rows") if normalized_mode == "volume_leaders" else snapshot.get("rows")
        model = {
            "label": _market_mover_mode_label(normalized_mode),
            "kind": "symbol",
            "sort_basis": "Legacy ranking rows",
            "rows": fallback_rows,
            "empty_reason": "No rows are available for this ranking view.",
            "boundary_note": "Context-only ranking view.",
        }

    rows = model.get("rows")
    if not isinstance(rows, pd.DataFrame):
        rows = pd.DataFrame()
    status = str(model.get("status") or ("OK" if not rows.empty else "INSUFFICIENT_DATA"))
    return {
        "mode": normalized_mode,
        "label": _market_mover_mode_label(normalized_mode),
        "kind": str(model.get("kind") or "symbol"),
        "status": status,
        "sort_basis": str(model.get("sort_basis") or ""),
        "empty_reason": str(model.get("empty_reason") or "No rows are available for this ranking view."),
        "boundary_note": str(model.get("boundary_note") or "Context-only ranking view."),
        "rows": rows,
    }


def _market_mover_row_value(row: pd.Series, *columns: str) -> Any:
    for column in columns:
        if column in row and row.get(column) not in (None, ""):
            return row.get(column)
    return None


def _market_mover_return_value(row: pd.Series) -> Any:
    return _market_mover_row_value(row, "Return %", "Market Cap Weighted Return %", "Average Return %")


def _market_mover_board_tone(row: pd.Series) -> str:
    numeric_return = pd.to_numeric(_market_mover_return_value(row), errors="coerce")
    if pd.isna(numeric_return):
        return "neutral"
    if float(numeric_return) < 0:
        return "danger"
    return "positive"


def _market_mover_board_primary_metric(row: pd.Series, mode: str) -> tuple[str, str]:
    if mode == "volume_leaders":
        return "거래량", _compact_number(_market_mover_row_value(row, "Volume", "Current Volume"))
    if mode == "unusual_volume":
        return "상대 거래량", _format_relative_volume(_market_mover_row_value(row, "Relative Volume"))
    if mode == "sector_leaders":
        return "섹터 수익률", _format_signed(_market_mover_return_value(row))
    return "수익률", _format_signed(_market_mover_return_value(row))


def _market_mover_board_secondary(row: pd.Series) -> str:
    parts: list[str] = []
    previous_return = _format_signed(_market_mover_row_value(row, "Previous Return %"))
    volume = _compact_number(_market_mover_row_value(row, "Volume", "Current Volume"))
    dollar_volume = _compact_number(_market_mover_row_value(row, "Dollar Volume"), prefix="$")
    relative_volume = _format_relative_volume(_market_mover_row_value(row, "Relative Volume"))
    if previous_return != "-":
        parts.append(f"직전 수익률 {previous_return}")
    if volume != "-":
        parts.append(f"거래량 {volume}")
    if dollar_volume != "-":
        parts.append(f"거래대금 {dollar_volume}")
    if relative_volume != "-":
        parts.append(f"상대 {relative_volume}")
    return " · ".join(parts) if parts else "-"


def _market_mover_board_row(row: pd.Series, *, mode: str, fallback_rank: int) -> dict[str, Any]:
    symbol = str(_market_mover_row_value(row, "Symbol", "Group", "Sector") or "-").strip() or "-"
    name = str(_market_mover_row_value(row, "Name", "Top Symbol", "Group", "Sector") or symbol).strip() or symbol
    sector = str(_market_mover_row_value(row, "Sector", "Group") or "-").strip() or "-"
    primary_label, primary_value = _market_mover_board_primary_metric(row, mode)
    return {
        "rank": _rank_token(_market_mover_row_value(row, "Rank"), fallback_rank),
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "primary_metric_label": primary_label,
        "primary_metric": primary_value,
        "secondary": _market_mover_board_secondary(row),
        "tone": _market_mover_board_tone(row),
    }


def build_market_mover_board_model(mode_model: dict[str, Any], *, top_n: int) -> dict[str, Any]:
    mode = _normalize_market_mover_mode(mode_model.get("mode"))
    rows = mode_model.get("rows")
    if not isinstance(rows, pd.DataFrame):
        rows = pd.DataFrame()
    limit = max(0, int(top_n or 0))
    board_rows = [
        _market_mover_board_row(row, mode=mode, fallback_rank=offset)
        for offset, (_, row) in enumerate(rows.head(limit).iterrows(), start=1)
    ]
    label = _market_mover_mode_label(mode)
    return {
        "schema_version": "market_mover_board_v1",
        "mode": mode,
        "title": MARKET_MOVER_BOARD_TITLES.get(mode, f"{label} 상위 종목"),
        "subtitle": f"{mode_model.get('sort_basis') or '-'} · {mode_model.get('boundary_note') or 'Context-only ranking view.'}",
        "summary": {"count": len(board_rows), "top_n": limit},
        "rows": board_rows,
        "boundary_note": str(mode_model.get("boundary_note") or "Context-only ranking view."),
    }


def _market_mover_chart_metric_value(row: pd.Series, mode: str) -> Any:
    if mode == "volume_leaders":
        return _market_mover_row_value(row, "Volume", "Current Volume")
    if mode == "unusual_volume":
        return _market_mover_row_value(row, "Relative Volume")
    return _market_mover_return_value(row)


def _market_mover_chart_metric_label(mode: str) -> str:
    if mode == "volume_leaders":
        return "거래량"
    if mode == "unusual_volume":
        return "상대 거래량"
    if mode == "sector_leaders":
        return "섹터 수익률"
    return "수익률"


def _format_market_mover_chart_metric(value: Any, mode: str) -> str:
    if mode == "volume_leaders":
        return _compact_number(value)
    if mode == "unusual_volume":
        return _format_relative_volume(value)
    return _format_signed(value)


def build_market_mover_chart_workspace_model(mode_model: dict[str, Any]) -> dict[str, Any]:
    mode = _normalize_market_mover_mode(mode_model.get("mode"))
    rows = mode_model.get("rows")
    if not isinstance(rows, pd.DataFrame):
        rows = pd.DataFrame()
    metric_values = pd.Series(dtype="float64")
    if not rows.empty:
        metric_values = pd.to_numeric(
            rows.apply(lambda row: _market_mover_chart_metric_value(row, mode), axis=1),
            errors="coerce",
        ).dropna()
    top_row = rows.iloc[0] if not rows.empty else pd.Series(dtype="object")
    top_symbol = str(_market_mover_row_value(top_row, "Symbol", "Group", "Sector") or "-").strip() or "-"
    top_value = _format_market_mover_chart_metric(_market_mover_chart_metric_value(top_row, mode), mode)
    if metric_values.empty:
        range_value = "-"
    else:
        min_value = _format_market_mover_chart_metric(metric_values.min(), mode)
        max_value = _format_market_mover_chart_metric(metric_values.max(), mode)
        range_value = f"{min_value} ~ {max_value}"
    return {
        "schema_version": "market_mover_chart_workspace_v1",
        "mode": mode,
        "kicker": MARKET_MOVER_CHART_WORKSPACE_KICKER,
        "title": MARKET_MOVER_CHART_TITLES.get(mode, f"{_market_mover_mode_label(mode)} 차트"),
        "subtitle": f"{mode_model.get('sort_basis') or '-'} · {mode_model.get('boundary_note') or 'Context-only ranking view.'}",
        "metric_label": _market_mover_chart_metric_label(mode),
        "facts": [
            {"label": "표시 rows", "value": _format_count(len(rows))},
            {"label": "상위", "value": top_symbol, "detail": top_value},
            {"label": "범위", "value": range_value},
        ],
        "boundary_note": str(mode_model.get("boundary_note") or "Context-only ranking view."),
    }


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


def _build_relative_volume_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    if not chart_rows.empty and "Relative Volume" in chart_rows:
        chart_rows["Relative Volume"] = pd.to_numeric(chart_rows["Relative Volume"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Relative Volume"])
    elif not chart_rows.empty:
        chart_rows = pd.DataFrame()
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Symbol": "No Data", "Name": "-", "Relative Volume": 0.0, "Sector": "Unknown"}])
    if "Rank" in chart_rows:
        chart_rows = chart_rows.sort_values("Rank").reset_index(drop=True)
    chart_rows["Relative Volume Label"] = chart_rows["Relative Volume"].map(
        lambda value: f"{float(value):.2f}x" if pd.notna(value) else "-"
    )
    if "Sector" not in chart_rows:
        chart_rows["Sector"] = "Unknown"
    chart_rows["Bar Color"] = chart_rows["Sector"].map(lambda value: _sector_bar_color(value))
    symbol_order = chart_rows["Symbol"].drop_duplicates().tolist()
    max_value = max(1.0, float(chart_rows["Relative Volume"].max()) if not chart_rows.empty else 1.0)
    base = alt.Chart(chart_rows).encode(
        x=alt.X("Relative Volume:Q", title="Relative Volume vs 10D Avg", scale=alt.Scale(domain=[0, max_value * 1.12])),
        y=alt.Y("Symbol:N", sort=symbol_order, title=None, axis=alt.Axis(labelLimit=80)),
        tooltip=["Rank:O", "Symbol:N", "Name:N", "Relative Volume Label:N", "Volume Basis:N", "Sector:N"],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    labels = base.mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT).encode(
        text=alt.Text("Relative Volume Label:N")
    )
    return (bars + labels).properties(height=_market_mover_chart_height(len(chart_rows)))


def _build_sector_leader_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    metric_column = "Market Cap Weighted Return %"
    if not chart_rows.empty and metric_column in chart_rows:
        chart_rows[metric_column] = pd.to_numeric(chart_rows[metric_column], errors="coerce")
        chart_rows = chart_rows.dropna(subset=[metric_column])
    elif not chart_rows.empty:
        chart_rows = pd.DataFrame()
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Group": "No Data", metric_column: 0.0, "Symbols": 0, "Top Symbol": "-"}])
    if "Rank" in chart_rows:
        chart_rows = chart_rows.sort_values("Rank").reset_index(drop=True)
    chart_rows["Return Magnitude %"] = chart_rows[metric_column].abs()
    chart_rows["Return Label"] = chart_rows[metric_column].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows["Bar Color"] = chart_rows.apply(
        lambda row: _sector_bar_color(row.get("Group"), row.get(metric_column)),
        axis=1,
    )
    group_order = chart_rows["Group"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Return Magnitude %:Q",
            title="Sector Move Magnitude %",
            stack=None,
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Return Magnitude %"])),
        ),
        y=alt.Y("Group:N", sort=group_order, title=None, axis=alt.Axis(labelLimit=150)),
        tooltip=["Rank:O", "Group:N", "Symbols:Q", "Return Label:N", "Top Symbol:N", "Top Symbol Return %:Q"],
    )
    bars = base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color("Bar Color:N", scale=None, legend=None))
    labels = base.mark_text(align="left", baseline="middle", dx=5, fontSize=11, color=OVERVIEW_COLOR_TEXT).encode(
        text=alt.Text("Return Label:N"),
    )
    return (bars + labels).properties(height=_market_mover_chart_height(len(chart_rows)))


def _build_market_mover_mode_chart(mode_model: dict[str, Any]) -> alt.Chart:
    mode = _normalize_market_mover_mode(mode_model.get("mode"))
    rows = mode_model.get("rows")
    if not isinstance(rows, pd.DataFrame):
        rows = pd.DataFrame()
    if mode == "volume_leaders":
        return _build_volume_bar_chart(rows)
    if mode == "unusual_volume":
        return _build_relative_volume_bar_chart(rows)
    if mode == "sector_leaders":
        return _build_sector_leader_bar_chart(rows)
    return _build_return_bar_chart(rows)


def _render_market_movers_universe_action(container: Any, *, universe_code: str) -> None:
    if universe_code == "SP500":
        if container.button(
            "유니버스 갱신",
            key="overview_sp500_universe_refresh",
            use_container_width=True,
        ):
            with st.spinner("Refreshing S&P 500 universe..."):
                _store_overview_job_result("overview_sp500_universe_result", run_overview_sp500_universe())
            st.rerun()
        return
    if universe_code == "NASDAQ":
        if container.button(
            "Nasdaq 목록 갱신",
            key="overview_nasdaq_symbol_directory_refresh",
            use_container_width=True,
            help="Nasdaq Symbol Directory current snapshot을 lifecycle evidence table에 저장합니다.",
        ):
            with st.spinner("Refreshing Nasdaq Symbol Directory current snapshot..."):
                _store_overview_job_result(
                    "overview_nasdaq_symbol_directory_result",
                    run_overview_nasdaq_symbol_directory(),
                )
            st.rerun()
        return
    container.button(
        "유니버스 기준",
        key=f"overview_{universe_code.lower()}_universe_static",
        use_container_width=True,
        disabled=True,
        help="Top universe는 market-cap ranked asset profile 기준입니다.",
    )


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
    control_cols = st.columns([0.75, 1.0, 0.9, 0.9], gap="small", vertical_alignment="bottom")
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
    _render_market_movers_universe_action(control_cols[2], universe_code=universe_code)
    if control_cols[3].button(
        "화면 새로고침",
        key=f"overview_{universe_code.lower()}_market_movers_reload",
        use_container_width=True,
    ):
        st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()

    if selected_mode == "auto" and auto_supported:
        _render_market_auto_refresh_summary(universe_code=universe_code)
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
    control_cols = st.columns([1.0, 1.0, 2.0], gap="small", vertical_alignment="bottom")
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
    control_cols[2].caption(f"{period_label}는 저장된 EOD 가격 이력 기준입니다. 자동 갱신은 Daily 일중 스냅샷만 지원합니다.")
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


def _render_market_movers_react_refresh_companion(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
) -> None:
    if controls.period == "daily":
        selected_mode = "manual"
        auto_supported = controls.coverage in BROWSER_AUTO_REFRESH_JOB_CONFIG
        if auto_supported:
            control_cols = st.columns([0.75, 2.25], gap="small", vertical_alignment="bottom")
            selected_mode = _select_market_refresh_mode(control_cols[0], auto_supported=True)
        if selected_mode == "auto" and auto_supported:
            _render_market_auto_refresh_summary(universe_code=controls.coverage)
        if controls.coverage == "SP500":
            _render_market_job_result("overview_sp500_universe_result")
        if controls.coverage == "NASDAQ":
            st.caption(
                "Nasdaq coverage는 Nasdaq Symbol Directory current listing snapshot 기준입니다. "
                "Nasdaq Composite 또는 Nasdaq-100 historical membership proof가 아닙니다."
            )
            _render_market_job_result("overview_nasdaq_symbol_directory_result")
        _render_market_job_result(f"overview_{controls.coverage.lower()}_intraday_result")
        return

    _render_market_job_result(f"overview_{controls.coverage.lower()}_{controls.period}_eod_history_result")


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


def _market_mover_catalyst_candidates(
    rows: pd.DataFrame,
    volume_rows: pd.DataFrame,
    *,
    primary_rank_source: str = "Return Rank",
    primary_id_prefix: str = "return",
    primary_label_prefix: str = "수익률",
    include_volume_candidates: bool = True,
) -> list[dict[str, Any]]:
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

    append_from_frame(
        rows,
        rank_source=primary_rank_source,
        id_prefix=primary_id_prefix,
        label_prefix=primary_label_prefix,
    )
    if include_volume_candidates:
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


def _market_movers_sector_float(value: Any) -> float | None:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)


def _market_movers_sector_pct_label(value: Any, *, decimals: int = 0) -> str:
    numeric = _market_movers_sector_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:.{decimals}f}%"


def _market_movers_sector_participation_label(value: Any) -> str:
    numeric = _market_movers_sector_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:.0f}%"


def _market_movers_sector_headline_label(value: Any) -> str:
    text = str(value or "").strip()
    mapping = {
        "Broad participation, balanced leadership": "넓은 참여, 균형 리더십",
        "Broad participation": "넓은 참여",
        "Mixed participation": "혼재된 참여",
        "Sector breadth context": "섹터 확산 맥락",
    }
    if text in mapping:
        return mapping[text]
    if not text:
        return "섹터 확산 맥락"
    return (
        text.replace("Broad participation", "넓은 참여")
        .replace("balanced leadership", "균형 리더십")
        .replace("Mixed participation", "혼재된 참여")
        .replace("Sector breadth context", "섹터 확산 맥락")
    )


def _market_movers_sector_detail_label(value: Any, *, leader: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "섹터별 움직임이 넓게 퍼졌는지 특정 그룹에 집중됐는지 확인합니다."
    if "leads the selected universe" in text:
        subject = text.split(" leads the selected universe", 1)[0].strip() or leader
        return f"{subject} 섹터가 선택 coverage를 주도합니다. 섹터별 확산이 넓은지 특정 그룹에 집중됐는지 확인합니다."
    return text.replace("Use sector lanes to see whether movement is broad or group-specific.", "섹터 레인에서 움직임의 확산/편중을 확인합니다.")


def _market_movers_sector_status_label(value: Any) -> str:
    text = str(value or "-").strip()
    mapping = {
        "OK": "정상",
        "INSUFFICIENT_DATA": "데이터 부족",
        "NO_UNIVERSE": "Universe 없음",
        "ERROR": "오류",
    }
    return mapping.get(text, text)


def _market_movers_sector_boundary_note(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text.lower().startswith("context-only sector breadth"):
        return "섹터 확산은 맥락 확인용입니다. 거래 행동, 매매 판단, 검증 게이트, Final Review 결정, 모니터링 지침이 아닙니다."
    return text.replace("Context-only sector breadth.", "섹터 확산은 맥락 확인용입니다.")


def build_market_movers_sector_map_model(model: dict[str, Any]) -> dict[str, Any]:
    rows = [dict(row) for row in list(model.get("heatmap_rows") or [])]
    summary = dict(model.get("summary") or {})
    coverage = dict(model.get("coverage") or {})
    return_values = [
        abs(value)
        for value in (_market_movers_sector_float(row.get("market_cap_weighted_return_pct")) for row in rows)
        if value is not None
    ]
    max_abs_return = max(return_values) if return_values else 0.0
    participation_values = [
        value
        for value in (_market_movers_sector_float(row.get("positive_symbol_share_pct")) for row in rows)
        if value is not None
    ]
    average_participation = sum(participation_values) / len(participation_values) if participation_values else None
    positive_groups = sum(
        1 for row in rows if (_market_movers_sector_float(row.get("market_cap_weighted_return_pct")) or 0.0) > 0
    )
    negative_groups = sum(
        1 for row in rows if (_market_movers_sector_float(row.get("market_cap_weighted_return_pct")) or 0.0) < 0
    )
    leader_row = max(
        rows,
        key=lambda row: _market_movers_sector_float(row.get("market_cap_weighted_return_pct")) or float("-inf"),
        default={},
    )
    leader_return = _market_movers_sector_float(leader_row.get("market_cap_weighted_return_pct"))
    lanes: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        sector_return = _market_movers_sector_float(row.get("market_cap_weighted_return_pct"))
        normalized = int(round((abs(sector_return or 0.0) / max_abs_return) * 100)) if max_abs_return > 0 else 0
        participation_label = _market_movers_sector_participation_label(row.get("positive_symbol_share_pct"))
        advancers = _format_count(row.get("advancers"))
        decliners = _format_count(row.get("decliners"))
        lane = {
            "rank": row.get("rank") or index,
            "sector": str(row.get("group") or "Unknown"),
            "tone": row.get("tone") or ("negative" if (sector_return or 0.0) < 0 else "positive"),
            "direction": "negative" if (sector_return or 0.0) < 0 else "positive",
            "return_label": _format_signed(sector_return),
            "bar_pct": normalized,
            "bar_width_pct": round(normalized / 2, 2),
            "participation_label": f"상승 {participation_label}",
            "participation_detail": f"상승 {advancers} / 하락 {decliners} · 상승 비중 {participation_label}",
            "cap_detail": f"시총비중 {_market_movers_sector_pct_label(row.get('market_cap_share_pct'), decimals=1)}",
            "top_gainer_detail": (
                f"상승 상위 {row.get('top_symbol') or '-'} "
                f"{_format_signed(row.get('top_symbol_return_pct'))}"
            ),
            "top_loser_detail": (
                f"하락 상위 {row.get('top_loser') or '-'} "
                f"{_format_signed(row.get('top_loser_return_pct'))}"
            ),
        }
        lanes.append(lane)
    participation_label = _market_movers_sector_participation_label(average_participation)
    participation_rail = 0 if average_participation is None else max(0, min(100, int(round(average_participation))))
    return {
        "schema_version": "market_movers_sector_map_v1",
        "tone": model.get("status") or "-",
        "status": _market_movers_sector_status_label(model.get("status") or "-"),
        "headline": _market_movers_sector_headline_label(summary.get("headline")),
        "detail": _market_movers_sector_detail_label(summary.get("detail"), leader=str(leader_row.get("group") or "-")),
        "freshness": coverage.get("freshness") or "-",
        "participation": {
            "label": "상승 참여",
            "value": participation_label,
            "detail": f"{len(participation_values)}개 섹터 평균",
            "rail_pct": participation_rail,
        },
        "leadership": {
            "label": "리더십",
            "value": str(leader_row.get("group") or "-"),
            "detail": f"{_format_signed(leader_return)} 시총가중",
        },
        "dispersion": {
            "label": "확산",
            "value": "넓음" if average_participation is not None and average_participation >= 60 else "혼재",
            "detail": f"{positive_groups}개 양수 섹터 · {negative_groups}개 음수 섹터",
        },
        "lanes": lanes,
        "leaders": lanes[:5],
        "boundary_note": _market_movers_sector_boundary_note(model.get("boundary_note")),
    }


def _market_mover_tone_style(tone: str) -> tuple[str, str, str]:
    if tone == "success":
        return OVERVIEW_COLOR_POSITIVE, "rgba(24, 130, 84, 0.10)", "rgba(24, 130, 84, 0.28)"
    if tone == "warning":
        return OVERVIEW_COLOR_WARNING, "rgba(214, 137, 16, 0.10)", "rgba(214, 137, 16, 0.30)"
    if tone == "error":
        return OVERVIEW_COLOR_DANGER, "rgba(197, 48, 48, 0.10)", "rgba(197, 48, 48, 0.30)"
    return OVERVIEW_COLOR_TEXT, OVERVIEW_COLOR_SURFACE_SUBTLE, OVERVIEW_COLOR_BORDER


def _detail_rows(items: list[tuple[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame([{"항목": label, "값": value if value not in (None, "") else "-"} for label, value in items])


def _format_detail_money(value: Any) -> str:
    return _compact_number(value, prefix="$")


def _format_detail_number(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return _compact_number(float(numeric))


def _format_relative_volume(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):.2f}x"


def _market_mover_peer_context(peer_rows: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if not isinstance(peer_rows, pd.DataFrame) or peer_rows.empty or "Symbol" not in peer_rows:
        return _detail_rows([("같은 섹터 맥락", "표시된 peer rows가 없습니다.")])
    normalized_symbol = str(symbol or "").strip().upper()
    rows = peer_rows.copy()
    rows["Symbol"] = rows["Symbol"].astype(str).str.strip().str.upper()
    selected_matches = rows[rows["Symbol"] == normalized_symbol]
    if selected_matches.empty:
        return _detail_rows([("같은 섹터 맥락", "선택 종목을 현재 표시 rows에서 찾을 수 없습니다.")])
    selected = selected_matches.iloc[0]
    sector = str(selected.get("Sector") or "Unknown").strip() or "Unknown"
    if "Sector" in rows:
        same_sector = rows[rows["Sector"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown") == sector]
    else:
        same_sector = rows.iloc[0:0]
    same_sector = same_sector.reset_index(drop=True)
    selected_positions = same_sector.index[same_sector["Symbol"] == normalized_symbol].tolist()
    position = selected_positions[0] + 1 if selected_positions else "-"
    avg_return = "-"
    top_symbol = "-"
    if not same_sector.empty and "Return %" in same_sector:
        numeric_returns = pd.to_numeric(same_sector["Return %"], errors="coerce")
        if numeric_returns.notna().any():
            avg_return = _format_signed(numeric_returns.mean())
            top_idx = numeric_returns.sort_values(ascending=False).index[0]
            top_row = same_sector.loc[top_idx]
            top_symbol = f"{top_row.get('Symbol', '-')} ({_format_signed(top_row.get('Return %'))})"
    return _detail_rows(
        [
            ("같은 섹터 내 표시 순위", f"{position} / {len(same_sector)}"),
            ("섹터", sector),
            ("같은 섹터 평균 수익률", avg_return),
            ("같은 섹터 상위 표시 종목", top_symbol),
        ]
    )


def _market_mover_detail_panel_model(
    selected: dict[str, Any],
    *,
    period: str,
    coverage: str,
    peer_rows: pd.DataFrame,
) -> dict[str, Any]:
    mover = dict(selected.get("mover") or {})
    rank_source = _market_mover_rank_source_label(selected.get("rank_source") or "Selected Rank")
    read_model = build_market_mover_why_it_moved_read_model(
        mover=mover,
        period=period,
        coverage=coverage,
        rank_source=rank_source,
    )
    identity = dict(read_model.get("identity") or {})
    context = dict(read_model.get("context") or {})
    movement = dict(read_model.get("movement") or {})
    symbol = str(identity.get("Symbol") or selected.get("symbol") or "").strip().upper()
    identity_rows = _detail_rows(
        [
            ("종목", symbol or "-"),
            ("회사", identity.get("Name") or "-"),
            ("섹터", identity.get("Sector") or "-"),
            ("산업", identity.get("Industry") or "-"),
            ("시가총액", _format_detail_money(identity.get("Market Cap"))),
        ]
    )
    context_rows = _detail_rows(
        [
            ("랭킹 기준", context.get("Rank Type") or rank_source),
            ("순위", context.get("Rank") or selected.get("rank") or "-"),
            ("기간", context.get("Period") or _market_mover_period_label(period)),
            ("Coverage", context.get("Coverage") or _coverage_label(coverage)),
        ]
    )
    movement_rows = _detail_rows(
        [
            ("수익률", _format_signed(movement.get("Return %"))),
            ("직전 수익률", _format_signed(movement.get("Previous Return %"))),
            ("모멘텀 변화", _format_signed(movement.get("Momentum Delta pp"), suffix="pp")),
            ("상대 거래량", _format_relative_volume(movement.get("Relative Volume"))),
            ("현재 거래량", _format_detail_number(movement.get("Current Volume") or movement.get("Volume"))),
            ("10일 평균 거래량", _format_detail_number(movement.get("Avg 10D Volume"))),
            ("거래량 기준", movement.get("Volume Basis") or "-"),
            ("거래대금", _format_detail_money(movement.get("Dollar Volume"))),
        ]
    )
    metadata = dict(read_model.get("metadata") or {})
    return {
        "selected": selected,
        "read_model": read_model,
        "identity_rows": identity_rows,
        "context_rows": context_rows,
        "movement_rows": movement_rows,
        "peer_context": _market_mover_peer_context(peer_rows, symbol),
        "status_strip": build_market_mover_metadata_status_strip(metadata),
        "links": read_model.get("links") if isinstance(read_model.get("links"), pd.DataFrame) else pd.DataFrame(),
    }


def build_market_mover_investigation_pane_model(detail_model: dict[str, Any]) -> dict[str, Any]:
    read_model = dict(detail_model.get("read_model") or {})
    identity = dict(read_model.get("identity") or {})
    context = dict(read_model.get("context") or {})
    movement = dict(read_model.get("movement") or {})
    symbol = str(identity.get("Symbol") or "-").strip().upper() or "-"
    name = str(identity.get("Name") or "-").strip() or "-"
    sector = str(identity.get("Sector") or "-").strip() or "-"
    industry = str(identity.get("Industry") or "-").strip() or "-"
    rank_type = str(context.get("Rank Type") or "-").strip() or "-"
    rank = context.get("Rank") or "-"
    coverage = str(context.get("Coverage") or "-").strip() or "-"
    period = str(context.get("Period") or "-").strip() or "-"
    status_strip = dict(detail_model.get("status_strip") or {})
    status_items = [dict(item) for item in list(status_strip.get("items") or [])]
    return {
        "schema_version": "market_mover_investigation_pane_v1",
        "title": f"{symbol} · {name}",
        "subtitle": f"{sector} · {industry} · {rank_type} #{rank} · {coverage} {period}",
        "rank_badge": f"{rank_type} #{rank}",
        "facts": [
            {"label": "수익률", "value": _format_signed(movement.get("Return %")), "detail": "selected period"},
            {"label": "상대 거래량", "value": _format_relative_volume(movement.get("Relative Volume")), "detail": "if available"},
            {
                "label": "현재 거래량",
                "value": _format_detail_number(movement.get("Current Volume") or movement.get("Volume")),
                "detail": "DB row",
            },
            {"label": "거래대금", "value": _format_detail_money(movement.get("Dollar Volume")), "detail": "if available"},
            {"label": "섹터", "value": sector, "detail": industry},
            {"label": "Coverage", "value": coverage, "detail": period},
        ],
        "status_items": status_items,
        "boundary_note": (
            "Manual investigation starter only: not a trading signal, recommendation, automated cause rating, "
            "validation gate, Final Review decision, or monitoring guidance."
        ),
    }


def _format_korean_money(value: Any, *, currency: str = "달러") -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    amount = float(numeric)
    sign = "-" if amount < 0 else ""
    absolute = abs(amount)
    if absolute >= 1_000_000_000_000:
        return f"{sign}{absolute / 1_000_000_000_000:.1f}조 {currency}"
    if absolute >= 100_000_000:
        return f"{sign}{absolute / 100_000_000:.1f}억 {currency}"
    return f"{sign}{absolute:,.0f} {currency}"


def _format_per(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):.2f}x"


def _format_eps(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"${float(numeric):,.2f}"


def _research_metric_item(
    label: str,
    value: str,
    detail: str,
    *,
    available: bool,
    tone: str = "neutral",
    rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    item = {
        "label": label,
        "value": value if value else "계산 불가",
        "detail": detail,
        "available": bool(available),
        "tone": tone,
    }
    if rows:
        item["rows"] = rows
    return item


def _financial_period_label(item: dict[str, Any], fallback: str) -> str:
    return str(item.get("period_end") or fallback)


def _financial_date_label(value: Any) -> str:
    if value in (None, ""):
        return "-"
    timestamp = pd.to_datetime(value, errors="coerce")
    if not pd.isna(timestamp):
        return timestamp.strftime("%Y-%m-%d")
    text = str(value).strip()
    return text[:10] if text else "-"


def _financial_disclosure_date_label(item: dict[str, Any]) -> str:
    for key in ("available_at", "filing_date", "latest_available_at", "latest_filing_date"):
        label = _financial_date_label(item.get(key))
        if label != "-":
            return label
    return "-"


def _financial_source_label(item: dict[str, Any]) -> str:
    source = str(item.get("financial_source") or "").strip()
    fallback_used = bool(item.get("fallback_used"))
    if source == "sec_edgar_statement_shadow":
        return "EDGAR statement shadow"
    if source == "legacy_broad_yfinance":
        return "legacy yfinance fallback" if fallback_used else "legacy yfinance"
    return source.replace("_", " ") if source else "source unknown"


def _financial_compact_source_label(item: dict[str, Any]) -> str:
    source = str(item.get("financial_source") or "").strip()
    if source == "sec_edgar_statement_shadow":
        return "EDGAR"
    if source == "legacy_broad_yfinance":
        return "legacy yfinance"
    return source.replace("_", " ") if source else "source unknown"


def _financial_compact_source_part(item: dict[str, Any]) -> tuple[str, str] | None:
    if str(item.get("status") or "").upper() != "OK":
        return None
    source_label = _financial_compact_source_label(item)
    form_type = str(item.get("form_type") or "").strip()
    period = _financial_period_label(item, "-")
    parts = [source_label]
    if form_type:
        parts.append(form_type)
    parts.append(period)
    return source_label, " ".join(part for part in parts if part and part != "-")


def _financial_compact_source_detail(*items: dict[str, Any]) -> str:
    parts = [part for part in (_financial_compact_source_part(item) for item in items if item) if part]
    if not parts:
        return "근거: 재무제표 snapshot 필요"
    first_label = parts[0][0]
    compact_parts = [parts[0][1]]
    for source_label, text in parts[1:]:
        compact_parts.append(text.removeprefix(f"{source_label} ") if source_label == first_label else text)
    detail = "근거: " + ", ".join(compact_parts)
    if any(_financial_disclosure_date_label(item) != "-" for item in items if item):
        detail += " · 공시일 기준"
    return detail


def _financial_source_detail(item: dict[str, Any], prefix: str) -> str:
    status = str(item.get("status") or "").upper()
    period = _financial_period_label(item, "-")
    source_label = _financial_source_label(item)
    parts = [f"{prefix} {period}", source_label]
    available_at = item.get("available_at")
    form_type = item.get("form_type")
    accession_no = item.get("accession_no")
    if available_at:
        parts.append(f"available {available_at}")
    if form_type:
        parts.append(str(form_type))
    if accession_no:
        parts.append(f"accession {accession_no}")
    if status != "OK":
        reason = str(item.get("reason") or "").strip()
        if reason:
            parts.append(reason)
    return " · ".join(str(part) for part in parts if str(part).strip())


def _per_eps_row(item: dict[str, Any], period_label: str) -> dict[str, str] | None:
    if str(item.get("status") or "").upper() != "OK":
        return None
    per = _format_per(item.get("per"))
    eps = _format_eps(item.get("eps"))
    if per == "-" and eps == "-":
        return None
    return {
        "period": period_label,
        "period_end": _financial_period_label(item, "-"),
        "disclosure_date": _financial_disclosure_date_label(item),
        "per": per,
        "eps": eps,
    }


def _income_row(item: dict[str, Any], period_label: str) -> dict[str, str] | None:
    if str(item.get("status") or "").upper() != "OK":
        return None
    net_income = item.get("net_income")
    if net_income is None:
        return None
    return {
        "period": period_label,
        "period_end": _financial_period_label(item, "-"),
        "disclosure_date": _financial_disclosure_date_label(item),
        "net_income": _format_korean_money(net_income),
    }


def _financial_statement_collection_model(collection: dict[str, Any]) -> dict[str, Any]:
    if not collection:
        return {}
    items = [
        {
            "label": str(item.get("label") or "-"),
            "value": str(item.get("value") or "-"),
            "detail": str(item.get("detail") or ""),
        }
        for item in list(collection.get("items") or [])
        if isinstance(item, dict)
    ]
    return {
        "status": str(collection.get("status") or "UNKNOWN"),
        "headline": str(collection.get("headline") or "재무제표 수집 상태 확인"),
        "detail": str(collection.get("detail") or ""),
        "tone": str(collection.get("tone") or "neutral"),
        "items": items,
        "missing_filings": list(collection.get("missing_filings") or []),
    }


def build_market_mover_research_snapshot_model(
    detail_model: dict[str, Any],
    *,
    research_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    read_model = dict(detail_model.get("read_model") or {})
    identity = dict(read_model.get("identity") or {})
    context = dict(read_model.get("context") or {})
    symbol = str(identity.get("Symbol") or "-").strip().upper() or "-"
    mover = dict(detail_model.get("selected", {}).get("mover") or {})
    if research_snapshot is None:
        research_snapshot = build_market_mover_research_snapshot(
            mover={
                **mover,
                "Symbol": symbol,
                "Market Cap": identity.get("Market Cap") or mover.get("Market Cap"),
            }
        )
    snapshot = dict(research_snapshot or {})
    current_market_cap = dict(snapshot.get("current_market_cap") or {})
    ytd_return = dict(snapshot.get("ytd_return") or {})
    annual = dict(snapshot.get("annual_financials") or {})
    quarterly = dict(snapshot.get("quarterly_financials") or {})
    collection = _financial_statement_collection_model(
        dict(snapshot.get("financial_statement_collection") or {})
    )

    current_available = str(current_market_cap.get("status") or "").upper() == "OK"
    ytd_available = str(ytd_return.get("status") or "").upper() == "OK"

    per_eps_rows = [
        row
        for row in [
            _per_eps_row(annual, "연간"),
            _per_eps_row(quarterly, "분기"),
        ]
        if row
    ]
    per_eps_available = bool(per_eps_rows)
    per_eps_value = (
        f"{' / '.join(row['period'] for row in per_eps_rows)} {'비교' if len(per_eps_rows) > 1 else '기준'}"
        if per_eps_rows
        else "계산 불가"
    )
    financial_detail = _financial_compact_source_detail(annual, quarterly)
    income_rows = [
        row
        for row in [
            _income_row(annual, "연간"),
            _income_row(quarterly, "분기"),
        ]
        if row
    ]
    income_value = (
        f"{' / '.join(row['period'] for row in income_rows)} {'비교' if len(income_rows) > 1 else '기준'}"
        if income_rows
        else "계산 불가"
    )

    items = [
        _research_metric_item(
            "현재 시총",
            _format_korean_money(current_market_cap.get("value")) if current_available else "계산 불가",
            str(current_market_cap.get("basis") or current_market_cap.get("reason") or "현재 asset profile 기준"),
            available=current_available,
            tone="positive" if current_available else "neutral",
        ),
        _research_metric_item(
            "올해 수익률",
            _format_signed(ytd_return.get("return_pct")) if ytd_available else "계산 불가",
            (
                f"{ytd_return.get('start_date')}부터 {ytd_return.get('end_date')}까지 · {ytd_return.get('basis')}"
                if ytd_available
                else str(ytd_return.get("reason") or "올해 가격 이력 필요")
            ),
            available=ytd_available,
            tone="positive" if ytd_available else "neutral",
        ),
        _research_metric_item(
            "PER / EPS",
            per_eps_value,
            (
                financial_detail
                if per_eps_available
                else str(annual.get("reason") or quarterly.get("reason") or "재무제표 net_income / shares_outstanding 필요")
            ),
            available=per_eps_available,
            tone="neutral",
            rows=per_eps_rows,
        ),
        _research_metric_item(
            "당기순이익",
            income_value,
            (
                financial_detail
                if income_rows
                else str(annual.get("reason") or quarterly.get("reason") or "재무제표 snapshot 필요")
            ),
            available=bool(income_rows),
            tone="neutral",
            rows=income_rows,
        ),
    ]
    return {
        "schema_version": "market_mover_research_metrics_v1",
        "title": "기본 지표",
        "subtitle": f"{symbol} · {context.get('Coverage') or '-'} · {context.get('Period') or '-'}",
        "as_of_label": str(snapshot.get("as_of_date") or "현재 선택 기준"),
        "items": items,
        "financial_statement_collection": collection,
        "boundary_note": str(
            snapshot.get("boundary_note")
            or "Context-only fundamentals snapshot; no trading signal or recommendation is produced."
        ),
    }


def _market_mover_metadata_session_key(read_model: dict[str, Any]) -> str:
    identity = dict(read_model.get("identity") or {})
    context = dict(read_model.get("context") or {})
    raw_parts = [
        "overview_market_mover_metadata",
        identity.get("Symbol") or "UNKNOWN",
        context.get("Coverage") or "-",
        context.get("Period") or "-",
        context.get("Rank Type") or "-",
    ]
    safe_parts = [
        str(part).strip().replace(" ", "_").replace("/", "_").replace(":", "_").lower()
        for part in raw_parts
    ]
    return "__".join(safe_parts)


def _market_mover_statement_refresh_session_key(metadata_key: str) -> str:
    return f"{metadata_key}__statement_refresh_result"


def _format_elapsed_seconds(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    amount = float(numeric)
    if amount < 60:
        return f"{amount:.1f}초"
    minutes, seconds = divmod(int(round(amount)), 60)
    return f"{minutes}분 {seconds:02d}초"


def _market_mover_statement_refresh_target(collection: dict[str, Any]) -> dict[str, Any]:
    status = str(collection.get("status") or "").strip().upper()
    missing_filings = [item for item in list(collection.get("missing_filings") or []) if isinstance(item, dict)]
    first = dict(missing_filings[0]) if missing_filings else {}
    form_type = str(first.get("form_type") or "").strip().upper()
    period_label = str(first.get("period_label") or "").strip()
    report_date = str(first.get("report_date") or first.get("period_end") or "").strip()
    freq = "annual" if form_type.startswith("10-K") or period_label == "연간" else "quarterly"
    freq_label = "연간" if freq == "annual" else "분기"
    enabled = status in {"ACTION_REQUIRED", "CHECK_REQUIRED"}
    if enabled and report_date:
        detail = f"{freq_label} {report_date} 기준 자료를 EDGAR statement path로 수집합니다."
    elif enabled:
        detail = f"{freq_label} 재무제표를 EDGAR statement path로 수집합니다."
    else:
        detail = "기본 지표 기준으로 지금 수집할 재무제표 항목이 없습니다."
    return {
        "enabled": enabled,
        "freq": freq,
        "freq_label": freq_label,
        "form_type": form_type or ("10-K" if freq == "annual" else "10-Q"),
        "report_date": report_date or "-",
        "detail": detail,
        "status": status or "UNKNOWN",
    }


def _render_market_mover_statement_refresh_result(payload: dict[str, Any] | None) -> None:
    if not isinstance(payload, dict):
        return
    result = dict(payload.get("result") or {})
    status = str(result.get("status") or "").lower()
    message = str(result.get("message") or "재무제표 수집 결과를 확인했습니다.")
    if status == "success":
        st.success(message)
    elif status in {"partial_success", "skipped", "locked"}:
        st.warning(message)
    else:
        st.error(message)
    st.caption(
        " · ".join(
            [
                f"시작 {payload.get('started_at') or '-'}",
                f"종료 {payload.get('finished_at') or '-'}",
                f"화면 대기 {_format_elapsed_seconds(payload.get('elapsed_sec'))}",
                f"job 소요 {_format_elapsed_seconds(result.get('duration_sec'))}",
                f"저장 rows {result.get('rows_written') or 0}",
                f"처리 {result.get('symbols_processed') or 0}/{result.get('symbols_requested') or 0}",
            ]
        )
    )


def _render_market_mover_status_strip(strip: dict[str, Any]) -> None:
    items = list(strip.get("items") or [])
    if not items:
        return
    blocks: list[str] = []
    for item in items:
        tone_color, tone_bg, tone_border = _market_mover_tone_style(str(item.get("tone") or "neutral"))
        blocks.append(
            "<div style='"
            f"border:1px solid {tone_border}; background:{tone_bg}; border-radius:8px; "
            "padding:8px 10px; min-width:120px;'>"
            f"<div style='font-size:11px; color:{OVERVIEW_COLOR_TEXT_MUTED};'>{escape(str(item.get('label') or '-'))}</div>"
            f"<div style='font-size:14px; font-weight:700; color:{tone_color};'>{escape(str(item.get('value') or '-'))}</div>"
            "</div>"
        )
    st.markdown(
        "<div style='display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 12px 0;'>"
        + "".join(blocks)
        + "</div>",
        unsafe_allow_html=True,
    )


def _render_market_mover_detail_table(title: str, frame: pd.DataFrame) -> None:
    st.markdown(f"##### {title}")
    st.dataframe(frame, width="stretch", hide_index=True)


def _render_market_mover_metadata_table(frame: pd.DataFrame, columns: list[str], empty_message: str) -> None:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        st.info(empty_message)
        return
    st.dataframe(
        _market_mover_open_link_frame(frame, columns),
        width="stretch",
        hide_index=True,
        column_config=_market_mover_metadata_column_config(),
    )


def _market_mover_sector_breadth_table(model: dict[str, Any]) -> pd.DataFrame:
    rows = model.get("table_rows")
    if isinstance(rows, pd.DataFrame):
        return rows
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame()


def _render_market_movers_sector_breadth_context(snapshot: dict[str, Any]) -> None:
    model = snapshot.get("sector_breadth")
    if not isinstance(model, dict):
        return
    render_market_movers_section_divider(
        "섹터 / 시장 확산 맥락",
        "선택 coverage의 움직임이 넓게 퍼졌는지, 특정 그룹에 집중됐는지 확인합니다.",
    )
    render_sector_breadth_market_map(build_market_movers_sector_map_model(model))
    table_rows = _market_mover_sector_breadth_table(model)
    with st.expander("섹터 breadth 상세 표", expanded=False):
        if table_rows.empty:
            st.info("선택한 coverage/period에서 표시할 sector breadth row가 없습니다.")
        else:
            st.dataframe(table_rows, width="stretch", hide_index=True)


@st.fragment
def _render_market_mover_selected_investigation_fragment(
    selected: dict[str, Any],
    *,
    period: str,
    universe_code: str,
    peer_rows: pd.DataFrame,
) -> None:
    detail_model = _market_mover_detail_panel_model(
        selected,
        period=period,
        coverage=universe_code,
        peer_rows=peer_rows,
    )
    read_model = dict(detail_model["read_model"])
    metadata_key = _market_mover_metadata_session_key(read_model)
    stored_metadata = st.session_state.get(metadata_key)
    if isinstance(stored_metadata, dict):
        read_model["metadata"] = stored_metadata
        detail_model["read_model"] = read_model
        detail_model["status_strip"] = build_market_mover_metadata_status_strip(stored_metadata)

    render_market_mover_investigation_pane(build_market_mover_investigation_pane_model(detail_model))
    identity = dict(read_model.get("identity") or {})
    symbol = str(identity.get("Symbol") or selected.get("symbol") or "").strip().upper()

    render_market_movers_section_divider("조사 단서", "기본 지표, 뉴스, SEC 공시, 외부 검색 시작점")
    metadata = dict(read_model.get("metadata") or {})
    research_snapshot = build_market_mover_research_snapshot(
        mover={
            **dict(selected.get("mover") or {}),
            "Symbol": symbol,
            "Market Cap": identity.get("Market Cap") or dict(selected.get("mover") or {}).get("Market Cap"),
        }
    )
    research_model = build_market_mover_research_snapshot_model(detail_model, research_snapshot=research_snapshot)
    clue_tabs = st.tabs(["기본 지표", "뉴스", "SEC 공시", "외부 검색"])
    with clue_tabs[0]:
        render_market_mover_research_snapshot(research_model)
    with clue_tabs[1]:
        st.caption("일반 뉴스와 한국어 뉴스를 같은 탭에서 확인합니다. 원문 본문은 조회하거나 저장하지 않습니다.")
        if st.button(
            "뉴스 메타데이터 조회",
            key=f"{metadata_key}__fetch_news",
            help="현재 선택 종목 1개에 대해 세션 전용 뉴스 / 한국어 뉴스 metadata만 조회합니다.",
        ):
            with st.spinner(f"{symbol} 뉴스 메타데이터를 조회하는 중입니다..."):
                metadata_update = fetch_market_mover_news_metadata(
                    symbol,
                    name=identity.get("Name"),
                    max_news=3,
                    max_korean_news=3,
                )
                metadata = merge_market_mover_metadata(st.session_state.get(metadata_key), metadata_update)
                st.session_state[metadata_key] = metadata
            st.success("뉴스와 한국어 뉴스 메타데이터를 세션 전용으로 조회했습니다.")
        st.caption("뉴스 메타데이터")
        _render_market_mover_metadata_table(
            metadata.get("news"),
            ["Title", "Source", "Published At", "Open"],
            "뉴스 메타데이터는 아직 조회하지 않았습니다. 필요할 때 현재 선택 종목만 조회하세요.",
        )
        st.caption("한국어 뉴스")
        _render_market_mover_metadata_table(
            metadata.get("korean_news"),
            ["Title", "Source", "Published At", "Snippet", "Open"],
            "한국어 뉴스 메타데이터는 아직 조회하지 않았습니다. 원문 기사 본문은 수집하거나 저장하지 않습니다.",
        )
    with clue_tabs[2]:
        st.caption("SEC 공시 메타데이터와 필요한 재무제표 수집을 이 탭에서 처리합니다.")
        if st.button(
            "SEC 공시 메타데이터 조회",
            key=f"{metadata_key}__fetch_sec",
            help="현재 선택 종목 1개에 대해 세션 전용 SEC filing metadata만 조회합니다.",
        ):
            with st.spinner(f"{symbol} SEC 공시 메타데이터를 조회하는 중입니다..."):
                metadata_update = fetch_market_mover_sec_metadata(
                    symbol,
                    max_filings=3,
                )
                metadata = merge_market_mover_metadata(st.session_state.get(metadata_key), metadata_update)
                st.session_state[metadata_key] = metadata
            st.success("SEC 공시 메타데이터를 세션 전용으로 조회했습니다.")
        _render_market_mover_metadata_table(
            metadata.get("sec_filings"),
            ["Form", "Filing Date", "Title", "Open"],
            "SEC 공시 메타데이터는 아직 조회하지 않았습니다. 공시 원문은 공식 링크에서 직접 확인합니다.",
        )

        collection = dict(research_model.get("financial_statement_collection") or {})
        refresh_target = _market_mover_statement_refresh_target(collection)
        statement_result_key = _market_mover_statement_refresh_session_key(metadata_key)
        st.markdown("##### 재무제표 수집")
        st.caption(refresh_target["detail"])
        if st.button(
            "필요 재무제표 수집",
            key=f"{metadata_key}__statement_refresh",
            disabled=not bool(refresh_target["enabled"]),
            help="기본 지표에서 받아야 할 연간 또는 분기 재무제표가 있을 때 선택 종목만 EDGAR statement path로 수집합니다.",
        ):
            started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            t0 = perf_counter()
            with st.spinner(f"{symbol} {refresh_target['freq_label']} 재무제표를 수집하는 중입니다..."):
                result = run_overview_market_mover_statement_refresh(
                    symbol=symbol,
                    freq=refresh_target["freq"],
                )
            finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state[statement_result_key] = {
                "started_at": started_at,
                "finished_at": finished_at,
                "elapsed_sec": perf_counter() - t0,
                "target": refresh_target,
                "result": result,
            }
            try:
                record_overview_action_result(result)
            except Exception as exc:  # pragma: no cover - UI resilience only
                st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"
        if not refresh_target["enabled"]:
            st.info("현재 기본 지표 기준으로 받아야 할 재무제표 수집 항목이 없습니다.")
        _render_market_mover_statement_refresh_result(st.session_state.get(statement_result_key))
    with clue_tabs[3]:
        table_model = _market_mover_external_search_table_model(detail_model["links"])
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
    rank_source: str = "Return Rank",
    id_prefix: str = "return",
    label_prefix: str = "수익률",
) -> None:
    candidates = _market_mover_catalyst_candidates(
        rows,
        volume_rows,
        primary_rank_source=rank_source,
        primary_id_prefix=id_prefix,
        primary_label_prefix=label_prefix,
        include_volume_candidates=False,
    )
    if not candidates:
        return
    render_market_movers_section_divider(
        "선택 종목 조사",
        "랭킹에서 고른 종목의 가격, 거래량, 섹터, 외부 조사 시작점을 한 곳에서 확인합니다.",
    )
    candidate_by_id = {item["id"]: item for item in candidates}
    option_ids = list(candidate_by_id)
    selection_key = "overview_market_mover_detail_selection"
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
    _render_market_mover_selected_investigation_fragment(
        selected,
        period=period,
        universe_code=universe_code,
        peer_rows=rows,
    )


def _render_market_movers_snapshot_panel(
    snapshot: dict[str, Any],
    *,
    controls: MarketMoverControls,
) -> None:
    _render_snapshot_warnings(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        render_market_movers_empty_state(build_market_movers_empty_state_model(snapshot, controls=controls))
        _render_missing_diagnostics(snapshot, universe_code=controls.coverage, period=controls.period)
        return
    volume_rows = snapshot.get("volume_rows")
    if not isinstance(volume_rows, pd.DataFrame) or volume_rows.empty:
        volume_rows = rows
    selected_model = _market_mover_view_model(snapshot, controls.mode)
    selected_rows = selected_model["rows"]

    if selected_rows.empty:
        st.markdown(f"#### {selected_model['label']} 상위 종목")
        st.info(selected_model["empty_reason"])
    else:
        render_market_mover_board(build_market_mover_board_model(selected_model, top_n=controls.top_n))

    _render_market_movers_sector_breadth_context(snapshot)
    _render_missing_diagnostics(snapshot, universe_code=controls.coverage, period=controls.period)
    mode_models = [_market_mover_view_model(snapshot, mode) for mode in MARKET_MOVER_MODE_ORDER]
    with st.expander("모드별 상세 표 전체 높이로 보기", expanded=False):
        table_tabs = st.tabs([model["label"] for model in mode_models])
        for tab, model in zip(table_tabs, mode_models, strict=True):
            with tab:
                mode_rows = model["rows"]
                st.caption(model["sort_basis"])
                if mode_rows.empty:
                    st.info(model["empty_reason"])
                    continue
                st.dataframe(
                    mode_rows,
                    width="stretch",
                    height=_market_mover_chart_height(len(mode_rows)) + MARKET_MOVER_TABLE_CHROME_HEIGHT,
                    hide_index=True,
                )
    investigation_rows = (
        selected_rows
        if selected_model["kind"] == "symbol" and isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty
        else rows
    )
    investigation_rank_source = selected_model["label"] if selected_model["kind"] == "symbol" else "Top Gainers"
    investigation_id_prefix = selected_model["mode"] if selected_model["kind"] == "symbol" else "top_gainers"
    investigation_label_prefix = selected_model["label"] if selected_model["kind"] == "symbol" else "Top Gainers"
    _render_market_mover_why_it_moved_panel(
        investigation_rows,
        volume_rows,
        universe_code=controls.coverage,
        period=controls.period,
        rank_source=investigation_rank_source,
        id_prefix=investigation_id_prefix,
        label_prefix=investigation_label_prefix,
    )


def render_market_movers_snapshot(controls: MarketMoverControls) -> None:
    snapshot = _load_market_movers_snapshot(
        universe_code=controls.coverage,
        universe_limit=controls.universe_limit,
        period=controls.period,
        top_n=controls.top_n,
        sector=controls.sector,
    )
    react_event = _render_market_movers_react_summary(snapshot, controls=controls)
    _dispatch_market_movers_react_event(react_event, controls=controls)
    if react_event is None:
        _render_market_movers_refresh_bar(
            snapshot,
            universe_code=controls.coverage,
            universe_limit=controls.universe_limit,
            period=controls.period,
        )
    else:
        _render_market_movers_react_refresh_companion(snapshot, controls=controls)
    _render_market_movers_coverage_trust(snapshot, controls=controls)
    _render_market_movers_snapshot_panel(
        snapshot,
        controls=controls,
    )
