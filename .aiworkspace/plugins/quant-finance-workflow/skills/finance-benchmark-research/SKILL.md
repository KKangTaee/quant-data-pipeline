---
name: finance-benchmark-research
description: Research comparable quant, portfolio analytics, backtesting, investment research, and portfolio monitoring products or services for quant-data-pipeline finance planning. Use this when Codex needs current external benchmarks, feature patterns, UI/workflow patterns, pricing or packaging signals, trend context, and sourced evidence before proposing feature opportunities.
---

# Finance Benchmark Research

Use this skill after `finance-product-audit` when external comparison is needed for finance product direction.

This is a web research and synthesis skill. It does not change roadmap docs, create phases, or implement features.

## First Reads

Read only what is needed:
- `.aiworkspace/note/finance/researches/README.md`
- the active research folder under `.aiworkspace/note/finance/researches/active/<research-id>/`
- `CURRENT_PROJECT_AUDIT.md` when available
- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`

For benchmark structure, read `references/benchmark-template.md`.
For citation and source quality rules, read `references/source-quality-rules.md`.

## Research Scope

Compare 3 to 5 relevant products or services unless the user asks otherwise.

Possible benchmark classes:
- quant research and backtesting platforms
- portfolio analytics and risk platforms
- ETF/fund research tools
- broker-adjacent portfolio monitoring tools
- open-source quant dashboards and notebooks

Prefer current, primary, and inspectable sources. Browse the web for current product information, pricing, docs, screenshots, and public changelogs when doing an actual benchmark run.

## Output Contract

Write or update these files in the active research folder:

```text
.aiworkspace/note/finance/researches/active/<research-id>/
```

- `BENCHMARKS.md`: product-by-product benchmark notes
- `UI_PATTERNS.md`: recurring workflow and UI patterns
- `SOURCES.md`: source list with access dates and what each source supports

If no active research folder exists, create one before writing benchmark output. Use `tasks/active/` only for the execution record of changing this workflow or its skills.

Include:
- product/service name and category
- target user and main workflow
- relevant features
- UI/workflow patterns
- data/evidence model when visible
- pricing/packaging signals when relevant
- applicability to this project
- explicit limits of the source evidence

## Workflow

1. Start from audit questions, not a broad market scan.
2. Pick a small benchmark set with different angles.
3. Use current web sources and capture source dates.
4. Separate observed product behavior from inference.
5. Extract reusable patterns rather than copying features literally.
6. Identify patterns that conflict with this project's non-goals.
7. Hand off synthesized opportunities to `finance-feature-opportunity`.

## Boundary

- Do not copy proprietary UI text or large source excerpts.
- Do not treat marketing claims as verified capability without supporting evidence.
- Do not recommend features that require live brokerage action unless marked as out of current product boundary.
- Do not rewrite registries, saved setup, or roadmap files.
