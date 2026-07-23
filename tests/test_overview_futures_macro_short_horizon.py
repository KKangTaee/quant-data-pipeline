from __future__ import annotations

from pathlib import Path
from typing import Any


FAMILY_VALUES = {
    "risk_on": (-0.2, -1.1, -0.7),
    "growth": (0.3, 0.7, 0.4),
    "rate_pressure": (-0.8, -0.6, 0.2),
    "dollar_pressure": (0.6, 0.9, 0.4),
    "safe_haven": (-0.4, -0.8, -0.1),
    "inflation_pressure": (0.1, 0.6, 0.8),
}


def _pattern() -> dict[str, Any]:
    families = {
        key: {
            "status": "READY",
            "one_day": values[0],
            "five_day": values[1],
            "twenty_day": values[2],
        }
        for key, values in FAMILY_VALUES.items()
    }
    return {
        "status": "READY",
        "as_of_date": "2026-07-22",
        "regime": "mixed",
        "regime_label": "혼재 체제",
        "transition": "conflicting",
        "transition_label": "신호 충돌",
        "summary": "핵심 방향과 확인 신호가 엇갈립니다.",
        "coverage": {
            "available_family_count": 6,
            "required_family_count": 6,
            "available_symbol_count": 15,
        },
        "families": families,
        "evidence": {"current": [], "transition": []},
        "change_conditions": [
            "주가지수 위험선호와 안전자산 선호가 같은 방향으로 정렬되는지 확인합니다."
        ],
        "path": [],
        "ribbon": [],
    }


def _outlook(status: str = "NO_EDGE") -> dict[str, Any]:
    horizons = []
    for horizon in (5, 20):
        horizons.append(
            {
                "horizon": horizon,
                "label": "다음 1주" if horizon == 5 else "다음 1개월",
                "probability_status": status,
                "coordinate_status": status,
                "vector_status": status,
                "probabilities": {
                    "risk_seeking": 0.25,
                    "defensive": 0.35,
                    "inflation_rate_pressure": 0.20,
                    "mixed": 0.20,
                },
                "baseline_probabilities": {
                    "risk_seeking": 0.30,
                    "defensive": 0.30,
                    "inflation_rate_pressure": 0.20,
                    "mixed": 0.20,
                },
                "probability_lift": {
                    "risk_seeking": -0.05,
                    "defensive": 0.05,
                    "inflation_rate_pressure": 0.0,
                    "mixed": 0.0,
                },
                "dominant_regime": "defensive",
                "episode_count": 120,
                "selected_candidate": "M1_MOMENTUM",
                "status_reason": "시간순 검증에서 baseline을 넘지 못했습니다.",
                "edge_label": "방향 우위 미확인",
                "terminal_regions": [],
                "direction_vector": None,
                "macro_adjustment": {"used": False, "reason": "M1 retained"},
                "asset_pathways": {},
            }
        )
    return {
        "status": "READY",
        "as_of_date": "2026-07-22",
        "current_pattern": _pattern(),
        "horizons": horizons,
        "session": {
            "status": "OBSERVED",
            "latest_final_session": "2026-07-22",
            "pending_session": None,
        },
        "method": {
            "effective_episodes": {"5": 120, "20": 100},
            "brier": {"5": 0.5582, "20": 0.56},
            "baseline_brier": {"5": 0.5567, "20": 0.55},
            "calibration": {"5": 0.1, "20": 0.12},
        },
        "limitations": [],
    }


def _payload(status: str = "NO_EDGE") -> dict[str, Any]:
    from app.web.overview.futures_macro_helpers import (
        build_futures_macro_react_workbench_payload,
    )

    return build_futures_macro_react_workbench_payload(
        {
            "coverage": {
                "standardized_count": 17,
                "symbol_count": 17,
                "latest_daily_date": "2026-07-22",
            },
            "summary": {"summary": "단기 선물 흐름을 확인합니다."},
        },
        pattern_outlook=_outlook(status),
    )


