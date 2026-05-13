# Finance Product Audit Checklist

Use this checklist to keep the audit grounded in the actual repo instead of vague product critique.

## Product Shape

- What is the current product promise?
- Which user journey exists today?
- Which journey is implied but not yet supported?
- Which boundaries are explicit non-goals?
- Which decisions require human approval?

## Workflow Coverage

Review the major surfaces:

- Ingestion
- Overview
- Backtest Analysis
- Practical Validation
- Final Review
- Candidate Library
- Backtest Run History
- Selected Portfolio Dashboard
- Reference / Guides

For each surface, capture:

- purpose
- role classification: user-facing product surface, internal/ops console, or mixed/transitional
- main inputs
- main outputs
- downstream handoff
- current friction
- missing evidence or unclear state

Use this distinction when the user asks about platform migration:

| Role | Meaning | Migration implication |
|---|---|---|
| User-facing product surface | A screen a target user would directly value or share | candidate for polished API-backed product UI |
| Internal/ops console | A screen for ingestion, QA, debugging, registry inspection, run health, or developer operations | can usually remain Streamlit longer |
| Mixed/transitional | A screen that contains both user value and internal workflow machinery | split read-only product views from write/debug controls before migration |

## Data And Validation

Check whether future product ideas would stress these assumptions:

- DB-backed runtime instead of direct UI fetch
- point-in-time correctness
- look-ahead bias
- survivorship bias
- provider coverage and field reliability
- compact evidence in registries versus full source data in DB
- `NOT_RUN` not being treated as pass

## Architecture And Ownership

Map only files relevant to product direction:

- UI entry points
- runtime glue
- data ingestion and loader boundaries
- strategy, transform, engine, performance ownership
- registry and saved setup boundaries
- durable docs, active research docs, and active task docs

## Audit Output Template

```markdown
# Current Project Audit

Status:
Last Updated:

## Summary

## Current Product Promise

## Current Workflow

## Implemented Capabilities

## Surface Role Classification

## Strengths

## Weak Points

## Data And Validation Risks

## UX / Workflow Friction

## Documentation Or Handoff Drift

## Benchmark Questions

## Open Questions
```
