from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest
import numpy as np


def _next_year_eps_rows(
    *,
    release_date: str,
    target_year: int,
    quarterly_values: tuple[float, float, float, float],
    basis: str = "operating",
) -> list[dict[str, object]]:
    return [
        {
            "period_end": f"{target_year}-{month_day}",
            "period_type": "quarterly",
            "earnings_basis": basis,
            "value_status": "estimate",
            "eps": value,
            "source": "sp_dow_jones_index_earnings",
            "source_ref": "official-workbook.xlsx",
            "source_release_date": release_date,
            "collected_at": f"{release_date}T12:05:00Z",
        }
        for month_day, value in zip(
            ("03-31", "06-30", "09-30", "12-31"),
            quarterly_values,
            strict=True,
        )
    ]


def _yield_rows(*dates: str) -> list[dict[str, object]]:
    offsets = {"DGS2": -0.75, "DGS10": 0.0, "DFII10": -2.15, "T10YIE": -2.0}
    rows: list[dict[str, object]] = []
    for index, observed in enumerate(dates):
        base = 4.0 + index * 0.05
        for series_id, offset in offsets.items():
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": observed,
                    "released_at": f"{observed}T23:59:00Z",
                    "value": base + offset,
                }
            )
    return rows


def test_equity_bundle_excludes_rows_not_known_at_cutoff() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_equity_bundle

    eps_rows = []
    for release_date, current_eps, next_eps in (
        ("2025-03-15", 220.0, 250.0),
        ("2025-06-15", 230.0, 270.0),
    ):
        eps_rows.extend(
            [
                {
                    "period_end": "2025-12-31",
                    "period_type": "annual",
                    "earnings_basis": "operating",
                    "value_status": "mixed",
                    "eps": current_eps,
                    "source": "factset_earnings_insight",
                    "source_ref": f"EarningsInsight_{release_date}.pdf",
                    "source_release_date": release_date,
                    "collected_at": f"{release_date}T23:59:59Z",
                },
                {
                    "period_end": "2026-12-31",
                    "period_type": "annual",
                    "earnings_basis": "operating",
                    "value_status": "estimate",
                    "eps": next_eps,
                    "source": "factset_earnings_insight",
                    "source_ref": f"EarningsInsight_{release_date}.pdf",
                    "source_release_date": release_date,
                    "collected_at": f"{release_date}T23:59:59Z",
                },
            ]
        )
    price_rows = [
        {"symbol": "^GSPC", "Date": "2025-03-31", "Close": 4000.0},
        {"symbol": "^GSPC", "Date": "2025-06-02", "Close": 4200.0},
    ]
    yield_rows = _yield_rows("2025-03-31", "2025-06-02")
    yield_rows.append(
        {
            "series_id": "DGS10",
            "observation_date": "2025-03-31",
            "released_at": "2025-05-15T12:00:00Z",
            "value": 4.25,
        }
    )

    def query(database: str, sql: str, _params: tuple[object, ...]):
        if database == "finance_price":
            return price_rows
        if "sp500_index_earnings" in sql:
            return eps_rows
        if "macro_series_vintage_observation" in sql:
            return yield_rows
        raise AssertionError(sql)

    bundle = load_inflation_policy_equity_bundle(
        as_of_at="2025-05-31T23:59:59Z",
        history_start="2025-01-01",
        query_fn=query,
    )

    assert len(bundle.eps_rows) == 2
    assert {row["source_release_date"] for row in bundle.eps_rows} == {"2025-03-15"}
    assert [row["Date"] for row in bundle.price_rows] == ["2025-03-31"]
    assert all(str(row["observation_date"]) <= "2025-05-31" for row in bundle.yield_rows)
    assert len(
        [
            row
            for row in bundle.yield_rows
            if row["series_id"] == "DGS10"
            and str(row["observation_date"]) == "2025-03-31"
        ]
    ) == 2
    assert bundle.coverage["verified_eps_vintage_status"] == "LIMITED"
    assert bundle.coverage["verified_eps_vintage_releases"] == 1


