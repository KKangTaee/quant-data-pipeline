# Overview Market Context Nasdaq-100 Coverage Repair Action V1 Notes

Last Updated: 2026-07-13

## Decisions

- 버튼명은 EPS 외 가격/holdings/materialization까지 포함하므로 `60개월 가치평가 자료 보강`으로 한다.
- 최근 구성 종목만이 아니라 최근 60개월 historical holdings universe를 대상으로 한다.
- 사용자는 같은 화면에서 동기적으로 완료까지 기다린다.
- planner가 부족한 target만 선택하고 종목 단위 DB UPSERT로 재실행을 이어받는다.
- foreign/FY-only annual proxy, coverage gate 완화, missing value 합성은 하지 않는다.
- READY 전환을 보장하지 않고 무료 원천 미지원이면 갱신된 blocker를 유지한다.

## Existing Boundaries To Reuse

- Nasdaq monthly reconstruction: `finance/data/nasdaq100_valuation.py`
- standard ingestion facade: `app/jobs/ingestion_jobs.py`
- Overview UI action facade: `app/jobs/overview_actions.py`
- combined valuation cache/renderer: `app/web/overview/market_context_helpers.py`
- React component event bridge: `app/web/overview/market_context_react_component.py`
- blocker surface: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`

## 1차 Discoveries

- provider가 `Equity`로 잘못 분류한 USD/future도 symbol/name 기준 보조 필터가 필요하다.
- 기존 latest-as-of price는 과거 마지막 가격을 이후 월까지 carry-forward해 상장폐지/거래중단 gap을 숨길 수 있었다.
- monthly valuation의 종목 가격은 observation month 안의 실제 EOD가 있을 때만 coverage로 인정한다.
- pandas DataFrame의 unresolved symbol은 `None`이 `NaN`으로 바뀌므로 identity normalization에서 null-like 처리가 필요하다.
