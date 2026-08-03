from __future__ import annotations

import importlib
import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

from finance.economic_cycle_model import PHASES


def _load_service():
    spec = importlib.util.find_spec("app.services.overview.economic_cycle")
    assert spec is not None, "economic cycle Overview service must exist"
    return importlib.import_module("app.services.overview.economic_cycle")


def _probabilities(winner: str) -> dict[str, float]:
    return {phase: 0.70 if phase == winner else 0.10 for phase in PHASES}


def _ready_snapshot() -> dict[str, object]:
    horizons = [
        {
            "horizon_months": 0,
            "probabilities": _probabilities("expansion"),
            "dominant_phase": "expansion",
            "confidence": 0.70,
            "publication_status": "READY",
            "reason": None,
        },
        {
            "horizon_months": 1,
            "probabilities": _probabilities("slowdown"),
            "dominant_phase": "slowdown",
            "confidence": 0.70,
            "publication_status": "READY",
            "reason": None,
        },
        {
            "horizon_months": 2,
            "probabilities": _probabilities("slowdown"),
            "dominant_phase": "slowdown",
            "confidence": 0.70,
            "publication_status": "READY",
            "reason": None,
        },
    ]
    evidence = [
        {
            "factor": "activity_score" if index < 8 else "financial_leading_score",
            "series_id": f"SERIES{index:02d}",
            "value": 0.4 if index % 3 == 0 else -0.3 if index % 3 == 1 else 0.0,
            "source_date": f"2026-06-{min(index + 1, 28):02d}",
        }
        for index in range(15)
    ]
    return {
        "as_of_date": "2026-06-30",
        "model_version": "cycle-v1",
        "status": "READY",
        "current_phase": "expansion",
        "expected_transition": "expansion_to_slowdown",
        "nber_recession": 0,
        "training_cutoff_date": "2026-05-31",
        "data_cutoff_date": "2026-06-30",
        "forecast_path_json": json.dumps(horizons),
        "probabilities_json": json.dumps(horizons[0]["probabilities"]),
        "factor_contributions_json": json.dumps(
            [{"factor": "activity_score", "value": 0.8}]
        ),
        "top_evidence_json": json.dumps(evidence),
        "warnings_json": "[]",
        "observed_state_json": json.dumps(
            {
                "as_of_date": "2026-06-30",
                "raw_level": 0.40,
                "level": 0.35,
                "momentum": 0.10,
                "phase": "expansion",
                "activity_level": 0.42,
                "labor_income_level": 0.28,
                "activity_momentum": 0.12,
                "labor_income_momentum": 0.08,
                "level_breadth": 0.75,
                "momentum_breadth": 0.75,
                "available_series": 8,
                "stale_series": 0,
                "duration_months": 4,
                "confidence": "HIGH",
                "revision_sensitivity": "STABLE",
                "revised_phase": "expansion",
                "data_status": "READY",
            }
        ),
        "recent_changes_json": "[]",
        "transition_monitor_json": json.dumps(
            {
                "observed_phase": "expansion",
                "anchor_phase": "expansion",
                "target_phase": "slowdown",
                "status": "MAINTAIN",
                "conditions_met": 0,
                "conditions_total": 3,
                "conditions": [],
                "context": [],
            }
        ),
    }