def test_equity_bundle_does_not_verify_other_source_quarterly_rows() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_equity_bundle

    eps_rows: list[dict[str, object]] = []
    for index in range(60):
        release = pd.Timestamp("2019-01-31") + pd.offsets.MonthEnd(index)
        eps_rows.append(
            {
                "period_end": release.strftime("%Y-%m-%d"),
                "period_type": "quarterly",
                "earnings_basis": "as_reported",
                "value_status": "actual",
                "eps": 50.0 + index,
                "source": "unverified_other_source",
                "source_ref": "other.xlsx",
                "source_release_date": release.strftime("%Y-%m-%d"),
                "collected_at": release.strftime("%Y-%m-%dT23:59:00Z"),
            }
        )

    def query(database: str, sql: str, _params: tuple[object, ...]):
        if "sp500_index_earnings" in sql:
            return eps_rows
        if database == "finance_price":
            return [{"symbol": "^GSPC", "Date": "2024-01-31", "Close": 4800.0}]
        if "macro_series_vintage_observation" in sql:
            return _yield_rows("2024-01-31")
        raise AssertionError(sql)

    bundle = load_inflation_policy_equity_bundle(
        as_of_at="2024-12-31T23:59:59Z",
        history_start="2018-01-01",
        query_fn=query,
    )

    assert bundle.eps_rows == ()
    assert bundle.coverage["verified_eps_vintage_status"] == "NOT_AVAILABLE"
    assert bundle.coverage["verified_eps_vintage_releases"] == 0


def test_panel_accepts_verified_annual_next_year_eps_vintages() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    eps = [
        {
            "period_end": "2026-12-31",
            "period_type": "annual",
            "earnings_basis": "operating",
            "value_status": "estimate",
            "eps": 280.0,
            "source": "factset_earnings_insight",
            "source_ref": "EarningsInsight_031425.pdf",
            "source_release_date": "2025-03-14",
        },
        {
            "period_end": "2026-12-31",
            "period_type": "annual",
            "earnings_basis": "operating",
            "value_status": "estimate",
            "eps": 294.0,
            "source": "factset_earnings_insight",
            "source_ref": "EarningsInsight_042525.pdf",
            "source_release_date": "2025-04-25",
        },
    ]
    panel = build_equity_calibration_panel(
        price_rows=[
            {"Date": "2025-03-31", "Close": 5600.0},
            {"Date": "2025-04-30", "Close": 5880.0},
        ],
        eps_rows=eps,
        yield_rows=_yield_rows("2025-03-31", "2025-04-30"),
        as_of_at="2025-05-01T23:59:59Z",
    )

    assert panel.loc[panel["origin_date"] == "2025-03-31", "forward_eps"].iloc[0] == pytest.approx(280.0)
    assert panel.loc[panel["origin_date"] == "2025-04-30", "forward_eps"].iloc[0] == pytest.approx(294.0)
    assert panel.iloc[-1]["measured_next_year_eps_revision_pct"] == pytest.approx(5.0)


def test_equity_bundle_excludes_same_day_close_before_us_market_close() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_equity_bundle

    eps_rows = _next_year_eps_rows(
        release_date="2025-03-15",
        target_year=2026,
        quarterly_values=(20, 25, 25, 30),
    )
    price_rows = [
        {"symbol": "^GSPC", "Date": "2025-05-30", "Close": 4100.0},
        {"symbol": "^GSPC", "Date": "2025-06-02", "Close": 4200.0},
    ]

    def query(database: str, sql: str, _params: tuple[object, ...]):
        if database == "finance_price":
            return price_rows
        if "sp500_index_earnings" in sql:
            return eps_rows
        if "macro_series_vintage_observation" in sql:
            return _yield_rows("2025-05-30")
        raise AssertionError(sql)

    bundle = load_inflation_policy_equity_bundle(
        as_of_at="2025-06-02T18:00:00Z",  # 14:00 New York, before the close.
        history_start="2025-01-01",
        query_fn=query,
    )

    assert [row["Date"] for row in bundle.price_rows] == ["2025-05-30"]


