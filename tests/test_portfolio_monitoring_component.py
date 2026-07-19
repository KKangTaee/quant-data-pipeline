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
    def test_value_chart_exposes_visible_pointer_and_keyboard_tooltip(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn('className="pm-chart-hit-area"', source)
        self.assertIn("onPointerMove=", source)
        self.assertIn("onFocus={() => setActiveIndex(index)}", source)
        self.assertIn('className="pm-chart-hover-line"', source)
        self.assertIn('className="pm-chart-tooltip"', source)

    def test_value_chart_hides_static_point_halo_and_renders_responsive_date_ticks(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn("buildChartDateTicks(series, 5)", source)
        self.assertIn("buildChartDateTicks(series, 3)", source)
        self.assertIn('className="pm-date-ticks-desktop"', source)
        self.assertIn('className="pm-date-ticks-mobile"', source)
        self.assertRegex(styles, r"\.pm-chart-point circle \{[^}]*opacity: 0;")
        self.assertIn("vector-effect: non-scaling-stroke;", styles)
        self.assertIn(".pm-date-ticks-mobile { display: none; }", styles)

    def test_selected_detail_supports_real_price_line_candles_and_strategy_value_only(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn("function MarketPriceChart", source)
        self.assertIn("function StrategyValueChart", source)
        self.assertIn("가격 차트", source)
        self.assertIn("라인", source)
        self.assertIn("캔들", source)
        self.assertIn("전략에는 OHLCV 캔들이 없습니다", source)
        self.assertIn('className="pm-market-volume-bar"', source)
        self.assertIn('className="pm-market-tooltip"', source)
        self.assertIn(".pm-market-candle.is-up", styles)
        self.assertIn(".pm-market-candle.is-down", styles)

    def test_market_chart_exposes_client_side_zoom_pan_controls(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn("zoomMarketChartViewport", source)
        self.assertIn("panMarketChartViewport", source)
        self.assertIn("onWheel={handleWheel}", source)
        self.assertIn("onDoubleClick={resetViewport}", source)
        self.assertIn("onLostPointerCapture={cancelPointerDrag}", source)
        self.assertIn('aria-label="가격 차트 확대"', source)
        self.assertIn('aria-label="가격 차트 축소"', source)
        self.assertIn("전체 보기", source)
        self.assertIn('event.pointerType === "touch"', source)
        self.assertIn(".pm-market-hit-area.is-draggable", styles)
        self.assertIn("touch-action: pan-y;", styles)

    def test_selected_chart_prioritizes_detail_width_and_readable_axes(self) -> None:
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn(
            ".pm-content-grid { display: grid; grid-template-columns: minmax(280px, .35fr) minmax(0, .65fr);",
            styles,
        )
        self.assertIn(
            ".pm-market-axis, .pm-market-date { fill: #63798a; font-size: 11px; font-weight: 700; }",
            styles,
        )
        self.assertRegex(
            styles,
            r"@media \(max-width: 900px\) \{[\s\S]*?\.pm-content-grid \{ grid-template-columns: 1fr; \}",
        )

    def test_portfolio_monitoring_typography_is_one_pixel_larger(self) -> None:
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertRegex(styles, r"\.pm-workbench \{[^}]*font-size: 17px;")
        self.assertIn(".pm-group-card strong { overflow: hidden; font-size: 14px;", styles)
        self.assertIn(".pm-hero h1 { margin: 6px 0 0; color: var(--ink); font-size: clamp(25px, 3vw, 36px);", styles)
        self.assertIn(".pm-section-heading h2 { margin: 4px 0 0; color: #243f53; font-size: 18px;", styles)
        self.assertIn(".pm-axis-label, .pm-axis-date { fill: #83919c; font-size: 10px;", styles)
        self.assertIn(".pm-diagnosis-card > header { display: flex; align-items: center; justify-content: space-between; gap: 8px; color: #788b98; font-size: 8px;", styles)
        self.assertIn(".pm-catalog-search input, .pm-field input { width: 100%; height: 38px; padding: 0 10px; border: 1px solid #cfdde5; border-radius: 9px; color: #203c50; background: #fff; font-size: 12px;", styles)
        self.assertIn("@media (max-width: 420px)", styles)
        self.assertIn(".pm-hero h1 { font-size: 26px; }", styles)

    def test_date_input_uses_immediate_input_event_without_blur_rerun(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")

        date_input = next(
            line for line in source.splitlines() if 'type="date"' in line
        )
        self.assertIn("onInput=", date_input)
        self.assertNotIn("onBlur=", date_input)
        self.assertIn("const requestedStartDate = event.currentTarget.value;", date_input)
        self.assertNotIn("requestedStartDate: event.currentTarget.value", date_input)

    def test_drawer_keeps_natural_component_height_and_consumes_recovery_once(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertNotIn("drawerFrameHeight", source)
        self.assertIn("Streamlit.setFrameHeight();", source)
        self.assertIn("consumedRecoveryKeyRef", source)
        self.assertIn("height: min(560px, calc(100% - 28px));", styles)

    def test_tracking_end_feedback_and_history_are_visible_outside_the_drawer(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn('className={`pm-command-feedback is-${latestCommand.status}`}', source)
        self.assertIn('className="pm-ended-items"', source)
        self.assertIn("종료 기록", source)
        self.assertIn("itemLifecycleLabel(selectedItem)", source)
        self.assertNotIn("{selectedItem.lane_status}", source)
        self.assertIn(".pm-command-feedback", styles)
        self.assertIn(".pm-ended-items", styles)

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
