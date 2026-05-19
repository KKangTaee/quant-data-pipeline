# Compare Service Boundary Plan

Status: Implementation complete
Created: 2026-05-19

## 이걸 하는 이유?

Compare / Weighted Portfolio는 `ui-engine-boundary-foundation` phase에서 Single Strategy 다음으로 큰 결합 지점이다.
현재 `app/web/backtest_compare.py`는 form render, strategy별 compare dispatch, multi-strategy 실행 loop, session state, history append, chart render, weighted portfolio builder, saved replay를 한 파일에서 함께 처리한다.

이 task의 목표는 한 번에 전체를 옮기는 것이 아니라, 먼저 Streamlit 없이 실행 가능한 compare execution boundary를 만들고 점진적으로 runner catalog / weighted builder / saved replay를 분리하는 것이다.

## Completed Slices

Slice 1:

- manual compare 실행 loop를 `app/services/backtest_compare_execution.py`로 분리
- compare input / data / system error normalization을 service result로 반환
- `app/web/backtest_compare.py`는 spinner, session state, history append, result render를 유지

Slice 2:

- strategy별 runner catalog와 compare defaults를 `app/services/backtest_compare_catalog.py`로 분리
- Equal Weight / GTAA / Global Relative Strength preset/manual universe resolution을 service가 담당
- Strict Quality / Value universe preset은 UI가 `ComparePresetCatalog`로 주입해 service가 `backtest_common.py`를 import하지 않음
- runtime runner signature filtering을 service가 담당

Slice 3:

- weighted portfolio bundle construction을 `app/services/backtest_weighted_portfolio.py`로 분리
- data trust rows와 monthly component contribution views를 `app/services/backtest_result_read_model.py`로 분리
- `app/web/backtest_result_display.py`는 기존 private helper names를 유지하되 새 read model helper로 위임
- `app/web/backtest_compare.py`는 weight form, session state, history append, result render를 유지

Slice 4:

- saved portfolio replay execution / data assembly를 `app/services/backtest_saved_portfolio_replay.py`로 분리
- service가 strategy rerun, weighted bundle 생성, replay source context, compare / weighted history context를 조립
- `app/web/backtest_compare.py`는 replay 결과를 session state에 반영하고 history append / notice / render를 유지
- Dynamic PIT universe 보정은 아직 `backtest_common.py` 의존이 있어 `resolve_dynamic_inputs` callback으로 주입

## Out Of Scope

이번 task에서 아직 제외:

- compare chart / tab / Candidate handoff UI 변경
- registry JSONL 변경
- preset constant source split from `backtest_common.py`

## Done Criteria

- compare execution / catalog service가 Streamlit을 import하지 않는다.
- weighted portfolio / result read model service가 Streamlit을 import하지 않는다.
- saved portfolio replay service가 Streamlit을 import하지 않는다.
- manual compare 실행은 service result를 통해 성공 / 실패를 UI에 반영한다.
- strategy별 runner dispatch는 service를 통해 수행한다.
- weighted portfolio result bundle은 service를 통해 생성한다.
- saved portfolio replay execution / data assembly는 service를 통해 수행한다.
- existing compare session state key와 history append는 유지한다.
- compile / import smoke / no-Streamlit check가 통과한다.

## Remaining Work

- Manual DB-backed Compare / Weighted / Saved Replay app QA is still needed when DB state is available.
- Next phase task: `practical-validation-service-boundary`.
