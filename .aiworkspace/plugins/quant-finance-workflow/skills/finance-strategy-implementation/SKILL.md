---
name: finance-strategy-implementation
description: Implement or update backtest strategies in the finance package. Use this when adding or changing transforms, strategy simulation logic, engine integration, result schema, samples, DB-backed runtime parity, or performance/reporting behavior for quant strategies in the quant-data-pipeline project. Pair with finance-task-management for task setup/status and finance-doc-sync for closeout documentation.
---

# Finance Strategy Implementation

Use this skill when work touches the strategy and backtest layer under `finance/`.

This is a strategy implementation skill. Use `finance-task-management` for active task setup and workflow ownership, then use `finance-doc-sync` near closeout when durable docs need alignment.

## First Reads

- `AGENTS.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md`
- `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` when the strategy is user-facing
- relevant code under `finance/engine.py`, `finance/strategy.py`, `finance/transform.py`, `finance/performance.py`, and `finance/sample.py`

For detailed separation, result schema, DB-backed runtime, and bias rules, read `references/strategy-rules.md`.

## Standard Goal

Each strategy should be easy to follow in this order:

1. required input data
2. preprocessing contract
3. rebalance or decision rule
4. portfolio state update
5. result schema
6. performance/reporting compatibility

## Core Workflow

1. Define what the strategy needs as input.
2. Move reusable preprocessing into `transform.py` when appropriate.
3. Keep simulation logic in `strategy.py`.
4. Expose orchestration through `BacktestEngine` and a `Strategy` subclass if needed.
5. Verify output works with existing performance and display functions.
6. Add or update `finance/sample.py` or an equivalent usage example.
7. Keep direct-fetch and DB-backed entrypoints intentionally separated when both exist.
8. If the strategy is user-facing, wire or explicitly defer catalog, single strategy UI, compare runner, history, and saved replay paths.
9. Update project / architecture / flow docs if behavior or assumptions changed.

## Critical Boundary

Do not hide strategy-specific preprocessing in UI code or engine methods. Keep reusable transforms, simulation logic, orchestration, and reporting compatibility separate.
