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


def _completed_fallback_payload() -> dict[str, Any]:
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
        pattern_outlook=_outlook(),
        current_observation={
            "status": "COMPLETED_FALLBACK",
            "observation_mode": "COMPLETED",
            "pattern": _pattern(),
            "session_date": "2026-08-10",
            "completed_as_of_date": "2026-08-07",
            "observed_at_utc": None,
            "observed_at_et": None,
            "freshness_minutes": None,
            "available_family_count": 0,
            "required_family_count": 6,
            "fallback_reason": "insufficient_complete_families",
        },
    )

def test_short_horizon_payload_orders_core_four_and_confirmation_two() -> None:
    payload = _payload()
    decision = payload["short_horizon_decision"]

    assert payload["schema_version"] == "futures_macro_react_workbench_v7"
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
    assert "observation_windows" not in decision
    risk_on = decision["core_directions"][0]
    assert risk_on["one_day"]["label"] == "중립"
    assert risk_on["five_day"]["label"] == "약화"
    assert risk_on["twenty_day"]["label"] == "약화"


def test_hero_names_short_horizon_scope_in_user_language() -> None:
    hero = _payload()["hero"]

    assert hero["kicker"] == "시장 재가격화 레이더"
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


def test_repricing_radar_replaces_future_validation_with_current_market_reading() -> None:
    decision = _payload("NO_EDGE")["short_horizon_decision"]
    radar = decision["market_repricing"]

    assert "future_five_day_validation" not in decision
    assert radar == {
        "status": "MIXED",
        "confidence_label": "해석 충돌",
        "headline": "주가지수 위험선호 약화가 재가격화의 중심입니다.",
        "interpretation": (
            "ES/NQ/YM/RTY 기반 위험선호 약화가 가장 강합니다. "
            "달러 압력 확대와 물가 압력 확대가 같은 방어 방향을 지지하지만, "
            "금리 부담 완화가 반대로 움직여 한 가지 거시 원인으로 확정할 수 없습니다."
        ),
        "supporting_evidence": [
            "위험선호 약화 · ES/NQ/YM/RTY 기반",
            "달러 압력 확대 · 주요 FX 기반",
            "물가 압력 확대 · CL/HG/NG 기반",
        ],
        "counter_evidence": [
            "금리 부담 완화 · ZN/ZB 기반",
            "성장 기대 강화 · RTY/HG/CL/6A 기반",
            "방어 수요 약화 · GC/ZN/ZB/6J 기반",
        ],
        "conditional_scenario": {
            "summary": (
                "위험선호 약화가 이어지면 주가지수와 경기민감 자산의 부담이 "
                "유지될 수 있습니다."
            ),
            "continuation_condition": (
                "1D와 5D에서 위험선호 약화가 함께 유지되고 달러·물가 압력이 "
                "약해지지 않을 때"
            ),
            "invalidation_condition": (
                "1D 위험선호가 강화로 반전하거나 5D 위험선호 약화가 "
                "중립권으로 낮아질 때"
            ),
            "sensitive_assets": ["주가지수", "성장주", "경기민감 자산"],
        },
    }


def test_repricing_radar_reports_low_signal_without_forcing_a_macro_story() -> None:
    payload = _payload()
    pattern = _pattern()
    for family in pattern["families"].values():
        family["one_day"] = 0.1
        family["five_day"] = 0.1
        family["twenty_day"] = 0.1

    from app.web.overview.futures_macro_helpers import (
        _short_horizon_decision_payload,
    )

    decision = _short_horizon_decision_payload(
        payload["calculation_trace"],
        pattern,
        _outlook(),
    )
    radar = decision["market_repricing"]

    assert radar["status"] == "LOW_SIGNAL"
    assert radar["confidence_label"] == "뚜렷한 중심축 없음"
    assert radar["headline"] == "뚜렷한 거시 재가격화가 없습니다."
    assert radar["supporting_evidence"] == []
    assert radar["counter_evidence"] == []
    assert radar["conditional_scenario"]["summary"] == (
        "현재는 특정 시나리오보다 관망이 우선입니다."
    )


