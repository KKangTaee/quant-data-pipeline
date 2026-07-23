# Practical Validation Final Review Route Fix V1 Design

## 문제

Practical Validation의 `저장하고 Final Review로 이동`은 validation JSONL append까지 완료하지만 화면은 Practical Validation에 남는다. 사용자가 이동 실패로 판단해 다시 누르면 같은 `validation_id`가 append-only registry에 반복 저장된다.

실제 GTAA 실행에서는 같은 validation row가 3번 저장됐고, 해당 row는 Final Review Gate와 current eligibility를 모두 통과했다. 따라서 데이터 생성이나 Final Review 후보 필터가 아니라 `Practical Validation fragment -> root workflow shell` 라우팅 경계의 문제다.

## 검토한 접근

### 1. 권장: persistence/navigation intent만 callback 선소비에서 분리

- `run_replay`, 재검증 범위 선택처럼 fragment 안에서 즉시 상태를 다시 투영해야 하는 local action은 기존 callback 경계를 유지한다.
- `save_audit_only`, `save_and_move`는 custom component `on_change` callback에서 소비하지 않는다.
- component가 fragment 본문에 반환한 intent를 기존 Python consumer가 검증·처리한다.
- `save_and_move` 성공 뒤 `st.rerun(scope="app")`이 root `init_backtest_state()`까지 도달해 `backtest_requested_panel = "Final Review"`를 소비한다.

장점은 replay UX를 유지하면서 저장과 navigation만 root rerun 경계로 옮기는 최소 변경이라는 점이다.

### 2. 모든 Practical Validation callback 제거

- component 반환 intent만 사용하므로 lifecycle은 단순해진다.
- replay 실행과 local selection까지 모두 fragment 본문 재실행에 의존해 기존 즉시 projection 계약을 넓게 바꾼다.
- 현재 결함보다 영향 범위가 커서 채택하지 않는다.

### 3. callback에서 active stage key 직접 변경

- `backtest_active_stage`, `backtest_active_panel`, `backtest_workflow_active_panel`을 직접 쓰면 즉시 이동할 수 있다.
- root shell의 route ownership을 복제하고 세 키의 drift 가능성을 만든다.
- 기존 `backtest_requested_panel` 계약을 우회하므로 채택하지 않는다.

## 선택 설계

### Intent lifecycle

- decision component callback의 `allowed_actions`에서 `save_audit_only`, `save_and_move`를 제외한다.
- fragment 본문의 `_consume_practical_validation_decision_workspace_intent(..., rerun_scope="fragment")`가 persistence intent를 처리한다.
- `save_audit_only`는 fragment rerun으로 저장 notice를 다시 투영한다.
- `save_and_move`는 기존 handler의 explicit `scope="app"` rerun을 유지해 root route owner로 승격한다.

### Idempotent persistence

- 저장 전에 현재 registry에서 같은 `validation_id`가 이미 존재하는지 확인한다.
- 이미 존재하면 row를 다시 append하지 않되 handoff session payload와 Final Review 이동은 계속 수행한다.
- append-only history는 재작성하거나 삭제하지 않는다. 이미 생긴 중복 3행도 보존한다.
- 중복 판정 identity는 display title이나 source id가 아니라 stable `validation_id`다.

### Final Review active candidate handoff

- Practical Validation은 현재 Final Review가 실제로 소비하는 `final_review_active_decision_brief_source_id`에 `practical_validation_result:<validation_id>`를 전달한다.
- 기존 `final_review_source_selected`, `final_review_confirmed_candidate_key`는 현재 남아 있는 fallback/compatibility 경계를 위해 유지한다.
- Final Review는 전달된 key가 현재 allowed candidate에 있을 때 해당 후보를 열고, 없으면 기존 첫 eligible 후보 fallback을 유지한다.

## 오류 처리

- current-session replay가 없거나 Gate가 차단되면 기존 방어 문구와 저장 차단을 유지한다.
- stale validation id, source mismatch, disabled intent는 기존 Python 검증이 계속 거부한다.
- registry read가 실패하면 중복 여부를 확정할 수 없으므로 기존 append 동작을 조용히 계속하지 않는다. 현재 runtime loader가 표면화하는 오류를 유지해 저장 성공을 오표시하지 않는다.
- 동일 validation이 이미 저장된 경우에는 성공 handoff로 처리하되, 별도 운영 진단 패널은 추가하지 않는다.

## 검증 계약

- callback action set에 persistence/navigation action이 포함되지 않는 RED/GREEN test
- 동일 `validation_id`로 save-and-move를 두 번 호출해 registry append가 한 번만 실행되는 test
- save-and-move가 current Final Review active candidate key를 설정하는 test
- root route owner가 요청 panel을 소비하는 기존 contract regression
- 실제 Browser에서 버튼 한 번으로 저장 1회와 Final Review 도달을 확인하는 lifecycle QA

## 범위 밖

- validation registry 기존 중복 행 삭제 또는 rewrite
- Final Review 판단/Monitoring 저장 의미 변경
- provider 수집, replay 계산, Gate 기준 변경
- run/job/row 중심 운영 진단 패널 추가
