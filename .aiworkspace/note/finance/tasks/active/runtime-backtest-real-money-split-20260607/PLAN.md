# Runtime Backtest Real-Money Split Plan

Status: Completed
Date: 2026-06-07

## Why

`app/runtime/backtest.py` still owned real-money hardening, cost / turnover postprocess, benchmark overlay, promotion policy, guardrail policy, ETF operability policy, and deployment readiness helper logic after 8A.

Those helpers are shared by multiple strategy runners, but they are not the strategy runner bodies themselves. Keeping them in the facade made the runtime boundary harder to review.

## Scope

- Move real-money / readiness helper family to `app/runtime/backtest_real_money.py`.
- Keep `app.runtime.backtest` imports stable for existing UI, service, replay, and tests.
- Preserve result bundle metadata strings and warnings.
- Add contract tests that lock the new ownership boundary.

## Not In Scope

- No strategy math changes.
- No DB / loader / schema changes.
- No Practical Validation or Final Review gate behavior changes.
- No generated artifact / registry / saved JSONL rewrite.
- No split of strict quality / value runner bodies. That remains 8C.

## Completion Criteria

- `app/runtime/backtest.py` no longer defines real-money helper implementation functions.
- `app/runtime/backtest_real_money.py` owns the helper implementation.
- Existing facade imports remain identical by object identity where compatibility matters.
- Focused and full service contract tests pass.
