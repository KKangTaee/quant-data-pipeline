from __future__ import annotations

import json
from pathlib import Path

import pytest


def _ready_snapshot() -> dict[str, object]:
    return {
        "as_of_at": "2026-08-02T00:00:00+00:00",
        "model_version": "inflation-policy-hybrid-v1",
        "run_kind": "current",
        "publication_status": "READY",
        "inflation_json": {
            "publication_status": "READY",
            "q4_quantiles_pct": {
                "p05": 2.8,
                "p20": 3.0,
                "p50": 3.4,
                "p80": 3.7,
                "p95": 4.0,
            },
            "state_probabilities": {
                "rapid_disinflation": 10,
                "gradual_disinflation": 20,
                "sticky": 40,
                "reacceleration": 20,
                "shock_reacceleration": 10,
            },
            "threshold_probabilities": {
                "3.4000": 0.50,
                "3.5000": 0.40,
                "3.6000": 0.30,
            },
            "next_release_scenarios": [
                {
                    "mom_pct": value,
                    "publication_status": "READY",
                    "reacceleration_delta": round((value - 0.3) * 0.5, 4),
                    "hike_delta": round((value - 0.3) * 0.4, 4),
                }
                for value in (0.1, 0.2, 0.3, 0.4, 0.5)
            ],
            "state_definition": {"definition_version": "sep-20260617-v1"},
        },
        "policy_json": {
            "publication_status": "READY",
            "next_meeting_probabilities": {"cut": 0.1, "hold": 0.6, "hike": 0.3},
            "net_move_probabilities": {
                "cut_1": 0.1,
                "cut_2": 0.0,
                "cut_3_plus": 0.0,
                "hold": 0.4,
                "hike_1": 0.2,
                "hike_2": 0.2,
                "hike_3_plus": 0.1,
            },
            "year_end_target_probabilities": {"3.6250": 0.4, "3.8750": 0.6},
        },
        "rates_json": {
            "publication_status": "READY",
            "reason": None,
            "term_premium_status": "READY",
            "DGS10": {
                "current_value_pct": 4.65,
                "observation_date": "2026-08-01",
                "active_test_zone": {
                    "zone_lower_pct": 4.58,
                    "zone_upper_pct": 4.65,
                    "state": "ATTEMPT",
                    "known_at_date": "2026-07-16",
                    "timeframes": [63, 252, 504],
                    "zone_strength": 7.9,
                },
                "next_overhead_zone": {
                    "zone_lower_pct": 4.67,
                    "zone_upper_pct": 4.67,
                    "state": "APPROACH",
                    "known_at_date": "2026-05-22",
                    "timeframes": [63, 252, 504],
                    "zone_strength": 2.8,
                },
                "zones": [],
            },
            "driver_decomposition": {
                "dominant_driver": "real_growth_driven",
                "policy_term_lens": {
                    "two_year_policy_proxy_change_bp": 24.0,
                    "term_premium_change_bp": 5.0,
                },
                "real_inflation_lens": {
                    "real_10y_change_bp": 26.0,
                    "breakeven_10y_change_bp": -2.0,
                    "identity_gap_bp": 3.0,
                },
            },
            "inflation_confirmation": {"status": "MIXED", "reason": "split_lenses"},
        },
        "reverse_json": {
            "publication_status": "READY",
            "target_probability": 0.25,
            "supporting_path_count": 400,
            "effective_path_count": 260.0,
            "q4_core_pce_quantiles_pct": {"p20": 3.3, "p50": 3.6, "p80": 3.9},
            "required_remaining_mom_quantiles_pct": {
                "p20": 0.22,
                "p50": 0.28,
                "p80": 0.35,
            },
            "policy_net_step_probabilities": {"hold": 0.2, "hike_2": 0.8},
        },
        "evidence_json": {
            "top_evidence": [
                {
                    "label": "Core PCE",
                    "supports": "inflation",
                    "observation_date": "2026-06-01",
                    "released_at": "2026-07-30T12:30:00Z",
                }
            ]
        },
        "freshness_json": {
            "PCEPILFE": {
                "latest_observation_date": "2026-06-01",
                "latest_released_at": "2026-07-30T12:30:00Z",
            }
        },
        "warnings_json": [],
    }


def _automatic_definition() -> dict[str, object]:
    return {
        "definition_id": "auto-1",
        "owner": "AUTO",
        "definition_name": "자동 경기 저항",
        "instrument": "DGS10",
        "short_lookback_days": 63,
        "long_lookback_days": 504,
        "zone_lower_pct": 4.58,
        "zone_upper_pct": 4.65,
        "buffer_pct": 0.05,
        "confirmation_profile_json": {"confirmation_count": 3, "confirmation_window": 5},
        "known_at": "2026-07-16T00:00:00Z",
        "algorithm_version": "yield-zone-v1",
        "saved_at": "2026-07-16T00:00:00Z",
        "is_active": 1,
    }


def _user_definition() -> dict[str, object]:
    return {
        **_automatic_definition(),
        "definition_id": "user-1",
        "owner": "USER",
        "definition_name": "내 4.7 기준",
        "zone_lower_pct": 4.68,
        "zone_upper_pct": 4.75,
        "algorithm_version": "user-criterion-v1",
        "saved_at": "2026-08-01T00:00:00Z",
    }