def _observed_snapshot() -> dict[str, object]:
    snapshot = _ready_snapshot()
    snapshot.update(
        {
            "status": "READY",
            "current_phase": "contraction",
            "observed_state_json": json.dumps(
                {
                    "as_of_date": "2026-06-30",
                    "raw_level": -0.63,
                    "level": -0.56,
                    "momentum": -0.24,
                    "phase": "contraction",
                    "activity_level": -0.70,
                    "labor_income_level": -0.42,
                    "activity_momentum": -0.31,
                    "labor_income_momentum": -0.17,
                    "level_breadth": 0.50,
                    "momentum_breadth": 0.50,
                    "available_series": 8,
                    "stale_series": 0,
                    "duration_months": 3,
                    "confidence": "MEDIUM",
                    "revision_sensitivity": "SENSITIVE",
                    "revised_phase": "recovery",
                    "data_status": "READY",
                }
            ),
            "recent_changes_json": json.dumps(
                [
                    {
                        "horizon_months": 1,
                        "status": "MIXED",
                        "composite_delta": 0.05,
                        "breadth": 0.50,
                        "available_pairs": 8,
                        "activity_delta": 0.08,
                        "labor_income_delta": 0.02,
                    },
                    {
                        "horizon_months": 3,
                        "status": "WEAKENING",
                        "composite_delta": -0.18,
                        "breadth": 0.25,
                        "available_pairs": 8,
                        "activity_delta": -0.22,
                        "labor_income_delta": -0.14,
                    },
                    {
                        "horizon_months": 6,
                        "status": "MIXED",
                        "composite_delta": -0.04,
                        "breadth": 0.50,
                        "available_pairs": 8,
                        "activity_delta": -0.06,
                        "labor_income_delta": -0.02,
                    },
                ]
            ),
            "transition_monitor_json": json.dumps(
                {
                    "observed_phase": "contraction",
                    "anchor_phase": "contraction",
                    "target_phase": "recovery",
                    "status": "WATCH",
                    "conditions_met": 1,
                    "conditions_total": 3,
                    "candidate_started_at": "2026-06-30",
                    "confirmed_at": None,
                    "non_adjacent_observation": False,
                    "conditions": [
                        {
                            "condition_id": "persistence",
                            "status": "UNMET",
                            "value": {"current": -0.24, "previous": -0.20},
                            "threshold": ">= 0 for two releases",
                        },
                        {
                            "condition_id": "diffusion",
                            "status": "UNMET",
                            "value": {"breadth": 0.50, "available_pairs": 8},
                            "threshold": ">= 0.60",
                        },
                        {
                            "condition_id": "corroboration",
                            "status": "MET",
                            "value": {"activity": 0.04, "labor_income": 0.02},
                            "threshold": "both >= 0",
                        },
                    ],
                    "context": [
                        {
                            "factor": "financial_leading_score",
                            "value": 0.22,
                            "relation": "TOWARD_TARGET",
                        },
                        {
                            "factor": "inflation_policy_score",
                            "value": 0.79,
                            "relation": "SUPPORT_CURRENT",
                        },
                    ],
                }
            ),
        }
    )
    return snapshot


def _observed_history(count: int = 12) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, origin in enumerate(
        pd.date_range("2025-07-31", periods=count, freq="ME")
    ):
        level = -1.1 + index * 0.05
        momentum = -0.4 + index * 0.01
        rows.append(
            {
                "as_of_date": origin.date().isoformat(),
                "status": "READY",
                "current_phase": "contraction",
                "nber_recession": 1 if index < 2 else 0,
                "observed_state_json": json.dumps(
                    {
                        "as_of_date": origin.date().isoformat(),
                        "level": level,
                        "momentum": momentum,
                        "phase": "contraction",
                        "confidence": "MEDIUM",
                        "revision_sensitivity": "STABLE",
                        "data_status": "READY",
                    }
                ),
            }
        )
    return rows


def _history_rows(count: int = 130) -> list[dict[str, object]]:
    rows = []
    for index in range(count):
        month = 1 + index
        year = 2015 + (month - 1) // 12
        month_number = ((month - 1) % 12) + 1
        phase = PHASES[index % 4]
        rows.append(
            {
                "as_of_date": f"{year:04d}-{month_number:02d}-28",
                "status": "LIMITED" if index % 17 == 0 else "READY",
                "current_phase": phase,
                "probabilities_json": json.dumps(_probabilities(phase)),
                "nber_recession": 1 if phase == "recession" else 0,
            }
        )
    return list(reversed(rows))


def test_v3_exposes_observed_state_recent_changes_and_actual_cycle_map() -> None:
    service = _load_service()

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _observed_snapshot(),
        history_loader=lambda **_kwargs: _observed_history(),
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
        price_reference_date=date(2026, 7, 17),
    )

    assert model["schema_version"] == "economic_cycle_v3"
    assert model["headline"] == {
        "phase": "contraction",
        "phase_label": "위축",
        "summary": "실물경제 수준이 낮고 최근 3개월 흐름도 약화된 상태입니다.",
        "reason_code": None,
    }
    assert model["observed_state"]["level"] == pytest.approx(-0.56)
    assert model["observed_state"]["momentum"] == pytest.approx(-0.24)
    assert model["observed_state"]["confidence_label"] == "보통"
    assert [item["horizon_months"] for item in model["recent_changes"]] == [
        1,
        3,
        6,
    ]
    assert model["transition_monitor"]["status"] == "WATCH"
    assert model["transition_monitor"]["conditions_met"] == 1
    assert len(model["cycle_map"]["points"]) == 12
    assert model["cycle_map"]["points"][-1]["level"] == pytest.approx(-0.56)
    assert model["cycle_map"]["points"][-1]["momentum"] == pytest.approx(-0.24)
    assert "horizons" not in model
    assert "cycle_clock" not in model
    assert "history" not in model
    json.dumps(model, allow_nan=False)


