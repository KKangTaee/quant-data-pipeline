# Runs

- Focused RED: Sector Breadth outer/lane background와 keyed investigation workspace contract가 구현 전 예상대로 실패했다.
- Focused GREEN 및 Market Movers combined: `OverviewAutomationContractTests` + `OverviewMarketIntelligenceServiceContractTests`의 `market_movers` 80 tests PASS.
- `npm run build` in `app/web/streamlit_components/market_movers_workbench` PASS. Static bundle은 `index-BixFx-ON.css` / `index-Befah7EU.js`로 갱신했다.
- `py_compile` for changed Python/test files and `git diff --check` PASS.
- Browser QA on `http://localhost:8507`: React Sector Breadth outer background, 상승 10개/하락 1개 lane direction tint, top/bottom border 확인. Screenshot: `market-movers-sector-color-group-qa.png` (generated, not staged).
- Investigation workspace Browser QA: keyed parent 1개, React investigation iframe 1개, selector/조사 단서/Snapshot/그래프가 동일 부모 안에 존재함을 확인. Screenshot: `market-movers-investigation-workspace-group-qa.png` (generated, not staged).
- Responsive QA at 760x900: page/workspace horizontal overflow false, workspace iframe 1개 유지. Server restart 완료 이후 신규 console error 0.
- 선택 종목 조사 헤더 후속 검증: Market Movers 80 tests와 변경 Python/test `py_compile` PASS.
- Browser QA on `http://localhost:8507`: `INVESTIGATION WORKSPACE`, `선택 종목 조사`, 설명의 순서와 타이포 계층, 기존 workspace surface를 확인했다. `모드별 상세 표 전체 높이로 보기` expander는 이번 범위에서 기존 위치를 유지한다. Screenshot: `market-movers-investigation-title-unification-qa.png` (generated, not staged).
- Console log에는 서버 재시작 구간의 과거 health/WebSocket 오류만 있었고, QA 시점 health endpoint는 HTTP 200이었다.
