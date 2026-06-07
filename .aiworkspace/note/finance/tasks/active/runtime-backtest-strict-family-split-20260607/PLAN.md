# Runtime Backtest Strict Family Split 2026-06-07

Status: Completed record
Last Verified: 2026-06-07

## Purpose

8차 runtime 대형 파일 분해의 8C 작업이다.

`app/runtime/backtest.py`에 남아 있던 strict quality / value / quality-value annual and quarterly wrapper family를 전용 runtime module로 옮기고, 기존 UI / service caller가 쓰는 `app.runtime.backtest` import path는 compatibility facade로 유지한다.

## 이걸 하는 이유?

8A에서 Risk-On Momentum runtime slice를 분리했고, 8B에서 real-money / guardrail / readiness helper family를 분리했다.
남은 큰 덩어리 중 strict family는 factor / statement snapshot, price freshness, dynamic universe, real-money hardening metadata를 한 흐름으로 묶고 있어 price-only ETF wrappers와 책임이 다르다.
전용 module로 분리하면 runtime facade는 ETF runner와 public compatibility export 중심으로 얇아지고, strict annual / quarterly prototype 변경 범위를 더 좁게 검토할 수 있다.

## Scope

- Create `app/runtime/backtest_strict.py`.
- Move strict quality / value / quality-value wrapper implementation and strict helper functions into the new module.
- Keep public compatibility imports in `app/runtime/backtest.py`.
- Add boundary contract tests that prevent strict implementation from moving back into the facade.
- Update durable architecture / project-map docs and retained task state pointers.

## Not In Scope

- Ingestion diagnostic facade 7B.
- Strategy math or factor ranking changes.
- Result bundle schema changes.
- DB schema, ingestion collector, registry / saved JSONL rewrite.
- Browser UI change or screenshot QA.
- Push / PR creation.

## Completion Criteria

- Existing `from app.runtime.backtest import run_quality_* / run_value_*` imports continue to work.
- `app/runtime/backtest.py` no longer owns strict wrapper function bodies.
- `tests/test_service_contracts.py` has a focused contract for the new facade/module boundary.
- Focused and broad service contract tests pass.
- Docs and root handoff logs identify 8C as the latest completed runtime split.
