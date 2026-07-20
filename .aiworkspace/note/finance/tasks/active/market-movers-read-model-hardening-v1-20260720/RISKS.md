# Risks

Last Updated: 2026-07-20

## Open Risks

### PIT diluted EPS coverage

current TTM PER는 네 개 연속 reported diluted EPS가 모두 있어야 한다. universe coverage가 낮으면 PER unavailable 비율이 높을 수 있다. 3차 DB smoke에서 실제 비율을 기록하고, 누락을 synthetic EPS로 숨기지 않는다.

### Industry taxonomy drift

첫 release는 provider current label을 stable display key로 정리할 뿐 historical membership taxonomy가 아니다. alias table은 작고 명시적으로 유지하고, industry conditional outlook은 계속 보류한다.

### Legacy contract coupling

`tests/test_service_contracts.py`와 기존 UI helper가 DataFrame column 및 research v1 schema에 결합되어 있다. public 함수명과 legacy keys를 유지하면서 새 additive payload로 전환한다.

### Real DB availability

로컬 MySQL이 실행 중이지 않으면 DB smoke를 완료할 수 없다. 이 경우 unit/contract test 결과와 환경 실패를 구분해 기록한다.