def test_panel_uses_only_eps_vintage_released_before_origin() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    prices = [
        {"Date": "2025-03-31", "Close": 4000.0},
        {"Date": "2025-04-30", "Close": 4050.0},
        {"Date": "2025-05-30", "Close": 4100.0},
    ]
    eps = _next_year_eps_rows(
        release_date="2025-03-15", target_year=2026, quarterly_values=(20, 25, 25, 30)
    ) + _next_year_eps_rows(
        release_date="2025-06-15", target_year=2026, quarterly_values=(25, 30, 30, 35)
    )

    panel = build_equity_calibration_panel(
        price_rows=prices,
        eps_rows=eps,
        yield_rows=_yield_rows("2025-03-31", "2025-04-30", "2025-05-30"),
        as_of_at="2025-05-31T23:59:59Z",
    )

    assert panel.iloc[-1]["origin_date"] == "2025-05-30"
    assert panel.iloc[-1]["eps_source_release_date"] == "2025-03-15"
    assert panel.iloc[-1]["forward_eps"] == pytest.approx(100.0)
    assert panel.iloc[-1]["forward_multiple"] == pytest.approx(41.0)


def test_panel_preserves_year_end_eps_times_multiple_identity() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    prices = [
        {"Date": "2025-06-30", "Close": 4000.0},
        {"Date": "2025-12-31", "Close": 3600.0},
    ]
    eps = _next_year_eps_rows(
        release_date="2025-06-15", target_year=2026, quarterly_values=(50, 50, 50, 50)
    ) + _next_year_eps_rows(
        release_date="2025-12-15", target_year=2026, quarterly_values=(45, 45, 45, 45)
    )

    yields = _yield_rows("2025-06-30", "2025-12-31")
    for month, level, released in (
        ("2024-10-01", 100.0, "2024-11-27T13:30:00Z"),
        ("2024-11-01", 100.0, "2024-12-20T13:30:00Z"),
        ("2024-12-01", 100.0, "2025-01-31T13:30:00Z"),
        ("2025-10-01", 103.0, "2025-11-26T13:30:00Z"),
        ("2025-11-01", 103.0, "2025-12-19T13:30:00Z"),
        ("2025-12-01", 103.0, "2026-01-30T13:30:00Z"),
    ):
        yields.append(
            {
                "series_id": "PCEPILFE",
                "observation_date": month,
                "released_at": released,
                "value": level,
            }
        )
    panel = build_equity_calibration_panel(
        price_rows=prices,
        eps_rows=eps,
        yield_rows=yields,
        as_of_at="2026-02-02T00:00:00Z",
    )
    june = panel.loc[panel["origin_date"] == "2025-06-30"].iloc[0]

    assert june["forward_eps"] == pytest.approx(200.0)
    assert june["forward_multiple"] == pytest.approx(20.0)
    assert june["future_forward_eps"] == pytest.approx(180.0)
    assert june["future_forward_multiple"] == pytest.approx(20.0)
    assert june["future_index_level"] == pytest.approx(
        june["future_forward_eps"] * june["future_forward_multiple"]
    )
    assert june["eps_change_pct"] == pytest.approx(-10.0)
    assert june["multiple_change_pct"] == pytest.approx(0.0)
    assert june["index_change_pct"] == pytest.approx(-10.0)
    assert june["months_to_year_end"] == 6
    assert june["q4_core_pce_pct"] == pytest.approx(3.0)
    assert june["label_available_at"].startswith("2026-01-30T13:30:00")
    assert june["dgs10_change_bp"] == pytest.approx(5.0)


