# Backtest Boundary Refactor V1 Plan

## Purpose

Backtest 화면, 실행 서비스, 런타임 엔진, Practical Validation / Final Review 판단 스크립트의 책임 경계를 명확히 한다.

## Development Flow

1. 1차: Backtest shared state / formatter extraction
2. 2차: Single Strategy payload boundary extraction
3. 3차: Portfolio Mix Builder pure service extraction
4. 4차: Practical Validation status / module policy extraction
5. 5차: Final Review selected-route policy boundary extraction
6. 6차: Runtime strategy runner catalog boundary extraction
7. 7차: Docs / QA / boundary map closeout

Each stage follows:

```text
write focused failing test -> implement minimal refactor -> run QA -> commit
```

## Non-Goals

- Change strategy math or validation thresholds.
- Rewrite DB loaders, provider collectors, registries, saved portfolio JSONL, or run history.
- Add live approval, broker order, or auto rebalance semantics.
- Convert all `app/web/backtest_*.py` modules into packages in one pass.

## Completion Criteria

- Backtest UI imports narrower shared modules instead of expanding `backtest_common.py`.
- Single Strategy and Portfolio Mix Builder have service-owned payload / readiness helpers.
- Practical Validation and Final Review decision semantics are discoverable in service modules.
- Runtime strategy ownership is discoverable through a catalog without reading UI files.
- Focused tests and compile checks pass after every stage.
