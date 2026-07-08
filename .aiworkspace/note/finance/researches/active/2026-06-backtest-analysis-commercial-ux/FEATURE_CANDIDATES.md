# Feature Candidates

Status: Active
Last Updated: 2026-06-29 KST

Scoring: 1 low, 5 high.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
|---|---|---:|---:|---:|---:|---:|---|
| Backtest Top Simplification | Now | 5 | 2 | 2 | 5 | 5 | Backtest web |
| Remove Reference / Research Panels From Default Backtest Analysis | Now | 5 | 2 | 2 | 5 | 5 | Backtest web |
| Latest Run Summary-First Redesign | Now | 5 | 3 | 3 | 5 | 5 | Backtest web + result read model |
| Validation Handoff Eligibility Policy | Now | 5 | 3 | 4 | 4 | 5 | Backtest web + Practical Validation handoff service |
| Strategy Maturity Chip Service | Next | 4 | 3 | 3 | 4 | 4 | Backtest service / web |
| Portfolio Mix Builder Commercial Workbench | Next | 4 | 4 | 3 | 4 | 4 | Backtest compare |
| Strategy Catalog Deep Audit / Test Matrix | Next | 4 | 4 | 3 | 4 | 5 | Strategy/runtime + Backtest web |
| Strict Quarterly / Risk-On Governance Decision | Later | 4 | 5 | 5 | 3 | 4 | Strategy/runtime + validation |

## Candidates

### Backtest Top Simplification

- Bucket: Now
- Problem: `Backtest 사용 안내` is a manual-like block that adds reading burden.
- User workflow change: User sees the 3-stage flow and next task immediately, not a bullet guide.
- Required areas: `app/web/pages/backtest.py`, maybe `app/web/backtest_ui_components.py`.
- Validation idea: Browser QA for `/backtest` first viewport.
- Owner skill: `finance-backtest-web-workflow`.
- Priority rationale: direct user pain, low risk, high visible improvement.

### Remove Reference / Research Panels From Default Backtest Analysis

- Bucket: Now
- Problem: `Reference help` and strategy development panels are not the main Backtest Analysis task.
- User workflow change: default Backtest Analysis contains strategy run / compare / candidate creation only.
- Required areas: `app/web/backtest_analysis.py`, `app/services/backtest_analysis_research_board.py` if retained only for Reference/research.
- Validation idea: Browser QA confirms no Reference help in Backtest Analysis.
- Owner skill: `finance-backtest-web-workflow`.
- Priority rationale: fixes "improvement = guide" anti-pattern.

### Latest Run Summary-First Redesign

- Bucket: Now
- Problem: Latest Run repeats checklists and warnings before giving a concise result and next action.
- User workflow change: result appears as summary-first artifact with details in tabs/disclosures.
- Required areas: `app/web/backtest_result_display.py`, `app/services/backtest_result_read_model.py`, tests.
- Validation idea: py_compile, focused unit tests for read model, Browser QA after running or loading a sample result.
- Owner skill: `finance-backtest-web-workflow`.
- Priority rationale: biggest usability gain after top cleanup.

### Validation Handoff Eligibility Policy

- Bucket: Now
- Problem: Current candidate readiness score may over-block Practical Validation by requiring promotion-style signals before validation.
- User workflow change: users can send supported, replayable results to Practical Validation even with review warnings; unsupported / empty / research-only paths are blocked.
- Required areas: `app/web/backtest_result_display.py`, possible Streamlit-free helper in `app/services/backtest_result_read_model.py` or dedicated service.
- Dependencies: Decide exact hard blockers.
- Risks: Too-permissive handoff could clutter Practical Validation. Mitigate with warning state and downstream gate.
- Owner skill: `finance-backtest-web-workflow`.

### Strategy Maturity Chip Service

- Bucket: Next
- Problem: Strategy maturity is useful but current inventory/panel form is too heavy.
- User workflow change: strategy selector and result overview show one compact maturity chip and one reason.
- Required areas: new or existing service around `app/services/backtest_strategy_catalog.py`; UI use in `backtest_single_strategy.py` and result display.
- Risks: mapping drift.
- Owner skill: `finance-backtest-web-workflow`; strategy changes only if mapping depends on runtime facts.

### Portfolio Mix Builder Commercial Workbench

- Bucket: Next
- Problem: Portfolio Mix Builder is core, but should feel like a model-portfolio lab rather than a collection of controls.
- User workflow change: components, weights, result comparison, and handoff status read as one compact workbench.
- Required areas: `app/web/backtest_compare.py`, `app/web/backtest_compare_components.py`, compare services.
- Risks: larger surface and Browser QA needed.
- Owner skill: `finance-backtest-web-workflow`.

### Strategy Catalog Deep Audit / Test Matrix

- Bucket: Next
- Problem: User explicitly wants confidence that each strategy works and how it works.
- User workflow change: not a UI feature first; it creates an implementation checklist / tests so future cleanup is not blind.
- Required areas: strategy docs/research, focused tests for dispatch and metadata contracts.
- Risks: can grow into broad strategy rewrite; keep as audit/test matrix.
- Owner skills: `finance-strategy-implementation` for core strategy tests, `finance-backtest-web-workflow` for UI contract.

### Strict Quarterly / Risk-On Governance Decision

- Bucket: Later
- Problem: both are valuable but high risk to over-promote.
- User workflow change: user chooses one dedicated maturation path after core Backtest Analysis cleanup.
- Required areas: strategy/runtime, Practical Validation modules, Final Review policy, docs.
- Risks: high data correctness and workflow-boundary risk.
- Owner skills: `finance-strategy-implementation`, `finance-backtest-web-workflow`.

## Rejected Ideas

- Add another Backtest guide panel.
- Keep Reference help in Backtest Analysis but make it prettier.
- Add a new evidence/workbench panel as the first improvement.
- Treat Data Trust warning as automatic hard block for Practical Validation.
- Promote Risk-On Momentum or quarterly prototypes as ready because performance looks good.
- Add provider / FRED fetch controls in Backtest Analysis.
