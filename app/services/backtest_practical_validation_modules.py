from __future__ import annotations

from typing import Any

from app.services.backtest_practical_validation_board_registry import (
    build_validation_board_map,
    evidence_boards_for_module,
)


BLOCKING_STATUSES = {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
REVIEW_STATUSES = {"REVIEW"}
PASS_STATUSES = {"PASS", "READY"}
STATUS_RANK = {
    "BLOCKED": 60,
    "NEEDS_INPUT": 50,
    "NOT_RUN": 40,
    "REVIEW": 30,
    "PASS": 20,
    "READY": 20,
    "INFO": 10,
    "NOT_APPLICABLE": 0,
}

ETF_STRATEGY_KEYS = {
    "equal_weight",
    "gtaa",
    "global_relative_strength",
    "dual_momentum",
    "risk_parity_trend",
    "weighted_portfolio",
}
TACTICAL_STRATEGY_KEYS = {
    "gtaa",
    "global_relative_strength",
    "dual_momentum",
    "risk_parity_trend",
}
FACTOR_KEYWORDS = ("quality", "value", "snapshot", "strict", "factor")
LEVERAGED_OR_INVERSE_SYMBOLS = {
    "TQQQ",
    "SQQQ",
    "UPRO",
    "SPXU",
    "SPXL",
    "TNA",
    "TZA",
    "TMF",
    "TBT",
    "UVXY",
    "SVXY",
}

MODULE_TYPE_LABELS = {
    "REQUIRED": "Required",
    "CONDITIONAL": "Conditional",
    "REFERENCE": "Reference",
}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, str):
        return [item.strip() for item in value.replace("\n", ",").split(",") if item.strip()]
    return [value]


def _status(value: Any) -> str:
    normalized = str(value or "NOT_RUN").strip().upper()
    if normalized in {"TRUE"}:
        return "PASS"
    if normalized in {"FALSE"}:
        return "NEEDS_INPUT"
    return normalized if normalized in STATUS_RANK else "NOT_RUN"


def _worst_status(values: list[Any], *, default: str = "NOT_RUN") -> str:
    statuses = [_status(value) for value in values if value is not None]
    if not statuses:
        return default
    return max(statuses, key=lambda item: STATUS_RANK.get(item, STATUS_RANK["NOT_RUN"]))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _component_settings(component: dict[str, Any]) -> dict[str, Any]:
    replay_contract = dict(component.get("replay_contract") or {})
    settings = dict(replay_contract.get("settings_snapshot") or {})
    if settings:
        return settings
    return dict(replay_contract.get("contract") or {})


def _component_symbols(component: dict[str, Any]) -> list[str]:
    symbols: list[str] = []
    for value in _as_list(component.get("universe")):
        text = str(value or "").strip().upper()
        if text:
            symbols.append(text)
    settings = _component_settings(component)
    for value in _as_list(settings.get("tickers")):
        text = str(value or "").strip().upper()
        if text:
            symbols.append(text)
    return list(dict.fromkeys(symbols))


def _strategy_key(component: dict[str, Any]) -> str:
    return str(component.get("strategy_key") or component.get("strategy_family") or "").strip().lower()


