# Backtest Entry Cleanup Tabs V1

## 이걸 하는 이유?

Backtest 첫 화면에 안내 expander, 전략 capability 보조 표, 하단 연구 참고 보드가 함께 보여 사용자가 실제로 해야 할 후보 생성 / 검증 / 최종 검토 흐름보다 보조 설명을 먼저 읽게 된다. 이번 1차는 사용자가 지적한 불필요한 표면을 제거하고, Backtest 단계 선택을 Overview와 같은 Korean-first text tab 문법으로 맞춘다.

## 범위

- `app/web/backtest_page.py`: 상단 안내 제거, 3단계 workflow selector를 `st.pills` + red underline text tab으로 변경한다.
- `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, `app/web/backtest_compare.py`, `app/web/backtest_common.py`: strategy capability snapshot 렌더 경로를 제거한다.
- `app/web/backtest_analysis.py`: 하단 연구 참고 보드를 기본 render path에서 제거한다.
- `tests/test_service_contracts.py`: 제거된 표면과 새 tab 문법이 유지되도록 계약 테스트를 추가한다.
- Durable docs: Backtest UI flow와 roadmap의 stale 설명을 현재 UI에 맞춘다.

## 완료 조건

- 첫 진입 화면에 `Backtest 사용 안내`, `Strategy Capability Snapshot`, `전략 개발 참고`가 보이지 않는다.
- 3개 stage selector가 `후보 분석 · Backtest Analysis`, `실전 검증 · Practical Validation`, `최종 검토 · Final Review`로 표시된다.
- focused tests, py_compile, `git diff --check`, Browser QA를 통과한다.

## 다음 차수 연결

- 2차 후보는 실제 Backtest Analysis 결과 영역의 spacing / Latest Run summary-first 정리다.
- 이번 1차에서는 실행 엔진, registry, saved setup, Practical Validation / Final Review gate 의미를 바꾸지 않는다.
