from __future__ import annotations

import importlib
import math
import tempfile
import unittest
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pandas as pd


def _load_component():
    try:
        return importlib.import_module("app.web.portfolio_monitoring_react_component")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring React component bridge is required") from exc


class PortfolioMonitoringComponentTests(unittest.TestCase):
    def test_build_availability_requires_index_html(self) -> None:
        component = _load_component()
        with tempfile.TemporaryDirectory() as directory:
            build_dir = Path(directory)
            self.assertFalse(component.portfolio_monitoring_react_component_available(build_dir))
            (build_dir / "index.html").write_text("<html></html>", encoding="utf-8")
            self.assertTrue(component.portfolio_monitoring_react_component_available(build_dir))

    def test_json_safe_payload_normalizes_python_pandas_and_non_finite_values(self) -> None:
        component = _load_component()

        @dataclass(frozen=True)
        class Snapshot:
            value: Decimal

        payload = {
            "money": Decimal("123.45"),
            "day": date(2026, 7, 19),
            "timestamp": datetime(2026, 7, 19, 12, 30),
            "frame": pd.DataFrame(
                {
                    "date": [pd.Timestamp("2026-07-18")],
                    "value": [float("nan")],
                }
            ),
            "series": pd.Series({"finite": 2.0, "infinite": float("inf")}),
            "missing": pd.NA,
            "negative_infinite": -math.inf,
            "snapshot": Snapshot(Decimal("7.5")),
        }

        safe = component._json_safe_payload(payload)

        self.assertEqual(safe["money"], 123.45)
        self.assertEqual(safe["day"], "2026-07-19")
        self.assertEqual(safe["timestamp"], "2026-07-19T12:30:00")
        self.assertEqual(safe["frame"], [{"date": "2026-07-18T00:00:00", "value": None}])
        self.assertEqual(safe["series"], {"finite": 2.0, "infinite": None})
        self.assertIsNone(safe["missing"])
        self.assertIsNone(safe["negative_infinite"])
        self.assertEqual(safe["snapshot"], {"value": 7.5})

    def test_component_name_and_default_key_are_stable(self) -> None:
        component = _load_component()
        calls = []

        def fake_component(**kwargs):
            calls.append(kwargs)
            return {"event": None}

        with patch.object(component, "_declare_portfolio_monitoring_component", return_value=fake_component):
            result = component.render_portfolio_monitoring_workbench({"value": Decimal("10")})

        self.assertEqual(component.PORTFOLIO_MONITORING_REACT_COMPONENT_NAME, "portfolio_monitoring_workbench")
        self.assertEqual(result, {"event": None})
        self.assertEqual(calls[0]["key"], "portfolio_monitoring_workbench")
        self.assertEqual(calls[0]["default"], {"event": None})
        self.assertEqual(calls[0]["payload"], {"value": 10.0})

    def test_missing_build_returns_none_without_declaring_component(self) -> None:
        component = _load_component()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(component, "PORTFOLIO_MONITORING_REACT_BUILD_DIR", Path(directory)):
                component._portfolio_monitoring_component = None
                self.assertIsNone(component.render_portfolio_monitoring_workbench({"schema_version": "v1"}))


if __name__ == "__main__":
    unittest.main()
