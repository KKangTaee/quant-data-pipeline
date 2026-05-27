# Practical Validation Helper Boundary Notes

Status: Complete
Created: 2026-05-27

## Initial Findings

- Current boundary lint has no hard violations.
- Remaining advisories are limited to 3 imports from `app/services` to `app/web`.
- `app/web/backtest_practical_validation_curve.py` contains no Streamlit use.
- `app/web/backtest_practical_validation_connectors.py` contains no Streamlit use and reads provider / macro loader output.

## Implementation Choice

- Keep `backtest_practical_validation_curve.py` filename in `app/services` because the public helper names already describe the responsibility.
- Rename `backtest_practical_validation_connectors.py` to `backtest_practical_validation_provider_context.py` because the file builds a provider context for diagnostics rather than UI connectors.

## Result

- `app/services/backtest_practical_validation_diagnostics.py` now imports curve/provider helpers from `app.services`.
- `app/services/backtest_practical_validation_replay.py` now imports curve helpers from `app.services`.
- The old `app/web` helper modules were removed.
- Browser QA was not used because no visible UI flow or displayed data shape changed.
