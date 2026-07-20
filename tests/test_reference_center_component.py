from __future__ import annotations

import importlib
import math
import tempfile
import unittest
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pandas as pd


def _load_component():
    try:
        return importlib.import_module("app.web.reference_center_react_component")
    except ModuleNotFoundError as exc:
        raise AssertionError("Reference Center React component bridge is required") from exc


class ReferenceCenterComponentTests(unittest.TestCase):
    def test_build_availability_requires_index_html(self) -> None:
        component = _load_component()
        with tempfile.TemporaryDirectory() as directory:
            build_dir = Path(directory)
            self.assertFalse(component.reference_center_react_component_available(build_dir))
            (build_dir / "index.html").write_text("<html></html>", encoding="utf-8")
            self.assertTrue(component.reference_center_react_component_available(build_dir))

    def test_json_safe_payload_normalizes_python_pandas_and_non_finite_values(self) -> None:
        component = _load_component()
        payload = {
            "money": Decimal("123.45"),
            "day": date(2026, 7, 20),
            "timestamp": datetime(2026, 7, 20, 12, 30),
            "frame": pd.DataFrame(
                {
                    "date": [pd.Timestamp("2026-07-19")],
                    "value": [float("nan")],
                }
            ),
            "series": pd.Series({"finite": 2.0, "infinite": float("inf")}),
            "missing": pd.NA,
            "negative_infinite": -math.inf,
        }

        safe = component._json_safe_payload(payload)

        self.assertEqual(safe["money"], 123.45)
        self.assertEqual(safe["day"], "2026-07-20")
        self.assertEqual(safe["timestamp"], "2026-07-20T12:30:00")
        self.assertEqual(safe["frame"], [{"date": "2026-07-19T00:00:00", "value": None}])
        self.assertEqual(safe["series"], {"finite": 2.0, "infinite": None})
        self.assertIsNone(safe["missing"])
        self.assertIsNone(safe["negative_infinite"])

    def test_component_name_default_key_and_event_dict_are_stable(self) -> None:
        component = _load_component()
        calls = []

        def fake_component(**kwargs):
            calls.append(kwargs)
            return {"event": {"id": "navigate_to_surface"}}

        with patch.object(component, "_declare_reference_center_component", return_value=fake_component):
            result = component.render_reference_center_workbench({"value": Decimal("10")})

        self.assertEqual(component.REFERENCE_CENTER_REACT_COMPONENT_NAME, "reference_center_workbench")
        self.assertEqual(component.REFERENCE_CENTER_REACT_BUILD_DIR.name, "component_static")
        self.assertEqual(result, {"event": {"id": "navigate_to_surface"}})
        self.assertEqual(calls[0]["key"], "reference_center_workbench")
        self.assertEqual(calls[0]["default"], {"event": None})
        self.assertEqual(calls[0]["payload"], {"value": 10.0})

    def test_non_dict_component_value_returns_none(self) -> None:
        component = _load_component()

        with patch.object(component, "_declare_reference_center_component", return_value=lambda **_: "invalid"):
            self.assertIsNone(component.render_reference_center_workbench({"schema_version": "v1"}))

    def test_missing_build_returns_none_without_declaring_component(self) -> None:
        component = _load_component()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(component, "REFERENCE_CENTER_REACT_BUILD_DIR", Path(directory)):
                component._reference_center_component = None
                self.assertIsNone(component.render_reference_center_workbench({"schema_version": "v1"}))


if __name__ == "__main__":
    unittest.main()
