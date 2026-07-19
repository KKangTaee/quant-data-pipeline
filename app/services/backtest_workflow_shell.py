from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.web.backtest_workflow_routes import (
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_OPTIONS,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


WORKFLOW_STAGE_PRESENTATION = (
    {
        "stage_key": BACKTEST_STAGE_ANALYSIS,
        "level_label": "LEVEL 1",
        "title": "후보 분석",
        "english_title": "Backtest Analysis",
        "responsibility": "전략을 실행하고 비교해 실전 검증 후보를 준비합니다.",
    },
    {
        "stage_key": BACKTEST_STAGE_PRACTICAL_VALIDATION,
        "level_label": "LEVEL 2",
        "title": "실전 검증",
        "english_title": "Practical Validation",
        "responsibility": "최신 데이터로 검증하고 해결할 일과 넘길 판단을 구분합니다.",
    },
    {
        "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
        "level_label": "LEVEL 3",
        "title": "최종 검토",
        "english_title": "Final Review",
        "responsibility": "검증된 한계와 Monitoring 이관 조건을 바탕으로 최종 판단합니다.",
    },
)


def _normalized_stage(active_stage: str | None) -> str:
    candidate = str(active_stage or "")
    return candidate if candidate in BACKTEST_STAGE_OPTIONS else BACKTEST_STAGE_ANALYSIS


def build_backtest_workflow_shell(active_stage: str | None) -> dict[str, Any]:
    """Project the page-level three-stage workflow without Level gate logic."""

    normalized = _normalized_stage(active_stage)
    stages = [
        {**row, "is_active": row["stage_key"] == normalized}
        for row in WORKFLOW_STAGE_PRESENTATION
    ]
    active_index = next(index for index, row in enumerate(stages) if row["is_active"])
    return {
        "schema_version": "backtest-workflow-shell-v1",
        "headline": "후보를 만들고 검증해 최종 투자 판단까지 이어갑니다",
        "description": "각 단계에서 해야 할 일을 분리하고, 검증된 근거만 다음 판단으로 넘깁니다.",
        "active_stage": normalized,
        "active_stage_index": active_index,
        "active_stage_context": dict(stages[active_index]),
        "stages": stages,
    }


def resolve_backtest_workflow_shell_intent(
    intent: Mapping[str, Any] | None,
    *,
    active_stage: str | None,
    consumed_nonce: str | None,
) -> dict[str, Any]:
    """Accept only a new, allowed, non-current stage-selection intent."""

    payload = dict(intent or {})
    nonce = str(payload.get("nonce") or "")
    stage_key = str(payload.get("stage_key") or "")
    accepted = bool(
        payload.get("type") == "select_stage"
        and nonce
        and nonce != consumed_nonce
        and stage_key in BACKTEST_STAGE_OPTIONS
        and stage_key != _normalized_stage(active_stage)
    )
    if not accepted:
        return {"accepted": False}
    return {
        "accepted": True,
        "stage_key": stage_key,
        "nonce": nonce,
    }


__all__ = [
    "WORKFLOW_STAGE_PRESENTATION",
    "build_backtest_workflow_shell",
    "resolve_backtest_workflow_shell_intent",
]