def test_short_horizon_payload_orders_core_four_and_confirmation_two() -> None:
    payload = _payload()
    decision = payload["short_horizon_decision"]

    assert payload["schema_version"] == "futures_macro_react_workbench_v4"
    assert [row["key"] for row in decision["core_directions"]] == [
        "risk_on",
        "rate_pressure",
        "dollar_pressure",
        "inflation_pressure",
    ]
    assert [row["key"] for row in decision["confirmation_signals"]] == [
        "growth",
        "safe_haven",
    ]
    assert decision["observation_windows"] == [
        {"key": "1D", "label": "최근 1거래일", "role": "새 충격"},
        {"key": "5D", "label": "최근 5거래일", "role": "단기 방향"},
        {"key": "20D", "label": "최근 20거래일", "role": "배경 흐름"},
    ]
    risk_on = decision["core_directions"][0]
    assert risk_on["one_day"]["label"] == "중립"
    assert risk_on["five_day"]["label"] == "약화"
    assert risk_on["twenty_day"]["label"] == "약화"


def test_hero_names_short_horizon_scope_in_user_language() -> None:
    hero = _payload()["hero"]

    assert hero["kicker"] == "단기 방향 진단"
    assert hero["coverage_label"] == "최근 1 · 5 · 20거래일"


def test_no_edge_copy_explains_baseline_without_exposing_internal_label() -> None:
    validation = _payload("NO_EDGE")["short_horizon_decision"][
        "future_five_day_validation"
    ]

    assert validation == {
        "status": "NO_EDGE",
        "title": "방향 예측 근거 부족",
        "detail": "유사 국면 모델이 평소 5거래일 결과 빈도보다 정확하지 않음",
        "episode_count": 120,
    }


def test_validation_copy_covers_all_publication_states() -> None:
    expected = {
        "VERIFIED": (
            "검증된 5거래일 방향 우위",
            "평소 결과 빈도보다 시간순 검증 성능이 높음",
        ),
        "PROVISIONAL": (
            "검증 중 · 방향 확정 보류",
            "계산은 가능하지만 공개 검증 기준을 모두 충족하지 못함",
        ),
        "UNAVAILABLE": (
            "검증 자료 부족",
            "독립 표본 또는 시간순 평가가 부족함",
        ),
    }

    for status, copy in expected.items():
        validation = _payload(status)["short_horizon_decision"][
            "future_five_day_validation"
        ]
        assert (validation["title"], validation["detail"]) == copy


def test_calculation_scope_is_derived_from_collection_and_score_members() -> None:
    scope = _payload()["short_horizon_decision"]["calculation_scope"]

    assert scope["collected_count"] == 17
    assert scope["direct_family_input_count"] == 15
    assert scope["available_family_count"] == 6
    assert scope["required_family_count"] == 6
    assert scope["shared_context_symbols"] == ["DX-Y.NYB"]
    assert scope["raw_observation_symbols"] == ["SI=F"]


def test_confirmation_conflict_does_not_claim_confirmed_defensive_alignment() -> None:
    decision = _payload()["short_horizon_decision"]

    assert "전형적 방어 정렬" in decision["confirmation_summary"]
    assert "아님" in decision["confirmation_summary"]
    assert [item["key"] for item in _payload()["horizons"]] == [
        "current",
        "5D",
        "20D",
    ]


def test_react_default_render_uses_short_horizon_sections_in_order() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    workbench = (root / "FuturesMacroWorkbench.tsx").read_text(encoding="utf-8")

    assert 'from "./ShortHorizonDecisionSection"' in workbench
    assert 'from "./FamilyDirectionSection"' in workbench
    assert 'from "./CalculationScopeSection"' in workbench
    render = workbench[workbench.index("return (") :]
    assert "<PatternHorizonSection" not in render
    assert "<PatternMapSection" not in render
    assert "<AssetPathwaysSection" not in render
    expected = [
        "<MacroContextSection",
        "<ShortHorizonDecisionSection",
        "<FamilyDirectionSection",
        "<CalculationScopeSection",
        "<PatternRibbonSection",
        "<MethodDisclosure",
        "<CalculationTraceDisclosure",
    ]
    offsets = [render.index(token) for token in expected]
    assert offsets == sorted(offsets)


def test_react_copy_keeps_recent_twenty_day_as_observation_only() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    decision = (root / "ShortHorizonDecisionSection.tsx").read_text(
        encoding="utf-8"
    )
    family = (root / "FamilyDirectionSection.tsx").read_text(encoding="utf-8")
    all_source = "\n".join(
        path.read_text(encoding="utf-8") for path in root.glob("*.tsx")
    )

    assert "최근 20거래일" in decision
    assert "핵심 방향 정렬" in family
    assert "확인 신호" in family
    assert "20D는 미래 예측이 아닙니다" not in all_source
