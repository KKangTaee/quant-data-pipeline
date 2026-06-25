from __future__ import annotations

from typing import Any

from app.web.overview import legacy_dashboard as _legacy


def render_market_movers_header() -> None:
    _legacy.st.markdown("### Market Movers")


def render_market_movers_controls() -> Any:
    return _legacy._render_market_movers_controls()


def render_market_movers_context_captions(controls: Any) -> None:
    reloaded_at = _legacy.st.session_state.get("overview_market_movers_reloaded_at")
    if reloaded_at:
        _legacy.st.caption(f"Last DB snapshot reload request: {reloaded_at}")
    if controls.period == "daily":
        _legacy.st.caption(
            "Daily는 저장된 quote snapshot을 previous close와 비교합니다. 갱신 방식은 아래 데이터 갱신 영역에서 선택합니다."
        )


def normalize_market_movers_refresh_mode(controls: Any) -> None:
    if controls.coverage not in _legacy.BROWSER_AUTO_REFRESH_JOB_CONFIG or controls.period != "daily":
        _legacy.st.session_state["overview_market_movers_refresh_mode"] = "manual"


def is_market_movers_auto_refresh_enabled(controls: Any) -> bool:
    return (
        controls.coverage in _legacy.BROWSER_AUTO_REFRESH_JOB_CONFIG
        and controls.period == "daily"
        and _legacy.st.session_state.get("overview_market_movers_refresh_mode") == "auto"
    )


def render_market_movers_auto_refresh_panel(controls: Any) -> None:
    @_legacy.st.fragment(run_every=_legacy.BROWSER_AUTO_REFRESH_SECONDS)
    def _market_movers_auto_refresh_panel() -> None:
        summary, checked_at = _legacy._get_browser_auto_refresh_state(controls.coverage)
        if _legacy._should_run_browser_auto_refresh_check(summary, checked_at=str(checked_at or "")):
            coverage_label = _legacy.MARKET_COVERAGE_LABELS.get(controls.coverage, controls.coverage)
            with _legacy.st.spinner(f"{coverage_label} 자동 갱신 조건을 확인하는 중입니다..."):
                _legacy._run_browser_auto_refresh_check(universe_code=controls.coverage)
        render_market_movers_snapshot(controls)

    _market_movers_auto_refresh_panel()


def render_market_movers_snapshot(controls: Any) -> None:
    snapshot = _legacy._load_market_movers_snapshot(
        universe_code=controls.coverage,
        universe_limit=controls.universe_limit,
        period=controls.period,
        top_n=controls.top_n,
        sector=controls.sector,
    )
    _legacy._render_market_movers_refresh_bar(
        snapshot,
        universe_code=controls.coverage,
        universe_limit=controls.universe_limit,
        period=controls.period,
    )
    _legacy._render_market_movers_snapshot_panel(
        snapshot,
        universe_code=controls.coverage,
        period=controls.period,
    )