def test_transition_monitor_recovers_confirmed_anchor_date_from_legacy_history() -> None:
    service = _load_service()
    current = _observed_snapshot()
    current["transition_monitor_json"] = json.dumps(
        {
            "observed_phase": "contraction",
            "anchor_phase": "recovery",
            "target_phase": "expansion",
            "status": "WATCH",
            "conditions_met": 0,
            "conditions_total": 3,
            "non_adjacent_observation": True,
            "conditions": [],
            "context": [],
        }
    )
    confirmed = _observed_history(1)[0]
    confirmed["as_of_date"] = "2025-08-31"
    confirmed["transition_monitor_json"] = json.dumps(
        {
            "anchor_phase": "contraction",
            "target_phase": "recovery",
            "status": "CONFIRMED",
            "confirmed_at": "2025-08-31",
        }
    )

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: current,
        history_loader=lambda **_kwargs: [confirmed],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    monitor = model["transition_monitor"]
    assert monitor["anchor_started_at"] == "2025-08-31"
    assert monitor["anchor_source"] == "CONFIRMED"
    assert monitor["anchor_source_label"] == "조건 확인"
    assert monitor["anchor_confirmed_at"] == "2025-08-31"


def test_transition_monitor_labels_first_seen_legacy_anchor_without_claiming_confirmation() -> None:
    service = _load_service()
    current = _observed_snapshot()
    current_transition = json.loads(str(current["transition_monitor_json"]))
    current_transition.update(
        {
            "anchor_phase": "recovery",
            "target_phase": "expansion",
            "non_adjacent_observation": True,
        }
    )
    current["transition_monitor_json"] = json.dumps(current_transition)
    first_seen = _observed_history(1)[0]
    first_seen["as_of_date"] = "2025-10-31"
    first_seen["transition_monitor_json"] = json.dumps(
        {
            "anchor_phase": "recovery",
            "target_phase": "expansion",
            "status": "MAINTAIN",
        }
    )

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: current,
        history_loader=lambda **_kwargs: [first_seen],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    monitor = model["transition_monitor"]
    assert monitor["anchor_started_at"] == "2025-10-31"
    assert monitor["anchor_source"] == "LEGACY_OBSERVED"
    assert monitor["anchor_source_label"] == "조회 이력 내 최초 관측"
    assert monitor["anchor_confirmed_at"] is None


@pytest.mark.parametrize("reverse_rows", [False, True])
def test_cycle_map_selects_latest_replay_deterministically_for_duplicate_date(
    reverse_rows: bool,
) -> None:
    service = _load_service()

    def replay(*, level: float, updated_at: str, row_id: int) -> dict[str, object]:
        return {
            "id": row_id,
            "as_of_date": "2026-05-31",
            "model_version": f"cycle-v{row_id}",
            "updated_at": updated_at,
            "nber_recession": 0,
            "observed_state_json": json.dumps(
                {
                    "as_of_date": "2026-05-31",
                    "level": level,
                    "momentum": 0.20,
                    "phase": "expansion",
                    "data_status": "READY",
                }
            ),
        }

    rows = [
        replay(level=-0.80, updated_at="2026-06-01 09:00:00", row_id=1),
        replay(level=0.75, updated_at="2026-06-02 09:00:00", row_id=2),
    ]
    if reverse_rows:
        rows.reverse()

    points = service._cycle_map(rows, _observed_snapshot())["points"]

    may = next(point for point in points if point["date"] == "2026-05-31")
    assert may["level"] == pytest.approx(0.75)


def test_cycle_map_current_snapshot_overrides_replay_for_same_date() -> None:
    service = _load_service()
    current = _observed_snapshot()
    replay = dict(current)
    replay["updated_at"] = "2099-01-01 00:00:00"
    replay["id"] = 999
    replay["observed_state_json"] = json.dumps(
        {
            "as_of_date": "2026-06-30",
            "level": 1.50,
            "momentum": 1.00,
            "phase": "expansion",
            "data_status": "READY",
        }
    )

    points = service._cycle_map([replay], current)["points"]

    assert len(points) == 1
    assert points[0]["level"] == pytest.approx(-0.56)
    assert points[0]["phase"] == "contraction"


def test_v3_legacy_probability_snapshot_does_not_restore_current_phase() -> None:
    service = _load_service()
    legacy_snapshot = _ready_snapshot()
    legacy_snapshot.pop("observed_state_json")
    legacy_snapshot.pop("recent_changes_json")
    legacy_snapshot.pop("transition_monitor_json")

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: legacy_snapshot,
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    assert model["schema_version"] == "economic_cycle_v3"
    assert model["status"] == "LIMITED"
    assert model["headline"]["phase"] is None
    assert model["headline"]["reason_code"] == "OBSERVED_STATE_MISSING"
    assert model["observed_state"]["data_status"] == "UNAVAILABLE"
    assert model["cycle_map"]["points"] == []
    assert len(model["market_implications"]) == 5
    source = Path("app/services/overview/economic_cycle.py").read_text(encoding="utf-8")
    assert "forecast_path_json" not in source
    assert "probabilities_json" not in source


