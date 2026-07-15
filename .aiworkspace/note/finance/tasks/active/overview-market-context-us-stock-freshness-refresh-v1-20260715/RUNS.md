# Overview Market Context US Stock Freshness Refresh V1 Runs

Last Updated: 2026-07-15

## Context Audit

- Confirmed branch `codex/sub-dev` and preserved unrelated untracked research folder.
- Inspected PER and turnaround collection planners, low-level jobs, Overview facades, Streamlit event bridge, React header/action routing, tests, and current NET DB read model.
- Confirmed both low-level selected-stock jobs currently validate CIK before every scope, while profile/price do not require SEC identity.
- Confirmed reusable last-completed NYSE session logic currently lives privately in `app/services/backtest_price_refresh.py`.
- No provider call, DB write, registry append, source change, or generated artifact was produced during design.

## Detailed Plan

- User approved cached DB UI first, automatic freshness diagnosis, and explicit provider refresh CTA.
- Expanded `PLAN.md` into six TDD tasks covering shared calendar, unified freshness, CIK-independent collection, Streamlit event, React UI, and actual/Browser QA closeout.
- Self-review checked spec coverage, placeholder patterns, interface names, scope exclusions, and step/commit boundaries before implementation.

## Baseline

- Confirmed the current directory is an existing linked worktree on `codex/sub-dev`; no new worktree or branch was created.
- The local `.venv` does not include `pytest`, so the plan commands were corrected to the repository's available `unittest` runner before code changes.
- Baseline: `python -m unittest tests.test_us_stock_valuation tests.test_us_stock_turnaround tests.test_market_context_valuation` -> 96 tests passed.

## 1차 — Freshness / Collection Boundary

- RED: missing `app.services.nyse_calendar`, missing `us_stock_freshness`, missing unified ingestion/facade functions, and missing coverage basis keys all failed for the expected contract reason.
- GREEN commits: `3645fb40` shared NYSE session; `9cc8edd9` unified freshness/basis; `49413211` market-first collection and partial-success facade.
- Focused verification: 111 calendar/freshness/PER/turnaround/Market Context tests passed; target `py_compile` and `git diff --check` passed.
- No provider call, DB write, schema change, registry append, or generated artifact occurred in 1차.