def test_repricing_radar_keeps_a_material_one_day_shock_when_five_day_is_neutral() -> None:
    pattern = _pattern()
    for family in pattern["families"].values():
        family["one_day"] = 0.1
        family["five_day"] = 0.1
        family["twenty_day"] = 0.1
    pattern["families"]["rate_pressure"]["one_day"] = 1.4
    pattern["families"]["dollar_pressure"]["one_day"] = -1.0
    pattern["families"]["safe_haven"]["one_day"] = -0.6

    from app.web.overview.futures_macro_helpers import (
        _short_horizon_decision_payload,
    )

    radar = _short_horizon_decision_payload({}, pattern, _outlook())[
        "market_repricing"
    ]

    assert radar["status"] == "NEW_SHOCK"
    assert radar["confidence_label"] == "1D 새 충격"
    assert radar["headline"] == (
        "1D 국채선물 기반 금리 부담 확대가 새로 두드러졌습니다."
    )
    assert radar["interpretation"] == (
        "ZN/ZB 기반 금리 부담 확대가 1D에서 가장 강하지만 아직 5D 핵심 방향으로 "
        "이어지지 않았습니다. 달러 압력 완화가 반대로 움직여 금리 충격 해석은 "
        "초기 단계입니다."
    )
    assert radar["supporting_evidence"] == [
        "금리 부담 확대 · ZN/ZB 기반",
    ]
    assert radar["counter_evidence"] == [
        "달러 압력 완화 · 주요 FX 기반",
        "방어 수요 약화 · GC/ZN/ZB/6J 기반",
    ]


def test_repricing_radar_reports_unavailable_when_core_values_are_missing() -> None:
    pattern = _pattern()
    for family in pattern["families"].values():
        family["one_day"] = None
        family["five_day"] = None
        family["twenty_day"] = None

    from app.web.overview.futures_macro_helpers import (
        _short_horizon_decision_payload,
    )

    radar = _short_horizon_decision_payload({}, pattern, _outlook())[
        "market_repricing"
    ]

    assert radar["status"] == "UNAVAILABLE"
    assert radar["headline"] == "시장 재가격화를 해석할 관측값이 부족합니다."
    assert radar["conditional_scenario"]["sensitive_assets"] == []


def test_intraday_payload_uses_current_pattern_for_repricing_radar() -> None:
    payload = _intraday_payload()

    assert payload["hero"]["observation_mode"] == "INTRADAY_PROVISIONAL"
    assert payload["hero"]["as_of_date"] == "2026-08-10"
    assert payload["hero"]["completed_as_of_date"] == "2026-08-07"
    assert payload["hero"]["observed_at_et"] == "2026-08-10T11:10:00-04:00"
    decision = payload["short_horizon_decision"]
    assert "future_five_day_validation" not in decision
    assert decision["market_repricing"]["headline"] == (
        "주가지수 위험선호 약화가 재가격화의 중심입니다."
    )


def test_observation_cards_report_changes_without_instruction_copy() -> None:
    cards = _intraday_payload()["short_horizon_decision"]["observation_cards"]

    assert [card["key"] for card in cards] == ["1D", "5D", "20D"]
    assert [card["title"] for card in cards] == [
        "1D · 지금 새로 생긴 변화",
        "5D · 현재 단기 방향",
        "20D · 기존 배경과의 관계",
    ]
    assert all("detail" not in card for card in cards)
    assert cards[0]["summary"] == (
        "금리 부담 완화와 달러 압력 확대가 하루 흐름에서도 이어지고 있습니다. "
        "다른 핵심축의 변화는 크지 않아 새로운 방향 전환으로 보기는 어렵습니다."
    )
    assert cards[1]["summary"] == (
        "최근 5거래일에는 위험선호 약화, 금리 부담 완화, "
        "달러 압력 확대와 물가 압력 확대가 함께 나타났지만 서로 가리키는 "
        "방향은 엇갈립니다. 핵심축이 한쪽으로 모이지 않아 전체 단기 방향에는 "
        "뚜렷한 우위가 없습니다."
    )
    assert cards[2]["summary"] == (
        "위험선호 약화와 물가 압력 확대는 최근 20거래일 배경과 "
        "같은 방향으로 이어지고, 금리 부담 완화는 반대로 움직이고 있습니다. "
        "지속과 반전이 함께 나타나 중기 배경과의 관계는 혼재합니다."
    )
    assert "확인합니다" not in str(cards)