def test_panel_does_not_substitute_trailing_eps_for_missing_next_year_quarter() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    incomplete = _next_year_eps_rows(
        release_date="2025-03-15", target_year=2026, quarterly_values=(20, 25, 25, 30)
    )[:3]
    incomplete.append(
        {
            "period_end": "2024-12-31",
            "period_type": "ttm",
            "earnings_basis": "as_reported",
            "value_status": "actual",
            "eps": 250.0,
            "source_release_date": "2025-03-15",
        }
    )

    panel = build_equity_calibration_panel(
        price_rows=[{"Date": "2025-03-31", "Close": 4000.0}],
        eps_rows=incomplete,
        yield_rows=_yield_rows("2025-03-31"),
        as_of_at=datetime(2025, 4, 1, tzinfo=timezone.utc),
    )

    assert panel.empty


def test_panel_does_not_mix_quarters_from_different_workbook_vintages() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    first = _next_year_eps_rows(
        release_date="2025-03-15",
        target_year=2026,
        quarterly_values=(20, 25, 25, 30),
    )[:3]
    later = _next_year_eps_rows(
        release_date="2025-04-15",
        target_year=2026,
        quarterly_values=(20, 25, 25, 30),
    )[3:]
    for row in later:
        row["source_ref"] = "later-partial-workbook.xlsx"

    panel = build_equity_calibration_panel(
        price_rows=[{"Date": "2025-04-30", "Close": 4100.0}],
        eps_rows=[*first, *later],
        yield_rows=_yield_rows("2025-04-30"),
        as_of_at="2025-05-01T00:00:00Z",
    )

    assert panel.empty


def test_panel_excludes_yield_revision_released_after_historical_origin() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    yields = _yield_rows("2025-03-31")
    yields.extend(
        [
            {
                "series_id": "DGS10",
                "observation_date": "2025-03-31",
                "released_at": "2025-06-01T00:00:00Z",
                "value": 9.99,
            }
        ]
    )
    panel = build_equity_calibration_panel(
        price_rows=[{"Date": "2025-03-31", "Close": 4000.0}],
        eps_rows=_next_year_eps_rows(
            release_date="2025-03-15",
            target_year=2026,
            quarterly_values=(20, 25, 25, 30),
        ),
        yield_rows=yields,
        as_of_at="2025-07-01T00:00:00Z",
    )

    assert panel.iloc[0]["dgs10_pct"] == pytest.approx(4.0)


def test_panel_returns_explicit_columns_when_inputs_are_empty() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    panel = build_equity_calibration_panel(
        price_rows=[], eps_rows=[], yield_rows=[], as_of_at="2025-05-31T23:59:59Z"
    )

    assert isinstance(panel, pd.DataFrame)
    assert panel.empty
    assert {"origin_date", "forward_eps", "forward_multiple"}.issubset(panel.columns)


def _synthetic_model_panel(*, rows: int = 84, regime_flip: bool = False) -> pd.DataFrame:
    dates = pd.date_range("2018-01-31", periods=rows, freq="ME")
    result: list[dict[str, object]] = []
    for index, origin in enumerate(dates):
        revision = ((index % 9) - 4) * 0.7
        policy = ((index % 7) - 3) * 8.0
        dgs10 = ((index % 11) - 5) * 5.0
        real = ((index % 5) - 2) * 7.0
        breakeven = dgs10 - real
        q4_core_pce = 2.6 + (index % 6) * 0.15
        shared_noise = ((index % 4) - 1.5) * 0.08
        sign = -1.0 if regime_flip and index >= rows // 3 else 1.0
        eps_change = sign * (
            0.75 * revision - 0.025 * policy - 0.015 * real
        ) + shared_noise
        multiple_change = sign * (
            -0.035 * dgs10 - 0.045 * real + 0.02 * breakeven
        ) + shared_noise * 1.4
        current_eps = 200.0 + index * 0.2
        current_index = 4000.0 + index * 4.0
        current_multiple = current_index / current_eps
        future_eps = current_eps * (1.0 + eps_change / 100.0)
        future_multiple = current_multiple * (1.0 + multiple_change / 100.0)
        future_index = future_eps * future_multiple
        result.append(
            {
                "origin_date": origin.strftime("%Y-%m-%d"),
                "label_available_at": f"{origin.year + 1}-01-01",
                "measured_next_year_eps_revision_pct": revision,
                "months_to_year_end": 12 - origin.month,
                "q4_core_pce_pct": q4_core_pce,
                "policy_repricing_bp": policy,
                "dgs10_change_bp": dgs10,
                "real_yield_change_bp": real,
                "breakeven_change_bp": breakeven,
                "current_index_level": current_index,
                "forward_eps": current_eps,
                "forward_multiple": current_multiple,
                "future_forward_eps": future_eps,
                "future_forward_multiple": future_multiple,
                "future_index_level": future_index,
                "eps_change_pct": eps_change,
                "multiple_change_pct": multiple_change,
                "index_change_pct": (future_index / current_index - 1.0) * 100.0,
            }
        )
    return pd.DataFrame(result)


