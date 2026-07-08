# Practical Validation Required Taxonomy Audit Runs

## 2026-07-08

Read current docs and boundaries:

```bash
sed -n '1,180p' .aiworkspace/note/finance/docs/INDEX.md
sed -n '1,180p' .aiworkspace/note/finance/docs/ROADMAP.md
rg -n "Practical Validation|Validation Efficacy|Data Coverage|Backtest Realism|Construction Risk|Risk Contribution|Component Role" .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md
sed -n '1,240p' /Users/taeho/.codex/skills/finance-backtest-web-workflow/references/backtest-ui-boundaries.md
```

Read current implementation surfaces:

```bash
sed -n '1,320p' app/services/backtest_practical_validation_modules.py
sed -n '320,760p' app/services/backtest_practical_validation_modules.py
rg -n "^def _.*_row|criteria=\"" app/services/backtest_validation_efficacy.py app/services/backtest_data_coverage_audit.py app/services/backtest_realism_audit.py app/services/backtest_construction_risk_audit.py app/services/backtest_risk_contribution_audit.py app/services/backtest_component_role_weight_audit.py app/services/backtest_practical_validation_stress_sensitivity.py app/services/backtest_temporal_validation.py
sed -n '1,160p' app/services/backtest_practical_validation_workspace.py
sed -n '520,700p' app/services/backtest_validation_efficacy.py
sed -n '626,690p' app/services/backtest_data_coverage_audit.py
sed -n '1166,1235p' app/services/backtest_realism_audit.py
```

Observed:

- `build_validation_efficacy_audit` still builds rows for source contract, Data Trust, runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT, survivorship, and execution boundary.
- `build_data_coverage_audit` already owns price DB window, provider snapshot freshness, PIT price window, universe/listing, survivorship/delisting, and data storage boundary.
- `build_backtest_realism_audit` owns cost model, net cost curve, turnover, cost/slippage sensitivity, liquidity, net performance, rebalance timing, tax/account, and execution boundary.

Verification:

```bash
git diff --check
find .aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-audit-v1-20260708 -maxdepth 1 -type f | sort
rg -n "TBD|TODO|fill in|implement later" .aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-audit-v1-20260708
```

Result:

- `git diff --check`: passed.
- Task folder contains `PLAN.md`, `DESIGN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`.
- New task docs placeholder scan: no matches.
