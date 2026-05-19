from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.web.backtest_practical_validation_helpers import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    build_practical_validation_result as _build_practical_validation_result,
    build_validation_profile,
    source_components_dataframe,
)
from app.web.runtime import append_portfolio_selection_source, append_practical_validation_result


@dataclass(frozen=True)
class PracticalValidationSourceHandoff:
    """UI-neutral contract for moving a selection source into Practical Validation."""

    source_payload: dict[str, Any]
    notice: str
    mode: str = "Selected Source"
    requested_panel: str = "Practical Validation"
    persisted: bool = False


@dataclass(frozen=True)
class PracticalValidationFinalReviewHandoff:
    """UI-neutral contract for moving a validation result into Final Review."""

    session_payload: dict[str, Any]
    notice: str
    requested_panel: str = "Final Review"
    persisted: bool = False


def build_practical_validation_result(
    source: dict[str, Any],
    *,
    validation_profile: dict[str, Any] | None = None,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the Practical Validation result without depending on Streamlit state."""

    return _build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )


def save_practical_validation_result(result: dict[str, Any]) -> None:
    append_practical_validation_result(dict(result or {}))


def prepare_practical_validation_source_handoff(
    source: dict[str, Any],
    *,
    persist: bool = True,
) -> PracticalValidationSourceHandoff:
    """Persist a selection source when requested and return the UI session contract."""

    source_row = dict(source or {})
    persisted = False
    if persist:
        append_portfolio_selection_source(source_row)
        persisted = True

    title = source_row.get("source_title") or source_row.get("selection_source_id")
    return PracticalValidationSourceHandoff(
        source_payload=source_row,
        notice=(
            f"`{title}`를 Practical Validation으로 보냈습니다. "
            "이 기록은 후보 검증 자료이며 live approval이나 주문 지시가 아닙니다."
        ),
        persisted=persisted,
    )


def prepare_final_review_handoff_from_validation(
    *,
    source: dict[str, Any],
    validation_result: dict[str, Any],
    persist_validation: bool = True,
) -> PracticalValidationFinalReviewHandoff:
    """Persist validation when requested and return the Final Review handoff payload."""

    persisted = False
    if persist_validation:
        save_practical_validation_result(validation_result)
        persisted = True

    title = validation_result.get("source_title") or validation_result.get("selection_source_id")
    return PracticalValidationFinalReviewHandoff(
        session_payload={
            "source": dict(source or {}),
            "validation_result": dict(validation_result or {}),
        },
        notice=f"`{title}`를 Final Review로 보냈습니다.",
        persisted=persisted,
    )


__all__ = [
    "PracticalValidationFinalReviewHandoff",
    "PracticalValidationSourceHandoff",
    "VALIDATION_PROFILE_OPTIONS",
    "VALIDATION_PROFILE_QUESTIONS",
    "build_practical_validation_result",
    "build_validation_profile",
    "prepare_final_review_handoff_from_validation",
    "prepare_practical_validation_source_handoff",
    "save_practical_validation_result",
    "source_components_dataframe",
]
