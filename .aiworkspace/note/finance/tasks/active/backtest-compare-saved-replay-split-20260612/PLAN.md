# Backtest Compare Saved Replay Split 6A Plan

Status: Active
Started: 2026-06-12

## Goal

Split the saved portfolio replay / saved mix replay UI responsibility out of `app/web/backtest_compare.py` into `app/web/backtest_compare_saved_replay.py` while preserving the existing Portfolio Mix Builder public entrypoint and saved replay behavior.

## 이걸 하는 이유?

`app/web/backtest_compare.py` remains a large Backtest Analysis surface after the 9차 visual shell split. Saved replay is already backed by `app/services/backtest_saved_portfolio_replay.py`, so the Streamlit rendering and helper responsibility can move into a focused UI module without changing calculation, persistence, or registry contracts.

## Scope

- Add `app/web/backtest_compare_saved_replay.py`.
- Move saved portfolio replay / saved mix replay UI helpers from `app/web/backtest_compare.py`.
- Keep `render_compare_portfolio_workspace` as the public entrypoint.
- Keep existing Streamlit session-state keys unchanged.
- Keep saved portfolio JSONL, registry JSONL, and run history JSONL append / rewrite behavior unchanged.
- Update focused tests and durable docs for the new ownership boundary.

## Out Of Scope

- Weighted result / Practical Validation handoff panel split; planned for 6B.
- Strategy-specific form body split; planned for 6C.
- Portfolio Monitoring runtime/read-model split; planned for 6D.
- Registry/saved/run history JSONL cleanup or rewrite.
- Backtest calculation, saved setup schema, or validation source contract changes.

## Stop Condition

6A is complete when `app/web/backtest_compare.py` delegates saved replay rendering to the new module, focused verification passes, docs explain the new boundary, and the next 6B handoff is recorded.
