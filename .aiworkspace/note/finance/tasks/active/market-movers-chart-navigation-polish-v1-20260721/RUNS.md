# Runs

Last Updated: 2026-07-21

## Red / Green

- baseline: `.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py -q` -> `20 passed`
- RED: 신규 차트 탐색/가격 카드 계약 2개 -> 요구 구현 및 기존 tint CSS 때문에 `2 failed`
- GREEN: 동일 2개 -> `2 passed`

## Final Automated Verification

- `.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py tests/test_overview_market_mover_research.py -q` -> `29 passed`
- `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_mover or market_movers' -q` -> `126 passed, 726 deselected`
- `npm run build` in `app/web/streamlit_components/market_movers_workbench` -> `170 modules transformed`, production build success
- `git diff --check` -> pass
- 추가 `npx tsc --noEmit`은 이 component package에 기존 `@types/react` / `@types/react-dom`이 없어 전체 TSX declaration error로 실행 불가했다. 이번 범위에서 dependency는 변경하지 않았고 canonical Vite build는 통과했다.

## Browser QA

- `http://localhost:8530/` reload 뒤 DOM snapshot 단계에서 Browser localhost URL policy가 접근을 차단했다.
- 우회 browser/alternate URL을 사용하지 않았으며 desktop/narrow hover·drag screenshot은 미생성 상태다.
