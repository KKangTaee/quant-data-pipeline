# Backtest UI Boundaries

## Current Backtest UI Ownership

- `app/web/backtest_page.py`: Backtest page entry
- `app/web/backtest_workflow_shell.py`, `backtest_workflow_routes.py`: workflow shell and panel dispatch
- `app/web/backtest_common.py`: shared presets, session state, navigation helpers
- `app/web/backtest_single_strategy.py`: Single Strategy orchestration
- `app/web/backtest_single_forms/`: strategy-specific forms
- `app/web/backtest_single_runner.py`: Single Strategy execution dispatch
- `app/web/backtest_compare/`: Compare & Portfolio Builder, saved weighted portfolio replay
- `app/web/backtest_result_display.py`: result summary / chart / trust / route UI
- `app/web/backtest_history.py`: Operations run history, replay, load into form, candidate draft handoff
- `app/web/backtest_candidate_library.py`: stored candidate inspection / replay
- `app/web/backtest_candidate_review.py`: Candidate Packaging, review note, current candidate, Pre-Live route
- `app/web/backtest_portfolio_proposal.py`: single-candidate direct readiness, multi-candidate proposal draft, saved proposal review / feedback
- `app/web/backtest_portfolio_proposal_helpers.py`: proposal rows, readiness, validation, monitoring / feedback, paper ledger compatibility, final decision calculation helpers
- `app/web/backtest_practical_validation/`: Practical Validation UI and evidence/action panels
- `app/web/backtest_final_review/`: Final Review UI for validation, robustness, final decision record, and final workflow completion
- `app/web/backtest_final_review_helpers.py`: final review source/evidence/decision helpers
- `app/services/backtest_*`: Streamlit-free workflow, evidence, validation, and read-model services
- `app/runtime/backtest/runners/`: strategy execution adapters
- `app/runtime/backtest/read_models/`: candidate and selected-portfolio read models
- `app/runtime/backtest/stores/`: candidate, proposal, decision, history, and saved-portfolio JSONL stores

## Route Safety Rules

- Candidate Review defines current candidates and Pre-Live operating records.
- Portfolio Proposal composes multiple current candidates into a proposal draft.
- Final Review records select / hold / reject / re-review judgment; it is not live approval.
- Selected Portfolio Dashboard monitors selected portfolios; it is not broker execution.
- Validation packs are read-only unless the user explicitly asks for persistence.
- Do not mutate current / pre-live registries when saving a portfolio proposal unless the requested workflow explicitly requires it.
- Do not auto-save when the user only opens a validation or review view.
- Make blockers actionable. Show what the user should fix, not only the criteria name.

## Verification

For code changes, run focused checks such as:

```bash
.venv/bin/python -m py_compile \
  app/web/backtest_page.py \
  app/web/backtest_workflow_shell.py \
  app/runtime/backtest/facade.py
```

Use targeted helper smoke snippets when the change is pure helper logic. Use Streamlit/Browser/Playwright smoke checks when layout, navigation, or interaction state is at risk.
