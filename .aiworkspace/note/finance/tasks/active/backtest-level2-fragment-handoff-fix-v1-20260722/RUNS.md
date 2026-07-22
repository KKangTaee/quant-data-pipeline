# Runs

- 진단 전 focused baseline: `50 passed, 3 warnings`.
- isolated Streamlit reproduction: handler count `0 -> 1`, fragment 밖 marker 미갱신, fragment callback warning 재현.
- RED: 새 lifecycle test가 component에 `on_change`가 전달되는 기존 동작 때문에 실패함을 확인했다.
- GREEN: result workspace와 decision workspace focused suite `51 passed, 3 warnings`.
- actual Browser QA: production adapter/component 기반 synthetic GTAA에서 버튼 1회 클릭 후 `LEVEL2_ROUTE_REACHED`, `HANDLER_COUNT 1`, console error/warning `0`을 확인했다.
- QA artifact: `backtest-level2-fragment-handoff-fix-qa.png`; generated artifact라 stage하지 않는다.
- temporary diagnostic app과 Streamlit process를 제거했다.
- final verification: result workspace, decision workspace, refactor boundary suite `102 passed, 3 warnings`; `py_compile`, `git diff --check`, temporary app/process absence 확인.
