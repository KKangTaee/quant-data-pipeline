# Notes

- GTAA validation `validation_selection_latest_backtest_run_gtaa_a9ab553b_5d2d4707`은 같은 JSON row로 3회 append됐다.
- 해당 validation은 `can_save_and_move=true`, current Final Review eligibility=true이며 실제 source option에 포함된다.
- 저장 handler와 Final Review candidate loader는 동작한다. 결함은 fragment callback이 persistence/navigation intent를 먼저 소비하는 lifecycle 경계다.
- current Final Review는 `final_review_active_decision_brief_source_id`를 소비하지만 Practical Validation handoff는 legacy selector key만 설정한다.
- 기존 registry 중복 행은 append-only 원칙에 따라 보존한다.
