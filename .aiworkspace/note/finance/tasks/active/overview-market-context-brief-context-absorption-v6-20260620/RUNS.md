# Runs

## 2026-06-20

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "absorbs_context_limits or splits_dashboard_from_reading_flow_contract or relabels_supporting_flow or copy_uses_korean_summary_first_language or summarizes_existing_context_snapshots or ui_css_defines_market_context_reading_sections"`
  - Result: failed as expected. Existing implementation still rendered `브리프 신뢰도`, limited brief rendering to 3 rows, and returned `brief_caveats`.
- GREEN narrow: same command
  - Result: `6 passed, 361 deselected, 3 warnings`.

- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: `367 passed, 3 warnings in 13.44s`.
- Browser QA: `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`, then opened `http://localhost:8525`.
  - Confirmed `오늘의 시장 브리프` renders with `Futures/Macro 배경` lowered to `장중 macro 해석 보류` when Futures OHLCV is stale.
  - Confirmed `이벤트 배경` renders as `직접 원인 근거 약함` for estimate/review event context.
  - Confirmed removed / forbidden copy was absent: `브리프 신뢰도`, `다음 맥락 체크`, `맥락 검토 결과`, `이벤트 일정`, `이벤트 요인은 약하게 읽기`, `선물 기반 장중 해석 제한`, `예측`, `추천`, `매수`, `매도`, `신호`, `PASS`, `BLOCKER`, `Final Review decision`, `Operations monitoring signal`.
  - Screenshot artifact, not staged: `overview-market-context-brief-context-absorption-v6-qa.png`.