def test_v3_keeps_asset_checkpoint_payload_identical() -> None:
    service = _load_service()
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    snapshot = _observed_snapshot()
    market_rows: list[dict[str, object]] = []
    asset_rows: list[dict[str, object]] = []
    earnings: dict[str, object] = {}
    reference = date(2026, 7, 17)
    expected = interpretation.build_market_implications(
        (),
        service._evidence(snapshot),
        asset_rows,
        market_rows=market_rows,
        sp500_earnings=earnings,
        economic_as_of_date="2026-06-30",
        price_reference_date=reference,
    )
    for item in expected:
        item["economic_as_of_date"] = "2026-06-30"

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: market_rows,
        asset_price_loader=lambda **_kwargs: asset_rows,
        sp500_earnings_loader=lambda **_kwargs: earnings,
        price_reference_date=reference,
    )

    assert model["market_implications"] == expected


def test_v3_intramonth_is_provisional_and_never_replaces_monthly_headline() -> None:
    service = _load_service()
    monthly = _observed_snapshot()
    intramonth = _intramonth_snapshot()
    intramonth["observed_state_json"] = json.dumps(
        {
            "as_of_date": "2026-07-21",
            "raw_level": -0.40,
            "level": -0.45,
            "momentum": 0.08,
            "phase": "recovery",
            "available_series": 8,
            "stale_series": 0,
            "confidence": "MEDIUM",
            "revision_sensitivity": "STABLE",
            "data_status": "READY",
        }
    )

    model = service.build_economic_cycle_read_model(
        as_of_date="2026-07-21",
        snapshot_loader=lambda **_kwargs: monthly,
        intramonth_loader=lambda **_kwargs: intramonth,
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    assert model["headline"]["phase"] == "contraction"
    assert model["as_of_date"] == "2026-06-30"
    assert model["intramonth_change"]["provisional"] is True
    assert model["intramonth_change"]["as_of_date"] == "2026-07-21"
    assert model["intramonth_change"]["raw_level_delta"] == pytest.approx(0.23)
    assert model["intramonth_change"]["observed_state"]["phase"] == "recovery"


def test_ready_read_model_maps_horizons_evidence_sources_and_separate_history() -> None:
    service = _load_service()
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _observed_snapshot(),
        history_loader=lambda **_kwargs: _observed_history(),
    )

    assert list(model) == [
        "schema_version",
        "status",
        "as_of_date",
        "model_version",
        "intramonth_change",
        "data_freshness",
        "headline",
        "observed_state",
        "recent_changes",
        "transition_monitor",
        "cycle_map",
        "evidence",
        "market_implications",
        "sources",
        "limitations",
    ]
    assert model["schema_version"] == "economic_cycle_v3"
    assert model["observed_state"]["phase"] == "contraction"
    assert model["transition_monitor"]["target_phase"] == "recovery"
    assert {item["direction"] for item in model["evidence"]} <= {
        "강화",
        "약화",
        "중립",
    }
    assert all(item["source_date"] for item in model["sources"])
    assert len(model["cycle_map"]["points"]) == 12
    assert all("nber_recession" in item for item in model["cycle_map"]["points"])
    json.dumps(model, allow_nan=False)


@pytest.mark.parametrize(
    ("phase", "expected"),
    [
        (
            "recovery",
            "실물경제 수준은 낮지만 최근 3개월 흐름이 개선된 상태입니다.",
        ),
        (
            "expansion",
            "실물경제 수준이 높고 최근 3개월 흐름도 개선된 상태입니다.",
        ),
        (
            "slowdown",
            "실물경제 수준은 높지만 최근 3개월 흐름이 약화된 상태입니다.",
        ),
        (
            "contraction",
            "실물경제 수준이 낮고 최근 3개월 흐름도 약화된 상태입니다.",
        ),
    ],
)
def test_headline_explains_phase_as_level_and_three_month_momentum(
    phase: str,
    expected: str,
) -> None:
    service = _load_service()
    snapshot = _ready_snapshot()
    observed = json.loads(str(snapshot["observed_state_json"]))
    observed["phase"] = phase
    snapshot["current_phase"] = phase
    snapshot["observed_state_json"] = json.dumps(observed)

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: _history_rows(),
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    assert model["headline"]["summary"] == expected


