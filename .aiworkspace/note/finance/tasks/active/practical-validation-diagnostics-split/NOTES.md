# Practical Validation Diagnostics Split Notes

Status: Active
Created: 2026-05-27

## Initial Findings

- `app/services/backtest_practical_validation_diagnostics.py` has 2956 lines before Task 7.
- Public helper imports are used by web modules and Practical Validation service:
  - `build_validation_profile`
  - `build_selection_source_from_candidate_draft`
  - `build_selection_source_from_saved_mix_prefill`
  - `build_selection_source_from_weighted_mix_prefill`
  - `compact_curve_snapshot_from_bundle`
  - `compact_benchmark_curve_snapshot_from_bundle`
  - `source_components_dataframe`
- The first safe split is source/profile builder logic because it has a small dependency surface and no provider/curve calculations.

## 7-01 Choice

- Add `app/services/backtest_practical_validation_source.py`.
- Keep diagnostics re-export compatibility for existing imports.
- Move no calculation formulas from stress, sensitivity, rolling, provider, or scoring in this step.

## 7-01 Result

- Added `app/services/backtest_practical_validation_source.py`.
- Moved validation profile constants / question contract / domain weights into the new source module.
- Moved selection source builders for candidate draft, saved mix, and weighted mix into the new source module.
- `app/services/backtest_practical_validation_diagnostics.py` still re-exports those public builders for compatibility.
- Updated direct callers in Practical Validation service, Compare, and Candidate Review to import source builders from the new module.
- Diagnostics line count dropped from 2956 to 2541.

## 7-02 Choice

- Add `app/services/backtest_practical_validation_curve_context.py`.
- Move shared curve helper logic that does not need diagnostics-specific component title / ticker interpretation:
  - compact curve and benchmark snapshot builders
  - result curve normalize, date / percent formatting
  - DB price proxy curve
  - component curve combination
  - window perturbation and aligned monthly returns helpers
- Keep `_build_curve_context` in diagnostics for now because it still orchestrates component-specific title, weight, and ticker helper logic.

## 7-02 Result

- Added `app/services/backtest_practical_validation_curve_context.py`.
- Updated Compare and Candidate Review direct imports to use the new curve context helper.
- Kept diagnostics re-export compatibility for compact snapshot builders.
- Diagnostics line count dropped from 2541 to 2258.
- No calculation formulas or Practical Validation result schema were changed.
