# Risks

Last Updated: 2026-07-20

## Open Risks

### PIT diluted EPS coverage

current TTM PER는 네 개 연속 reported diluted EPS가 모두 있어야 한다. 2026-07-20 대형주 10개 bounded DB smoke는 `0/10 READY`였고 모두 `INCOMPLETE_REPORTED_DILUTED_EPS`였다. filing-derived Q4를 reported 값으로 승격하거나 synthetic EPS로 숨기지 않는다. 4차 UI는 unavailable을 정확히 표시하고, coverage 개선은 reported provider quarterly EPS 또는 별도 승인된 PIT source 계약으로 다뤄야 한다.

### Industry taxonomy drift

첫 release는 provider current label을 stable display key로 정리할 뿐 historical membership taxonomy가 아니다. alias table은 작고 명시적으로 유지하고, industry conditional outlook은 계속 보류한다.

### Legacy contract coupling

public façade와 legacy DataFrame key는 유지했으며 research schema는 v2로 전환했다. 기존 visible helper는 legacy snapshot도 계속 읽지만 4차 React shell은 `market_movers_decision_payload_v1`만 사용해야 한다.

### Real DB availability

로컬 MySQL read-only smoke는 완료됐다. 세 coverage의 모든 기간이 `PARTIAL`이므로 4차 trust line에서 valid/total과 gap summary를 숨기지 않는다.

### Repository-wide unrelated regressions

전체 `tests/test_service_contracts.py`는 `839 passed, 13 failed`였다. 실패는 Backtest Practical Validation / Final Review와 Market Sentiment의 기존 코드-계약 drift이며 이번 scoped 파일과 Market Movers focused 126개에는 실패가 없다. 4차 시작 전에 이 결과를 새 회귀로 오인하지 않는다.
