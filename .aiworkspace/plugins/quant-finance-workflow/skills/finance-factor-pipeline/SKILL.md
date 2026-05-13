---
name: finance-factor-pipeline
description: Build or update factor-generation workflows in the finance package. Use this when deriving quantitative factors from fundamentals, financial statements, and market prices, especially for point-in-time handling, fallback accounting logic, as-of price matching, and factor storage in the quant-data-pipeline project. Pair with finance-task-intake before broad work and finance-doc-sync for closeout documentation.
---

# Finance Factor Pipeline

Use this skill when work touches factor creation or the accounting-to-factor path under `finance/data/`.

This is a factor implementation skill. Use `finance-task-intake` before broad work, then use `finance-doc-sync` near closeout when durable docs need alignment.

## First Reads

- `AGENTS.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/data/README.md`
- `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- relevant code under `finance/data/fundamentals.py`, `finance/data/factors.py`, `finance/data/financial_statements.py`, and `finance/data/db/schema.py`

For detailed factor classification, PIT, storage, and data-quality rules, read `references/factor-rules.md`.

## Standard Goal

Every factor workflow should be easy to reason about in this order:

1. source accounting fields
2. normalization or fallback logic
3. timing rule
4. market data attachment rule
5. factor formula
6. storage and downstream use

## Core Workflow

1. Define the business meaning of the factor.
2. Identify source fields and precedence order.
3. Make fallback accounting logic explicit.
4. Define timing basis: `period_end`, filing date, or accepted date.
5. Define market price attachment rule.
6. Preserve missingness honestly; do not fill missing factors with arbitrary defaults.
7. Store the factor with clear schema meaning.
8. Update data and architecture docs if assumptions or table meanings changed.

## Critical Boundary

Do not describe `period_end` factor snapshots as point-in-time safe unless filing timing is actually enforced.
