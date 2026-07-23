# Runs

- protected Practical Validation registry를 read-only로 확인해 latest GTAA validation 3개가 byte-identical row임을 확인했다.
- current Final Review helper로 latest source / eligibility / source option을 계산해 GTAA가 eligible first option임을 확인했다.
- current focused direct-handler tests 2개는 통과했지만 fragment callback -> root route lifecycle을 검증하지 않음을 확인했다.
- backtest-dev Streamlit process는 current commit 뒤 시작된 fresh process여서 stale server가 직접 원인은 아니다.
- callback ownership RED: 신규 constant 부재로 실패. 구현 뒤 decision workspace 전체 `34 passed`.
- stable-id idempotency RED: 기존 save가 `None`을 반환하고 반복 append해 실패. 구현 뒤 선택 service contract `3 passed`.
- active selector RED: `final_review_active_decision_brief_source_id` 미설정으로 실패. 구현 뒤 선택 route/decision tests `36 passed`.
- boundary regression: decision workspace + refactor boundary `85 passed`; 선택 service contracts `9 passed`.
- wider Practical Validation service class: 변경 소유 26개 통과, 기존 CNN/AAII sentiment expectation drift 2개 실패. 저장/route 호출 경로와 무관한 branch baseline이다.
- full `tests/test_service_contracts.py`: `849 passed`, `18 failed`, subtests 41개 통과. 실패 18개는 기존 branch baseline의 sentiment / Final Review legacy source assertion / Futures Macro / AAII parser drift와 동일하며 이번 신규 저장·route 계약은 통과했다.
- isolated actual Browser lifecycle: 버튼 한 번 뒤 `SAVE_COUNT=1`, `FULL_APP_RUNS=2`, `ACTIVE_STAGE=Final Review`, active candidate key 일치, console warning/error 0.
- `py_compile` 3개 Python surface와 `git diff --check` 통과. 임시 diagnostic app/server는 제거했고 QA screenshot만 generated artifact로 남겼다.
