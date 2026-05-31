# Overview Sector / Industry Polish Plan

Status: Active
Owner: sub-dev
Started: 2026-05-30

## 이걸 하는 이유?

Sector / Industry 화면은 Market Movers보다 더 넓은 그룹 흐름을 읽는 영역이다. 현재 1차 구현은 ranking / line trend / positive ticker detail을 제공하지만, 컨트롤 변경 시 Trend Groups 선택이 과하게 초기화되고 상승/하락 흐름이 선 차트만으로는 빠르게 읽히지 않는다. 그룹별 breadth, 개선/악화, ticker leader의 직전 기간 맥락을 함께 보여 사용자가 섹터 회전과 내부 참여도를 더 빠르게 판단하도록 개선한다.

## Scope

- Trend Groups 선택값을 탭 내부 컨트롤 변경에도 유지한다.
- Trend visual을 line-only에서 heatmap / line / latest delta로 확장한다.
- Positive Group Detail ticker bar에 sector color와 previous-return marker를 적용한다.
- Group read model에 breadth, cap-vs-equal gap, concentration, latest trend delta를 추가한다.
- Browser QA screenshot을 남긴다.

## Out Of Scope

- 저장, 메모, 사용자 watchlist persistence.
- broker order, live alert, auto rebalance.
- 새 외부 provider 수집.
- Backtest / Practical Validation workflow 변경.

## Verification

- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py`
- focused `tests.test_service_contracts`
- `git diff --check`
- Browser QA on `http://localhost:8501`
