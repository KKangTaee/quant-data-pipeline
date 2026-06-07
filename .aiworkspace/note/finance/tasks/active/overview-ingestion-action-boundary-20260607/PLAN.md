# Overview / Ingestion Action Boundary Plan

Status: Complete
Last Updated: 2026-06-07

## Why

5차 code boundary audit found that `Workspace > Overview` already has bounded refresh controls even though the durable docs still described `Workspace > Ingestion` as the only UI collector trigger surface.

This task aligns code and docs without changing user-facing behavior.

## Scope

- Keep Overview market context refresh buttons available.
- Move Overview refresh / browser automation / run-history write calls behind a narrow Streamlit-free action facade.
- Keep external provider access under `finance/data/*` and collection wrappers under `app/jobs/*`.
- Update durable architecture / data / roadmap docs so the policy is explicit.
- Add focused tests that prevent Overview UI from importing `app.jobs.ingestion_jobs`, `app.jobs.overview_automation`, or `app.jobs.run_history` directly.

## Out Of Scope

- Ingestion Console render split.
- DB schema or collector behavior changes.
- New scheduler / launchd setup.
- Registry / saved JSONL rewrite.
- Browser UI layout changes.
- Backtest, Practical Validation, Final Review, or Portfolio Monitoring refactor.

## Completion Criteria

- `app/web/overview_dashboard.py` calls Overview action facade functions instead of direct ingestion job wrappers.
- New action facade is covered by service contract tests.
- `SYSTEM_BOUNDARIES.md`, `PROJECT_MAP.md`, and related maps describe the current collection / read boundary.
- Focused tests, boundary checker, py_compile, and Streamlit health pass.
