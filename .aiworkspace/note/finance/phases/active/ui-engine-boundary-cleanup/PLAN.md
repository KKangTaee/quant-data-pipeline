# UI Engine Boundary Cleanup Plan

Status: Active
Created: 2026-05-27

## 이걸 하는 이유?

`ui-engine-boundary-foundation` phase에서 Streamlit 화면 코드와 engine / runtime 책임을 1차로 분리했다.
지금의 목적은 새 UI framework로 갈아타는 것이 아니라, 현재 Python / Streamlit 구조 안에서 이미 만든 경계를 더 선명하게 만드는 것이다.

현재 hard violation은 없다.
다만 `app/services`가 아직 `app/web`의 Streamlit-free helper를 일부 import하고 있고, Practical Validation diagnostics와 runtime wrapper 일부 파일이 커져서 이후 UI agent와 engine agent가 같은 파일을 만질 가능성이 남아 있다.

이 phase는 그 남은 구조 부채를 정리해, 다음 개발자가 파일 위치만 보고도 "화면 책임", "service orchestration", "runtime / repository", "finance engine"을 구분할 수 있게 만드는 cleanup phase다.

## Scope

포함한다.

- `app.services/app.runtime -> app.web` advisory import 제거
- Practical Validation provider context / curve helper의 위치 재정리
- 큰 Practical Validation diagnostics helper의 책임 단위 분리 계획 및 안전한 extraction
- 큰 runtime wrapper의 분리 후보를 함수군 단위로 분석하고, 안전한 부분부터 정리
- boundary lint와 service contract test를 후속 구조에 맞게 강화
- docs / runbook / root handoff log 정렬

포함하지 않는다.

- Next.js / React / FastAPI 전환
- Streamlit 화면 UX polish
- DB schema 변경
- provider ingestion source 추가
- strategy simulation 알고리즘 변경
- registry / saved JSONL 재작성
- live trading, broker order, auto rebalance

## Current Baseline

2026-05-27 audit 기준:

- `check_ui_engine_boundary.py` 결과: hard violations 없음, PASS
- 남은 advisory 3건:
  - `app/services/backtest_practical_validation_diagnostics.py` -> `app.web.backtest_practical_validation_curve`
  - `app/services/backtest_practical_validation_diagnostics.py` -> `app.web.backtest_practical_validation_connectors`
  - `app/services/backtest_practical_validation_replay.py` -> `app.web.backtest_practical_validation_curve`
- 큰 cleanup 후보:
  - `app/services/backtest_practical_validation_diagnostics.py`: 2956 lines
  - `app/runtime/backtest.py`: 5191 lines
  - `app/runtime/final_selected_portfolios.py`: 1064 lines
  - `app/runtime/candidate_library.py`: 800 lines

## Target Architecture

```text
app/web
  Streamlit 화면, form, session state, routing, user feedback

app/services
  Streamlit-free use-case service, validation/result/evidence orchestration

app/runtime
  Streamlit-free DB-backed runtime wrapper, registry/repository/read model

finance/*
  data ingestion, loaders, strategy engine, transform, performance
```

cleanup 이후에는 `app/services`와 `app/runtime`이 `app/web`을 import하지 않는 상태를 목표로 한다.
UI는 service / runtime 결과를 받아 표시하지만, service / runtime은 UI helper에 기대지 않는다.

## Phase Done Criteria

- boundary lint advisory가 0건이다.
- `app.services/app.runtime -> app.web` import를 hard fail로 올릴 수 있다.
- Practical Validation provider context / curve helper가 Streamlit-free 위치로 이동했다.
- diagnostics service는 orchestration file과 계산 helper file의 책임이 구분되어 있다.
- runtime 큰 파일은 최소한 function-family map과 안전한 split 기준이 문서화되어 있고, 가능한 낮은 위험 split이 적용되어 있다.
- service contract test와 boundary lint가 phase 이후 구조를 보호한다.
- 브라우저로 확인 가능한 UI 변경이 생긴 task는 Streamlit 화면에서 직접 확인한다.
