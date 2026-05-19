# Compare Service Boundary Plan

Status: In progress
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

## Remaining Scope

이번 task에서 아직 제외:

- weighted portfolio bundle builder 이동
- saved portfolio replay 이동
- compare chart / tab / Candidate handoff UI 변경
- registry JSONL 변경

## Done Criteria For Current Slice

- compare execution / catalog service가 Streamlit을 import하지 않는다.
- manual compare 실행은 service result를 통해 성공 / 실패를 UI에 반영한다.
- strategy별 runner dispatch는 service를 통해 수행한다.
- existing compare session state key와 history append는 유지한다.
- compile / import smoke / no-Streamlit check가 통과한다.

## Remaining Work In This Task

- `_build_weighted_portfolio_bundle`를 service로 옮기려면 `backtest_result_display.py`의 data-only helper 의존성을 먼저 분리해야 한다.
- saved portfolio replay는 manual compare service pattern이 안정된 뒤 별도 slice로 옮긴다.
