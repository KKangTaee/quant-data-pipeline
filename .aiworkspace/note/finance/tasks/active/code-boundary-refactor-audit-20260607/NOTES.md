# Notes

Status: Complete
Last Updated: 2026-06-07

## Observations

- 1차~4차는 docs / handoff cleanup이었다. 코드 리뷰 완료로 해석하면 안 된다.
- `check_ui_engine_boundary.py`가 통과하므로 현재 hard import boundary는 비교적 건강하다.
- `app/web/pages/backtest.py`는 112 lines로 page shell 목표를 지키고 있다.
- 대형 파일 문제는 page shell이 아니라 feature body / runtime facade / action rendering에서 발생한다.
- Overview는 product docs상 context surface지만, 실제로는 bounded refresh action을 가진 mixed surface다.
- Ingestion은 collector trigger surface로 남아 있으나, Overview refresh와 Ingestion diagnostics 때문에 action boundary를 더 명확히 해야 한다.
- Ingestion diagnostic cards can stay in the Ingestion surface, but data / loader / live source inspection orchestration should move behind a narrow service or job facade.
- Compatibility code는 필요한 부분이 많다. 삭제보다 cataloging / demotion / migration path가 먼저다.

## Refactor Principle

Behavior-preserving refactor only.
Each step should keep one existing user-visible flow working and move one responsibility boundary at a time.

Recommended unit shape:

```text
app/web/*       -> render, form, session state, user feedback
app/services/*  -> pure read model, action facade, use-case orchestration
app/runtime/*   -> DB-backed strategy/runtime adapters, JSONL helpers
app/jobs/*      -> ingestion job wrappers, automation, run result normalization
finance/data/*  -> collector / UPSERT / source normalization
finance/loaders -> DB-backed read paths
```

## Preferred Verification Per Refactor

- `git diff --check`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- focused `py_compile` for touched modules
- focused service contract tests for moved helpers
- Browser smoke only when a Streamlit screen or route behavior changed
