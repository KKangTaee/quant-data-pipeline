# 검증 공백과 기존 이슈

요청 범위의 수집·DB·GTAA 기간 복구 검증은 완료했다. 전체 프로젝트 테스트는 실행하지 않았고, 영향 범위 테스트 36개를 실행했다.

기존 사용자 registry 변경, run-history, saved setup, QA image는 보존하고 커밋에서 제외한다. 이번 수정은 상장폐지/종목 변경/실제 provider no-data 등 별도 기존 제외 조건을 변경하지 않는다.

## 변경 전 정책에서도 재현된 기존 테스트 불일치

넓은 BacktestRuntimeContractTests에서 발견한 아래 12개는 이번 변경 전 제외 정책으로도 동일하게 실패했다. 이 task에서 Final Review / Practical Validation UI와 오래된 source-string 계약을 수정하지 않았다.

- `tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_queue_is_integrated_into_decision_desk`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_investment_report_react_component_emits_intent_only`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_sentiment_timing_rebalance_boundary_is_documented`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_liquidity_layer_copy_is_connected_to_strict_form_and_result_display`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_downstream_flows_wait_for_explicit_replay`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_step1_receives_backtest_review_focus_queue`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_candidate_must_be_confirmed_before_decision_surfaces_render`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_final_review_decision_intent_appends_once_in_python`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow3_uses_conclusion_summary`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board`
- `tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_profile_belongs_to_flow2_execution_setup`
