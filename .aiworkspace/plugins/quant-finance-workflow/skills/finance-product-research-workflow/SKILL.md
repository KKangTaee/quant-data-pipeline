---
name: finance-product-research-workflow
description: Run or harden end-to-end product direction research for quant-data-pipeline finance. Use this when Codex needs to create a product research bundle, coordinate current-product audit, external benchmark research, UI/workflow pattern synthesis, feature opportunity prioritization, recommendation handoff, or validate the research output contract before later pluginization or implementation planning.
---

# Finance Product Research Workflow

Use this skill when the user wants an end-to-end product direction research run, or when a repeated research run should be hardened into the finance plugin workflow.

This is an orchestration skill. It does not replace `finance-product-audit`, `finance-benchmark-research`, or `finance-feature-opportunity`; it coordinates them and validates the research bundle contract.

## First Reads

Read only what is needed:
- `AGENTS.md`
- `.aiworkspace/note/finance/researches/README.md`
- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- the active research folder under `.aiworkspace/note/finance/researches/active/<research-id>/` when continuing a run
- the active task under `.aiworkspace/note/finance/tasks/active/<task-id>/` when changing this workflow or its skills

## Helper Scripts

Use these scripts from repo root when a deterministic step helps:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_product_research_bundle.py \
  --title "Research Title" \
  --research-id 2026-05-example-research \
  --focus "Why this research exists." \
  --dry-run

.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_product_research_bundle.py \
  --research-id 2026-05-example-research
```

Script roles:

- `bootstrap_product_research_bundle.py`: creates the required research files under `researches/active/<research-id>/`.
- `check_product_research_bundle.py`: checks required files, basic section hints, source date, evidence labels, and README listing.

## Workflow

1. Classify the request.
   - Actual research output goes under `.aiworkspace/note/finance/researches/active/<research-id>/`.
   - Workflow, skill, script, or plugin changes go under `.aiworkspace/note/finance/tasks/active/<task-id>/`.
2. Confirm or create the research bundle.
   - Use the bootstrap script for a new bundle when helpful.
   - Update `.aiworkspace/note/finance/researches/README.md` so the active research is visible.
3. Run current product audit.
   - Use `finance-product-audit`.
   - Write `CURRENT_PROJECT_AUDIT.md`.
4. Run benchmark research.
   - Use `finance-benchmark-research`.
   - Browse current primary sources when external product, framework, API, pricing, or trend details matter.
   - Write `BENCHMARKS.md`, `UI_PATTERNS.md`, and `SOURCES.md`.
5. Synthesize opportunities.
   - Use `finance-feature-opportunity`.
   - Write `FEATURE_CANDIDATES.md` and `RECOMMENDATION.md`.
   - Keep `Now`, `Next`, `Later`, and `Parking Lot` clearly separated.
6. Record risks.
   - Write or update `RISKS.md` with evidence gaps, product boundary risks, and implementation handoff risks.
7. Validate the bundle.
   - Run `check_product_research_bundle.py`.
   - Fix missing required files or structural gaps before closeout.
8. Handoff.
   - Research output is evidence, not approval.
   - Do not update `docs/ROADMAP.md`, create phases, or implement features until the user approves the next build scope.

## Output Contract

A complete product research run should contain:

```text
.aiworkspace/note/finance/researches/active/<research-id>/
  RESEARCH_PLAN.md
  CURRENT_PROJECT_AUDIT.md
  BENCHMARKS.md
  UI_PATTERNS.md
  FEATURE_CANDIDATES.md
  RECOMMENDATION.md
  SOURCES.md
  RISKS.md
```

When hardening the workflow or plugin itself, use a task folder instead:

```text
.aiworkspace/note/finance/tasks/active/<task-id>/
  PLAN.md
  STATUS.md
  NOTES.md
  RUNS.md
  RISKS.md
```

## Boundaries

- Do not put product research body into `tasks/active/`.
- Do not treat research recommendations as committed roadmap.
- Do not create live trading, broker order, or auto rebalance plans under the current product boundary.
- Do not rewrite registry JSONL, saved setup, run history, or generated artifacts during research.
- Do not create a separate product research plugin until the existing in-plugin workflow has been validated across more repeated runs.