def test_ready_read_model_keeps_forward_reverse_and_quality_separate() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: _ready_snapshot(),
        definitions_loader=lambda **_: [_automatic_definition(), _user_definition()],
    )

    assert list(model) == [
        "schema_version",
        "publication_status",
        "as_of_at",
        "model_version",
        "headline",
        "inflation",
        "policy",
        "rates",
        "reverse_scenario",
        "equity_stress",
        "recession",
        "evidence",
        "freshness",
        "warnings",
    ]
    assert model["schema_version"] == "inflation_policy_v1"
    assert sum(model["inflation"]["state_probabilities"].values()) == pytest.approx(1.0)
    assert {item["owner"] for item in model["rates"]["resistance_zones"]} == {
        "AUTO",
        "USER",
    }
    assert model["reverse_scenario"]["publication_status"] == "READY"
    assert model["recession"] == {
        "publication_status": "NOT_AVAILABLE",
        "reason": "침체 모델은 5차 개발 전까지 연결하지 않습니다.",
    }
    json.dumps(model, allow_nan=False)


def test_equity_read_model_exposes_identity_ranges_and_assumption_provenance() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    snapshot = _ready_snapshot()
    snapshot["equity_json"] = {
        "publication_status": "READY",
        "reason": "validated_conditional_association",
        "as_of_at": "2026-08-02T00:00:00Z",
        "index_quantiles": {"p20": 6200.0, "p50": 6800.0, "p80": 7200.0},
        "eps_quantiles": {"p20": 285.0, "p50": 300.0, "p80": 315.0},
        "multiple_quantiles": {"p20": 21.0, "p50": 22.67, "p80": 23.4},
        "threshold_probabilities": {"below_or_equal:6400.0000": 0.25},
        "target_decompositions": {
            "below_or_equal:6400.0000": {
                "target_level": 6400.0,
                "probability": 0.25,
                "eps_quantiles": {"p50": 290.0},
                "multiple_quantiles": {"p50": 21.5},
            }
        },
        "measured_next_year_eps_revision_pct": 3.2,
        "user_ai_eps_uplift_pct": 5.0,
        "scenario_kind": "USER_ASSUMPTION",
        "current_index_level": 6800.0,
        "base_forward_eps": 300.0,
    }

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: snapshot,
        definitions_loader=lambda **_: [],
    )

    assert model["equity_stress"]["publication_status"] == "READY"
    assert model["equity_stress"]["index_quantiles"]["p50"] == pytest.approx(6800.0)
    assert model["equity_stress"]["measured_next_year_eps_revision_pct"] == pytest.approx(3.2)
    assert model["equity_stress"]["user_ai_eps_uplift_pct"] == pytest.approx(5.0)
    assert model["equity_stress"]["threshold_probabilities"] == {
        "below_or_equal:6400.0000": 0.25
    }


def test_invalid_equity_payload_fails_only_equity_section() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    snapshot = _ready_snapshot()
    snapshot["equity_json"] = {
        "publication_status": "READY",
        "index_quantiles": {"p50": float("nan")},
    }

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: snapshot,
        definitions_loader=lambda **_: [],
    )

    assert model["publication_status"] == "READY"
    assert model["inflation"]["publication_status"] == "READY"
    assert model["policy"]["publication_status"] == "READY"
    assert model["rates"]["publication_status"] == "READY"
    assert model["equity_stress"]["publication_status"] == "FAILED"
    assert model["equity_stress"]["index_quantiles"] == {}


def test_missing_snapshot_returns_typed_not_available_sections() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: None,
        definitions_loader=lambda **_: [],
    )

    assert model["publication_status"] == "NOT_AVAILABLE"
    assert model["inflation"]["state_probabilities"] == {}
    assert model["policy"]["net_move_probabilities"] == {}
    assert model["rates"]["resistance_zones"] == []
    assert model["reverse_scenario"]["publication_status"] == "NOT_AVAILABLE"


def test_invalid_probability_payload_fails_closed_without_partial_numbers() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    snapshot = _ready_snapshot()
    inflation = dict(snapshot["inflation_json"])
    inflation["state_probabilities"] = {
        "rapid_disinflation": 0.2,
        "gradual_disinflation": -0.1,
        "sticky": 0.5,
        "reacceleration": 0.3,
        "shock_reacceleration": 0.1,
    }
    snapshot["inflation_json"] = inflation

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: snapshot,
        definitions_loader=lambda **_: [],
    )

    assert model["publication_status"] == "FAILED"
    assert model["inflation"]["state_probabilities"] == {}
    assert "확률" in model["headline"]["summary"]


def test_historical_limited_snapshot_is_labeled_and_reason_is_translated() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    snapshot = _ready_snapshot()
    snapshot["run_kind"] = "historical_replay"
    snapshot["publication_status"] = "LIMITED"
    inflation = dict(snapshot["inflation_json"])
    inflation["publication_status"] = "LIMITED"
    inflation["reason"] = "q4_path_rolling_origin_validation_not_ready"
    snapshot["inflation_json"] = inflation

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: snapshot,
        definitions_loader=lambda **_: [],
    )

    assert model["headline"]["history_label"] == "과거 기준"
    assert model["headline"]["is_historical"] is True
    assert model["inflation"]["reason"] == "연말 Core PCE 경로의 시점별 검증이 아직 부족합니다."


def test_limited_overall_snapshot_does_not_hide_ready_macro_path() -> None:
    from app.services.overview.inflation_policy import build_inflation_policy_read_model

    snapshot = _ready_snapshot()
    snapshot["publication_status"] = "LIMITED"
    snapshot["equity_json"] = {
        "publication_status": "NOT_AVAILABLE",
        "reason": "equity_model_not_available",
    }

    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: snapshot,
        definitions_loader=lambda **_: [],
    )

    assert model["publication_status"] == "LIMITED"
    assert "가장 큰 물가 상태" in model["headline"]["summary"]
    assert "검증이 제한적" not in model["headline"]["summary"]


def test_service_is_db_only_and_cycle_independent() -> None:
    source = Path("app/services/overview/inflation_policy.py").read_text()

    assert "finance.data." not in source
    assert "requests" not in source and "urlopen" not in source
    assert "economic_cycle" not in source