def infer_validation_source_traits(source: dict[str, Any]) -> dict[str, Any]:
    """Infer stable traits that decide which validation modules apply."""

    source_row = dict(source or {})
    construction = dict(source_row.get("construction") or {})
    components = [dict(item or {}) for item in list(source_row.get("components") or [])]
    active_components = [
        component for component in components if _safe_float(component.get("target_weight")) > 0.0
    ]
    strategy_keys = sorted({key for key in (_strategy_key(component) for component in active_components) if key})
    symbols = sorted({symbol for component in active_components for symbol in _component_symbols(component)})
    source_kind = str(source_row.get("source_kind") or "").strip().lower()
    construction_source = str(construction.get("source") or "").strip().lower()
    weighted_mix = (
        len(active_components) > 1
        or source_kind in {"weighted_portfolio_mix", "saved_portfolio_mix"}
        or construction_source in {"weighted_mix", "saved_mix"}
    )
    single_component = len(active_components) == 1
    factor_equity = any(any(keyword in key for keyword in FACTOR_KEYWORDS) for key in strategy_keys)
    etf_like = bool(symbols) and not factor_equity and (
        any(key in ETF_STRATEGY_KEYS for key in strategy_keys)
        or source_kind in {"weighted_portfolio_mix", "saved_portfolio_mix", "latest_backtest_run"}
    )
    tactical = any(key in TACTICAL_STRATEGY_KEYS for key in strategy_keys)
    high_turnover = False
    for component in active_components:
        settings = _component_settings(component)
        interval = _safe_float(settings.get("interval") or settings.get("rebalance_interval"), default=999.0)
        cadence = str(settings.get("rebalance_freq") or settings.get("factor_freq") or "").lower()
        if interval <= 3 or cadence in {"d", "daily", "w", "weekly", "m", "monthly", "month_end"}:
            high_turnover = True
    leveraged_or_inverse = any(symbol in LEVERAGED_OR_INVERSE_SYMBOLS for symbol in symbols)
    target_weight_total = round(sum(_safe_float(component.get("target_weight")) for component in active_components), 4)
    max_component_weight = max([_safe_float(component.get("target_weight")) for component in active_components], default=0.0)
    return {
        "source_kind": source_kind or "-",
        "construction_source": construction_source or "-",
        "active_component_count": len(active_components),
        "strategy_keys": strategy_keys,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "target_weight_total": target_weight_total,
        "max_component_weight": max_component_weight,
        "is_single_component": single_component,
        "is_weighted_mix": weighted_mix,
        "is_etf_like": etf_like,
        "is_factor_equity": factor_equity,
        "is_tactical": tactical,
        "is_high_turnover": high_turnover,
        "has_leveraged_or_inverse_symbols": leveraged_or_inverse,
    }


def _check_status(row: dict[str, Any]) -> str:
    if bool(row.get("Ready")):
        return "PASS"
    current = str(row.get("Current") or "").upper()
    if "BLOCK" in current:
        return "BLOCKED"
    if "NOT_RUN" in current:
        return "NOT_RUN"
    return "NEEDS_INPUT"


def _check_map(checks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("Criteria") or "").strip(): dict(row or {}) for row in checks}


def _diagnostic_map(diagnostics: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("domain") or "").strip(): dict(row or {}) for row in diagnostics}


def _row_statuses(rows: list[dict[str, Any]], *, exclude: set[str] | None = None) -> list[str]:
    excluded = exclude or set()
    statuses: list[str] = []
    for row in rows:
        criteria = str(row.get("Criteria") or row.get("Module") or "").strip()
        if criteria in excluded:
            continue
        statuses.append(_status(row.get("Status")))
    return statuses


def _module(
    *,
    module_id: str,
    label: str,
    group: str,
    status: str,
    requirement: str,
    stage_owner: str,
    applies: bool = True,
    reason: str = "",
    next_action: str = "",
    evidence: str = "",
    profile_effect: str = "-",
    applicability_reason: str = "",
    resolution_surface: str = "",
    resolution_action: str = "",
) -> dict[str, Any]:
    normalized_status = _status(status) if applies else "NOT_APPLICABLE"
    requirement_text = str(requirement or "").upper()
    return {
        "module_id": module_id,
        "label": label,
        "group": group,
        "status": normalized_status,
        "requirement": requirement,
        "module_type": MODULE_TYPE_LABELS.get(requirement_text, requirement_text or "-"),
        "stage_owner": stage_owner,
        "applies": bool(applies),
        "applicability_reason": applicability_reason or (
            "현재 후보에 적용됩니다." if applies else "현재 후보 특성상 이 검증은 적용하지 않습니다."
        ),
        "reason": reason,
        "next_action": next_action,
        "resolution_surface": resolution_surface or "-",
        "resolution_action": resolution_action or next_action or "-",
        "evidence": evidence,
        "profile_effect": profile_effect or "-",
    }


def _module_blocks_gate(module: dict[str, Any]) -> bool:
    if not module.get("applies"):
        return False
    status = _status(module.get("status"))
    requirement = str(module.get("requirement") or "").upper()
    if requirement == "REQUIRED":
        return status in BLOCKING_STATUSES
    if requirement == "CONDITIONAL":
        return status == "BLOCKED"
    return False


