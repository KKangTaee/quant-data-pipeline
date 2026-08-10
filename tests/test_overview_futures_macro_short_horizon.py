from __future__ import annotations

from copy import deepcopy
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
        "as_of_date": "2026-08-07",
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
                "evaluation_count": 325,
                "brier_score": 0.5582,
                "baseline_brier_scores": {
                    "B0_UNCONDITIONAL": 0.5567,
                    "B1_PERSISTENCE": 0.5601,
                },
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
        "as_of_date": "2026-08-07",
        "current_pattern": _pattern(),
        "horizons": horizons,
        "session": {
            "status": "OBSERVED",
            "latest_final_session": "2026-08-07",
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
                "latest_daily_date": "2026-08-07",
            },
            "summary": {"summary": "단기 선물 흐름을 확인합니다."},
        },
        pattern_outlook=_outlook(status),
    )


def _intraday_observation() -> dict[str, Any]:
    pattern = deepcopy(_pattern())
    pattern["as_of_date"] = "2026-08-10"
    pattern["families"]["rate_pressure"].update(
        {"one_day": -0.9, "five_day": -0.7, "twenty_day": 0.7}
    )
    return {
        "status": "INTRADAY_READY",
        "observation_mode": "INTRADAY_PROVISIONAL",
        "pattern": pattern,
        "session_date": "2026-08-10",
        "completed_as_of_date": "2026-08-07",
        "observed_at_utc": "2026-08-10T15:10:00+00:00",
        "observed_at_et": "2026-08-10T11:10:00-04:00",
        "freshness_minutes": 7,
        "available_family_count": 6,
        "required_family_count": 6,
        "fallback_reason": None,
    }


def _intraday_payload(status: str = "NO_EDGE") -> dict[str, Any]:
    from app.web.overview.futures_macro_helpers import (
        build_futures_macro_react_workbench_payload,
    )

    return build_futures_macro_react_workbench_payload(
        {
            "coverage": {
                "standardized_count": 17,
                "symbol_count": 17,
                "latest_daily_date": "2026-08-07",
            },
            "summary": {"summary": "완료 일봉 기준 배경입니다."},
        },
        pattern_outlook=_outlook(status),
        current_observation=_intraday_observation(),
    )

def test_short_horizon_payload_orders_core_four_and_confirmation_two() -> None:
    payload = _payload()
    decision = payload["short_horizon_decision"]

    assert payload["schema_version"] == "futures_macro_react_workbench_v5"
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
        {"key": "1D", "label": "최근 1거래일", "role": "지금 새로 생긴 변화"},
        {"key": "5D", "label": "최근 5거래일", "role": "현재 단기 방향"},
        {"key": "20D", "label": "최근 20거래일", "role": "기존 배경과의 관계"},
    ]
    risk_on = decision["core_directions"][0]
    assert risk_on["one_day"]["label"] == "중립"
    assert risk_on["five_day"]["label"] == "약화"
    assert risk_on["twenty_day"]["label"] == "약화"


def test_hero_names_short_horizon_scope_in_user_language() -> None:
    hero = _payload()["hero"]

    assert hero["kicker"] == "단기 방향 진단"
    assert hero["coverage_label"] == "최근 1 · 5 · 20거래일"


def test_refresh_action_describes_overlap_and_selective_bootstrap() -> None:
    detail = _payload()["command"]["actions"][0]["detail"]

    assert "최근 1년" in detail
    assert "이력이 부족한 종목만" in detail
    assert "10년 1D OHLCV를 다시 수집" not in detail
    helper_source = Path("app/web/overview/futures_macro_helpers.py").read_text(
        encoding="utf-8"
    )
    assert "FUTURES_MACRO_HISTORY_YEARS}년 일봉을 yfinance에서 수집" not in helper_source


def test_no_edge_copy_explains_baseline_without_exposing_internal_label() -> None:
    validation = _payload("NO_EDGE")["short_horizon_decision"][
        "future_five_day_validation"
    ]

    assert validation["status"] == "NO_EDGE"
    assert validation["title"] == "기본 빈도 대비 예측력 확인 안 됨"
    assert validation["question"] == "현재 흐름을 향후 5거래일로 연장할 수 있는가?"
    assert validation["policy"] == "현재 흐름을 미래 5거래일 방향으로 연장하지 않습니다."
    assert validation["episode_count"] == 120
    assert validation["evaluation_count"] == 325
    assert validation["model_brier"] == 0.5582
    assert validation["baseline_brier"] == 0.5567
    assert validation["reference_date"] == "2026-08-07"


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


