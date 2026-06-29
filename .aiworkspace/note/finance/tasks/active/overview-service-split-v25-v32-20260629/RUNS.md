# Overview Service Split V25-V32 Runs

## 2026-06-29

- V25 QA: `test -f .../PLAN.md && test -f .../STATUS.md` -> pass.
- V25 QA: `.venv/bin/python -m py_compile app/services/overview_market_intelligence.py app/services/overview/sentiment.py app/services/overview/events.py app/services/overview/data_health.py app/services/overview/market_movers.py app/services/overview/market_context.py tests/test_service_contracts.py` -> pass.
