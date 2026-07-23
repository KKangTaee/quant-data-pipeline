# Notes

- 기존 `app/services/backtest_price_refresh.py`가 bounded OHLCV refresh plan과 `run_collect_ohlcv` 실행을 이미 소유한다.
- 기존 visible action은 legacy `_render_last_run_details()` 아래에 있으나 current `_render_last_run()`은 새 Result Workspace만 렌더링한다.
- current Result Workspace intent는 `save_and_move`만 지원해 refresh action과 rerun action이 없다.
- 현재 Level1 technical handoff gate는 가격 freshness gap을 blocker로 사용하지 않는다.
- GTAA 재계산 정확성을 위해 현재 보유 종목만이 아니라 평가 Universe, cash proxy, required benchmark가 refresh 범위에 포함되어야 한다.
- 사용자는 자동 재실행을 원하지 않으며, 최신화 후 `같은 설정으로 다시 백테스트`를 선택했다.
- 사용자는 stale 결과의 Level2 인계를 차단하도록 승인했다.
- 공통 service는 종목/날짜 evidence와 네 상태만 만들고 DB plan과 ingestion은 web adapter가 소유한다.
- Single refresh intent는 run id와 Python 발급 configuration fingerprint를 되받아 current result identity를 재검증한다.
- Mix는 weighted bundle과 component bundle의 Universe/cash/benchmark/guardrail 종목을 합집합·중복 제거한다.
- 수집 성공은 백테스트 성공이 아니다. refresh result가 row를 저장했으면 기존 결과를 참고용으로 유지하고 rerun action만 연다.
- Browser QA에서 pending Single 실행 뒤 `st.rerun(scope="fragment")`가 full run에서 예외를 내는 기존 orchestration 결함을 발견해 app-scope로 교정했다.
