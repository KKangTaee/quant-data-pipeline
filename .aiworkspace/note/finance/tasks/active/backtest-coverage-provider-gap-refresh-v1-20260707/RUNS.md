# Runs

## 2026-07-07

- `git status --short`: 기존 generated QA 이미지와 local run history가 다수 untracked 상태임을 확인. 이번 작업에서 stage하지 않는다.
- `rg`: Backtest Coverage 최신화 플랜과 렌더링 경로가 `app/services/backtest_price_refresh.py`, `app/web/backtest_result_display.py`에 있음을 확인.
- RED: 새 provider-gap exclusion / no-row unresolved retry-block 테스트가 기존 코드에서 실패함을 확인.
- GREEN: `.venv/bin/python -m unittest`로 Backtest price refresh focused 11개 테스트 통과.
- `.venv/bin/python -m py_compile app/services/backtest_price_refresh.py app/web/backtest_result_display.py`: 통과.
- `git diff --check -- app/services/backtest_price_refresh.py app/web/backtest_result_display.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/backtest-coverage-provider-gap-refresh-v1-20260707`: 통과.
- Browser smoke: `http://localhost:8511/backtest`에서 Backtest Analysis 로드 확인, QA screenshot `backtest-provider-gap-refresh-v1-qa.png` 생성. Screenshot은 generated artifact라 stage하지 않는다.