def _intramonth_snapshot() -> dict[str, object]:
    probabilities = {
        "recovery": 0.16,
        "expansion": 0.64,
        "slowdown": 0.10,
        "recession": 0.10,
    }
    horizons = [
        {
            "horizon_months": 0,
            "probabilities": probabilities,
            "dominant_phase": "expansion",
            "confidence": 0.64,
            "publication_status": "READY",
            "reason": None,
        }
    ]
    return {
        "as_of_date": "2026-07-21",
        "baseline_as_of_date": "2026-06-30",
        "model_version": "cycle-v1",
        "status": "READY",
        "forecast_path_json": json.dumps(horizons),
        "top_evidence_json": json.dumps(
            [
                {"factor": "activity_score", "value": -0.80},
                {"factor": "labor_income_score", "value": -0.29},
                {"factor": "financial_leading_score", "value": 0.28},
                {"factor": "inflation_policy_score", "value": 0.74},
            ]
        ),
        "source_collected_at": "2026-07-16 10:02:56",
        "source_coverage_json": json.dumps(
            {
                "requested_series": 17,
                "available_series": 17,
                "series": [
                    {
                        "series_id": "PAYEMS",
                        "status": "ACTUAL",
                        "latest_observation_date": "2026-06-01",
                    }
                ],
            }
        ),
        "observed_state_json": json.dumps(
            {
                "as_of_date": "2026-07-21",
                "raw_level": 0.46,
                "level": 0.39,
                "momentum": 0.12,
                "phase": "expansion",
                "available_series": 8,
                "stale_series": 0,
                "confidence": "MEDIUM",
                "revision_sensitivity": "STABLE",
                "data_status": "READY",
            }
        ),
        "recent_changes_json": "[]",
    }


def test_service_pairs_latest_intramonth_with_exact_monthly_baseline() -> None:
    service = _load_service()
    monthly = _ready_snapshot()
    monthly["top_evidence_json"] = json.dumps(
        [
            {"factor": "activity_score", "value": -0.82},
            {"factor": "labor_income_score", "value": -0.44},
            {"factor": "financial_leading_score", "value": 0.22},
            {"factor": "inflation_policy_score", "value": 0.79},
        ]
    )

    model = service.build_economic_cycle_read_model(
        as_of_date="2026-07-21",
        snapshot_loader=lambda **_kwargs: monthly,
        intramonth_loader=lambda **_kwargs: _intramonth_snapshot(),
        history_loader=lambda **_kwargs: _history_rows(12),
    )

    bridge = model["intramonth_change"]
    assert bridge["baseline_as_of_date"] == "2026-06-30"
    assert bridge["as_of_date"] == "2026-07-21"
    assert bridge["provisional"] is True
    assert bridge["raw_level_delta"] == pytest.approx(0.06)
    assert bridge["observed_state"]["phase"] == "expansion"
    factor = next(
        item for item in bridge["factor_deltas"] if item["factor"] == "labor_income_score"
    )
    assert factor["delta"] == pytest.approx(0.15)
    assert bridge["source_collected_at"] == "2026-07-16 10:02:56"
    assert bridge["source_coverage"]["available_series"] == 17
    assert [item["date"] for item in model["cycle_map"]["points"]] == ["2026-06-30"]


def test_service_attaches_intramonth_freshness() -> None:
    service = _load_service()

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        intramonth_loader=lambda **_kwargs: _intramonth_snapshot(),
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
        freshness_date=date(2026, 7, 25),
    )

    assert model["data_freshness"]["persisted_as_of_date"] == "2026-07-21"
    assert model["data_freshness"]["target_as_of_date"] == "2026-07-24"
    assert model["data_freshness"]["status"] == "REFRESH_AVAILABLE"
    assert model["data_freshness"]["last_checked_at"] == "2026-07-16 10:02:56"
    assert (
        model["data_freshness"]["latest_source_observation_date"]
        == "2026-06-01"
    )


def test_service_preserves_asset_specific_summary_without_common_state_copy() -> None:
    service = _load_service()
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
    )

    by_asset = {
        item["asset_group"]: item
        for item in model["market_implications"]
    }
    common_summary = by_asset["gold"]["economic_state"]["summary"]
    for asset_group in ("gold", "dollar"):
        item = by_asset[asset_group]
        assert common_summary not in item["summary"]
        assert item["summary"] != item["narrative"]
        assert item["current_interpretation"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda row: row.update(baseline_as_of_date="2026-05-31"),
        lambda row: row.update(model_version="different-model"),
        lambda row: row.update(as_of_date="2026-06-30"),
    ],
)
def test_service_hides_unpaired_or_malformed_intramonth_rows(mutator) -> None:
    service = _load_service()
    nowcast = _intramonth_snapshot()
    mutator(nowcast)

    model = service.build_economic_cycle_read_model(
        as_of_date="2026-07-21",
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        intramonth_loader=lambda **_kwargs: nowcast,
        history_loader=lambda **_kwargs: [],
    )

    assert model["intramonth_change"] is None


