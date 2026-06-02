# Risk-On Momentum 5D V1 Status

Status: Complete / verified

## Current

- Core swing strategy implemented in `finance/swing.py`.
- Daily swing feature helper added to `finance/transform.py`.
- Futures daily OHLCV loader added in `finance/loaders/futures.py`.
- DB-backed runtime wrapper added in `app/runtime/backtest.py`.
- Single Strategy UI, result `Swing Detail` tab, History replay fields, and Compare default runner are wired.
- Focused synthetic tests, small manual DB-backed smoke, full service contract tests, and Browser QA passed.

## Verified

- `Backtest Analysis > Single Strategy > Risk-On Momentum 5D` renders Top1000 / Top2000 / Manual universe controls.
- Manual universe mode reveals ticker input immediately and runs a DB-backed short smoke.
- Latest result includes the `Swing Detail` tab with comparison / trade / scanner drill-down.
- QA screenshot: `risk-on-momentum-5d-qa.png` (generated artifact, not a commit target).