def test_single_five_day_axis_explains_why_direction_is_not_aligned() -> None:
    from app.web.overview.futures_macro_helpers import (
        _pattern_core_alignment_summary,
    )

    rows = [
        {
            "key": "risk_on",
            "five_day": {
                "tone": "neutral",
                "semantic_label": "주가지수 위험선호 중립",
                "value": 0.1,
            },
        },
        {
            "key": "rate_pressure",
            "five_day": {
                "tone": "neutral",
                "semantic_label": "금리 부담 중립",
                "value": 0.2,
            },
        },
        {
            "key": "dollar_pressure",
            "five_day": {
                "tone": "negative",
                "semantic_label": "달러 압력 완화",
                "value": -0.8,
            },
        },
        {
            "key": "inflation_pressure",
            "five_day": {
                "tone": "neutral",
                "semantic_label": "물가 압력 중립",
                "value": -0.1,
            },
        },
    ]

    assert _pattern_core_alignment_summary(rows) == (
        "최근 5거래일에는 달러 압력 완화만 뚜렷합니다. "
        "다른 핵심축이 함께 움직이지 않아 전체 단기 방향이 한쪽으로 "
        "정렬됐다고 보기는 어렵습니다."
    )


def test_background_relationship_reports_continuation_and_reversal_together() -> None:
    from app.web.overview.futures_macro_helpers import (
        _pattern_background_relationship_summary,
    )

    rows = deepcopy(_payload()["short_horizon_decision"]["core_directions"])
    rates = next(row for row in rows if row["key"] == "rate_pressure")
    rates["twenty_day"] = {
        "label": "강화",
        "semantic_label": "금리 부담 확대",
        "tone": "positive",
        "value": 0.8,
    }

    summary = _pattern_background_relationship_summary(rows)

    assert summary == (
        "위험선호 약화와 물가 압력 확대는 최근 20거래일 배경과 "
        "같은 방향으로 이어지고, 금리 부담 완화는 반대로 움직이고 있습니다. "
        "지속과 반전이 함께 나타나 중기 배경과의 관계는 혼재합니다."
    )


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


def test_completed_fallback_exposes_latest_available_reason() -> None:
    payload = _completed_fallback_payload()
    hero = payload["hero"]

    assert hero["fallback_reason"] == "insufficient_complete_families"
    assert hero["completed_as_of_date"] == "2026-08-07"
    assert "마지막 완료 일봉" in hero["observation_detail"]

    source = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/"
        "MacroContextSection.tsx"
    ).read_text(encoding="utf-8")
    assert "새 장중 관측이 없어" in source
    assert "hero.evidence.slice(0, 2)" in source
    assert "command.detail" not in source
    assert '["no_active_session", "no_pending_session"]' not in source


def test_futures_header_has_compact_futures_only_layout() -> None:
    style = Path(
        "app/web/streamlit_components/market_research_header/style.css"
    ).read_text(encoding="utf-8")

    assert ".research-header--futures .research-header__grid" in style
    assert ".research-header--futures .research-header__facts" in style
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in style


