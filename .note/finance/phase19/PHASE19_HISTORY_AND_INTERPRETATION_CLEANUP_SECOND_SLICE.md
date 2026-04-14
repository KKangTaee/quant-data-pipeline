# Phase 19 History And Interpretation Cleanup Second Slice

## 무엇을 바꿨는가
- strict annual selection history와 interpretation summary가
  `Rejected Slot Handling Contract`를 같은 언어로 읽도록 정리했다.

## 기존 문제
- first slice에서 explicit contract는 single / compare / payload / warning까지는 정리됐지만,
  history와 interpretation summary는 아직 그 언어를 끝까지 쓰지 못했다.
- 내부적으로는 아래 정보가 result row에 있었지만,
  selection history를 만드는 중간 단계에서 일부가 빠져
  operator가 실제 fill / cash-retention 상태를 자연스럽게 읽기 어려웠다.
  - `Rejected Slot Fill Count`
  - `Rejected Slot Fill Active`
  - `Partial Cash Retention Active`

## 이번 slice의 정리 포인트
- selection history row에 `Rejected Slot Handling` 컬럼을 추가했다.
- interpretation summary에 아래 요약값을 추가했다.
  - `Rejected Slot Handling`
  - `Filled Events`
  - `Cash-Retained Events`
- row-level interpretation 문구도
  - 어떤 handling contract가 실행되었는지
  - fill이 있었는지
  - 현금 유지가 있었는지
  를 explicit contract 기준으로 설명하게 바꿨다.

## 화면에서 어떻게 달라졌는가
- `Selection History`
  - operator는 내부 boolean 조합 대신
    `Rejected Slot Handling`, `Filled Tickers`, `Filled Count` 같은 읽기 쉬운 컬럼을 본다.
- `Interpretation`
  - 요약 표에서 현재 run이 어떤 handling contract를 썼는지,
    fill event와 cash-retained event가 얼마나 있었는지 바로 읽을 수 있다.
- `History` 표 자체는 계속 깔끔하게 유지한다.
  - 내부 boolean 컬럼은 interpretation 계산에만 쓰고
  - display surface에서는 숨긴다.

## 구현 위치
- `app/web/pages/backtest.py`
  - selection history row builder
  - interpretation summary builder
  - interpretation help popover
  - history tab dataframe rendering

## 왜 필요한가
- `Phase 19`의 목적은
  structural option을 "쓸 수 있는 contract"로 정리하는 것이다.
- 그러려면 form에서만 contract 이름이 보이는 것으로는 부족하고,
  history와 interpretation도 같은 언어를 써야
  이후 candidate review와 deep validation이 덜 흔들린다.

## 이번 slice에서 확인한 것
- `python3 -m py_compile app/web/pages/backtest.py`
- `.venv/bin/python` import smoke
- broad rerun은 이번 slice 범위에 포함하지 않음

## 남은 일
- risk-off / weighting contract도 history / interpretation에서 같은 수준으로 읽기 쉽게 맞출지 검토
- manual UI validation checklist 수행
