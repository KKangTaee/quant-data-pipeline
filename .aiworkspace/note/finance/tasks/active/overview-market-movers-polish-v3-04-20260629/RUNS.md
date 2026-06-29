# Runs

## 2026-06-29

- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_polish_phase4` failed before implementation because chart workspace and `상세 표로 보기` were still in the main panel.
- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover_board_model_formats` failed before implementation because board rows did not include previous return preview.
- GREEN: both focused tests passed after implementation.
- Browser QA: SP500 Daily board is full width; chart workspace count is 0; `상세 표로 보기` is absent; mode detail expander remains.
- Browser QA: SP500 Weekly keeps board flow without chart workspace.
- Browser QA: NASDAQ empty state remains understandable.
- Browser QA: 390x844 viewport has no horizontal overflow.
