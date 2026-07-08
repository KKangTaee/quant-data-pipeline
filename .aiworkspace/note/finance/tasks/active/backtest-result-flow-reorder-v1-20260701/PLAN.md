# Backtest Result Flow Reorder V1

## 이걸 하는 이유?

Run Backtest 직후 결과 화면이 `데이터 기준 요약 -> 전략 결과 -> 실전 검증 -> 상세 결과` 순서로 읽혀, 사용자가 먼저 보고 싶은 전략 성과보다 해석 조건과 다음 단계 action을 먼저 보게 됐다.

이번 작업은 결과 화면의 목적을 `결과 확인 -> 기준 확인 -> 상세 검토 -> 다음 단계 판단`으로 재정렬한다.

## Scope

- `app/web/backtest_result_display.py`의 latest run 결과 렌더 순서만 변경
- `Latest Backtest Run` 제목 제거
- 전략명 기반 `백테스트 결과` 헤더 추가
- 순서를 `결과 헤더 -> 핵심 성과 metric -> 데이터 기준 요약 -> 상세 결과 tabs -> 실전 검증 Handoff`로 변경
- Strategy runtime, result bundle schema, registry / saved / Practical Validation persistence는 변경하지 않음

## Completion Criteria

- Run Backtest 후 `Latest Backtest Run` 제목 없이 전략명 중심 결과 헤더가 먼저 보인다.
- 핵심 성과 metric이 Data Trust보다 먼저 보인다.
- Data Trust는 성과 해석 기준으로 metric 다음에 위치한다.
- Practical Validation handoff는 상세 결과 tabs 아래 다음 단계 영역으로 내려간다.
- Focused contract, service contract, py_compile, Browser QA를 통과한다.
