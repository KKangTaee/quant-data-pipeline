# Market Movers Chart Navigation Polish V1 Plan

Status: Approved
Last Updated: 2026-07-21

## 이걸 하는 이유?

재무 차트는 최대 40개 분기 자료를 한 폭에 압축하면서 시작일과 종료일만 표시해 중간 기간을 식별하기 어렵다. 가격 요약 카드는 값의 방향보다 배경색과 좌측선이 먼저 보여 기존 Overview 시각 체계보다 장식이 강하다. 사용자가 긴 이력을 직접 탐색하고 특정 기간의 정확한 값과 결산일을 확인할 수 있도록 차트 상호작용과 정보 위계를 다듬는다.

## Goal

- 재무 차트 X축에 분기 또는 연간 기간을 표시한다.
- 긴 재무 이력은 가로 스크롤과 pointer drag로 이동한다.
- 막대와 선 모두 hover/focus에서 정확한 결산일과 값을 표시한다.
- 가격 요약은 배경색과 좌측 강조선을 제거하고 값의 양수·음수 텍스트 색만 유지한다.

## Scope

- Modify `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`
- Modify `app/web/streamlit_components/market_movers_workbench/src/style.css`
- Modify `tests/test_overview_market_movers_decision_ui.py`
- Rebuild `component_static/`
- Browser QA at desktop and narrow widths

## Stop Condition

관련 테스트와 React build가 통과하고, 실제 재무 막대·선 차트에서 X축·hover·drag를 확인하며, 가격 요약 카드의 배경·좌측선이 제거된 QA 이미지가 확보되면 종료한다.

## Steps

- [x] 재무 차트 탐색·가격 카드 시각 계약의 실패 테스트 작성
- [x] 실패가 요구사항 부재 때문인지 확인
- [x] 재무 차트 viewport, adaptive period ticks, hover/focus, pointer drag 구현
- [x] 가격 요약 카드 semantic text-only style 적용
- [x] focused tests와 React build 실행
- [ ] desktop/narrow Browser QA 및 스크린샷 저장
- [x] task/root 문서 동기화
- [x] 관련 파일만 커밋