def _module_needs_review(module: dict[str, Any]) -> bool:
    if not module.get("applies"):
        return False
    return _status(module.get("status")) in REVIEW_STATUSES


def _module_gate_effect(module: dict[str, Any]) -> str:
    if not module.get("applies"):
        return "Not applicable"
    if _module_blocks_gate(module):
        return "Blocks Final Review"
    if _module_needs_review(module):
        return "Final Review review"
    requirement = str(module.get("requirement") or "").upper()
    if requirement == "REFERENCE":
        return "Reference only"
    return "Ready"


def _module_gate_reason(module: dict[str, Any]) -> str:
    if not module.get("applies"):
        return str(module.get("applicability_reason") or "후보 특성상 이 검증은 적용하지 않습니다.")
    status = _status(module.get("status"))
    if _module_blocks_gate(module):
        return f"Final Review 이동 전 보강 필요: {module.get('next_action') or module.get('reason') or status}"
    if _module_needs_review(module):
        return f"이동 가능하지만 Final Review 판단 근거로 확인: {module.get('next_action') or module.get('reason') or status}"
    requirement = str(module.get("requirement") or "").upper()
    if requirement == "REFERENCE":
        return "Practical Validation 이동 차단 기준은 아니며 후속 화면의 참고 근거입니다."
    return "필수 이동 기준을 충족했습니다."


def _module_gate_row(module: dict[str, Any]) -> dict[str, Any]:
    return {
        "module_id": module.get("module_id"),
        "label": module.get("label"),
        "status": module.get("status"),
        "gate_effect": module.get("gate_effect") or _module_gate_effect(module),
        "gate_reason": module.get("gate_reason") or _module_gate_reason(module),
        "resolution_surface": module.get("resolution_surface"),
        "resolution_action": module.get("resolution_action") or module.get("next_action"),
        "reason": module.get("reason"),
        "next_action": module.get("next_action"),
    }


def _module_display_rows(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Group": module.get("group"),
            "Module Type": module.get("module_type"),
            "Module": module.get("label"),
            "Applies": "Yes" if module.get("applies") else "No",
            "Applicability": module.get("applicability_reason"),
            "Requirement": module.get("requirement"),
            "Status": module.get("status"),
            "Gate Effect": module.get("gate_effect") or _module_gate_effect(module),
            "Gate Reason": module.get("gate_reason") or _module_gate_reason(module),
            "Evidence Boards": " / ".join(
                str(board.get("label") or "")
                for board in list(module.get("evidence_boards") or [])
                if board.get("label")
            )
            or "-",
            "Fix Location": module.get("resolution_surface"),
            "Fix Action": module.get("resolution_action"),
            "Reason": module.get("reason"),
            "Next Action": module.get("next_action"),
            "Profile / Traits": module.get("profile_effect"),
        }
        for module in modules
    ]


