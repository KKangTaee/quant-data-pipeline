from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_futures_macro_header() -> None:
    _legacy.st.markdown("### 선물 매크로")
    _legacy.st.caption("저장된 선물 일봉으로 현재 macro 상태와 과거 점검 근거를 함께 확인합니다.")


def render_futures_macro_fragment(*, detail_expanded: bool) -> None:
    _legacy._render_futures_macro_fragment(detail_expanded=detail_expanded)
