# Overview Market Context Analog Repair V4

Status: Active
Date: 2026-06-15
Worktree: `sub-dev`

## 이걸 하는 이유?

V3에서 Market Context 하단을 `다음 맥락 체크`, `참고: 과거 유사 맥락`, `근거: 자료 기준 / 출처 상태`로 나누었지만, live UI에서는 여전히 `자료 부족`을 확인만 하고 끝나는 느낌이 강했다. 특히 `참고: 과거 유사 맥락`은 부족한 sector ETF 가격 이력을 어떻게 채워야 하는지 사용자가 바로 알기 어려웠다.

이번 V4는 자료 부족 상태를 숨기지 않고, 부족한 ticker와 row 기준을 보여준 뒤 기존 Overview bounded action facade를 통해 필요한 OHLCV 보강을 실행할 수 있게 만든다. 동시에 `자료 기준 / 출처 상태`는 접힌 상태에서도 정상 / 확인 / 부족 수와 핵심 출처를 바로 읽을 수 있게 보강한다.

## Scope

- Historical analog model에 `coverage_gaps`와 `repair_action`을 추가한다.
- 부족한 sector ETF / 비교 자산 ticker를 일반화해 `Technology -> XLK`에 고정되지 않게 한다.
- `app/jobs/overview_actions.py`에 기존 `run_collect_ohlcv`를 쓰는 bounded Overview action facade를 추가한다.
- `Workspace > Overview > Market Context > 보조 갱신`에서 부족 ETF 가격 이력 보강 버튼을 노출한다.
- `참고: 과거 유사 맥락` 자료 부족 상태를 action-oriented gap panel로 렌더링한다.
- `근거: 자료 기준 / 출처 상태` summary에 상태 개수와 핵심 source pill을 표시한다.

## Out Of Scope

- 새 provider, DB schema, loader, registry / saved JSONL write.
- Overview render 중 자동 provider fetch.
- CSV upload flow.
- 과거 유사 맥락을 예측 모델, 매수 / 매도 신호, validation gate, Final Review decision, Operations monitoring signal로 승격.
- macro / futures / event regime 조건을 붙인 analog expansion.

## Completion Criteria

- historical analog coverage가 부족할 때 부족 ticker / row 기준 / 보강 action metadata가 model에 포함된다.
- UI는 generic `자료 부족` 문구 대신 `부족 ETF 가격 이력 보강` gap panel을 보여준다.
- 보조 갱신에는 부족 ticker만 대상으로 하는 OHLCV 보강 버튼이 연결된다.
- source confidence footer는 접힌 상태에서도 정상 / 확인 / 부족 count와 핵심 source label을 보여준다.
- focused unittest, overview regression suite, py_compile, diff check, Browser QA가 완료된다.
