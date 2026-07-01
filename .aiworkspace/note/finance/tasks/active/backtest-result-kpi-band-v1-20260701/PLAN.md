# Plan

## 이걸 하는 이유?

Run Backtest 후 결과 상단이 `전략 정보 pill -> 별도 metric row -> 데이터 기준 요약`으로 끊겨 보여 핵심 성과와 결과 제목이 한 덩어리로 읽히지 않았다.
사용자는 먼저 전략 결과와 핵심 성과를 한 화면 덩어리로 보고, 그 다음 데이터 기준 요약으로 해석 가능성을 확인해야 한다.

## Scope

- `app/web/backtest_result_display.py`
  - latest run result header에 `summary_df` 기반 KPI band를 통합한다.
  - 기존 별도 `_render_summary_metrics(summary_df)` row는 latest run 기본 path에서 제거한다.
- `tests/test_service_contracts.py`
  - latest run result order와 integrated KPI band contract를 고정한다.
- Backtest UI flow 문서와 root handoff log를 갱신한다.

## Non-Scope

- Strategy runtime, result bundle schema, DB loader, registry / saved setup, Practical Validation / Final Review persistence는 변경하지 않는다.
- Compare / Candidate Library 등 다른 화면의 공용 `_render_summary_metrics` 사용은 유지한다.
