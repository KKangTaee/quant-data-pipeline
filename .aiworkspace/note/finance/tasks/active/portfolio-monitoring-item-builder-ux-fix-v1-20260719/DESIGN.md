# Portfolio Monitoring Item Builder UX Fix V1 Design

Status: Implemented and verified
Last Updated: 2026-07-19

## Problem

React component는 일반 화면에서 전체 workbench 높이를 `Streamlit.setFrameHeight()`로
iframe에 전달한다. Drawer의 `position: fixed; inset: 0`과 `height: 100%`는 브라우저가
아니라 이 긴 iframe viewport를 기준으로 계산되어 footer가 약 1,536px 지점까지 내려간다.

요청 시작일은 controlled input이지만 blur 시 `search_catalog`를 전송한다. Python route는
view-state event도 rerun하므로 component remount 시 local wizard state가 사라질 수 있다.

## Chosen Design

1. Streamlit iframe은 drawer open 여부와 무관하게 workbench의 자연 높이를 유지한다.
   overlay는 전체 component를 덮고 drawer panel만 `560px`로 제한한다. header/stepper/footer는
   고정 row, body만 `overflow-y: auto`로 스크롤한다.
2. 날짜 input은 로컬 draft만 갱신한다. blur는 서버 요청을 만들지 않는다.
3. catalog 검색처럼 서버 왕복이 필요한 event에는 `item_builder_state`를 넣는다.
4. Python은 drawer step, query, draft의 허용 필드만 정규화해 session에 저장하고 다음
   workspace에 한 번만 포함한다. React는 이 recovery projection으로 초기 state를 만들고,
   stable recovery key를 소비해 동일 snapshot이 X 닫기 상태를 다시 덮어쓰지 못하게 한다.
5. 실제 entry price와 effective date의 최종 권위는 기존 `add_item` command에 유지한다.
   review의 사전 표시가 없으면 기존 문구 `등록 시 확정`을 사용한다.

## Tradeoff

날짜 blur 직후 effective start를 미리 조회하지 않으므로 review 전 자동 price preview는
줄어든다. 대신 입력이 사라지는 rerun을 제거하고, 최종 등록 시 backend가 동일한 가격
검증을 수행한다. 추후 명시적 `시작 가격 확인` CTA가 필요하면 같은 recovery contract로
안전하게 추가할 수 있다.

## Files

- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- `app/web/final_selected_portfolio_dashboard.py`
- `tests/test_portfolio_monitoring_page.py`

## Test Contract

- recovery state는 valid step/query/draft를 보존하고 invalid enum·shape를 안전한 기본값으로 정규화한다.
- catalog search event는 current wizard state를 포함한다.
- drawer open/closed 모두 auto measurement를 사용하고 drawer panel만 560px다.
- 동일 recovery snapshot은 새 object identity로 다시 전달돼도 한 번만 적용한다.
- 날짜 input source에는 server-emitting `onBlur`가 없다.
- Python projection은 임의 필드를 전달하지 않고 한 번 사용 후 제거한다.
