# Backtest Data Trust Summary Redesign V1

## 이걸 하는 이유?

`Latest Backtest Run`의 기존 `Data Trust Summary`는 영어 상태 카드와 raw 날짜 badge를 먼저 보여줘, 처음 쓰는 사용자가 `이 결과를 읽어도 되는지`, `어디까지 계산됐는지`, `무엇을 먼저 확인해야 하는지`를 바로 판단하기 어려웠다.

## Scope

- `app/web/backtest_result_display.py`의 Data Trust Summary 렌더만 변경
- 상단을 한국어 `데이터 기준 요약` 패널로 재구성
- `계산 기준일 / 가격 기준 / 사용 데이터 / 검토 큐` 요약으로 중복 정보를 압축
- raw guide row와 `세부 데이터 기준` expander를 기본 화면에서 제거하고, warnings / 제외 종목 / 결측 row는 같은 패널의 `이번 실행 검토 큐`로 통합
- Strategy runtime, result bundle schema, run history, registry / saved, Practical Validation / Final Review persistence는 변경하지 않음

## Completion Criteria

- Run Backtest 직후 Data Trust 영역에서 기존 `Result Integrity`, `Price Freshness`, `Requested End` 중심 카드 / badge가 보이지 않는다.
- 사용자가 결과 기준일과 확인할 점을 한국어 결론 중심으로 읽을 수 있다.
- Focused contract, service contract, py_compile, Browser QA를 통과한다.
