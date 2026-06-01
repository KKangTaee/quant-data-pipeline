# Notes

- `app/services/backtest_practical_validation_modules.py` owns the module-level Final Review handoff gate.
- `app/services/backtest_evidence_read_model.py` already owns selection-vs-deployment policy severity for Final Review.
- Reusing the Final Review selection policy as a Practical Validation preflight avoids two diverging definitions of “selected-route ready.”
- `REVIEW` is still allowed only when selection policy treats it as `WATCH` / open review. If the same `REVIEW` is selection-critical, for example gross-only / net performance evidence, the preflight blocks movement before Final Review.
- Existing saved Practical Validation rows are not rewritten. Final Review eligibility computes preflight dynamically when the stored row does not have the new preflight snapshot.
