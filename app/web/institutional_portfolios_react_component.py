from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit.components.v1 as components


INSTITUTIONAL_PORTFOLIOS_REACT_COMPONENT_NAME = "institutional_portfolios_workbench"
INSTITUTIONAL_PORTFOLIOS_REACT_COMPONENT_ROOT = (
    Path(__file__).resolve().parent
    / "streamlit_components"
    / "institutional_portfolios_workbench"
)
INSTITUTIONAL_PORTFOLIOS_REACT_BUILD_DIR = INSTITUTIONAL_PORTFOLIOS_REACT_COMPONENT_ROOT / "component_static"

_institutional_portfolios_component = None


def institutional_portfolios_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else INSTITUTIONAL_PORTFOLIOS_REACT_BUILD_DIR
    return (target / "index.html").exists()


def _declare_institutional_portfolios_component():
    global _institutional_portfolios_component
    if not institutional_portfolios_react_component_available():
        return None
    if _institutional_portfolios_component is None:
        _institutional_portfolios_component = components.declare_component(
            INSTITUTIONAL_PORTFOLIOS_REACT_COMPONENT_NAME,
            path=str(INSTITUTIONAL_PORTFOLIOS_REACT_BUILD_DIR),
        )
    return _institutional_portfolios_component


def _json_safe_payload(value: Any) -> Any:
    """Convert Python/Pandas payload values before Streamlit JSON marshaling."""
    if isinstance(value, dict):
        return {str(key): _json_safe_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe_payload(item) for item in value]
    if isinstance(value, pd.DataFrame):
        return _json_safe_payload(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _json_safe_payload(value.to_dict())
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
            return _json_safe_payload(value.item())
        except (TypeError, ValueError):
            pass
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def render_institutional_portfolios_workbench(
    payload: dict[str, Any],
    *,
    key: str = "institutional_portfolios_workbench",
) -> dict[str, Any] | None:
    component = _declare_institutional_portfolios_component()
    if component is None:
        return None
    value = component(
        payload=_json_safe_payload(payload),
        key=key,
        default={"event": None},
    )
    return value if isinstance(value, dict) else None
