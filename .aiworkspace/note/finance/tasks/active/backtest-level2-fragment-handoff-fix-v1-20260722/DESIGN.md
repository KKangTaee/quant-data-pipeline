# Backtest Level2 Fragment Handoff Fix V1 Design

## 문제

Level1 결과 컴포넌트는 `@st.fragment` 안에서 렌더링된다. React 버튼의 `on_change` callback이 intent를 먼저 소비하면서 후보 source와 `backtest_requested_panel = "Practical Validation"`을 만들지만, callback에서 요청한 full-app rerun은 실제로 fragment rerun으로 끝난다. root `init_backtest_state()`가 다시 실행되지 않아 화면은 Level1에 남는다.

## 검토한 접근

1. **권장: callback 선소비 제거**
   - custom component가 fragment를 재실행하게 두고 반환 intent를 fragment 본문에서 소비한다.
   - 본문에서 `st.rerun(scope="app")`을 요청하면 root route owner가 기존 요청을 처리한다.
   - 저장·route source-of-truth를 바꾸지 않는 최소 수정이다.

2. callback에서 active stage 세 키를 직접 변경
   - 즉시 이동할 수 있지만 `_init_backtest_state()`의 route ownership을 복제한다.
   - stage 관련 session key drift 위험이 있어 채택하지 않는다.

3. 전체 Level1 work fragment 제거
   - 문제는 사라지지만 모든 설정 상호작용을 full-app rerun으로 돌려 비용과 변경 범위를 키운다.
   - 이 버그의 최소 수정이 아니므로 채택하지 않는다.

## 선택 설계

- `render_backtest_analysis_result_workspace_component()` 호출에서 `on_change`를 제거한다.
- component가 반환한 intent는 기존 `consume_result_workspace_intent()`로 검증한다.
- 성공한 경우 기존대로 `st.rerun(scope="app")`을 호출한다.
- callback 전용 helper와 `partial` import를 제거한다.
- React source, candidate source builder, JSONL store, workflow route mapping은 변경하지 않는다.

## 오류와 중복 처리

- invalid/stale identity, fingerprint mismatch, disabled action은 기존 validation이 계속 거부한다.
- consumed nonce는 handler 실행 뒤 기록되므로 같은 component value의 후속 rerun에서 재저장하지 않는다.
- actual handler 예외는 기존과 동일하게 표면화하며 이번 task에서 숨기거나 retry하지 않는다.

## 검증

- 자동 테스트는 component 호출에 callback이 없고 반환 intent가 한 번 소비되며 full-app rerun이 요청되는지 확인한다.
- 실제 Browser QA는 registry를 쓰지 않는 in-memory handler로 fragment 밖 marker가 갱신되는지 확인한다.
- high-level Backtest 단계 의미와 storage boundary는 바뀌지 않으므로 flow/project map은 수정하지 않는다.
