"""Task-oriented Data Operations views."""

from app.web.ingestion.views.advanced import render_advanced_view
from app.web.ingestion.views.history import render_history_view
from app.web.ingestion.views.imports import render_imports_view
from app.web.ingestion.views.preparation import render_preparation_view
from app.web.ingestion.views.recovery import render_recovery_view

__all__ = [
    "render_advanced_view",
    "render_history_view",
    "render_imports_view",
    "render_preparation_view",
    "render_recovery_view",
]