def test_service_suppresses_intramonth_coordinate_when_real_economy_coverage_is_low() -> None:
    service = _load_service()
    nowcast = _intramonth_snapshot()
    observed = json.loads(str(nowcast["observed_state_json"]))
    observed.update({"available_series": 5, "data_status": "UNAVAILABLE"})
    nowcast["observed_state_json"] = json.dumps(observed)

    model = service.build_economic_cycle_read_model(
        as_of_date="2026-07-21",
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        intramonth_loader=lambda **_kwargs: nowcast,
        history_loader=lambda **_kwargs: [],
    )

    assert model["intramonth_change"] is not None
    assert model["intramonth_change"]["observed_state"] is None


def test_service_isolates_intramonth_loader_error() -> None:
    service = _load_service()

    def broken_loader(**_kwargs):
        raise RuntimeError("nowcast table unavailable")

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        intramonth_loader=broken_loader,
        history_loader=lambda **_kwargs: [],
    )

    assert model["status"] == "READY"
    assert model["intramonth_change"] is None
    assert "nowcast table unavailable" not in json.dumps(model, ensure_ascii=False)


def test_no_snapshot_and_read_failure_have_stable_states_without_collector() -> None:
    service = _load_service()
    not_materialized = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: None,
        history_loader=lambda **_kwargs: pytest.fail("history should not load"),
    )
    assert not_materialized["status"] == "LIMITED"
    assert not_materialized["headline"]["reason_code"] == "NOT_MATERIALIZED"

    def broken_loader(**_kwargs):
        raise RuntimeError("schema unavailable")

    failed = service.build_economic_cycle_read_model(snapshot_loader=broken_loader)
    assert failed["status"] == "ERROR"
    assert failed["headline"]["reason_code"] == "READ_ERROR"
    assert "schema unavailable" not in json.dumps(failed, ensure_ascii=False)

    source = Path("app/services/overview/economic_cycle.py").read_text(encoding="utf-8")
    assert "economic_cycle_vintages" not in source
    assert "collect_economic_cycle" not in source


def test_service_truncates_evidence_and_cycle_map_without_recalculation() -> None:
    service = _load_service()
    snapshot = _ready_snapshot()
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: _observed_history(20),
    )

    assert len(model["evidence"]) == 10
    assert len(model["cycle_map"]["points"]) == 12
    assert model["cycle_map"]["points"][0]["date"] > "2020-01-01"
    assert all("probabilities" not in item for item in model["cycle_map"]["points"])


def test_service_requests_only_the_recent_twelve_month_cycle_map_window() -> None:
    service = _load_service()
    requested: dict[str, object] = {}

    def load_history(**kwargs):
        requested.update(kwargs)
        return _history_rows(60)

    service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=load_history,
    )

    assert str(requested["start_date"]) == "2025-07-30"
    assert str(requested["end_date"]) == "2026-06-30"


def test_market_implications_are_conditional_context_not_directional_predictions() -> (
    None
):
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    horizons = json.loads(str(_ready_snapshot()["forecast_path_json"]))
    evidence = [
        {"factor": "activity_score", "value": -0.82},
        {"factor": "labor_income_score", "value": -0.44},
        {"factor": "financial_leading_score", "value": 0.22},
        {"factor": "inflation_policy_score", "value": 0.79},
    ]
    implications = interpretation.build_market_implications(
        horizons,
        evidence,
    )

    assert [item["asset_group"] for item in implications] == [
        "rates",
        "equities",
        "gold",
        "dollar",
        "commodities",
    ]
    assert all(
        item["analysis_status"] != "PATHWAYS_NOT_CONNECTED"
        for item in implications
    )
    gold = next(item for item in implications if item["asset_group"] == "gold")
    dollar = next(item for item in implications if item["asset_group"] == "dollar")
    assert {row["pathway_id"] for row in gold["pathways"]} == {
        "real_yield",
        "dollar",
        "short_rate",
        "risk_aversion",
    }
    assert any(
        row["pathway_id"] == "relative_rates"
        for row in dollar["unmeasured_pathways"]
    )
    assert all(item["is_directional_forecast"] is False for item in implications)
    serialized = json.dumps(implications, ensure_ascii=False).lower()
    for forbidden in (
        "target price",
        "buy",
        "sell",
        "directional return",
        "alignment",
        "assessment",
        "macro_signal_label",
    ):
        assert forbidden not in serialized


