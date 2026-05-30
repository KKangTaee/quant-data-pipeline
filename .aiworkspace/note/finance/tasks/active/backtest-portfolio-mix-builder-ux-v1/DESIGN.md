# Design

## Current Shape

- `app/web/backtest_compare.py`가 Portfolio Mix Builder 전체를 렌더링한다.
- `_render_strategy_compare_workspace()`가 component 실행 section과 결과 container를 만든다.
- `_render_compare_results()`가 component 실행 결과를 9개 tab으로 보여준다.
- `_render_weighted_portfolio_builder()`가 weight 입력과 weighted result / 후보 판단 / saved mix 저장을 렌더링한다.
- `_render_weighted_portfolio_practical_validation_panel()`이 mix 후보 1차 판단과 handoff button을 담당한다.

## Direction

- 화면 상단에 단계 strip을 추가해 현재 흐름을 먼저 보여준다.
- component 실행 결과는 compact overview card + 4개 tab(`요약`, `차트`, `진단`, `상세`)로 재구성한다.
- raw summary, meta, focused strategy detail은 기본 접힘 또는 detail tab으로 낮춘다.
- weight 입력 영역은 total weight progress와 next action copy를 함께 보여준다.
- mix 후보 판단은 결론 / 차단 사유 / handoff action을 먼저 보여주고 criteria table은 접힘 처리한다.

## Tradeoff

- 기존 상세 정보는 제거하지 않고 낮은 위계로 이동한다.
- 계산 결과와 handoff gate의 의미는 유지한다.
- CSS는 Portfolio Mix Builder 전용 class로 제한해 다른 Backtest tab의 스타일 영향 범위를 줄인다.
