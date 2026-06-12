# Backtest Compare Saved Replay Split 6A Design

Status: Complete
Started: 2026-06-12

## Initial Direction

`app/web/backtest_compare.py` remains the Portfolio Mix Builder orchestration owner. The new `app/web/backtest_compare_saved_replay.py` should own only the saved replay UI/render/helper surface that is already service-backed by `app/services/backtest_saved_portfolio_replay.py`.

## Preserve

- Public entrypoint: `render_compare_portfolio_workspace`.
- Existing session-state keys.
- Existing service boundary: `app/services/backtest_saved_portfolio_replay.py`.
- Existing Practical Validation handoff helper path.
- Existing run history append behavior.

## Inventory

Moved to `app/web/backtest_compare_saved_replay.py`:

- Saved Mix workspace render entrypoint: `render_saved_portfolio_workspace`.
- Saved Mix replay context detector: `is_saved_mix_replay_context`.
- Saved replay service action and run-history append wrapper around `app/services/backtest_saved_portfolio_replay.py`.
- Saved Mix Practical Validation prefill payload and validation board.
- Saved portfolio replay / edit parity snapshot, display rows, override summary, workflow reference scan, replay result card, and form prefill queue.

Kept in `app/web/backtest_compare.py`:

- Public entrypoint `render_compare_portfolio_workspace`.
- New Mix form orchestration, component strategy execution, current weighted portfolio builder/result/save panel, and current weighted mix Practical Validation handoff.
- Strategy-specific form body and dynamic input resolution.
- Shared compare evidence helpers used by both new mix and saved replay flows.

## Proposed Boundary

`app/web/backtest_compare.py` stays the Portfolio Mix Builder orchestration owner. It constructs a `SavedReplayRenderContext` with callbacks for strategy rerun, dynamic input resolution, data-trust assessment, weighted result rendering, and compare source labels, then delegates the saved workspace render to `app/web/backtest_compare_saved_replay.py`.

`app/web/backtest_compare_saved_replay.py` owns Streamlit UI for the saved Mix path only. It may read existing saved portfolio records, invoke `replay_saved_portfolio_record`, update the same session-state keys as before, append the same run-history rows as before, and queue the same Practical Validation source handoff as before. It does not introduce a new persistence source, registry, saved setup schema, or calculation path.

The next split should start from `app/web/backtest_compare.py` weighted-result functions: `_build_weighted_mix_practical_validation_prefill_payload`, `_render_weighted_portfolio_practical_validation_panel`, `_render_save_weighted_portfolio_panel`, and `_render_weighted_portfolio_result`.
