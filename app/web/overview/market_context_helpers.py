from __future__ import annotations

from typing import Any

from app.web.overview import legacy_dashboard as _legacy


def render_market_context_header() -> None:
    """Render the compact Market Context tab heading."""
    _legacy.st.markdown("### 시장 맥락")
    _legacy.st.caption("저장된 시장 자료로 현재 세션의 움직임, 확산, 이벤트 배경을 빠르게 확인합니다.")


def render_market_context_refresh_reflection() -> None:
    _legacy._render_overview_market_context_refresh_reflection()


def load_market_context_cockpit_model() -> dict[str, Any]:
    market_session_context = _legacy._market_context_session_payload()
    return _legacy.load_overview_macro_context_cockpit(
        market_session_context=market_session_context,
    )


def render_market_context_refresh_bar(cockpit_model: dict[str, Any]) -> None:
    _legacy._render_overview_market_context_refresh_bar(cockpit_model)
