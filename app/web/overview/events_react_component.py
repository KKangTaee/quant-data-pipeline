from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit.components.v1 as components


EVENTS_REACT_COMPONENT_NAME = "events_workbench"
EVENTS_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "events_workbench"
)
EVENTS_REACT_BUILD_DIR = EVENTS_REACT_COMPONENT_ROOT / "component_static"

_events_component = None


def events_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else EVENTS_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_events_component():
    global _events_component
    if not events_react_component_available():
        return None
    if _events_component is None:
        _events_component = components.declare_component(
            EVENTS_REACT_COMPONENT_NAME,
            path=str(EVENTS_REACT_BUILD_DIR),
        )
    return _events_component


def _events_json_safe_payload(value: Any) -> Any:
    """Convert Python/Pandas payload values before Streamlit JSON marshaling."""
    if isinstance(value, dict):
        return {str(key): _events_json_safe_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_events_json_safe_payload(item) for item in value]
    if isinstance(value, pd.DataFrame):
        return _events_json_safe_payload(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _events_json_safe_payload(value.to_dict())
    if value is pd.NaT or value is pd.NA:
        return None
    if isinstance(value, pd.Timestamp):
        return None if pd.isna(value) else value.isoformat()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value) if value.is_finite() else None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "item") and callable(value.item):
        try:
            return _events_json_safe_payload(value.item())
        except (TypeError, ValueError):
            pass
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def render_events_react_workbench(
    payload: dict[str, Any],
    *,
    key: str = "events_workbench",
) -> dict[str, Any] | None:
    component = _declare_events_component()
    if component is None:
        return None
    value = component(
        payload=_events_json_safe_payload(payload),
        key=key,
        default={"event": None},
    )
    return value if isinstance(value, dict) else None
