from __future__ import annotations

from typing import Any


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

MODULE_TYPE_LABELS = {
    "REQUIRED": "Required",
    "CONDITIONAL": "Conditional",
    "REFERENCE": "Reference",
}

BOARD_SPECS = [
    {
        "board_id": "final_review_gate",
        "label": "Final Review Readiness Preview",
        "board_type": "Readiness Preview",
        "surface": "Practical Validation",
        "module_ids": [
            "source_integrity",
            "latest_replay",
            "benchmark_parity",
            "validation_efficacy",
            "data_coverage",
            "construction_risk",
            "backtest_realism",
            "stress_robustness",
            "selected_route_preflight",
        ],
        "primary_module_ids": [],
        "applies_when": "always",
        "role": "Final Review 이동 전 먼저 해결할 evidence gap과 준비 상태를 요약합니다.",
    },
    {
        "board_id": "input_evidence",
        "label": "Input Evidence",
        "board_type": "Shared Input",
        "surface": "Practical Validation",
        "module_ids": [
            "source_integrity",
            "latest_replay",
            "benchmark_parity",
            "provider_investability",
        ],
        "primary_module_ids": ["source_integrity", "latest_replay", "benchmark_parity"],
        "applies_when": "always",
        "role": "source 자격, runtime replay, comparator parity 같은 공통 입력 근거를 보여줍니다.",
    },
    {
        "board_id": "validation_efficacy_audit",
        "label": "Validation Method Strength",
        "board_type": "Evidence Board",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["validation_efficacy"],
        "primary_module_ids": ["validation_efficacy"],
        "role": "walk-forward, OOS, regime split 근거가 충분한지 확인합니다.",
    },
    {
        "board_id": "data_coverage_audit",
        "label": "Data Coverage Audit",
        "board_type": "Evidence Board",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["data_coverage"],
        "primary_module_ids": ["data_coverage"],
        "role": "가격, provider freshness, PIT window, universe / lifecycle coverage를 확인합니다.",
    },
    {
        "board_id": "construction_risk_audit",
        "label": "Construction Risk Audit",
        "board_type": "Evidence Board",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["construction_risk", "provider_investability"],
        "primary_module_ids": ["construction_risk"],
        "role": "비중 집중, look-through, top holding, overlap, asset exposure를 확인합니다.",
    },
    {
        "board_id": "risk_contribution_audit",
        "label": "Risk Contribution Audit",
        "board_type": "Conditional Evidence",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["risk_contribution"],
        "primary_module_ids": ["risk_contribution"],
        "role": "여러 component mix에서 correlation, risk contribution, drop-one dependency를 확인합니다.",
    },
    {
        "board_id": "component_role_weight_audit",
        "label": "Component Role / Weight Audit",
        "board_type": "Conditional Evidence",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["component_role_weight"],
        "primary_module_ids": ["component_role_weight"],
        "role": "여러 component mix에서 role, target weight, weight rationale을 확인합니다.",
    },
    {
        "board_id": "backtest_realism_audit",
        "label": "Backtest Realism Audit",
        "board_type": "Evidence Board",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["backtest_realism", "tax_account_scope"],
        "primary_module_ids": ["backtest_realism"],
        "role": "비용, turnover, liquidity, net performance, rebalance timing을 확인합니다.",
    },
    {
        "board_id": "practical_diagnostics",
        "label": "Practical Diagnostics",
        "board_type": "Diagnostic Board",
        "surface": "Practical Validation",
        "module_ids": [
            "stress_robustness",
            "provider_investability",
            "leverage_inverse",
            "macro_regime",
            "monitoring_baseline",
        ],
        "primary_module_ids": ["stress_robustness", "provider_investability", "macro_regime"],
        "role": "profile과 source traits에 따라 실전성 진단 row를 compact하게 보여줍니다.",
    },
    {
        "board_id": "provider_coverage",
        "label": "Provider Coverage",
        "board_type": "Conditional Evidence",
        "surface": "Practical Validation",
        "module_ids": ["provider_investability", "data_coverage", "backtest_realism"],
        "primary_module_ids": ["provider_investability"],
        "role": "ETF-like source에서 provider / macro snapshot 연결 상태를 보여줍니다.",
    },
    {
        "board_id": "look_through_exposure",
        "label": "Look-through Exposure Board",
        "board_type": "Conditional Evidence",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["provider_investability", "construction_risk"],
        "primary_module_ids": ["provider_investability"],
        "role": "ETF holdings / exposure를 portfolio weight 기준으로 접어 보여줍니다.",
    },
    {
        "board_id": "provider_data_gaps",
        "label": "Provider Data Gaps",
        "board_type": "Action Board",
        "surface": "Practical Validation",
        "module_ids": ["provider_investability", "data_coverage"],
        "primary_module_ids": ["provider_investability"],
        "role": "ETF provider snapshot 부족분과 이 화면에서 실행 가능한 보강 작업을 보여줍니다.",
    },
    {
        "board_id": "robustness_lab",
        "label": "Robustness Lab",
        "board_type": "Evidence Board",
        "surface": "Practical Validation / Final Review",
        "module_ids": ["stress_robustness"],
        "primary_module_ids": ["stress_robustness"],
        "role": "stress, rolling, sensitivity, overfit 근거를 하나의 board로 묶습니다.",
    },
]


def _status(value: Any) -> str:
    normalized = str(value or "NOT_RUN").strip().upper()
    return normalized if normalized in STATUS_RANK else "NOT_RUN"


