from __future__ import annotations

from typing import Any


BACKTEST_STAGE_ANALYSIS = "Backtest Analysis"
BACKTEST_STAGE_PRACTICAL_VALIDATION = "Practical Validation"
BACKTEST_STAGE_FINAL_REVIEW = "Final Review"

BACKTEST_STAGE_OPTIONS = [
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
    BACKTEST_STAGE_FINAL_REVIEW,
]

BACKTEST_LEGACY_PANEL_OPTIONS = [
    "Single Strategy",
    "Compare & Portfolio Builder",
    "Candidate Review",
    "Portfolio Proposal",
    "Final Review",
]

BACKTEST_ANALYSIS_MODE_SINGLE = "Single Strategy"
BACKTEST_ANALYSIS_MODE_COMPARE = "Compare & Portfolio Builder"
BACKTEST_ANALYSIS_MODE_OPTIONS = [
    BACKTEST_ANALYSIS_MODE_SINGLE,
    BACKTEST_ANALYSIS_MODE_COMPARE,
]

PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE = "Selected Source"
PRACTICAL_VALIDATION_MODE_SAVED_MIX = "Saved Mix"
PRACTICAL_VALIDATION_MODE_LEGACY = "Legacy Registry Tools"
PRACTICAL_VALIDATION_MODE_OPTIONS = [
    PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE,
    PRACTICAL_VALIDATION_MODE_SAVED_MIX,
    PRACTICAL_VALIDATION_MODE_LEGACY,
]


def _route_target_to_stage_and_mode(target: str | None) -> dict[str, Any]:
    """Map legacy Backtest panel requests onto the new 3-stage workflow."""
    normalized = str(target or "").strip()
    if normalized in BACKTEST_STAGE_OPTIONS:
        return {"stage": normalized, "analysis_mode": None, "practical_mode": None}
    if normalized == "Single Strategy":
        return {
            "stage": BACKTEST_STAGE_ANALYSIS,
            "analysis_mode": BACKTEST_ANALYSIS_MODE_SINGLE,
            "practical_mode": None,
        }
    if normalized == "Compare & Portfolio Builder":
        return {
            "stage": BACKTEST_STAGE_ANALYSIS,
            "analysis_mode": BACKTEST_ANALYSIS_MODE_COMPARE,
            "practical_mode": None,
        }
    if normalized in {"Candidate Review", "Portfolio Proposal"}:
        return {
            "stage": BACKTEST_STAGE_PRACTICAL_VALIDATION,
            "analysis_mode": None,
            "practical_mode": PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE,
        }
    if normalized == "Final Review":
        return {"stage": BACKTEST_STAGE_FINAL_REVIEW, "analysis_mode": None, "practical_mode": None}
    return {
        "stage": BACKTEST_STAGE_ANALYSIS,
        "analysis_mode": BACKTEST_ANALYSIS_MODE_SINGLE,
        "practical_mode": None,
    }


def _valid_backtest_route_targets() -> set[str]:
    return set(BACKTEST_STAGE_OPTIONS) | set(BACKTEST_LEGACY_PANEL_OPTIONS)
