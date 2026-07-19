from __future__ import annotations

import importlib
import unittest
from datetime import date


def _macro_context():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.macro_context")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring macro context module is required") from exc


def _cycle(*, status="READY", as_of="2026-07-18"):
    return {
        "status": status,
        "as_of_date": as_of,
        "horizons": [
            {"horizon_months": 0, "dominant_phase": "slowdown", "publication_status": "READY"},
            {"horizon_months": 1, "dominant_phase": "contraction", "publication_status": "LIMITED"},
            {"horizon_months": 2, "dominant_phase": None, "publication_status": "LIMITED"},
        ],
    }


def _futures(*, status="READY", as_of="2026-07-18", publication="READY"):
    families = {
        "risk_on": {"five_day": -0.4, "twenty_day": -0.2},
        "growth": {"five_day": -0.3, "twenty_day": -0.1},
        "rate_pressure": {"five_day": 0.25, "twenty_day": 0.15},
        "dollar_pressure": {"five_day": 0.2, "twenty_day": 0.1},
        "safe_haven": {"five_day": 0.35, "twenty_day": 0.2},
        "inflation_pressure": {"five_day": 0.15, "twenty_day": 0.05},
    }
    return {
        "status": status,
        "macro": {"coverage": {"latest_daily_date": as_of}},
        "pattern_outlook": {
            "status": publication,
            "as_of_date": as_of,
            "current_pattern": {"families": families, "regime": "defensive"},
            "horizons": [
                {"horizon": 5, "dominant_regime": "defensive", "estimate_status": "PROVISIONAL"},
                {"horizon": 20, "dominant_regime": "mixed", "estimate_status": "PROVISIONAL"},
            ],
        },
        "metadata": {"as_of_date": as_of, "snapshot_status": publication},
    }


def _assets(*, as_of="2026-07-18"):
    return {
        "status": "READY", "as_of_date": as_of,
        "pathways": {
            "gold": {"status": "OBSERVED", "return_63d": -0.12, "real_yield": "ADVERSE"},
            "dollar": {"status": "OBSERVED", "direction": "UP"},
            "wti": {"status": "OBSERVED", "direction": "DOWN"},
            "copper": {"status": "OBSERVED", "direction": "DOWN"},
            "rates": {"status": "OBSERVED", "pressure": 0.3},
            "sp500": {"status": "OBSERVED", "return_20d": -0.05},
        },
    }


class PortfolioMonitoringMacroContextTests(unittest.TestCase):
    def test_extracts_cycle_families_outlooks_and_asset_pathways(self) -> None:
        macro = _macro_context()
        calls = []
        context = macro.load_portfolio_macro_context(
            cycle_loader=lambda **kwargs: calls.append(("cycle", kwargs)) or _cycle(),
            futures_loader=lambda: calls.append(("futures", {})) or _futures(),
            asset_context_loader=lambda **kwargs: calls.append(("assets", kwargs)) or _assets(),
            as_of_date=date(2026, 7, 19),
        )

        self.assertEqual(context.status, "READY")
        self.assertEqual(context.cycle[0]["phase"], "slowdown")
        self.assertEqual(context.cycle[1]["phase"], "contraction")
        self.assertEqual(context.family_scores["risk_on"]["5d"], -40.0)
        self.assertEqual(context.family_scores["rate_pressure"]["20d"], 15.0)
        self.assertEqual(context.outlooks[5]["regime"], "defensive")
        self.assertEqual(context.outlooks[20]["regime"], "mixed")
        self.assertEqual(context.pathways["gold"]["real_yield"], "ADVERSE")
        self.assertEqual(set(context.pathways), {"gold", "dollar", "wti", "copper", "rates", "sp500"})
        self.assertEqual([name for name, _ in calls], ["cycle", "futures", "assets"])

    def test_missing_and_malformed_sources_are_limited_without_fabricated_values(self) -> None:
        macro = _macro_context()
        context = macro.load_portfolio_macro_context(
            cycle_loader=lambda **kwargs: None,
            futures_loader=lambda: {"status": "READY", "pattern_outlook": "broken"},
            asset_context_loader=lambda **kwargs: {"status": "MISSING"},
            as_of_date=date(2026, 7, 19),
        )

        self.assertEqual(context.status, "LIMITED")
        self.assertEqual(context.family_scores, {})
        self.assertEqual(context.pathways, {})
        self.assertLess(context.coverage, 0.7)
        self.assertTrue(any("missing" in warning.lower() or "malformed" in warning.lower() for warning in context.warnings))

    def test_stale_mismatched_and_provisional_dates_lower_publication(self) -> None:
        macro = _macro_context()
        context = macro.load_portfolio_macro_context(
            cycle_loader=lambda **kwargs: _cycle(as_of="2026-06-01"),
            futures_loader=lambda: _futures(as_of="2026-07-18", publication="PROVISIONAL"),
            asset_context_loader=lambda **kwargs: _assets(as_of="2026-07-10"),
            as_of_date=date(2026, 7, 19),
        )

        self.assertEqual(context.status, "LIMITED")
        self.assertEqual(context.publication, "PROVISIONAL")
        self.assertEqual(context.as_of_dates["economic_cycle"], "2026-06-01")
        self.assertTrue(any("stale" in warning.lower() for warning in context.warnings))
        self.assertTrue(any("mismatch" in warning.lower() for warning in context.warnings))

    def test_adapter_only_invokes_injected_read_loaders(self) -> None:
        macro = _macro_context()

        class ReadOnlyLoader:
            def __init__(self, value):
                self.value = value
                self.calls = 0

            def __call__(self, **kwargs):
                self.calls += 1
                return self.value

            def materialize(self):  # pragma: no cover - must never be invoked
                raise AssertionError("materialization is outside portfolio monitoring")

        cycle, futures, assets = ReadOnlyLoader(_cycle()), ReadOnlyLoader(_futures()), ReadOnlyLoader(_assets())
        macro.load_portfolio_macro_context(
            cycle_loader=cycle, futures_loader=futures, asset_context_loader=assets,
            as_of_date=date(2026, 7, 19),
        )
        self.assertEqual((cycle.calls, futures.calls, assets.calls), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
