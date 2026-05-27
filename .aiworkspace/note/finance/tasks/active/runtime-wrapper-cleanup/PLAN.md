# Runtime Wrapper Cleanup Plan

Status: Complete
Created: 2026-05-27

## 이걸 하는 이유?

`ui-engine-boundary-foundation`과 cleanup Task 6~7에서 Streamlit UI와 service layer의 책임은 많이 정리됐다.
남은 큰 경계 부채는 `app/runtime/backtest.py`다.

이 파일은 UI payload를 DB-backed strategy runtime으로 변환하는 중심 wrapper지만, 5000 line 이상으로 커져 있다.
그래서 UI agent가 payload / display 흐름을 수정하고, engine agent가 strategy / policy runtime을 다룰 때 같은 파일을 자주 만질 위험이 있다.

이번 task의 목적은 runtime public API를 유지하면서 함수군을 지도화하고, 숫자 결과를 바꾸지 않는 낮은 위험 helper부터 별도 파일로 분리하는 것이다.

## Scope

포함한다.

- `app/runtime/backtest.py` 함수군 map 작성
- public runtime API와 import 사용처 확인
- result bundle / error class / helper contract 중심 characterization test 추가
- 안전한 helper split 적용
- 관련 architecture / project map / phase 문서 정렬

포함하지 않는다.

- strategy simulation 알고리즘 변경
- DB schema / loader 변경
- Streamlit UI 화면 구조 변경
- result 숫자 변경
- registry / saved JSONL 재작성

## Steps

| Step | Goal | Status |
| --- | --- | --- |
| `8-01` | runtime function-family map 작성 | Complete |
| `8-02` | import cycle / public API 사용처 확인 | Complete |
| `8-03` | characterization test 후보 추가 | Complete |
| `8-04` | 낮은 위험 split 적용 | Complete |

## Done Criteria

- `app/runtime/backtest.py`의 함수군과 public caller surface가 task / docs에 기록된다.
- public import path `app.runtime.backtest`와 `app.runtime`은 기존 이름을 유지한다.
- 새 helper 파일이 생기면 책임이 script map에 반영된다.
- `py_compile`, boundary lint, service contract test, diff check가 통과한다.
- 화면 동작이 바뀌지 않는 helper split이면 browser QA는 생략 사유를 기록한다.
