# Futures Macro Thermometer Validation V1 Plan

## 이걸 하는 이유?

Macro Thermometer V1은 현재 선물 일봉 움직임을 표준화해 해석을 돕지만, 단순 heuristic만 표시하면 사용자가 신호의 과거 일관성과 데이터 신뢰도를 과대평가할 수 있다. 이번 task는 과거 daily row를 point-in-time으로 재계산해 scenario별 hit / sample / forward return evidence를 만들고, 현재 해석 옆에 confidence를 표시한다.

## Scope

- 저장된 `futures_ohlcv` daily row를 우선 사용한 historical validation read model
- 부족한 비교 대상은 `nyse_price_history` ETF proxy row로 대체
- 날짜별 Macro Thermometer score / scenario point-in-time 재계산
- 1D / 5D / 20D forward return, hit rate, false positive, max adverse move, threshold sensitivity, score-target relationship summary
- current snapshot confidence 산출과 UI 표시
- `Overview > Futures Monitor > Macro Thermometer` UI 보강
- focused service contract tests, synthetic scenario test, actual smoke run, Browser QA
- runbook / project map / data docs alignment

## Non Goals

- 투자 판단 자동화
- 미래 수익률 보장 또는 trading signal promotion
- live alert, order, approval, broker / account sync, auto rebalance
- exchange-grade futures roll model 구현
- 새 validation registry / saved setup persistence

## Proposed File Areas

| Area | Files |
| --- | --- |
| Current snapshot service | `app/services/futures_macro_thermometer.py` |
| Historical validation service | `app/services/futures_macro_validation.py` |
| Overview UI | `app/web/overview_dashboard.py` |
| Ingestion helper defaults | `app/web/overview_dashboard.py`, `app/web/streamlit_app.py` |
| Tests | `tests/test_service_contracts.py` |
| Docs | `.aiworkspace/note/finance/docs/`, `.aiworkspace/note/finance/tasks/active/futures-macro-thermometer-validation-v1/` |

## Done Criteria

- Historical validation service returns compact summary without Streamlit imports.
- Current Macro Thermometer snapshot includes confidence and validation summary fields.
- UI shows confidence, sample size / hit rate, validation caveats, and strong / weak / conflicting evidence separately.
- Tests cover confidence downgrade, point-in-time validation, scenario metrics, and proxy/source labeling.
- Smoke run attempts actual stored-data validation.
- Browser QA confirms the enhanced Macro Thermometer renders.
