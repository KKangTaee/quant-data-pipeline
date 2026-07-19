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

## 2차 Decisions

- EPS batch는 canonical `run_collect_financial_statements(freq=quarterly)`만 사용한다.
- price batch는 requested start와 end+1 provider boundary를 사용해 마지막 observation date를 포함한다.
- provider exception/failed symbol은 다음 실행에서 재시도한다.
- 수집 성공 뒤에도 planner가 같은 EOD gap을 반환한 종목만 existing `market_data_issue.limited_price_history`에 기록한다.

## 3차 Decisions

- repair job의 성공 의미는 provider job 성공이 아니라 after plan의 requested-month 전체 READY다.
- partial collection도 이미 저장된 usable rows를 반영하기 위해 materialization을 계속한다.
- 화면 action은 최신 EPS coverage뿐 아니라 60개월 history 부족도 보강할 수 있도록 final Nasdaq status가 BLOCKED인 동안 제공한다.

## 4차 Decisions

- React는 action id/nonce만 전달하고 collection/progress/cache는 Python이 소유한다.
- duplicate event는 React pending state가 아니라 Python session token을 최종 경계로 차단한다.
- repair result는 다음 rerun payload에 한 번만 주입해 성공/부분/실패를 사용자 중심 summary로 보여준다.
- failed job은 기존 cache를 유지하고, partial/success만 valuation cache를 clear한다.

## 5차 Findings And Decisions

- 첫 actual full repair는 2021-08 coverage 94.83% 때문에 59/60으로 끝났다. 기준을 낮추지 않고 missing weight를 다시 추적했다.
- DOCU/OKTA는 당시 basic EPS와 diluted EPS가 동일해 SEC US-GAAP `EarningsPerShareBasicAndDiluted` concept으로 공시했다. edgartools가 이 concept의 `statement_type`을 비워 반환해 canonical statement collector가 유효한 actual을 버리고 있었다.
- 이 combined concept은 이름 그대로 basic/diluted 동일 actual이므로 income statement row와 diluted EPS fallback으로 허용한다. `EarningsPerShareBasic` 단독, FY-only annual proxy, estimate는 계속 제외한다.
- actual DB에 DOCU/OKTA를 재적재하고 60개월을 다시 materialize해 60/60 READY를 확인했다.
- repair plan은 월 gate가 READY여도 구성 종목별 source gap target을 남길 수 있다. 화면 action은 final Nasdaq status가 BLOCKED일 때만 제공하므로 READY 화면에서 불필요한 재수집은 노출되지 않는다.
