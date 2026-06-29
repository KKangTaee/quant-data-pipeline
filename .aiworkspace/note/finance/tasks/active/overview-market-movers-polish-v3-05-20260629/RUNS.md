# Runs

## 2026-06-29

- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_polish_phase5` failed before implementation because sector component still contained English display strings.
- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_sector_map_model_builds` failed before implementation because the sector model returned English headline/detail labels.
- GREEN: both focused tests passed after implementation.
- Browser QA: SP500 Daily sector map has Korean labels and no `Freshness:`, `Top Loser`, `% positive`, or `adv / dec` text.
- Browser QA: SP500 Weekly sector map uses the same localized language.
- Browser QA: NASDAQ empty state remains stable.
- Browser QA: 390x844 viewport has no horizontal overflow.
