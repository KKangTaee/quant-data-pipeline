# Practical Validation Replay Service Boundary Notes

## Findings

- `app/web/backtest_practical_validation_replay.py` did not import Streamlit before the move.
- Only `app/web/backtest_practical_validation.py` imports the replay helper today.
- Moving the file to `app/services` is a low-risk boundary improvement because call signatures can stay unchanged.

## Decisions

- Move the whole helper module rather than adding a thin wrapper, so file ownership matches its Streamlit-free runtime role.
- Keep `app.web.backtest_practical_validation_curve` and `app.web.runtime.backtest` imports as transitional advisory debt for a later runtime / curve relocation task.