def test_intraday_payload_uses_current_pattern_but_completed_forecast() -> None:
    payload = _intraday_payload()

    assert payload["hero"]["observation_mode"] == "INTRADAY_PROVISIONAL"
    assert payload["hero"]["as_of_date"] == "2026-08-10"
    assert payload["hero"]["completed_as_of_date"] == "2026-08-07"
    assert payload["hero"]["observed_at_et"] == "2026-08-10T11:10:00-04:00"
    gate = payload["short_horizon_decision"]["future_five_day_validation"]
    assert gate["reference_date"] == "2026-08-07"


def test_current_observation_cards_explain_one_five_twenty_day_roles() -> None:
    cards = _intraday_payload()["short_horizon_decision"]["observation_cards"]

    assert [card["key"] for card in cards] == ["1D", "5D", "20D"]
    assert [card["title"] for card in cards] == [
        "1D · 지금 새로 생긴 변화",
        "5D · 현재 단기 방향",
        "20D · 기존 배경과의 관계",
    ]
    assert "20D" in cards[2]["detail"]


def test_family_states_use_semantic_polarity_labels() -> None:
    rows = _intraday_payload()["short_horizon_decision"]["core_directions"]
    rates = next(row for row in rows if row["key"] == "rate_pressure")

    assert rates["one_day"]["semantic_label"] == "금리 부담 완화"
    assert rates["five_day"]["semantic_label"] == "금리 부담 완화"
    assert rates["twenty_day"]["semantic_label"] == "금리 부담 확대"


def test_completed_fallback_is_explicit_in_hero_provenance() -> None:
    payload = _payload()

    assert payload["hero"]["observation_mode"] == "COMPLETED"
    assert payload["hero"]["completed_as_of_date"] == "2026-08-07"
    assert payload["hero"]["observation_label"] == "마지막 완료 일봉"


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
    assert 'from "./ForecastValidationGate"' in workbench
    assert 'from "./FamilyDirectionSection"' in workbench
    assert 'from "./CalculationScopeSection"' in workbench
    render = workbench[workbench.index("return (") :]
    assert "<PatternHorizonSection" not in render
    assert "<PatternMapSection" not in render
    assert "<AssetPathwaysSection" not in render
    expected = [
        "<MacroContextSection",
        "<ShortHorizonDecisionSection",
        "<ForecastValidationGate",
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


def test_confirmation_signals_use_explicit_recent_window_headers() -> None:
    family = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/"
        "FamilyDirectionSection.tsx"
    ).read_text(encoding="utf-8")

    assert 'firstLabel="신호"' in family
    assert 'oneDayLabel="최근 1D"' in family
    assert 'fiveDayLabel="최근 5D"' in family
    assert 'twentyDayLabel="최근 20D"' in family
    assert "최근 1D · 5D · 20D" not in family


def test_react_separates_current_observation_from_future_validation_gate() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    decision = (root / "ShortHorizonDecisionSection.tsx").read_text(
        encoding="utf-8"
    )
    forecast = (root / "ForecastValidationGate.tsx").read_text(
        encoding="utf-8"
    )

    assert "decision.observation_cards" in decision
    assert "future_five_day_validation" not in decision
    assert "현재 흐름을 향후 5거래일로 연장할 수 있는가?" in forecast
    assert "모델 Brier" in forecast
    assert "기본 빈도 Brier" in forecast
    assert "validation.policy" in forecast


def test_react_header_no_longer_says_active_session_is_excluded() -> None:
    source = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/"
        "MacroContextSection.tsx"
    ).read_text(encoding="utf-8")

    assert "현재 위치와 전망에서 제외했습니다" not in source
    assert "hero.observation_label" in source
    assert "hero.completed_as_of_date" in source


def test_react_family_cells_render_semantic_labels() -> None:
    source = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/"
        "FamilyDirectionSection.tsx"
    ).read_text(encoding="utf-8")

    assert "state.semantic_label" in source