def test_market_implications_do_not_invent_reasons_when_factor_coverage_is_low() -> (
    None
):
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")

    implications = interpretation.build_market_implications(
        [],
        [{"factor": "activity_score", "value": -0.4}],
    )

    gold = next(item for item in implications if item["asset_group"] == "gold")
    observations = gold["economic_state"]["observations"]
    activity = next(row for row in observations if row["factor"] == "activity_score")
    assert activity["direction"] == "WEAKENING"
    assert sum(row["direction"] == "UNAVAILABLE" for row in observations) == 3
    assert gold["coverage"] == "INSUFFICIENT"
    summary = gold["economic_state"]["summary"]
    assert "현재 수준:" in summary
    assert "전망 여건:" in summary
    assert "자료가 부족합니다" in summary
    assert "원인" not in summary


def test_market_implications_separate_observed_state_from_asset_pathways() -> None:
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    horizons = json.loads(str(_ready_snapshot()["forecast_path_json"]))
    evidence = [
        {"factor": "activity_score", "value": -0.82},
        {"factor": "labor_income_score", "value": -0.44},
        {"factor": "financial_leading_score", "value": 0.22},
        {"factor": "inflation_policy_score", "value": 0.79},
    ]
    implications = interpretation.build_market_implications(
        horizons,
        evidence,
        price_reference_date=date(2026, 7, 17),
    )
    gold = next(row for row in implications if row["asset_group"] == "gold")
    dollar = next(row for row in implications if row["asset_group"] == "dollar")

    assert gold["economic_state"] == dollar["economic_state"]
    summary = gold["economic_state"]["summary"]
    assert summary == (
        "현재 수준: 생산·소비 활동과 고용·소득은 자기 과거 기준 이하입니다. "
        "전망 여건: 금융·선행 여건은 전망을 지원합니다. "
        "물가·정책 압력은 전망에 부담을 줍니다."
    )
    assert [row["direction"] for row in gold["economic_state"]["observations"]] == [
        "WEAKENING",
        "WEAKENING",
        "STRENGTHENING",
        "STRENGTHENING",
    ]
    assert summary not in gold["summary"]
    assert summary not in gold["narrative"]
    assert all(
        summary not in row
        for row in gold["current_interpretation"]
    )
    assert gold["summary"] != gold["narrative"]
    assert "가격 원인을 확정하지 않습니다" in gold["narrative"]
    assert "해외 상대금리" in dollar["narrative"]
    assert gold["price_context"]["status"] == "UNAVAILABLE"
    assert dollar["price_context"]["status"] == "UNAVAILABLE"


def test_unavailable_pathways_stay_conservative() -> None:
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    evidence = [
        {"factor": "activity_score", "value": -0.82},
        {"factor": "labor_income_score", "value": -0.44},
        {"factor": "financial_leading_score", "value": 0.22},
        {"factor": "inflation_policy_score", "value": 0.79},
    ]

    implications = interpretation.build_market_implications([], evidence)
    rates = next(row for row in implications if row["asset_group"] == "rates")
    gold = next(row for row in implications if row["asset_group"] == "gold")

    assert rates["analysis_status"] == "LIMITED"
    assert gold["coverage"] == "INSUFFICIENT"
    assert all(row["status"] == "UNAVAILABLE" for row in gold["pathways"])
    assert gold["price_context"]["status"] == "UNAVAILABLE"
    assert "alignment" not in gold
    assert "assessment" not in gold


def test_asset_price_loader_is_db_only_and_price_failure_is_isolated() -> None:
    service = _load_service()
    end = date(2026, 7, 16)
    price_rows = [
        {
            "provider_symbol": symbol,
            "candle_time_utc": end - timedelta(days=63 - index),
            "close": latest if index == 63 else 100.0,
            "source": "yfinance",
            "provider_status": "ok",
        }
        for symbol, latest in (("GC=F", 90.0), ("DX-Y.NYB", 110.0))
        for index in range(64)
    ]
    calls: list[str] = []

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: calls.append("prices") or price_rows,
        price_reference_date=date(2026, 7, 17),
    )

    assert calls == ["prices"]
    assert model["market_implications"][2]["price_context"]["status"] == "UNAVAILABLE"
    assert model["market_implications"][3]["price_context"]["status"] == "UNAVAILABLE"
    assert all(
        item["economic_as_of_date"] == "2026-06-30"
        for item in model["market_implications"]
    )

    def broken_price_loader(**_kwargs):
        raise RuntimeError("price table unavailable")

    isolated = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: [],
        asset_price_loader=broken_price_loader,
        price_reference_date=date(2026, 7, 17),
    )

    assert isolated["status"] == "READY"
    assert isolated["market_implications"][2]["price_context"]["status"] == "UNAVAILABLE"
    assert isolated["market_implications"][3]["price_context"]["status"] == "UNAVAILABLE"
    assert "price table unavailable" not in json.dumps(isolated, ensure_ascii=False)


