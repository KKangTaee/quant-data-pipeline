from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy_dashboard
from app.web.overview.page import render_overview_dashboard as _render_overview_dashboard


for _name in dir(_legacy_dashboard):
    if _name.startswith("__") and _name.endswith("__"):
        continue
    globals()[_name] = getattr(_legacy_dashboard, _name)

render_overview_dashboard = _render_overview_dashboard
