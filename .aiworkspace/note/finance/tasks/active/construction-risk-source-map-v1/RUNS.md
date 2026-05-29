# Construction Risk Source Map V1 Runs

Status: Complete
Created: 2026-05-29

## Commands

```bash
sed -n '580,980p' app/services/backtest_practical_validation_diagnostics.py
sed -n '980,1260p' app/services/backtest_practical_validation_diagnostics.py
rg -n "def _correlation_risk_evidence|def _sensitivity_rows|def _sensitivity_interpretation_result|drop-one|drop_one|Risk contribution|Correlation|correlation" app/services/backtest_practical_validation_stress_sensitivity.py
rg -n "look_through|look-through|top_holding|top holding|overlap|asset_bucket|dominant_asset|holdings_coverage|exposure_coverage" app/services/backtest_practical_validation_provider_context.py
sed -n '456,580p' app/services/backtest_practical_validation_provider_context.py
sed -n '680,940p' app/services/backtest_practical_validation_provider_context.py
sed -n '680,1040p' app/services/backtest_practical_validation_stress_sensitivity.py
sed -n '1,260p' app/services/backtest_evidence_read_model.py
```

## Result

- Current concentration / overlap / exposure domain exists in Practical Validation.
- Current provider look-through board already supplies compact holdings and exposure evidence.
- Current robustness sensitivity code already supplies drop-one and weight tilt rows.
- Current Final Review gate has no explicit construction risk group.

## Verification

```bash
git diff --check
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
find .aiworkspace/note/finance/tasks/active/construction-risk-source-map-v1 .aiworkspace/note/finance/phases/active/phase11-portfolio-construction-risk-controls -type f | sort
rg -n 'Current implementation focus: construction risk source map|next work is `construction-risk-source-map-v1`|11-1 `construction-risk-source-map-v1`: Next|next task is `construction-risk-source-map-v1`' .aiworkspace/note/finance/docs .aiworkspace/note/finance/phases/active/phase11-portfolio-construction-risk-controls .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
```

Result:

- `git diff --check`: pass
- `check_finance_refinement_hygiene.py`: pass
- source map / phase file list: present
- stale current-pointer search: no matches

No code files were changed, so py_compile / service contract tests were not required for this task.
