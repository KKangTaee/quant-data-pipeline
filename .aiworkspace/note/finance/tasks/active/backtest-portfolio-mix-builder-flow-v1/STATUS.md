# Status

## 2026-05-30

- 작업 시작.
- 사용자 승인 범위: 기존 `Compare & Portfolio Builder`를 `Portfolio Mix Builder`로 재정의하고, 여러 전략을 weighted mix 하나의 후보로 만들어 Practical Validation에 보내는 흐름으로 정리한다.
- 초기 조사 결과 핵심 수정 파일은 `app/web/backtest_workflow_routes.py`, `app/web/backtest_analysis.py`, `app/web/pages/backtest.py`, `app/web/backtest_compare.py`, 관련 docs / tests다.
- 구현 완료.
- Backtest Analysis visible mode를 `Portfolio Mix Builder`로 바꾸고, legacy `Compare & Portfolio Builder` route는 계속 새 mode로 normalize한다.
- `새 Mix 만들기`는 component portfolio 실행 / weight 구성 / mix 후보 1차 판단 / Practical Validation handoff 흐름으로 정리했다.
- 개별 전략 handoff 보드는 Portfolio Mix Builder 주 흐름에서 호출하지 않고, current weighted mix 전체만 Clean V2 source handoff 대상으로 둔다.
- Mix 후보 handoff 버튼은 mix result, weight discipline, component data trust, component 1차 후보 판단에 hard blocker가 없을 때만 활성화된다.
- 검증 통과: py_compile, targeted gate tests, full `tests.test_service_contracts` 133 tests, `git diff --check`, Browser smoke on `http://127.0.0.1:8502/backtest`.
