# Robustness Experiment Registry Notes

## Evidence Owner Map

| Evidence | Owner |
|---|---|
| Robustness Lab board | `app/services/backtest_practical_validation_stress_sensitivity.py::build_robustness_lab_board` |
| PV diagnostic assembly | `app/services/backtest_practical_validation_diagnostics.py::build_practical_validation_result` |
| Walk-forward / OOS / regime | `app/services/backtest_temporal_validation.py` |
| Validation Efficacy audit | `app/services/backtest_validation_efficacy.py` |
| Backtest Realism audit | `app/services/backtest_realism_audit.py` |
| Final Review packet / saved evidence rows / dossier | `app/services/backtest_evidence_read_model.py` |
| PV display surface | `app/web/backtest_practical_validation.py` |
| Final Review display surface | `app/web/backtest_final_review.py` |

## Design Decision

The run-set layer should not replace Robustness Lab. Robustness Lab remains the board users inspect. The run-set is the provenance/grouping contract that Practical Validation, Final Review, saved decision rows, and dossier-style outputs can cite.

## Boundaries

- No new DB table.
- No append-only registry rewrite in this task.
- No generated artifact staging.
- No full trade/scanner/holdings/macro/provider payload in workflow JSONL.
