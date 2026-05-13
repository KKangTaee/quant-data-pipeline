---
name: finance-product-audit
description: Audit the current quant-data-pipeline finance product before roadmap or feature planning. Use this when Codex needs to understand existing finance capabilities, workflow boundaries, code/documentation structure, data assumptions, UX gaps, and product weaknesses before benchmarking or proposing new feature opportunities.
---

# Finance Product Audit

Use this skill at the beginning of product-direction research for the `finance` workspace.

This is a research and diagnosis skill. It does not benchmark external products, change roadmap docs, create phases, or implement code.

## First Reads

Read only what is needed:
- `AGENTS.md`
- `.aiworkspace/note/finance/docs/INDEX.md`
- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/README.md` when system structure matters
- `.aiworkspace/note/finance/docs/flows/README.md` when user workflow matters
- the active research task folder when one exists

For the detailed audit prompts, read `references/audit-checklist.md`.

## Output Contract

Write or update `CURRENT_PROJECT_AUDIT.md` in the active research/task folder.

Include:
- current product promise and active user workflow
- implemented capabilities by area
- important non-goals and safety boundaries
- code and data ownership map relevant to future work
- weak points, missing links, and product friction
- data correctness risks, especially point-in-time, look-ahead, survivorship, provider coverage, and DB-backed runtime assumptions
- documentation drift or unclear handoff points
- implications for benchmark research

## Workflow

1. Confirm the active research/task output folder.
2. Read the minimum docs needed to understand current scope.
3. Inspect code only where docs are ambiguous or stale.
4. Separate implemented facts from assumptions and hypotheses.
5. Record open questions instead of treating guesses as findings.
6. Keep the audit focused on product direction and workflow gaps, not implementation fixes.
7. Hand off benchmark questions to `finance-benchmark-research`.

## Boundary

- Do not modify `docs/ROADMAP.md` or `docs/PRODUCT_DIRECTION.md` directly.
- Do not create phase/task plans from the audit alone.
- Do not treat backtest performance as sufficient evidence for product direction.
- Do not recommend live trading, broker order, or auto rebalance features unless the user explicitly changes the product boundary.
