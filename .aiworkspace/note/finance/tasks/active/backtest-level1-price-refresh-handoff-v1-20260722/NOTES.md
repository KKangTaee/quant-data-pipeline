# Notes

- 기존 `app/services/backtest_price_refresh.py`가 bounded OHLCV refresh plan과 `run_collect_ohlcv` 실행을 이미 소유한다.
- 기존 visible action은 legacy `_render_last_run_details()` 아래에 있으나 current `_render_last_run()`은 새 Result Workspace만 렌더링한다.
- current Result Workspace intent는 `save_and_move`만 지원해 refresh action과 rerun action이 없다.
- 현재 Level1 technical handoff gate는 가격 freshness gap을 blocker로 사용하지 않는다.
- GTAA 재계산 정확성을 위해 현재 보유 종목만이 아니라 평가 Universe, cash proxy, required benchmark가 refresh 범위에 포함되어야 한다.
- 사용자는 자동 재실행을 원하지 않으며, 최신화 후 `같은 설정으로 다시 백테스트`를 선택했다.
- 사용자는 stale 결과의 Level2 인계를 차단하도록 승인했다.
