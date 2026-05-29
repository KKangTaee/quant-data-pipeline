# Walk-forward / OOS Source Map V1 Runs

Status: Complete
Created: 2026-05-29

## Commands

Source inspection:

- `rg -n "walk|rolling|stress|sensitivity|overfit|regime|macro|benchmark|replay|curve|monthly|window|holdout|out.of.sample|out_of_sample|oos" app/services app/runtime app/web tests -g '*.py'`
- `rg -n "^def |^class |SCHEMA_VERSION|rolling|stress|sensitivity|overfit|market_context|regime" app/services/backtest_practical_validation_stress_sensitivity.py`
- `rg -n "^def |^class |SCHEMA_VERSION|audit|gate|route|robustness|benchmark|period|replay|look-ahead|survivorship" app/services/backtest_validation_efficacy.py app/services/backtest_evidence_read_model.py`
- `rg -n "curve_evidence|curve_context|benchmark_parity|curve_provenance|robustness_lab_board|rolling_evidence|overfit|stress_interpretation|regime|macro|replay_result|period_coverage" app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation.py`
- `rg -n "out_of_sample|rolling_review|benchmark_policy|market_regime|promotion|guardrail|replay_contract|curve" app/runtime app/services app/web -g '*.py'`
- `nl -ba app/services/backtest_practical_validation_diagnostics.py | sed -n '393,486p'`
- `nl -ba app/services/backtest_practical_validation_stress_sensitivity.py | sed -n '269,352p'`
- `nl -ba app/runtime/backtest.py | sed -n '754,952p'`
- `nl -ba app/services/backtest_validation_efficacy.py | sed -n '424,482p'`
- `nl -ba app/services/backtest_evidence_read_model.py | sed -n '641,821p'`

Verification commands are added after final checks.

## Verification

2026-05-29:

- `find .aiworkspace/note/finance/tasks/active/walkforward-oos-source-map-v1 -type f | sort` passed; expected task files are present.
- `git diff --check` passed.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` completed with advisories:
  - `CURRENT_CHAPTER_TODO` is not present in the current `.aiworkspace/note/finance` structure, so there is no active phase TODO file to sync.
  - `docs/INDEX.md` was reviewed and did not need a content change for this task because discovery paths did not change.
  - existing generated artifact `finance/.DS_Store` remains unstaged.
- `git status --short` reviewed; only this task's docs, Phase 10 handoff docs, root logs, Roadmap, and existing unstaged `finance/.DS_Store` are changed.
