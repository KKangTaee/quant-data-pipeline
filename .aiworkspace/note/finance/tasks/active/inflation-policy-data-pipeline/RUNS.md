# Inflation Policy Data Pipeline Runs

- 2026-08-02: `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -q`
  - Result: 27 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_schema.py -q`
  - RED: `INFLATION_POLICY_SCHEMAS`가 없어 3 failed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_schema.py tests/test_economic_cycle_vintages.py -q`
  - GREEN: 30 passed
- 2026-08-02: `git diff --check`
  - Result: passed
