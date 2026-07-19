from __future__ import annotations

import importlib
import importlib.util
import json
from datetime import date, timedelta
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
    assert model["schema_version"] == "economic_cycle_v2"
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
    assert summary in gold["narrative"]
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

    assert model["schema_version"] == "economic_cycle_v2"
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
