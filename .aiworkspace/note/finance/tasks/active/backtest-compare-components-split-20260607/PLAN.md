# Backtest Compare Components Split 2026-06-07

Status: Completed
Last Verified: 2026-06-07

## Purpose

9차 코드 구조 정리 작업이다.

`app/web/backtest_compare.py`는 Portfolio Mix Builder 화면의 실행, saved replay, weighted mix, candidate handoff, visual shell을 모두 함께 갖고 있었다.
이번 작업은 계산 / 저장 / service 호출을 건드리지 않고, Compare 화면의 CSS / stepper / section heading / component card visual shell을 별도 module로 이동한다.

## 이걸 하는 이유?

Compare 화면은 Backtest Analysis에서 여러 전략을 섞어 하나의 후보 source를 만드는 중요한 화면이다.
visual shell과 실행 orchestration이 같은 대형 파일에 있으면, 이후 saved replay나 strategy form 분해 때 변경 범위가 커진다.
먼저 시각적 component를 분리하면 UI 모양은 유지하면서 Compare 본문 파일을 실행 / 상태 orchestration 중심으로 읽을 수 있다.

## Scope

- Create `app/web/backtest_compare_components.py`.
- Move Portfolio Mix Builder visual helpers into that module.
- Keep compare execution, saved replay, weighted bundle construction, registry handoff, and runtime/service calls in `app/web/backtest_compare.py`.
- Add boundary contract tests for the new component module.
- Update durable docs and retained task manifests.

## Not In Scope

- Strategy math, runtime dispatch, service contracts, DB loader behavior.
- New Compare UX feature, saved portfolio schema, registry rewrite, run history rewrite.
- Splitting the large `_render_strategy_compare_workspace` form body.
- Backtest Compare saved replay orchestration split.
- Push / PR creation.

## Completion Criteria

- Completed: `app/web/backtest_compare.py` imports `app.web.backtest_compare_components`.
- Completed: `app/web/backtest_compare.py` no longer defines Portfolio Mix visual shell helper functions.
- Completed: `app/web/backtest_compare_components.py` owns the public visual entrypoints.
- Completed: focused RED/GREEN contract tests pass.
- Completed: Backtest UI compile, service contract suite, and UI / engine boundary checker pass.
- Completed: Browser QA confirms the Portfolio Mix Builder page still renders.
