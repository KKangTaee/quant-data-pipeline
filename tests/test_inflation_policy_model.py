from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone


def _month_add(value: date, months: int) -> date:
    index = value.year * 12 + value.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def _hybrid_vintages() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = date(2017, 1, 1)
    core_level = 100.0
    series_levels = {
        "CPILFESL": 200.0,
        "CPIAUCSL": 190.0,
        "PPIACO": 180.0,
        "CES0500000003": 25.0,
    }
    previous_core_mom = 0.20
    for index in range(114):
        month = _month_add(start, index)
        core_cpi_mom = 0.18 + (index % 5) * 0.025
        headline_cpi_mom = 0.15 + (index % 4) * 0.02
        ppi_mom = 0.10 + (index % 3) * 0.03
        wage_mom = 0.20 + (index % 2) * 0.02
        core_mom = (
            0.45 * previous_core_mom
            + 0.35 * core_cpi_mom
            + 0.10 * headline_cpi_mom
            + 0.05 * ppi_mom
            + 0.05 * wage_mom
        )
        for series_id, mom in (
            ("CPILFESL", core_cpi_mom),
            ("CPIAUCSL", headline_cpi_mom),
            ("PPIACO", ppi_mom),
            ("CES0500000003", wage_mom),
        ):
            series_levels[series_id] *= 1.0 + mom / 100.0
            release = datetime(
                month.year,
                month.month,
                20,
                13,
                30,
                tzinfo=timezone.utc,
            )
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": month.isoformat(),
                    "released_at": release.isoformat(),
                    "realtime_start": release.date().isoformat(),
                    "value": series_levels[series_id],
                }
            )
        rows.extend(
            (
                {
                    "series_id": "PCETRIM12M159SFRBDAL",
                    "observation_date": month.isoformat(),
                    "released_at": datetime(
                        month.year, month.month, 22, 15, 0, tzinfo=timezone.utc
                    ).isoformat(),
                    "realtime_start": month.isoformat(),
                    "value": core_mom * 12.0,
                },
                {
                    "series_id": "MICH",
                    "observation_date": month.isoformat(),
                    "released_at": datetime(
                        month.year, month.month, 15, 15, 0, tzinfo=timezone.utc
                    ).isoformat(),
                    "realtime_start": month.isoformat(),
                    "value": 2.5 + (index % 4) * 0.1,
                },
            )
        )
        core_level *= 1.0 + core_mom / 100.0
        release_month = _month_add(month, 1)
        release = datetime(
            release_month.year,
            release_month.month,
            25,
            12,
            30,
            tzinfo=timezone.utc,
        )
        rows.append(
            {
                "series_id": "PCEPILFE",
                "observation_date": month.isoformat(),
                "released_at": release.isoformat(),
                "realtime_start": release.date().isoformat(),
                "value": core_level,
            }
        )
        # A later revision must not replace the value at earlier origins.
        if index < 90:
            revision = release + timedelta(days=380)
            rows.append(
                {
                    "series_id": "PCEPILFE",
                    "observation_date": month.isoformat(),
                    "released_at": revision.isoformat(),
                    "realtime_start": revision.date().isoformat(),
                    "value": core_level * 1.0002,
                }
            )
        previous_core_mom = core_mom
    return rows


def test_hybrid_panel_uses_only_vintages_released_before_each_target() -> None:
    from finance.inflation_policy_model import build_core_pce_nowcast_panel

    rows = _hybrid_vintages()
    panel = build_core_pce_nowcast_panel(
        rows,
        as_of_at="2026-07-29T18:00:00+00:00",
    )

    assert len(panel) >= 90
    assert all(
        item.training_values_released_through_at < item.target_available_at
        for item in panel
    )
    assert all(0.0 <= item.complete_feature_ratio <= 1.0 for item in panel)
    assert panel[-1].features["core_lag_1"] is not None


def test_hybrid_core_model_blends_bridge_ridge_and_momentum_with_capped_weights() -> None:
    from finance.inflation_policy_model import fit_core_pce_hybrid_artifact
    from finance.inflation_policy_validation import PublicationThresholds

    artifact = fit_core_pce_hybrid_artifact(
        _hybrid_vintages(),
        as_of_at="2026-07-29T18:00:00+00:00",
        thresholds=PublicationThresholds(
            minimum_origins=24,
            minimum_complete_feature_ratio=0.80,
            maximum_calibration_error=0.35,
            require_baseline_improvement=True,
        ),
        minimum_training_rows=36,
        ridge_alpha=1.0,
        max_component_weight=0.60,
    )

    assert set(artifact.component_weights) == {"bridge", "ridge", "momentum"}
    assert math.isclose(sum(artifact.component_weights.values()), 1.0)
    assert max(artifact.component_weights.values()) <= 0.60 + 1e-12
    assert set(artifact.latest_component_mom_pct) == {
        "bridge",
        "ridge",
        "momentum",
    }
    assert artifact.validation_metrics["origin_count"] >= 24
    baseline_scores = [
        artifact.validation_metrics["baseline_persistence_crps"],
        artifact.validation_metrics["baseline_rolling_3m_crps"],
        artifact.validation_metrics["baseline_rolling_6m_crps"],
    ]
    assert artifact.validation_metrics["baseline_crps"] == min(baseline_scores)
    assert artifact.publication_status == "READY"
    assert "benchmark_suite_incomplete" not in artifact.publication_reasons
    assert artifact.predictive_residuals_pct
    assert abs(sum(artifact.predictive_residuals_pct)) < 1e-12


def test_same_release_batch_counts_one_origin_and_cannot_train_sibling_target() -> None:
    from finance.inflation_policy_model import (
        build_core_pce_nowcast_panel,
        fit_core_pce_hybrid_artifact,
    )
    from finance.inflation_policy_validation import PublicationThresholds

    rows = []
    for row in _hybrid_vintages():
        if (
            row["series_id"] == "PCEPILFE"
            and row["observation_date"] == "2022-05-01"
            and str(row["released_at"]).startswith("2022-06-25")
        ):
            rows.append({**row, "released_at": "2022-07-25T12:30:00+00:00"})
        else:
            rows.append(row)
    panel = build_core_pce_nowcast_panel(
        rows,
        as_of_at="2026-07-29T18:00:00+00:00",
    )
    eligible_origins = {
        row.forecast_origin_at
        for row in panel
        if sum(
            candidate.target_available_at < row.target_available_at
            for candidate in panel
        )
        >= 36
    }

    artifact = fit_core_pce_hybrid_artifact(
        rows,
        as_of_at="2026-07-29T18:00:00+00:00",
        thresholds=PublicationThresholds(24, 0.80, 0.35, True),
        minimum_training_rows=36,
        ridge_alpha=1.0,
        max_component_weight=0.60,
    )

    assert artifact.validation_metrics["origin_count"] == float(
        len(eligible_origins)
    )
    assert artifact.validation_metrics["target_count"] > artifact.validation_metrics[
        "origin_count"
    ]


def test_hybrid_model_source_has_no_cycle_dependency() -> None:
    from pathlib import Path

    source = Path("finance/inflation_policy_model.py").read_text()

    assert "economic_cycle" not in source
