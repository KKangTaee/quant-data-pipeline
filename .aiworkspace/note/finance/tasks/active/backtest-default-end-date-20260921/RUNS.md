# 검증

- RED: 새 날짜 기본값 회귀 테스트 1개가 고정값 2026-07-18 때문에 실패, prefill/draft 보존 2개는 통과.
- venv에 pytest가 없어 `/tmp/codex-backtest-pytest`에 테스트 runner만 설치하고 PYTHONPATH로 사용. 프로젝트 의존성/lock 변경 없음.
- GREEN: 설정 workspace 및 결과 workspace pytest: 91 passed, 1 기존 실패, deprecation warning 3개.
- 기존 실패: `test_tactical_strategy_default_payload_has_exact_legacy_key_set[Risk-On Momentum 5D]`. payload에 analysis_intensity가 있고 오래된 기대값에는 random_iterations/run_sensitivity_suite/run_comparison_suite가 있어 불일치. HEAD의 변경 전 `_date_fields`를 메모리에서 복원하여 동일 실패를 확인했다.
- 독립 코드 리뷰: actionable finding 없음.
- 실행 중인 Streamlit이 이전 module 기본값을 유지해 8510 서버 재시작 (PID 44578). 새 브라우저 세션의 핵심 실행 설정 종료일 2026-09-21 확인.
- GTAA 새 설정 종료일 2026-09-21 Browser QA 확인. screenshot `/tmp/backtest-default-end-date-20260921-qa.png` (generated, commit 제외). Python compile 및 git diff --check 통과.
