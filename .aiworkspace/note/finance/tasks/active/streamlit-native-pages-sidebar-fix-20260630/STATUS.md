# Status

Status: Complete
Last Updated: 2026-06-30

## Current State

- RED 확인: `tests.test_service_contracts.BoundaryContractHardeningTests.test_streamlit_shell_does_not_expose_legacy_pages_sidebar`가 `app/web/pages/backtest.py` 존재 때문에 실패했다.
- 구현: Backtest shell을 `app/web/backtest_page.py`로 이동하고 `app/web/streamlit_app.py` import를 변경했다. Tracked `app/web/pages/` package는 제거했다.
- 문서: Backtest shell 경로를 durable docs에서 `app/web/backtest_page.py`로 정렬했다.
- QA: direct `/backtest` cold startup에서 top navigation이 보이고 native sidebar / `Page not found` 문구가 없는 것을 Browser QA로 확인했다.

## Remaining

- None for this task.
