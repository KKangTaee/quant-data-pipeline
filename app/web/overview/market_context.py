from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy
from app.web.overview.components.market_context import render_macro_context_cockpit


def render_market_context_tab() -> None:
    """Render the Market Context Overview tab."""
    _legacy.st.markdown("### 시장 맥락")
    _legacy.st.caption("저장된 시장 자료로 현재 세션의 움직임, 확산, 이벤트 배경을 빠르게 확인합니다.")
    _legacy._render_overview_market_context_refresh_reflection()
    market_session_context = _legacy._market_context_session_payload()
    cockpit_model = _legacy.load_overview_macro_context_cockpit(
        market_session_context=market_session_context,
    )
    render_macro_context_cockpit(cockpit_model, include_reading_flow=False)
    _legacy._render_overview_market_context_refresh_bar(cockpit_model)