def test_equity_model_uses_chronological_validation_and_beats_constant_baseline() -> None:
    from finance.inflation_policy_equity_stress import fit_equity_stress_model

    artifact = fit_equity_stress_model(
        _synthetic_model_panel(), minimum_origins=60, ridge_alpha=1.0
    )

    assert artifact.publication_status == "READY"
    assert artifact.validation_metrics["origin_count"] == pytest.approx(84.0)
    assert artifact.validation_metrics["fold_count"] >= 24.0
    assert artifact.validation_metrics["index_mae"] < artifact.validation_metrics[
        "baseline_index_mae"
    ]
    assert artifact.validation_metrics["validation_scheme"] == (
        "rolling_origin_label_available"
    )
    assert artifact.validation_metrics["interval_calibration_scheme"] == (
        "prior_oos_residuals"
    )
    assert artifact.validation_metrics["interval_fold_count"] == pytest.approx(
        artifact.validation_metrics["fold_count"] - 12.0
    )
    assert artifact.validation_metrics["publication_contract_version"] == (
        "equity-stress-publication-v1"
    )
    assert set(artifact.validation_metrics["baseline_mae_by_name"]) == {
        "constant_eps",
        "constant_multiple",
        "unconditional_index_change",
    }
    assert artifact.validation_metrics["baseline_index_mae"] == pytest.approx(
        min(artifact.validation_metrics["baseline_mae_by_name"].values())
    )
    assert artifact.trained_through == "2024-12-31"
    assert set(artifact.eps_response) >= {
        "intercept",
        "measured_next_year_eps_revision_pct",
        "policy_repricing_bp",
    }
    assert set(artifact.multiple_response) >= {
        "intercept",
        "dgs10_change_bp",
        "real_yield_change_bp",
    }


def test_rolling_validation_waits_until_year_end_label_is_available() -> None:
    from finance.inflation_policy_equity_stress import (
        rolling_origin_validate_equity_stress,
    )

    report = rolling_origin_validate_equity_stress(
        _synthetic_model_panel(rows=60), minimum_origins=60
    )

    assert report.fold_count == 24


def test_equity_model_that_fails_coverage_gate_is_limited() -> None:
    from finance.inflation_policy_equity_stress import fit_equity_stress_model

    artifact = fit_equity_stress_model(
        _synthetic_model_panel(),
        minimum_origins=60,
        maximum_coverage_80_error=0.0,
    )

    assert artifact.publication_status == "LIMITED"
    assert "coverage_80_miscalibrated" in artifact.reason_codes


