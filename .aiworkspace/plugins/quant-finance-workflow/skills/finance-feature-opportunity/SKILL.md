---
name: finance-feature-opportunity
description: Turn finance product audits and benchmark research into sourced feature candidates, impact/effort/risk prioritization, recommendation notes, parking lots, and next-step handoffs for quant-data-pipeline finance roadmap planning.
---

# Finance Feature Opportunity

Use this skill after `finance-product-audit` and `finance-benchmark-research` have produced research inputs.

This is a synthesis and prioritization skill. It does not directly edit roadmap docs, create phase files, or implement code.

## First Reads

Read `.aiworkspace/note/finance/researches/README.md`, then read only what is needed from the active research folder under `.aiworkspace/note/finance/researches/active/<research-id>/`:
- `CURRENT_PROJECT_AUDIT.md`
- `BENCHMARKS.md`
- `UI_PATTERNS.md`
- `SOURCES.md`
- `RISKS.md` when present

Also read:
- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`

For scoring, read `references/impact-effort-risk.md`.
For recommendation output, read `references/recommendation-template.md`.

## Output Contract

Write or update these files in the active research folder:

```text
.aiworkspace/note/finance/researches/active/<research-id>/
```

- `FEATURE_CANDIDATES.md`
- `RECOMMENDATION.md`

If no active research folder exists, create one before writing feature opportunity output. Use `tasks/active/` only for the execution record of changing this workflow or its skills.

Include:
- candidate title and problem statement
- evidence from audit and benchmarks
- expected user workflow change
- required code/data/doc areas
- impact, effort, risk, confidence, and strategic fit
- dependencies and blockers
- rejected or parked ideas
- recommended next step

## Workflow

1. Convert audit gaps and benchmark patterns into distinct candidate features.
2. Merge duplicates and split oversized ideas.
3. Score candidates with impact, effort, risk, confidence, and strategic fit.
4. Separate `Now`, `Next`, `Later`, and `Parking Lot`.
5. Keep feature recommendations compatible with current product boundaries.
6. Identify which existing domain skill would own future implementation.
7. Produce a recommendation that a human can approve, reject, or narrow.

## Handoff

After human approval:

- use a future roadmap proposal skill to update `docs/ROADMAP.md`
- use a future research-to-phase skill to create phase/task plans
- use `finance-task-intake` and the relevant domain skill for implementation

## Boundary

- Do not treat research synthesis as approval to change product direction.
- Do not claim a feature is validated unless the evidence supports it.
- Do not create live trading, broker order, or auto rebalance plans under the current product boundary.
- Do not rewrite registries, saved setup, or generated run history.
