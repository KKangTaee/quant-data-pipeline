# Backtest Boundary Refactor V1 Status

Status: Complete

## Current

- 2026-07-01: User approved staged `1차 -> QA -> commit -> ... -> 7차` refactor flow.
- 2026-07-01: Follow-up V2-V8 package refactor completed with development -> QA -> commit cadence through final docs / Browser QA closeout.

## Stage Log

- 1차: Completed. Added `app/web/backtest_state.py` and `app/web/backtest_formatters.py`; `backtest_page.py` now uses the state boundary instead of importing workflow state helpers directly from `backtest_common.py`.
- 2차: Completed. Added `app/services/backtest_single_payload.py`; Single Strategy runner now normalizes execution payload through the service boundary before display/execution.
- 3차: Completed. Added `app/services/backtest_portfolio_mix_readiness.py`; Portfolio Mix role flag detection now lives in the service layer with a web compatibility wrapper.
- 4차: Completed. Added `app/services/backtest_validation_status_policy.py`; Practical Validation module planner now imports shared status normalization/ranking policy.
- 5차: Completed. Added `app/services/backtest_final_review_policy.py`; selected-route preflight now delegates packet-to-policy mapping to the Final Review policy boundary.
- 6차: Completed. Added `app/runtime/backtest_runner_catalog.py`; Single Strategy and Compare services now attach runtime owner metadata to result bundle meta.
- 7차: Completed. Updated durable Backtest structure docs, root handoff logs, and task QA log. Browser QA confirmed `/backtest` renders stage tabs without import/traceback errors.

## V2-V8 Package Refactor Log

- V2: Completed. Converted `app/runtime/backtest.py` into `app/runtime/backtest/` package with `__init__.py`, `facade.py`, and `common.py`.
- V3: Completed. Moved result bundle, runner catalog, real-money helper, strict / risk-on momentum runners, and price strategy runners under `app/runtime/backtest/`.
- V4: Completed. Moved JSONL stores into `app/runtime/backtest/stores/` and read models into `app/runtime/backtest/read_models/`.
- V5: Completed. Split Single Strategy presets / inputs / strategy-specific forms into focused web modules.
- V6: Completed. Split Portfolio Mix Builder into `app/web/backtest_compare/` package with execution, saved replay, weight builder, handoff, and component modules.
- V7: Completed. Split Practical Validation and Final Review into package page / panel / component modules.
- V8: Completed. Updated durable docs, restored runtime runner compatibility hooks for legacy patch surfaces, ran focused full QA, and completed Browser QA for Backtest first entry and stage transitions.

## Closeout

- Completed stages: V1 through V8.
- Remaining scope: none for this boundary/package refactor.
- Follow-up candidate: smaller cleanup of transitional shared helpers such as `app/web/backtest_common.py`; strategy math, validation thresholds, registry row format, and provider DB semantics were not changed.