def test_equity_artifact_uses_live_unlabelled_origin_only_for_scenario_context() -> None:
    from finance.inflation_policy_equity_stress import fit_equity_stress_model

    panel = _synthetic_model_panel()
    live = dict(panel.iloc[-1])
    live.update(
        {
            "origin_date": "2025-08-29",
            "label_available_at": None,
            "measured_next_year_eps_revision_pct": 9.0,
            "months_to_year_end": 4,
            "dgs10_pct": 4.55,
            "real_yield_10y_pct": 2.05,
            "breakeven_10y_pct": 2.50,
            "future_forward_eps": None,
            "future_forward_multiple": None,
            "future_index_level": None,
            "eps_change_pct": None,
            "multiple_change_pct": None,
            "index_change_pct": None,
        }
    )

    artifact = fit_equity_stress_model(
        pd.concat([panel, pd.DataFrame([live])], ignore_index=True),
        minimum_origins=60,
    )

    assert artifact.trained_through == "2024-12-31"
    assert artifact.latest_measured_next_year_eps_revision_pct == pytest.approx(9.0)
    assert artifact.scenario_feature_values["months_to_year_end"] == pytest.approx(4.0)
    assert artifact.scenario_feature_values["dgs10_pct"] == pytest.approx(4.55)


def test_equity_model_keeps_paired_eps_multiple_residuals() -> None:
    from finance.inflation_policy_equity_stress import fit_equity_stress_model

    artifact = fit_equity_stress_model(
        _synthetic_model_panel(), minimum_origins=60, ridge_alpha=1.0
    )
    residuals = np.asarray(artifact.joint_residuals, dtype=float)

    assert residuals.shape == (
        int(artifact.validation_metrics["fold_count"]),
        2,
    )
    assert artifact.validation_metrics["residual_calibration_scheme"] == (
        "chronological_oos_fold_pairs"
    )
    assert np.isfinite(residuals).all()
    assert np.corrcoef(residuals[:, 0], residuals[:, 1])[0, 1] > 0.5


def test_equity_model_fails_closed_with_insufficient_completed_origins() -> None:
    from finance.inflation_policy_equity_stress import fit_equity_stress_model

    panel = _synthetic_model_panel(rows=30)
    panel.loc[10:, "future_index_level"] = np.nan
    panel.loc[10:, "eps_change_pct"] = np.nan
    panel.loc[10:, "multiple_change_pct"] = np.nan
    panel.loc[10:, "index_change_pct"] = np.nan

    artifact = fit_equity_stress_model(panel, minimum_origins=60)

    assert artifact.publication_status == "NOT_AVAILABLE"
    assert "insufficient_origins" in artifact.reason_codes
    assert artifact.validation_metrics["origin_count"] == pytest.approx(10.0)


def test_equity_model_that_does_not_beat_baseline_is_limited() -> None:
    from finance.inflation_policy_equity_stress import fit_equity_stress_model

    artifact = fit_equity_stress_model(
        _synthetic_model_panel(regime_flip=True),
        minimum_origins=60,
        ridge_alpha=0.25,
    )

    assert artifact.publication_status == "LIMITED"
    assert "baseline_not_beaten" in artifact.reason_codes
    assert artifact.validation_metrics["index_mae"] >= artifact.validation_metrics[
        "baseline_index_mae"
    ]


def _ready_equity_artifact(*, status: str = "READY"):
    from finance.inflation_policy_equity_stress import EquityStressArtifact

    return EquityStressArtifact(
        model_version="equity-stress-test-v1",
        eps_response={
            "intercept": 0.0,
            "measured_next_year_eps_revision_pct": 0.4,
            "months_to_year_end": 0.0,
            "policy_repricing_bp": -0.01,
            "dgs10_change_bp": 0.0,
            "real_yield_change_bp": -0.01,
            "breakeven_change_bp": 0.0,
        },
        multiple_response={
            "intercept": -2.0,
            "measured_next_year_eps_revision_pct": 0.0,
            "months_to_year_end": 0.0,
            "policy_repricing_bp": -0.005,
            "dgs10_change_bp": -0.03,
            "real_yield_change_bp": -0.04,
            "breakeven_change_bp": 0.01,
        },
        joint_residuals=((-0.5, -1.0), (0.0, 0.0), (0.5, 1.0)),
        validation_metrics={
            "origin_count": 84.0,
            "index_mae": 1.2,
            "baseline_index_mae": 2.0,
            "validation_scheme": "rolling_origin",
        },
        trained_through="2025-12-31",
        publication_status=status,
        reason_codes=(),
        latest_measured_next_year_eps_revision_pct=2.5,
        scenario_feature_values={
            "months_to_year_end": 5.0,
            "dgs2_pct": 3.7,
            "dgs10_pct": 4.4,
            "real_yield_10y_pct": 2.0,
            "breakeven_10y_pct": 2.4,
        },
    )


