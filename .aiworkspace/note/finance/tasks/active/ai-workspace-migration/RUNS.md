# RUNS - AI Workspace Migration

Status: Active
Last Updated: 2026-05-13

## Initial Path Scan

Commands:

```bash
rg -n "\.note/finance" AGENTS.md README.md app finance plugins .note | wc -l
rg -n "plugins/quant-finance-workflow" AGENTS.md README.md app finance plugins .note | wc -l
```

Result:

- `.note/finance` references: about 828
- `plugins/quant-finance-workflow` references: about 81

## Move

Commands:

```bash
mkdir -p /tmp/quant_aiworkspace_migration
cp .note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl /tmp/quant_aiworkspace_migration/BACKTEST_RUN_HISTORY.jsonl.dirty
git restore -- .note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl
mkdir -p .aiworkspace/note .aiworkspace/plugins
git mv .note/finance .aiworkspace/note/finance
git mv plugins/quant-finance-workflow .aiworkspace/plugins/quant-finance-workflow
cp /tmp/quant_aiworkspace_migration/BACKTEST_RUN_HISTORY.jsonl.dirty .aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl
```

Result:

- tracked files moved with git rename detection
- dirty local run history reapplied at the new location

## Path Rewrite

Command:

```bash
rg -l -0 "\.note/finance|plugins/quant-finance-workflow" AGENTS.md README.md app finance .aiworkspace plugins \
  --glob '!*.jsonl' \
  --glob '!*.csv' \
  --glob '!*.pyc' \
  --glob '!**/__pycache__/**' \
  | xargs -0 perl -pi -e 's#\.note/finance#.aiworkspace/note/finance#g; s#plugins/quant-finance-workflow#.aiworkspace/plugins/quant-finance-workflow#g'
```

Result:

- code / docs / skill text paths now point to `.aiworkspace/note/finance` and `.aiworkspace/plugins/quant-finance-workflow`
- JSONL was excluded from this bulk pass to avoid accidental data rewrites

## Registry Path Migration

Reason:

- `manage_current_candidate_registry.py validate` failed because existing registry rows still pointed to old report paths.

Action:

- Updated registry path strings from `.note/finance/backtest_reports/` to `.aiworkspace/note/finance/reports/backtests/`.
- Updated registry source refs such as `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` to `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`.

## Validation

Commands:

```bash
.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/backtest_compare.py app/web/reference_guides.py app/web/streamlit_app.py .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase 999 --title "AI Workspace Smoke" --dry-run
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

Result:

- Python compile passed.
- phase bootstrap dry-run printed `.aiworkspace/note/finance/phases/active/phase999/...` paths.
- current candidate registry validate: `validated 10 registry row(s) with no missing required fields`.
- pre-live registry validate: `validated 5 pre-live registry row(s) with no missing required fields`.
- hygiene helper passed and reported generated artifacts should remain unstaged.

Skill validation:

- repo-local 7 skill dirs passed `quick_validate.py`.
- global mirror 6 finance skill dirs passed `quick_validate.py`.

Stale path check:

- active code/docs old `.note/finance` and root `plugins/quant-finance-workflow` references not found after excluding migration history notes and generated Playwright snapshots.
