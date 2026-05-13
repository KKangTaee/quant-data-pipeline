---
name: finance-db-pipeline
description: Build or update finance package data ingestion and MySQL persistence workflows. Use this when adding or changing collectors, DB schemas, UPSERT logic, batch ingestion, logging, retries, loaders, provider connectors, or finance/data pipeline behavior in the quant-data-pipeline project. Pair with finance-task-management for task setup/status and finance-doc-sync for closeout documentation.
---

# Finance DB Pipeline

Use this skill when work touches ingestion and persistence under `finance/data/*`, `finance/data/db/*`, or `finance/loaders/*`.

This is a data implementation skill. Use `finance-task-management` for active task setup and workflow ownership, then use `finance-doc-sync` near closeout when durable docs need alignment.

## First Reads

- `AGENTS.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/data/README.md`
- `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- `finance/data/db/schema.py` before adding or changing persistence

For detailed schema, source, PIT, and done-condition rules, read `references/db-pipeline-rules.md`.

## Core Workflow

1. Identify the source and target table.
2. Inspect existing schema definitions and writer/reader functions.
3. Reuse existing DB groupings, naming, and UPSERT conventions where possible.
4. Normalize provider data before DB writes.
5. Make writes idempotent with stable unique keys.
6. Add bounded retry/logging behavior for remote providers when appropriate.
7. Verify reader/downstream consumer alignment.
8. Update `docs/data/` and architecture docs if table meaning, source boundary, or data flow changed.

## Standard Goal

Every ingestion path should be easy to reason about in this order:

1. source
2. normalization
3. schema
4. UPSERT or canonical refresh scope
5. retry/logging
6. downstream consumer

## Avoid

- New hardcoded credentials
- Non-idempotent writes for repeat collectors
- Silent coercion that hides data loss
- Schema changes without documentation sync
- Splitting stock/ETF price history into separate tables without a clear downstream need