def test_futures_workbench_mobile_layout_does_not_expand_the_page_width() -> None:
    style = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/style.css"
    ).read_text(encoding="utf-8")

    assert ".fm-workbench > * { min-width: 0; }" in style
    assert "@media (max-width: 480px)" in style
    assert "repeat(3, minmax(58px, 1fr))" in style


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
    assert "아닙니다" in decision["confirmation_summary"]
    assert [item["key"] for item in _payload()["horizons"]] == [
        "current",
        "5D",
        "20D",
    ]


def test_react_default_render_uses_short_horizon_sections_in_order() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    workbench = (root / "FuturesMacroWorkbench.tsx").read_text(encoding="utf-8")

    assert 'from "./ShortHorizonDecisionSection"' in workbench
    assert 'from "./MarketRepricingSection"' in workbench
    assert 'from "./ForecastValidationGate"' not in workbench
    assert 'from "./FamilyDirectionSection"' in workbench
    assert 'from "./CalculationScopeSection"' not in workbench
    assert not (root / "CalculationScopeSection.tsx").exists()
    assert not (root / "ForecastValidationGate.tsx").exists()
    render = workbench[workbench.index("return (") :]
    assert "<PatternHorizonSection" not in render
    assert "<PatternMapSection" not in render
    assert "<AssetPathwaysSection" not in render
    expected = [
        "<MacroContextSection",
        "<ShortHorizonDecisionSection",
        "<MarketRepricingSection",
        "<FamilyDirectionSection",
        "<PatternRibbonSection",
        "<MethodDisclosure",
        "<CalculationTraceDisclosure",
    ]
    offsets = [render.index(token) for token in expected]
    assert offsets == sorted(offsets)
    assert "scope={payload.short_horizon_decision.calculation_scope}" in render


def test_short_horizon_react_renders_results_without_reading_guide() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    decision = (root / "ShortHorizonDecisionSection.tsx").read_text(
        encoding="utf-8"
    )
    method = (root / "MethodDisclosure.tsx").read_text(encoding="utf-8")
    repricing = (root / "MarketRepricingSection.tsx").read_text(encoding="utf-8")

    assert "decision.observation_windows" not in decision
    assert "card.detail" not in decision
    assert "순서로 읽습니다" not in decision
    assert "시장 재가격화 흐름" in decision
    assert "유력한 해석" in repricing
    assert "반대 근거" in repricing
    assert "조건부 시나리오" in repricing
    assert "지속 조건" in repricing
    assert "무효화 조건" in repricing
    assert "계산 범위" in method
    assert "scope.collected_count" in method
    assert "Brier" not in method
    assert "probability_status" not in method
    assert "horizons" not in method


def test_react_copy_keeps_recent_twenty_day_as_observation_only() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    decision = (root / "ShortHorizonDecisionSection.tsx").read_text(
        encoding="utf-8"
    )
    family = (root / "FamilyDirectionSection.tsx").read_text(encoding="utf-8")
    all_source = "\n".join(
        path.read_text(encoding="utf-8") for path in root.glob("*.tsx")
    )

    assert "decision.observation_cards" in decision
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


def test_react_removes_future_validation_gate_from_the_product_surface() -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    python_source = Path("app/web/overview/futures_macro_helpers.py").read_text(
        encoding="utf-8"
    )
    decision = (root / "ShortHorizonDecisionSection.tsx").read_text(
        encoding="utf-8"
    )
    workbench = (root / "FuturesMacroWorkbench.tsx").read_text(encoding="utf-8")
    all_source = "\n".join(
        path.read_text(encoding="utf-8") for path in root.glob("*.tsx")
    )

    assert "decision.observation_cards" in decision
    assert "future_five_day_validation" not in decision
    assert "ForecastValidationGate" not in workbench
    assert "현재 흐름을 향후 5거래일로 연장할 수 있는가?" not in all_source
    assert "현재 흐름을 향후 5거래일로 연장할 수 있는가?" not in python_source
    assert "기본 대비 Brier" not in all_source


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
