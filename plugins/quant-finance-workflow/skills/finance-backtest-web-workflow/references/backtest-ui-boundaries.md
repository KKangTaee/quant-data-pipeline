# Backtest UI Boundaries

## Current Backtest UI Ownership

- `app/web/pages/backtest.py`: page shell and panel dispatch
- `app/web/backtest_common.py`: shared presets, session state, navigation helpers
- `app/web/backtest_single_strategy.py`: Single Strategy orchestration
- `app/web/backtest_single_forms.py`: strategy-specific forms
- `app/web/backtest_single_runner.py`: Single Strategy execution dispatch
- `app/web/backtest_compare.py`: Compare & Portfolio Builder, saved weighted portfolio replay
- `app/web/backtest_result_display.py`: result summary / chart / trust / route UI
- `app/web/backtest_history.py`: Operations run history, replay, load into form, candidate draft handoff
- `app/web/backtest_candidate_library.py`: stored candidate inspection / replay
- `app/web/backtest_candidate_review.py`: Candidate Packaging, review note, current candidate, Pre-Live route
- `app/web/backtest_portfolio_proposal.py`: single-candidate direct readiness, multi-candidate proposal draft, saved proposal review / feedback
- `app/web/backtest_portfolio_proposal_helpers.py`: proposal rows, readiness, validation, monitoring / feedback, paper ledger compatibility, final decision calculation helpers
- `app/web/backtest_final_review.py`: Final Review UI for validation, robustness, paper observation criteria, final decision record, and final workflow completion
- `app/web/backtest_final_review_helpers.py`: final review source/evidence/decision helpers
- `app/web/runtime/candidate_registry.py`: current / Pre-Live JSONL registry helpers
- `app/web/runtime/portfolio_proposal.py`: portfolio proposal JSONL helpers
- `app/web/runtime/final_selection_decisions.py`: final selection decision JSONL helpers
- `app/web/runtime/history.py`: run history helpers
- `app/web/runtime/portfolio_store.py`: saved portfolio setup helpers

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
.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_*.py app/web/runtime/*.py
```

Use targeted helper smoke snippets when the change is pure helper logic. Use Streamlit/Browser/Playwright smoke checks when layout, navigation, or interaction state is at risk.
