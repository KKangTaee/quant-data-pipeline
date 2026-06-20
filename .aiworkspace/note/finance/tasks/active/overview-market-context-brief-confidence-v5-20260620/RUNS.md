# Runs

## 2026-06-20

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "separates_brief_confidence or splits_dashboard_from_reading_flow_contract or relabels_supporting_flow or copy_uses_korean_summary_first_language or summarizes_existing_context_snapshots or ui_css_defines_market_context_reading_sections"`
  - Result: failed as expected. Existing implementation still had Events / 자료 신뢰도 inside `brief_rows`, no `brief_caveats`, and no `브리프 신뢰도` renderer.
- GREEN narrow: same command
  - Result: `6 passed, 361 deselected, 3 warnings`.

Full verification and Browser QA are recorded after final run.

- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: `367 passed, 3 warnings`.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Result: app loaded at `http://localhost:8525`.
- Browser QA:
  - Confirmed `Market Context` selected.
  - Confirmed `오늘의 시장 브리프` renders 3 rows: `무엇이 움직였나`, `확산/집중인가`, `Futures/Macro 배경`.
  - Confirmed `브리프 신뢰도` renders 2 rows: `이벤트 일정 / 이벤트 요인은 약하게 읽기`, `자료 기준 / 선물 기반 장중 해석 제한`.
  - Confirmed old user-facing copy was not detected in page text: `맥락 검토 결과`, `다음 맥락 체크`, `이벤트 caveat`, `자료 신뢰도 caveat`, `신뢰도 caveat`, `자료 caveat`.
  - Confirmed forbidden copy was not detected in visible page text: `예측`, `추천`, `매수`, `매도`, `신호`, `PASS`, `BLOCKER`, `Final Review decision`, `Operations monitoring signal`.
  - Screenshot artifact: `overview-market-context-brief-confidence-v5-qa.png` (generated artifact, not staged).