def _forward_paths():
    from finance.inflation_policy_simulation import SimulationPath

    return (
        SimulationPath(
            path_id="mild",
            weight=0.25,
            q4_core_pce_pct=3.2,
            remaining_monthly_mom_pct=(0.2, 0.2),
            policy_net_steps=0,
            year_end_policy_midpoint_pct=3.875,
            rate_paths_pct={
                "DGS2": (3.7, 3.7),
                "DGS10": (4.4, 4.45),
                "DFII10": (2.0, 2.05),
                "T10YIE": (2.4, 2.4),
            },
        ),
        SimulationPath(
            path_id="central",
            weight=0.50,
            q4_core_pce_pct=3.5,
            remaining_monthly_mom_pct=(0.3, 0.3),
            policy_net_steps=1,
            year_end_policy_midpoint_pct=4.125,
            rate_paths_pct={
                "DGS2": (3.7, 3.95),
                "DGS10": (4.4, 4.7),
                "DFII10": (2.0, 2.2),
                "T10YIE": (2.4, 2.5),
            },
        ),
        SimulationPath(
            path_id="stress",
            weight=0.25,
            q4_core_pce_pct=3.9,
            remaining_monthly_mom_pct=(0.4, 0.4),
            policy_net_steps=2,
            year_end_policy_midpoint_pct=4.375,
            rate_paths_pct={
                "DGS2": (3.7, 4.2),
                "DGS10": (4.4, 5.0),
                "DFII10": (2.0, 2.5),
                "T10YIE": (2.4, 2.5),
            },
        ),
    )


def test_ai_uplift_changes_eps_only_and_keeps_measured_revision_separate() -> None:
    from finance.inflation_policy_equity_stress import simulate_equity_stress

    base = simulate_equity_stress(
        _ready_equity_artifact(),
        _forward_paths(),
        current_index=6800.0,
        forward_eps=300.0,
    )
    uplift = simulate_equity_stress(
        _ready_equity_artifact(),
        _forward_paths(),
        current_index=6800.0,
        forward_eps=300.0,
        user_ai_eps_uplift_pct=5.0,
        target_levels=(6400.0,),
    )

    assert uplift.publication_status == "READY"
    assert uplift.measured_next_year_eps_revision_pct == pytest.approx(2.5)
    assert uplift.user_ai_eps_uplift_pct == pytest.approx(5.0)
    assert uplift.scenario_kind == "USER_ASSUMPTION"
    assert uplift.eps_quantiles["p50"] == pytest.approx(
        base.eps_quantiles["p50"] * 1.05
    )
    assert uplift.multiple_quantiles == base.multiple_quantiles
    assert set(uplift.threshold_probabilities) == {"below_or_equal:6400.0000"}
    assert 0.0 <= uplift.threshold_probabilities["below_or_equal:6400.0000"] <= 1.0
    assert "below_or_equal:6400.0000" in uplift.target_decompositions


def test_equity_target_is_arbitrary_positive_input_not_a_fixed_level() -> None:
    from finance.inflation_policy_equity_stress import simulate_equity_stress

    result = simulate_equity_stress(
        _ready_equity_artifact(),
        _forward_paths(),
        current_index=6800.0,
        forward_eps=300.0,
        target_levels=(6123.0,),
    )

    assert set(result.threshold_probabilities) == {"below_or_equal:6123.0000"}
    assert set(result.target_decompositions) == {"below_or_equal:6123.0000"}