def test_service_uses_one_reference_date_for_market_pathway_reads() -> None:
    service = _load_service()
    calls: dict[str, object] = {}

    def market_loader(**kwargs):
        calls["market"] = kwargs
        return []

    def price_loader(**kwargs):
        calls["price"] = kwargs
        return []

    def earnings_loader(**kwargs):
        calls["earnings"] = kwargs
        return {"status": "INSUFFICIENT_HISTORY", "quarter_count": 0}

    model = service.build_economic_cycle_read_model(
        as_of_date="2026-06-30",
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: [],
        market_series_loader=market_loader,
        asset_price_loader=price_loader,
        sp500_earnings_loader=earnings_loader,
        price_reference_date="2026-06-30",
    )

    assert model["schema_version"] == "economic_cycle_v3"
    assert calls["market"]["end_date"] == date(2026, 6, 30)
    assert calls["price"] == {
        "lookback_rows": 1500,
        "end_date": date(2026, 6, 30),
    }
    assert calls["earnings"] == {"end_date": date(2026, 6, 30)}


def test_all_five_asset_groups_expose_connected_observation_contracts() -> None:
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    implications = interpretation.build_market_implications(
        [],
        [
            {"factor": "activity_score", "value": -0.4},
            {"factor": "labor_income_score", "value": -0.3},
            {"factor": "financial_leading_score", "value": 0.2},
            {"factor": "inflation_policy_score", "value": 0.3},
        ],
        sp500_earnings={"status": "INSUFFICIENT_HISTORY", "quarter_count": 0},
        price_reference_date="2026-07-17",
    )

    assert [row["asset_group"] for row in implications] == [
        "rates",
        "equities",
        "gold",
        "dollar",
        "commodities",
    ]
    assert all(
        row["analysis_status"] != "PATHWAYS_NOT_CONNECTED"
        for row in implications
    )
    assert all(row["is_directional_forecast"] is False for row in implications)
    for item in implications:
        text = " ".join(
            [
                str(item.get("narrative") or ""),
                *map(str, item.get("current_interpretation") or []),
            ]
        )
        assert not any(
            term in text for term in ("때문에", "원인입니다", "확률", "매수", "매도")
        )


def test_earnings_loader_failure_is_local_to_equities_earnings_path() -> None:
    service = _load_service()

    def broken_earnings_loader(**_kwargs):
        raise RuntimeError("earnings table unavailable")

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=broken_earnings_loader,
        price_reference_date="2026-07-17",
    )

    equities = next(
        row
        for row in model["market_implications"]
        if row["asset_group"] == "equities"
    )
    earnings = next(
        row
        for row in equities["observed_pathways"]
        if row["pathway_id"] == "actual_earnings"
    )
    assert earnings["status"] == "UNAVAILABLE"
    assert "earnings table unavailable" not in json.dumps(model, ensure_ascii=False)


def test_market_loader_failure_limits_cards_without_hiding_cycle_model() -> None:
    service = _load_service()

    def broken_market_loader(**_kwargs):
        raise RuntimeError("macro table unavailable")

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: [],
        market_series_loader=broken_market_loader,
        asset_price_loader=lambda **_kwargs: [],
        price_reference_date="2026-07-17",
    )

    assert model["status"] == "READY"
    gold = next(
        row for row in model["market_implications"] if row["asset_group"] == "gold"
    )
    assert gold["coverage"] in {"PARTIAL", "INSUFFICIENT"}
    assert "macro table unavailable" not in json.dumps(model, ensure_ascii=False)


def test_all_stable_reason_codes_have_concise_korean_labels() -> None:
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    reason_codes = (
        "NOT_COLLECTED",
        "STALE",
        "VINTAGE_GAP",
        "VALIDATION_FAILED",
        "PARTIAL_FACTORS",
        "READ_ERROR",
    )

    labels = [interpretation.translate_reason_code(code) for code in reason_codes]
    assert all(
        label and label != code
        for label, code in zip(labels, reason_codes, strict=True)
    )
    assert len(set(labels)) == len(reason_codes)
