# Overview / Ingestion Action Boundary Design

Status: Complete
Last Updated: 2026-06-07

## Decision

`Workspace > Overview` remains a market context / investigation surface, but it is allowed to expose bounded manual or browser-session refresh controls for the data it displays.

The boundary is not "Overview can collect anything." The boundary is:

```text
Overview UI button
  -> app/jobs/overview_actions.py
  -> app/jobs/ingestion_jobs.py or app/jobs/overview_automation.py
  -> finance/data/*
  -> MySQL
  -> finance/loaders/* / app/services/*
  -> Overview read model render
```

## Responsibilities

| Layer | Responsibility |
|---|---|
| `app/web/overview_dashboard.py` | Render controls, session state, result display, user feedback |
| `app/jobs/overview_actions.py` | Approved Overview action facade for manual refresh, browser auto refresh, quote-gap diagnostics, and run-history recording |
| `app/jobs/ingestion_jobs.py` | Generic collection job wrappers and `JobResult` normalization |
| `app/jobs/overview_automation.py` | Cadence / market-hours / lock guarded automation orchestration |
| `finance/data/*` | External source access, normalization, DB writes |
| `app/services/*` and `finance/loaders/*` | DB-backed read models and context interpretation |

## Policy

- Ingestion remains the primary collector console.
- Overview can run only the approved Overview market-context actions exposed by `app/jobs/overview_actions.py`.
- Overview render paths must not directly import external provider code, ingestion job wrappers, automation runner internals, or run-history append helpers.
- Overview context remains context-only and cannot create validation PASS / BLOCKER, Final Review selected-route decisions, monitoring signals, registry writes, saved setup writes, broker orders, or auto rebalance actions.

## Verification Strategy

- AST import contract test for `app/web/overview_dashboard.py`.
- Action facade wrapper test for intraday refresh defaults.
- Existing Overview automation tests.
- UI / engine boundary checker.
- `py_compile` for touched modules.
- Streamlit health endpoint.
