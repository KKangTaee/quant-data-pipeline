# Sources

Status: Active
Date: 2026-07-06

No external web sources were used. This audit is based on local product code and durable finance documentation.

## Local Code Sources

| Source | Evidence Used |
| --- | --- |
| `app/services/backtest_validation_status_policy.py` | Blocking / review / pass status taxonomy |
| `app/services/backtest_practical_validation_modules.py` | Required / conditional / reference module definitions and Final Review gate aggregation |
| `app/services/backtest_practical_validation_board_registry.py` | Flow 4 board mapping and current `Final Review Readiness Preview` board role |
| `app/services/backtest_practical_validation_workspace.py` | Current source / validation / preflight / conditional grouping and user-facing display fields |
| `app/web/backtest_practical_validation/page.py` | Current Flow 4 title, metrics, group rendering, criteria card rendering |
| `app/web/backtest_practical_validation/workspace_panel.py` | Current Flow 3 workspace / React Fix Queue contract |
| `app/services/backtest_validation_efficacy.py` | Validation efficacy rows and duplicated evidence responsibilities |
| `app/services/backtest_data_coverage_audit.py` | Price / provider / PIT / universe / survivorship data coverage rows |
| `app/services/backtest_realism_audit.py` | Cost / net curve / turnover / liquidity / tax / execution boundary rows |
| `app/services/backtest_construction_risk_audit.py` | Construction / look-through / overlap / exposure audit rows |
| `app/services/backtest_risk_contribution_audit.py` | Weighted mix risk contribution audit rows |
| `app/services/backtest_component_role_weight_audit.py` | Weighted mix role / weight audit rows |
| `app/services/backtest_practical_validation_diagnostics.py` | Practical diagnostics domains including macro, sentiment, stress, monitoring baseline |

## Local Documentation Sources

| Source | Evidence Used |
| --- | --- |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Current Practical Validation file ownership and documented Flow 4 meaning |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Current Backtest to Practical Validation to Final Review user flow |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Recent Practical Validation task state and unchanged boundaries |
| `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | Prior decisions on Practical Validation entry, Flow 3, and sentiment context |
