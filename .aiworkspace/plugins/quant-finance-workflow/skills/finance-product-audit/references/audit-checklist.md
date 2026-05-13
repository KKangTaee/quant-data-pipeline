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
- main inputs
- main outputs
- downstream handoff
- current friction
- missing evidence or unclear state

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

## Strengths

## Weak Points

## Data And Validation Risks

## UX / Workflow Friction

## Documentation Or Handoff Drift

## Benchmark Questions

## Open Questions
```
