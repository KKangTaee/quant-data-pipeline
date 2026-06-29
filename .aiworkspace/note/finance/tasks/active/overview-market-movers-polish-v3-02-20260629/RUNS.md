# Runs

## 2026-06-29

- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_polish_phase2` failed before implementation because `build_market_movers_unified_summary_model` was missing.
- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_unified_summary_model` failed before implementation because the model import was missing.
- GREEN: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_polish_phase2` passed.
- GREEN: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_unified_summary_model` passed.
- Browser QA: SP500 Daily shows one unified summary and no command/data-trust duplicate strip.
- Browser QA: SP500 Weekly keeps the unified summary and coverage trust detail expander.
- Browser QA: NASDAQ empty state keeps the unified summary plus understandable no-universe state.
- Browser QA: 390x844 viewport has no horizontal overflow.