def _worst_status(values: list[Any], *, default: str = "NOT_APPLICABLE") -> str:
    statuses = [_status(value) for value in values if value is not None]
    if not statuses:
        return default
    return max(statuses, key=lambda item: STATUS_RANK.get(item, STATUS_RANK["NOT_RUN"]))


def _module_type(module: dict[str, Any]) -> str:
    requirement = str(module.get("requirement") or "").upper()
    return str(module.get("module_type") or MODULE_TYPE_LABELS.get(requirement) or requirement or "-")


def _join_unique(values: list[Any], *, fallback: str = "-") -> str:
    clean = [str(value or "").strip() for value in values if str(value or "").strip()]
    if not clean:
        return fallback
    return " / ".join(dict.fromkeys(clean))


def _spec_modules(spec: dict[str, Any], module_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [module_by_id[module_id] for module_id in spec.get("module_ids", []) if module_id in module_by_id]


def _primary_modules(spec: dict[str, Any], module_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    primary_ids = list(spec.get("primary_module_ids") or [])
    if not primary_ids:
        return _spec_modules(spec, module_by_id)
    return [module_by_id[module_id] for module_id in primary_ids if module_id in module_by_id]


def _board_applies(spec: dict[str, Any], module_by_id: dict[str, dict[str, Any]]) -> bool:
    if spec.get("applies_when") == "always":
        return True
    primary_modules = _primary_modules(spec, module_by_id)
    if primary_modules:
        return any(bool(module.get("applies")) for module in primary_modules)
    return any(bool(module.get("applies")) for module in _spec_modules(spec, module_by_id))


def _not_applicable_reason(spec: dict[str, Any], module_by_id: dict[str, dict[str, Any]]) -> str:
    primary_modules = _primary_modules(spec, module_by_id)
    reasons = [
        module.get("applicability_reason") or module.get("profile_effect") or module.get("reason")
        for module in primary_modules
        if not module.get("applies")
    ]
    return _join_unique(reasons, fallback="현재 후보 특성상 이 보드는 실행하지 않습니다.")


def evidence_boards_for_module(module_id: str) -> list[dict[str, Any]]:
    """Return visible evidence boards that read or explain a validation module."""

    target = str(module_id or "").strip()
    boards: list[dict[str, Any]] = []
    for spec in BOARD_SPECS:
        if target not in set(spec.get("module_ids") or []):
            continue
        boards.append(
            {
                "board_id": spec.get("board_id"),
                "label": spec.get("label"),
                "board_type": spec.get("board_type"),
                "surface": spec.get("surface"),
                "role": spec.get("role"),
            }
        )
    return boards


def build_validation_board_map(
    *,
    modules: list[dict[str, Any]],
    source_traits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map screen boards to validation modules for UI explanation and gating context."""

    module_by_id = {str(module.get("module_id") or ""): dict(module or {}) for module in modules}
    traits = dict(source_traits or {})
    board_rows: list[dict[str, Any]] = []
    for spec in BOARD_SPECS:
        modules_for_board = _spec_modules(spec, module_by_id)
        primary_modules = _primary_modules(spec, module_by_id)
        applies = _board_applies(spec, module_by_id)
        applicable_modules = [module for module in modules_for_board if module.get("applies")]
        status_modules = applicable_modules if applies else primary_modules
        status = _worst_status([module.get("status") for module in status_modules])
        gate_effects = _join_unique(
            [
                module.get("gate_effect")
                for module in modules_for_board
                if applies and module.get("applies")
            ]
        )
        row = {
            "Board ID": spec.get("board_id"),
            "Board": spec.get("label"),
            "Board Type": spec.get("board_type"),
            "Surface": spec.get("surface"),
            "Applies": "Yes" if applies else "No",
            "Applicability": "Shown for this candidate" if applies else _not_applicable_reason(spec, module_by_id),
            "Status": status,
            "Module Types": _join_unique([_module_type(module) for module in modules_for_board]),
            "Feeds Modules": _join_unique([module.get("label") for module in modules_for_board]),
            "Primary Modules": _join_unique([module.get("label") for module in primary_modules]),
            "Gate Effects": gate_effects,
            "Why It Appears": spec.get("role"),
            "Traits": _join_unique(
                [
                    "ETF-like" if traits.get("is_etf_like") else "",
                    "Tactical" if traits.get("is_tactical") else "",
                    "Weighted Mix" if traits.get("is_weighted_mix") else "",
                    "Factor" if traits.get("is_factor_equity") else "",
                ],
                fallback="Basic",
            ),
        }
        board_rows.append(row)

    applied_rows = [row for row in board_rows if row.get("Applies") == "Yes"]
    not_applicable_rows = [row for row in board_rows if row.get("Applies") != "Yes"]
    return {
        "board_rows": board_rows,
        "applied_board_rows": applied_rows,
        "not_applicable_board_rows": not_applicable_rows,
        "summary": {
            "total": len(board_rows),
            "applied": len(applied_rows),
            "not_applicable": len(not_applicable_rows),
            "required_boards": len(
                [
                    row
                    for row in applied_rows
                    if "Required" in str(row.get("Module Types") or "")
                ]
            ),
            "conditional_boards": len(
                [
                    row
                    for row in applied_rows
                    if "Conditional" in str(row.get("Module Types") or "")
                ]
            ),
        },
    }


__all__ = [
    "BOARD_SPECS",
    "build_validation_board_map",
    "evidence_boards_for_module",
]
