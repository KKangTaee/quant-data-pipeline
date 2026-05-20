# Practical Validation Diagnostics Service Boundary Notes

## Findings

- `app/web/backtest_practical_validation_helpers.py` is about 2,900 lines and contains validation profile config, selection source builders, compact curve snapshot helpers, and the 12-domain Practical Diagnostics builder.
- It does not import Streamlit, so the safest first move is module relocation rather than formula refactor.
- `app/web/backtest_compare.py` and `app/web/backtest_candidate_review_helpers.py` use compact curve / source construction helpers from the same module.
