# Notes

- GTAA validation `validation_selection_latest_backtest_run_gtaa_a9ab553b_5d2d4707`은 같은 JSON row로 3회 append됐다.
- 해당 validation은 `can_save_and_move=true`, current Final Review eligibility=true이며 실제 source option에 포함된다.
- 저장 handler와 Final Review candidate loader는 동작한다. 결함은 fragment callback이 persistence/navigation intent를 먼저 소비하는 lifecycle 경계다.
- current Final Review는 `final_review_active_decision_brief_source_id`를 소비하지만 Practical Validation handoff는 legacy selector key만 설정한다.
- 기존 registry 중복 행은 append-only 원칙에 따라 보존한다.
- callback은 replay / recheck selection / resolution action만 선소비하고, `save_audit_only`와 `save_and_move`는 fragment 본문 consumer가 소유한다.
- `save_practical_validation_result()`는 stable `validation_id`가 이미 있으면 append하지 않고 `False`를 반환한다. handoff는 저장 여부와 무관하게 현재 validation payload로 계속 가능하다.
- 성공 handoff는 compatibility key와 함께 `final_review_active_decision_brief_source_id`를 설정해 Final Review가 방금 인계한 후보를 연다.
- isolated Browser QA는 production component adapter와 handler를 사용하되 persistence만 in-memory counter로 대체해 protected registry를 쓰지 않았다.
