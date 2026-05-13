# Finance Doc Sync Matrix

## Change Classification

| Change type | Typical trigger | Code inspection required? |
|---|---|---|
| Code implementation | `finance/*`, `app/web/pages/backtest.py`, DB/schema/runtime changes | Yes |
| Data / DB pipeline | ingestion, persistence, schema, UPSERT, collector changes | Yes |
| Strategy / backtest behavior | strategy inputs, transforms, engine, performance, result schema | Yes |
| Phase planning | new phase, roadmap, phase plan, TODO board | Usually no |
| Phase QA / closeout | checklist updates, manual validation, completion summary | Usually no |
| Backtest report | durable result report, strategy log, candidate note | Inspect scripts/code only if result source is uncertain |
| Roadmap refresh | product direction, phase ordering, support track, scope change | Usually no |
| User-requested analysis | user asks to analyze a result, compare candidates, or interpret metrics | Usually no unless rerunning code |
| Skill / workflow guidance sync | AGENTS, skills, templates, hygiene workflow | Usually no |

## Code Implementation

Review `docs/PROJECT_MAP.md` and `docs/PRODUCT_DIRECTION.md` when a finance feature or workflow changes the high-level current-state map or product boundary.

Good reasons to update project/product maps:

- product surface changed
- major system layers or architectural boundaries changed
- source boundary, DB source-of-truth, or table meaning changed at a summary level
- strategy family, runtime behavior, result contract, or Backtest UI workflow changed at a summary level
- operator-facing concept boundary changed
- existing text would mislead a future reader

Do not add one-off backtest results, phase progress notes, detailed call flows, table-by-table details, small UI copy changes, or minor bug fixes to high-level maps.

## Data / DB Pipeline

Inspect:

- `finance/data/db/schema.py`
- relevant writer/reader functions under `finance/data/*`

Document table/column meaning, upstream writer, downstream consumer, idempotency, UPSERT behavior, and PIT/look-ahead/survivorship risks.

Update `.note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` and `.note/finance/docs/data/` when ingestion, schema, persistence, loader read path, table semantics, or timing interpretation changes.

## Strategy / Backtest Behavior

Inspect:

- `finance/transform.py`
- `finance/strategy.py`
- `finance/engine.py`
- `finance/performance.py`
- Backtest UI files when user-facing

Document strategy purpose, required inputs/transforms, output contract, benchmark/guardrail semantics, and result interpretation changes.

Update architecture/flow docs when runtime/result bundle flow, UI flow, or strategy family implementation path changes.

## Phase And Task Closeout

For phase/task plans, include `이걸 하는 이유?` or an equivalent purpose section. Explain the problem, why it matters now, and the concrete value created when finished.

For closeout, sync:

- active task or phase `STATUS.md`
- `RUNS.md`, `NOTES.md`, `RISKS.md` when relevant
- `.note/finance/docs/ROADMAP.md`
- `.note/finance/docs/INDEX.md`
- `.note/finance/WORK_PROGRESS.md`
- `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` when a durable decision was made

## Backtest Reports

Durable backtest reports should capture goal, period/universe, key settings, factor/ticker set, result summary, interpretation/next action, and whether the result is development validation, user analysis, or investment-candidate review.

Store result-oriented reports under `.note/finance/reports/backtests/`.

For repeated strategy experimentation, update the matching strategy backtest log and strategy hub when applicable.

## Registry And Artifact Boundary

- Do not rewrite registry JSONL unless explicitly requested or the workflow requires an append.
- Do not stage run history, generated artifacts, temp CSVs, notebooks, `.DS_Store`, or browser scratch directories without explicit request.
- If a registry append is part of the user-facing workflow, note that clearly in the closeout summary.
