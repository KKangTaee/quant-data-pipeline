# Finance Doc Sync Matrix

## Change Classification

| Change type | Typical trigger | Code inspection required? |
|---|---|---|
| Code implementation | `finance/*`, `app/web/backtest_*`, `app/services/backtest_*`, `app/runtime/backtest/`, DB/schema/runtime changes | Yes |
| Data / DB pipeline | ingestion, persistence, schema, UPSERT, collector changes | Yes |
| Strategy / backtest behavior | strategy inputs, transforms, engine, performance, result schema | Yes |
| Phase planning | explicit phase-managed work, phase plan, task board | Usually no |
| Phase QA / closeout | phase status, integration result, validation summary | Usually no |
| Backtest report | durable result report, strategy log, candidate note | Inspect scripts/code only if result source is uncertain |
| Roadmap refresh | baseline, workflow state, approved scope, next decision, priority change | Usually no |
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

Update `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` and `.aiworkspace/note/finance/docs/data/` when ingestion, schema, persistence, loader read path, table semantics, or timing interpretation changes.

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

For every closeout, sync the owning task or phase records:

- active task or phase `STATUS.md`
- `RUNS.md`, `NOTES.md`, `RISKS.md` when relevant

Then apply this change-based matrix:

| Observed change | Update |
|---|---|
| Product promise, user journey, surface purpose, principle, or non-goal changed | `docs/PRODUCT_DIRECTION.md` |
| Implemented code/screen/workflow/storage ownership boundary changed | `docs/PROJECT_MAP.md` and the owning architecture/flow/data doc |
| Baseline, Active/Paused/Verification-Only state, approved scope, or priority changed | `docs/ROADMAP.md` |
| Document discovery, canonical path, or read order changed | `docs/INDEX.md` |
| Repeated operating procedure changed | owning runbook |
| Durable term changed | `docs/GLOSSARY.md` |
| Backtest report discovery changed | `reports/backtests/INDEX.md` |
| Next worker needs a high-signal milestone or decision | the relevant root handoff log, limited to 3-5 lines |
| None of the above changed | no canonical/root-log update; record “canonical doc change 없음” in task closeout when useful |

Do not use INDEX or ROADMAP as completed-task chronology. Keep completion history in task/phase documents.

## Common Scenarios

| Scenario | Default documentation |
|---|---|
| Small UI copy, minor bug fix, or focused QA | task docs only |
| Navigation or user journey change | Product Direction, Project Map, owning flow; Roadmap only if baseline/state changed |
| Ownership refactor | Project Map and owning architecture doc |
| DB schema/source change | data and architecture docs; Project Map only for a high-level boundary change |
| Pause, resume, or verification-only decision | task status, compact manifest, Roadmap |
| Unapproved product research | research bundle only |
| Approved product direction | Product Direction and Roadmap; Project Map after implementation changes ownership |
| Documentation structure change | Index, AGENTS, and owning runbook |

## Backtest Reports

Durable backtest reports should capture goal, period/universe, key settings, factor/ticker set, result summary, interpretation/next action, and whether the result is development validation, user analysis, or investment-candidate review.

Store result-oriented reports under `.aiworkspace/note/finance/reports/backtests/`.

For repeated strategy experimentation, update the matching strategy backtest log and strategy hub when applicable.

## Registry And Artifact Boundary

- Do not rewrite registry JSONL unless explicitly requested or the workflow requires an append.
- Do not stage run history, generated artifacts, temp CSVs, notebooks, `.DS_Store`, or browser scratch directories without explicit request.
- If a registry append is part of the user-facing workflow, note that clearly in the closeout summary.
