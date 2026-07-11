# Runs

- Focused RED: section header payload/result wrapper/React source contract가 구현 전 예상대로 실패했다.
- Focused GREEN: section divider, payload, fallback, React component 계약 4건 통과.
- `npm run build` in `app/web/streamlit_components/market_movers_workbench` -> PASS. Static bundle rebuilt as `index-CBMJUDPA.css` / `index-C5p5EiF2.js`.
- `.venv/bin/python -m unittest -k market_movers tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> PASS, 79 tests.
- `py_compile` for changed Python/test files and `git diff --check` -> PASS.
- Wider Overview combined run: 302/303 relevant tests passed; one unrelated pre-existing Sentiment source assertion (`payload.summary.metrics.map`) remains outside this task.
- Browser QA on `http://localhost:8507`: external sector divider absent, one React sector component present, `SECTOR BREADTH / 섹터 / 시장 확산 맥락 / 정상 / 넓은 참여, 균형 리더십` order confirmed, legacy `시장 확산 지도` exact label count 0, console errors 0. Screenshot: `market-movers-section-title-unification-qa.png` (generated, not staged).
