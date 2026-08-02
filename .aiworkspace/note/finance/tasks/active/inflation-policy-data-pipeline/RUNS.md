# Inflation Policy Data Pipeline Runs

- 2026-08-02: `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -q`
  - Result: 27 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_schema.py -q`
  - RED: `INFLATION_POLICY_SCHEMAS`가 없어 3 failed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_schema.py tests/test_economic_cycle_vintages.py -q`
  - GREEN: 30 passed
- 2026-08-02: `git diff --check`
  - Result: passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fred_vintages.py -q`
  - RED: module 부재로 7 failed
  - GREEN: release clock, pagination, normalization, UPSERT 7 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fred_vintages.py tests/test_economic_cycle_vintages.py tests/test_economic_cycle_refresh.py -q`
  - Result: 41 passed, dependency deprecation warning 3개
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_catalog.py tests/test_bea_pce_components.py -q`
  - RED: 독립 catalog와 BEA component module 부재로 6 failed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_catalog.py tests/test_fred_vintages.py tests/test_bea_pce_components.py tests/test_economic_cycle_vintages.py -q`
  - Result: 42 passed