def build_validation_module_plan(
    *,
    source: dict[str, Any],
    validation_profile: dict[str, Any],
    checks: list[dict[str, Any]],
    diagnostics: list[dict[str, Any]],
    validation_efficacy_rows: list[dict[str, Any]],
    data_coverage_rows: list[dict[str, Any]],
    construction_risk_rows: list[dict[str, Any]],
    risk_contribution_rows: list[dict[str, Any]],
    component_role_weight_rows: list[dict[str, Any]],
    backtest_realism_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the module-level Practical Validation plan and Final Review gate."""

    traits = infer_validation_source_traits(source)
    profile = dict(validation_profile or {})
    profile_id = str(profile.get("profile_id") or "balanced_core")
    profile_label = str(profile.get("profile_label") or profile_id)
    check_rows = _check_map(checks)
    diagnostic_rows = _diagnostic_map(diagnostics)

    def check_status(name: str) -> str:
        row = check_rows.get(name)
        return _check_status(row) if row else "NOT_RUN"

    def diagnostic_status(domain: str) -> str:
        return _status(dict(diagnostic_rows.get(domain) or {}).get("status"))

    source_integrity_status = _worst_status(
        [
            check_status("Selection source"),
            check_status("Active components"),
            check_status("Target weight total"),
            check_status("Data Trust"),
            check_status("Execution boundary"),
            check_status("Curve evidence"),
        ]
    )
    latest_replay_status = _worst_status(
        [check_status("Runtime recheck"), check_status("Runtime period coverage")]
    )
    benchmark_status = check_status("Benchmark parity")
    validation_efficacy_status = _worst_status(
        _row_statuses(
            validation_efficacy_rows,
            exclude={"Runtime replay evidence", "Runtime period coverage"},
        )
    )
    data_coverage_status = _worst_status(_row_statuses(data_coverage_rows))
    construction_status = _worst_status(_row_statuses(construction_risk_rows))
    realism_status = _worst_status(
        _row_statuses(backtest_realism_rows, exclude={"Tax / account scope"})
    )
    robustness_status = _worst_status(
        [
            diagnostic_status("stress_scenario_diagnostics"),
            diagnostic_status("robustness_sensitivity_overfit"),
        ]
    )
    provider_status = _worst_status(
        [
            check_status("Provider coverage"),
            diagnostic_status("asset_allocation_fit"),
            diagnostic_status("concentration_overlap_exposure"),
            diagnostic_status("operability_cost_liquidity"),
        ]
    )
    leverage_status = diagnostic_status("leveraged_inverse_etf_suitability")
    risk_contribution_status = _worst_status(_row_statuses(risk_contribution_rows))
    role_weight_status = _worst_status(_row_statuses(component_role_weight_rows))
    macro_status = _worst_status(
        [diagnostic_status("regime_macro_suitability"), diagnostic_status("sentiment_risk_on_off_overlay")]
    )
    monitoring_status = diagnostic_status("monitoring_baseline_seed")
    tax_scope_status = next(
        (_status(row.get("Status")) for row in backtest_realism_rows if row.get("Criteria") == "Tax / account scope"),
        "NOT_RUN",
    )

    modules = [
        _module(
            module_id="source_integrity",
            label="Source Integrity",
            group="Required for Final Review",
            status=source_integrity_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="Backtest Analysis에서 넘어온 source가 식별 가능하고 active component, target weight, Data Trust, execution boundary, curve evidence를 갖춘 검증 가능한 후보인지 확인합니다.",
            next_action="source 자격이 부족하면 Backtest Analysis에서 source를 다시 구성하거나 handoff evidence를 보강합니다.",
            profile_effect=profile_label,
            resolution_surface="1. 선택 후보 확인 / Backtest Analysis handoff",
            resolution_action="source id, active component, target weight, Data Trust, curve evidence를 확인하고 부족하면 Backtest Analysis에서 후보를 다시 보냅니다.",
        ),
        _module(
            module_id="latest_replay",
            label="Latest Runtime Replay",
            group="Required for Final Review",
            status=latest_replay_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="저장 당시 성과가 아니라 현재 DB 최신 시장일까지 같은 전략이 재현되는지 확인합니다.",
            next_action="Practical Validation의 전략 재검증을 실행하고 runtime period coverage를 확인합니다.",
            profile_effect="all profiles require current replay evidence",
            resolution_surface="3. 최신 데이터 기준 전략 재검증",
            resolution_action="`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
        ),
        _module(
            module_id="benchmark_parity",
            label="Benchmark / Comparator Parity",
            group="Required for Final Review",
            status=benchmark_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="후보와 benchmark, cash, simple baseline, custom comparator 같은 비교 기준이 같은 기간 / frequency / coverage로 비교되는지 확인합니다.",
            next_action="비교 기준 curve coverage가 부족하면 source comparator나 replay evidence를 보강합니다.",
            profile_effect=profile_label,
            resolution_surface="Input Evidence / Curve / Recheck Evidence",
            resolution_action="benchmark 또는 comparator curve가 후보와 같은 기간 / coverage / frequency로 만들어졌는지 확인합니다.",
        ),
        _module(
            module_id="validation_efficacy",
            label="Validation Efficacy",
            group="Required for Final Review",
            status=validation_efficacy_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="walk-forward, OOS, regime, PIT, survivorship 등 검증 방식이 후보 판단에 충분한 효력을 갖는지 봅니다.",
            next_action="검증 효력의 NEEDS_INPUT row를 보강하고 REVIEW row는 Final Review 판단 근거로 넘깁니다.",
            profile_effect=profile_label,
            resolution_surface="Validation Efficacy Audit",
            resolution_action="NEEDS_INPUT row를 확인해 walk-forward / OOS / regime / PIT / survivorship evidence 부족분을 보강합니다.",
        ),
        _module(
            module_id="data_coverage",
            label="Data Coverage",
            group="Required for Final Review",
            status=data_coverage_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="최신 가격, provider freshness, PIT window, universe / survivorship coverage가 Practical Validation 판단에 충분한지 확인합니다.",
            next_action="가격 / provider / lifecycle / replay coverage 부족분을 보강합니다.",
            profile_effect=profile_label,
            resolution_surface="Data Coverage Audit / Provider Data Gaps",
            resolution_action="가격 window, provider freshness, lifecycle / survivorship row 중 NEEDS_INPUT 항목을 확인하고 provider gap 수집 또는 데이터 보강을 진행합니다.",
        ),
        _module(
            module_id="construction_risk",
            label="Construction Risk",
            group="Required for Final Review",
            status=construction_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="단일 후보와 mix 후보 모두 실제 보유 관점의 비중 집중, look-through, top holding, overlap, asset bucket exposure를 확인합니다.",
            next_action="REVIEW row는 Final Review에서 선택 근거 또는 보류 근거로 확인합니다.",
            profile_effect=f"max weight {traits.get('max_component_weight')}%",
            resolution_surface="Construction Risk Audit / Look-through Exposure Board",
            resolution_action="비중 집중, holdings / exposure coverage, top holding, overlap, unknown exposure row를 확인합니다.",
        ),
        _module(
            module_id="backtest_realism",
            label="Backtest Realism",
            group="Required for Final Review",
            status=realism_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="비용, turnover, liquidity, net performance, rebalance timing이 실전 해석에 충분한지 확인합니다.",
            next_action="비용 / turnover / 유동성 / net curve evidence가 부족하면 보강하고 assumption-only row는 Final Review review 근거로 넘깁니다.",
            profile_effect=profile_label,
            resolution_surface="Backtest Realism Audit",
            resolution_action="cost / turnover / liquidity / net performance / rebalance timing row 중 blocker를 보강합니다.",
        ),
        _module(
            module_id="stress_robustness",
            label="Stress / Robustness",
            group="Required for Final Review",
            status=robustness_status,
            requirement="REQUIRED",
            stage_owner="practical_validation",
            reason="최소 실전 stress window, rolling, sensitivity, overfit warning 근거가 있는지 확인합니다.",
            next_action="최소 stress / rolling / sensitivity 근거가 부족하면 보강하고 고급 parameter perturbation은 REVIEW 또는 후속 검증으로 남깁니다.",
            profile_effect="stricter for defensive / tactical profiles",
            resolution_surface="Robustness Lab",
            resolution_action="stress, rolling, sensitivity, overfit summary에서 NOT_RUN / NEEDS_INPUT row를 확인합니다.",
        ),
        _module(
            module_id="provider_investability",
            label="ETF Provider Investability",
            group="Conditional / Strategy-specific",
            status=provider_status,
            requirement="CONDITIONAL",
            stage_owner="practical_validation",
            applies=bool(traits.get("is_etf_like")),
            reason="ETF-like source에서 운용성, holdings, exposure, provider freshness를 확인합니다.",
            next_action="ETF source이면 provider gap 수집을 먼저 실행합니다.",
            profile_effect="ETF-like source" if traits.get("is_etf_like") else "not ETF-like",
            applicability_reason=(
                "ETF-like source이므로 provider 운용성 / holdings / exposure를 확인합니다."
                if traits.get("is_etf_like")
                else "ETF-like source가 아니므로 provider 전용 검증은 적용하지 않습니다."
            ),
            resolution_surface="Provider Coverage / Provider Data Gaps",
            resolution_action="ETF provider operability / holdings / exposure gap을 확인하고 수집 가능한 부족분을 보강합니다.",
        ),
        _module(
            module_id="leverage_inverse",
            label="Leveraged / Inverse Suitability",
            group="Conditional / Strategy-specific",
            status=leverage_status,
            requirement="CONDITIONAL",
            stage_owner="practical_validation",
            applies=bool(traits.get("has_leveraged_or_inverse_symbols")),
            reason="레버리지 / 인버스 노출이 profile의 복잡도 허용 범위와 맞는지 확인합니다.",
            next_action="노출이 있으면 목적, 보유기간, 손실 감내 기준을 Final Review에 남깁니다.",
            profile_effect="leveraged/inverse symbols detected"
            if traits.get("has_leveraged_or_inverse_symbols")
            else "no leveraged/inverse symbols",
            applicability_reason=(
                "레버리지 / 인버스 ticker가 포함되어 suitability 검증을 적용합니다."
                if traits.get("has_leveraged_or_inverse_symbols")
                else "현재 universe에 레버리지 / 인버스 ticker가 없어 이 조건부 검증은 적용하지 않습니다."
            ),
            resolution_surface="Practical Diagnostics / Final Review",
            resolution_action="레버리지 / 인버스 노출이 있으면 목적, 보유기간, 손실 감내 기준을 Final Review 판단 근거로 남깁니다.",
        ),
        _module(
            module_id="risk_contribution",
            label="Risk Contribution",
            group="Conditional / Strategy-specific",
            status=risk_contribution_status,
            requirement="CONDITIONAL",
            stage_owner="practical_validation",
            applies=bool(traits.get("is_weighted_mix")),
            reason="여러 component mix에서 correlation, risk contribution, drop-one dependency를 확인합니다.",
            next_action="single component 후보에는 적용하지 않고, weighted mix에서 component return matrix를 보강합니다.",
            profile_effect="weighted mix" if traits.get("is_weighted_mix") else "single component",
            applicability_reason=(
                "weighted mix 후보이므로 component별 위험 기여를 확인합니다."
                if traits.get("is_weighted_mix")
                else "single component 후보이므로 component 간 risk contribution 검증은 적용하지 않습니다."
            ),
            resolution_surface="Risk Contribution Audit",
            resolution_action="weighted mix의 component return matrix, correlation, risk contribution, drop-one dependency row를 확인합니다.",
        ),
        _module(
            module_id="component_role_weight",
            label="Component Role / Weight",
            group="Conditional / Strategy-specific",
            status=role_weight_status,
            requirement="CONDITIONAL",
            stage_owner="practical_validation",
            applies=bool(traits.get("is_weighted_mix")),
            reason="여러 component mix에서 role, target weight, weight reason coverage를 확인합니다.",
            next_action="single component 후보는 Final Review에서 core role로 해석합니다.",
            profile_effect="weighted mix" if traits.get("is_weighted_mix") else "single component",
            applicability_reason=(
                "weighted mix 후보이므로 component role / target weight 근거를 확인합니다."
                if traits.get("is_weighted_mix")
                else "single component 후보이므로 mix role / weight 검증은 적용하지 않습니다."
            ),
            resolution_surface="Component Role / Weight Audit",
            resolution_action="weighted mix의 role source, target weight, profile intent, weight rationale row를 확인합니다.",
        ),
        _module(
            module_id="macro_regime",
            label="Macro / Regime Fit",
            group="Conditional / Strategy-specific",
            status=macro_status,
            requirement="CONDITIONAL",
            stage_owner="practical_validation",
            applies=bool(traits.get("is_tactical") or profile_id == "hedged_tactical"),
            reason="전술 / 헤지형 source에서 macro regime과 risk-on/off context를 확인합니다.",
            next_action="전술형이면 FRED macro snapshot과 historical regime split을 함께 확인합니다.",
            profile_effect="tactical source" if traits.get("is_tactical") else profile_label,
            applicability_reason=(
                "전술형 source 또는 전술 / 헤지 profile이므로 macro / regime fit을 확인합니다."
                if traits.get("is_tactical") or profile_id == "hedged_tactical"
                else "전술형 source가 아니므로 macro / regime 조건부 검증은 적용하지 않습니다."
            ),
            resolution_surface="Practical Diagnostics / Macro / Regime",
            resolution_action="macro regime, risk-on/off context, FRED snapshot, regime split evidence를 확인합니다.",
        ),
        _module(
            module_id="monitoring_baseline",
            label="Monitoring Baseline",
            group="Downstream Reference",
            status=monitoring_status,
            requirement="REFERENCE",
            stage_owner="selected_dashboard",
            reason="선정 이후 recheck / monitoring seed를 구성합니다.",
            next_action="Final Review 이후 Selected Dashboard에서 운영 확인 근거로 사용합니다.",
            profile_effect="downstream",
            resolution_surface="Selected Portfolio Dashboard",
            resolution_action="Final Review 이후 recheck / monitoring baseline으로 확인합니다.",
        ),
        _module(
            module_id="tax_account_scope",
            label="Tax / Account Scope",
            group="Downstream Reference",
            status=tax_scope_status,
            requirement="REFERENCE",
            stage_owner="final_review",
            reason="세금, 계좌 유형, 최소 주문 단위는 Stage 2 계산이 아니라 최종 판단 메모 성격입니다.",
            next_action="Final Review에서 선택 / 보류 사유로 남깁니다.",
            profile_effect="final review",
            resolution_surface="Final Review",
            resolution_action="세금, 계좌 유형, 주문 단위는 최종 판단의 보류 / 선택 사유로 남깁니다.",
        ),
    ]

    for module in modules:
        module["gate_effect"] = _module_gate_effect(module)
        module["gate_reason"] = _module_gate_reason(module)
        module["evidence_boards"] = evidence_boards_for_module(str(module.get("module_id") or ""))
        module["evidence_board_labels"] = [
            board.get("label")
            for board in list(module.get("evidence_boards") or [])
            if board.get("label")
        ]

    blockers = [module for module in modules if _module_blocks_gate(module)]
    review_modules = [module for module in modules if _module_needs_review(module)]
    required_modules = [module for module in modules if module.get("requirement") == "REQUIRED"]
    applicable_modules = [module for module in modules if module.get("applies")]
    status_counts: dict[str, int] = {}
    for module in applicable_modules:
        status = _status(module.get("status"))
        status_counts[status] = status_counts.get(status, 0) + 1

    if blockers:
        gate_route = "BLOCKED_FOR_FINAL_REVIEW"
        gate_verdict = "필수 검증 모듈에 보강이 필요한 항목이 있어 Final Review 이동을 막습니다."
        next_action = "필수 모듈의 BLOCKED / NEEDS_INPUT / NOT_RUN 항목을 먼저 해결합니다."
    elif review_modules:
        gate_route = "READY_WITH_REVIEW"
        gate_verdict = "Final Review 이동 가능하지만 REVIEW 항목을 최종 판단 근거로 확인해야 합니다."
        next_action = "검증 결과를 저장하고 Final Review에서 보강 필요 상태와 최종 선정 가능 여부를 확인합니다."
    else:
        gate_route = "READY_FOR_FINAL_REVIEW"
        gate_verdict = "필수 검증 모듈이 통과되어 Final Review로 이동할 수 있습니다."
        next_action = "검증 결과를 저장하고 Final Review에서 최종 후보 선정 저장을 진행합니다."

    board_map = build_validation_board_map(modules=modules, source_traits=traits)

    return {
        "source_traits": traits,
        "modules": modules,
        "module_display_rows": _module_display_rows(modules),
        "board_map": board_map,
        "board_display_rows": list(board_map.get("board_rows") or []),
        "applied_board_display_rows": list(board_map.get("applied_board_rows") or []),
        "not_applicable_board_display_rows": list(board_map.get("not_applicable_board_rows") or []),
        "board_summary": dict(board_map.get("summary") or {}),
        "summary": {
            "applicable": len(applicable_modules),
            "required": len([module for module in required_modules if module.get("applies")]),
            "conditional": len([module for module in modules if module.get("requirement") == "CONDITIONAL" and module.get("applies")]),
            "reference": len([module for module in modules if module.get("requirement") == "REFERENCE" and module.get("applies")]),
            "status_counts": status_counts,
        },
        "final_review_gate": {
            "route": gate_route,
            "can_save_and_move": not blockers,
            "verdict": gate_verdict,
            "next_action": next_action,
            "blocking_modules": [
                _module_gate_row(module)
                for module in blockers
            ],
            "review_modules": [
                _module_gate_row(module)
                for module in review_modules
            ],
        },
    }


__all__ = [
    "BLOCKING_STATUSES",
    "build_validation_module_plan",
    "infer_validation_source_traits",
]
