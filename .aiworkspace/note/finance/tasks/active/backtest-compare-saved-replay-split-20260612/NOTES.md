# Backtest Compare Saved Replay Split 6A Notes

## Decisions

- 6A is limited to saved replay UI/module ownership.
- `app/services/backtest_saved_portfolio_replay.py` remains the Streamlit-free replay service boundary.
- Registry and saved JSONL data are preserved and will not be rewritten.
- `app/web/backtest_compare.py` keeps orchestration-only ownership through `SavedReplayRenderContext`; the saved replay module receives callbacks instead of importing the whole compare module back.
- Current weighted mix result / save / Practical Validation handoff functions stay in `app/web/backtest_compare.py` for 6B.
- Strategy-specific form body stays in `app/web/backtest_compare.py` for 6C.

## Discoveries

- Saved replay was a cohesive UI slice: saved record table, replay parity snapshot, service call, replay result card, validation board, and saved-mix Practical Validation handoff all share saved portfolio context.
- Saved replay needs several compare-owned helpers, but those are better passed as callbacks to avoid creating a circular import and to keep `backtest_compare.py` as the orchestration owner.
- Browser QA generated a local run-history JSONL row and screenshot artifact. These are runtime/generated artifacts and should remain unstaged.
- The full `tests.test_service_contracts` suite currently has an unrelated macro thermometer expectation mismatch (`OK` expected, `REVIEW` returned). The focused 6A boundary tests pass.