def test_equity_simulation_is_invariant_to_forward_path_order() -> None:
    from finance.inflation_policy_equity_stress import simulate_equity_stress

    paths = _forward_paths()
    forward = simulate_equity_stress(
        _ready_equity_artifact(),
        paths,
        current_index=6800.0,
        forward_eps=300.0,
        target_levels=(6400.0,),
    )
    reversed_order = simulate_equity_stress(
        _ready_equity_artifact(),
        tuple(reversed(paths)),
        current_index=6800.0,
        forward_eps=300.0,
        target_levels=(6400.0,),
    )

    assert reversed_order.index_quantiles == forward.index_quantiles
    assert reversed_order.eps_quantiles == forward.eps_quantiles
    assert reversed_order.multiple_quantiles == forward.multiple_quantiles
    assert reversed_order.threshold_probabilities == forward.threshold_probabilities


def test_equity_simulation_fails_closed_when_live_scenario_context_is_incomplete() -> None:
    from dataclasses import replace

    from finance.inflation_policy_equity_stress import simulate_equity_stress

    artifact = _ready_equity_artifact()
    incomplete_features = dict(artifact.scenario_feature_values)
    incomplete_features.pop("dgs10_pct")
    artifact = replace(
        artifact,
        scenario_feature_values=incomplete_features,
        latest_measured_next_year_eps_revision_pct=None,
    )

    result = simulate_equity_stress(
        artifact,
        _forward_paths(),
        current_index=6800.0,
        forward_eps=300.0,
    )

    assert result.publication_status == "NOT_AVAILABLE"
    assert result.index_quantiles == {}
    assert result.reason_codes == (
        "scenario_context_incomplete:dgs10_pct,measured_next_year_eps_revision_pct",
    )


def test_equity_simulation_fails_closed_when_joint_path_endpoint_is_missing() -> None:
    from dataclasses import replace

    from finance.inflation_policy_equity_stress import simulate_equity_stress

    path = _forward_paths()[0]
    incomplete_rates = dict(path.rate_paths_pct)
    incomplete_rates.pop("T10YIE")

    result = simulate_equity_stress(
        _ready_equity_artifact(),
        (replace(path, rate_paths_pct=incomplete_rates),),
        current_index=6800.0,
        forward_eps=300.0,
    )

    assert result.publication_status == "NOT_AVAILABLE"
    assert result.reason_codes == (
        "scenario_context_incomplete:path.mild.T10YIE_endpoint",
    )


@pytest.mark.parametrize("uplift", (-30.01, 50.01, float("nan")))
def test_equity_ai_uplift_rejects_values_outside_bounded_range(uplift: float) -> None:
    from finance.inflation_policy_equity_stress import simulate_equity_stress

    with pytest.raises(ValueError, match="AI EPS uplift"):
        simulate_equity_stress(
            _ready_equity_artifact(),
            _forward_paths(),
            current_index=6800.0,
            forward_eps=300.0,
            user_ai_eps_uplift_pct=uplift,
        )


def test_equity_target_rejects_non_positive_level() -> None:
    from finance.inflation_policy_equity_stress import simulate_equity_stress

    with pytest.raises(ValueError, match="target level"):
        simulate_equity_stress(
            _ready_equity_artifact(),
            _forward_paths(),
            current_index=6800.0,
            forward_eps=300.0,
            target_levels=(0.0,),
        )


def test_limited_equity_model_hides_target_probability_but_keeps_wide_ranges() -> None:
    from finance.inflation_policy_equity_stress import simulate_equity_stress

    result = simulate_equity_stress(
        _ready_equity_artifact(status="LIMITED"),
        _forward_paths(),
        current_index=6800.0,
        forward_eps=300.0,
        target_levels=(6400.0,),
    )

    assert result.publication_status == "LIMITED"
    assert result.index_quantiles
    assert result.threshold_probabilities == {}
    assert result.target_decompositions == {}
