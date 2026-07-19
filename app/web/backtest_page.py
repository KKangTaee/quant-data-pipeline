from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.web.backtest_state import (  # noqa: F401
    QUALITY_STRICT_PRESETS,
    clear_backtest_preview_caches,
    init_backtest_state,
    request_backtest_panel,
    set_single_strategy_target_from_strategy_key,
)
from app.web.backtest_analysis import render_backtest_analysis_workspace
from app.web.backtest_compare import (
    _queue_current_candidate_compare_prefill,  # noqa: F401
    render_compare_portfolio_workspace,
)
from app.web.backtest_final_review import render_final_review_workspace
from app.web.backtest_portfolio_proposal import render_portfolio_proposal_workspace
from app.web.backtest_candidate_review import render_candidate_review_workspace
from app.web.backtest_practical_validation import render_practical_validation_workspace
from app.web.backtest_single_runner import _handle_backtest_run  # noqa: F401
from app.web.backtest_single_strategy import render_single_strategy_workspace
from app.web.backtest_workflow_shell import render_backtest_workflow_shell
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


def render_backtest_tab() -> None:
    init_backtest_state()

    active_panel = render_backtest_workflow_shell()

    if active_panel == BACKTEST_STAGE_ANALYSIS:
        render_backtest_analysis_workspace()
    elif active_panel == BACKTEST_STAGE_PRACTICAL_VALIDATION:
        render_practical_validation_workspace()
    elif active_panel == BACKTEST_STAGE_FINAL_REVIEW:
        render_final_review_workspace()
    elif active_panel == "Single Strategy":
        render_single_strategy_workspace()
    elif active_panel in {"Compare & Portfolio Builder", BACKTEST_ANALYSIS_MODE_COMPARE}:
        render_compare_portfolio_workspace()
    elif active_panel == "Candidate Review":
        render_candidate_review_workspace()
    elif active_panel == "Portfolio Proposal":
        render_portfolio_proposal_workspace()
    else:
        render_final_review_workspace()


if __name__ == "__main__":
    render_backtest_tab()
