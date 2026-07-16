from __future__ import annotations

import importlib
import importlib.util
import json
from pathlib import Path

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
    }


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


def test_ready_read_model_maps_horizons_evidence_sources_and_separate_history() -> None:
    service = _load_service()
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=lambda **_kwargs: _history_rows(),
    )

    assert list(model) == [
        "schema_version",
        "status",
        "as_of_date",
        "model_version",
        "headline",
        "horizons",
        "cycle_clock",
        "evidence",
        "market_implications",
        "history",
        "sources",
        "limitations",
    ]
    assert model["schema_version"] == "economic_cycle_v1"
    assert [item["label"] for item in model["horizons"]] == [
        "현재",
        "1개월 후",
        "2개월 후",
    ]
    assert all(set(item["probabilities"]) == set(PHASES) for item in model["horizons"])
    assert all(item["estimate_status"] == "VERIFIED" for item in model["horizons"])
    assert model["cycle_clock"]["expected_transition"] == "expansion_to_slowdown"
    assert {item["direction"] for item in model["evidence"]} <= {
        "강화",
        "약화",
        "중립",
    }
    assert all(item["source_date"] for item in model["sources"])
    assert len(model["history"]) == 60
    assert model["history"] == sorted(model["history"], key=lambda item: item["date"])
    assert all("nber_recession" in item for item in model["history"])
    assert all(
        "phase" in item
        and "probabilities" in item
        and "estimate_status" in item
        for item in model["history"]
    )
    json.dumps(model, allow_nan=False)


def test_limited_horizon_exposes_provisional_probabilities_with_validation_reason() -> (
    None
):
    service = _load_service()
    snapshot = _ready_snapshot()
    horizons = json.loads(str(snapshot["forecast_path_json"]))
    horizons[1].update(
        {
            "publication_status": "LIMITED",
            "reason": "CALIBRATION_ERROR",
        }
    )
    snapshot["forecast_path_json"] = json.dumps(horizons)

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: [],
    )

    assert model["horizons"][0]["probabilities"] is not None
    assert model["horizons"][1]["probabilities"] == _probabilities("slowdown")
    assert model["horizons"][1]["dominant_phase"] == "slowdown"
    assert model["horizons"][1]["estimate_status"] == "PROVISIONAL"
    assert model["horizons"][1]["estimate_label"] == "잠정 모델 추정"
    assert "확률 보정" in model["horizons"][1]["reason"]
    assert model["horizons"][2]["probabilities"] is not None


def test_missing_limited_probabilities_are_unavailable_instead_of_provisional() -> None:
    service = _load_service()
    snapshot = _ready_snapshot()
    horizons = json.loads(str(snapshot["forecast_path_json"]))
    horizons[2].update(
        {
            "probabilities": None,
            "dominant_phase": None,
            "confidence": None,
            "publication_status": "LIMITED",
            "reason": "PARTIAL_FACTORS",
        }
    )
    snapshot["forecast_path_json"] = json.dumps(horizons)

    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: [],
    )

    assert model["horizons"][2]["estimate_status"] == "UNAVAILABLE"
    assert model["horizons"][2]["estimate_label"] == "판단 불가"
    assert model["horizons"][2]["probabilities"] is None


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


def test_service_truncates_evidence_and_history_without_recalculation() -> None:
    service = _load_service()
    snapshot = _ready_snapshot()
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: snapshot,
        history_loader=lambda **_kwargs: _history_rows(140),
    )

    assert len(model["evidence"]) == 10
    assert len(model["history"]) == 60
    assert model["history"][0]["date"] > "2020-01-01"
    assert all(item["status"] in {"READY", "LIMITED"} for item in model["history"])


def test_service_requests_only_the_recent_sixty_month_display_window() -> None:
    service = _load_service()
    requested: dict[str, object] = {}

    def load_history(**kwargs):
        requested.update(kwargs)
        return _history_rows(60)

    service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        history_loader=load_history,
    )

    assert str(requested["start_date"]) == "2021-07-30"
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
        "gold_dollar",
        "commodities",
    ]
    assert [item["assessment"] for item in implications] == [
        "MIXED",
        "BURDEN",
        "FAVORABLE",
        "MIXED",
    ]
    assert [item["assessment_label"] for item in implications] == [
        "혼재",
        "부담",
        "우호",
        "혼재",
    ]
    assert all(len(item["drivers"]) == 2 for item in implications)
    assert {
        driver["impact"]
        for driver in implications[0]["drivers"]
    } == {"FAVORABLE", "BURDEN"}
    assert {
        driver["impact"]
        for driver in implications[3]["drivers"]
    } == {"FAVORABLE", "BURDEN"}
    assert all(item["change_condition"] for item in implications)
    assert all(item["is_directional_forecast"] is False for item in implications)
    serialized = json.dumps(implications, ensure_ascii=False).lower()
    for forbidden in ("target price", "buy", "sell", "directional return"):
        assert forbidden not in serialized
    assert all(item["context"] == item["summary"] for item in implications)


def test_market_implications_do_not_invent_reasons_when_factor_coverage_is_low() -> (
    None
):
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")

    implications = interpretation.build_market_implications(
        [],
        [{"factor": "activity_score", "value": -0.4}],
    )

    assert all(item["assessment"] == "INSUFFICIENT" for item in implications)
    assert all(item["assessment_label"] == "자료 부족" for item in implications)
    assert all(item["drivers"] == [] for item in implications)
    assert all("2개 이상" in item["change_condition"] for item in implications)


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
