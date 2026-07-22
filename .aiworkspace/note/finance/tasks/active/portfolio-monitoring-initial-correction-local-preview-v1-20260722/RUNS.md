# Runs

## TDD

- React helper RED: 신규 helper export 부재로 2개 테스트 실패를 확인했다.
- Python component RED: 명시적 preview action과 local-only input contract 부재를 확인했다.
- React focused GREEN: `positionEditorState.test.ts` 8개 통과.
- Python component GREEN: `tests.test_portfolio_monitoring_component` 19개 통과.

## Regression And Build

- Portfolio Monitoring Python discovery: 173개 통과.
- Python compile: `app/web/final_selected_portfolio_dashboard.py` 통과.
- React: 35개 통과.
- TypeScript typecheck: 통과.
- Vite production build: 통과, `component_static/` 갱신.

## Actual Browser QA

- route: `http://localhost:8502/selected-portfolio-dashboard`
- actual item: AMD, 기존 요청일 `2024-12-19`, 최초 수량 `28`.
- local edit: `2024-06-15`, `31`; dialog 1개 유지, preview action 활성, 저장 비활성.
- explicit preview 후: dialog 1개 유지, `변경값 확인 완료`, 저장 활성.
- projected result: 적용일 `2024-06-17`, 종가 `$158.40`, 최초 투자금 `$4,910.40`.
- browser console errors: 0.
- 실제 저장: 실행하지 않음.
