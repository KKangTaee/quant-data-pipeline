# Runs

## 2026-06-29

- RED: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_polish_phase3` failed before implementation because refresh mode still used segmented/radio logic.
- GREEN: `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_polish_phase3` passed.
- Browser QA: SP500 Daily shows one compact refresh rail, one `방식` selectbox, and no `Run Update Daily Snapshot.` text.
- Browser QA: SP500 Weekly keeps the compact refresh rail and EOD refresh action.
- Browser QA: NASDAQ empty state keeps the compact refresh rail.
- Browser QA: 390x844 viewport has no horizontal overflow.
