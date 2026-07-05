from __future__ import annotations

from app.web.overview.futures_macro_helpers import (
    render_futures_macro_fragment,
    render_futures_macro_header,
)


def render_futures_macro_tab() -> None:
    """Render the Futures Macro Overview tab."""
    render_futures_macro_header()
    render_futures_macro_fragment(detail_expanded=False)
