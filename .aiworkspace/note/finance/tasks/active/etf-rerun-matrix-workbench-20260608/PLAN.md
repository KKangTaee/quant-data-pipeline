# ETF Rerun Matrix Workbench 4B Plan

## Why

4A가 ETF 3종의 current-anchor readiness를 read-only로 보여줬지만, 다음 판단에는 최신 DB-backed rerun을 같은 화면에서 session-only로 비교할 실행 표면이 필요하다.

4B는 Global Relative Strength, Risk Parity Trend, Dual Momentum의 rerun scenario matrix를 Backtest Analysis에 추가해 ETF current-candidate promotion 전의 실행 근거를 모은다. 결과는 화면 session state에만 두며 workflow registry, saved setup, run history, provider snapshot, validation/final/monitoring artifact는 쓰지 않는다.

## Scope

- Streamlit-free rerun matrix service를 만든다.
- ETF 3종의 scenario plan과 storage boundary를 read model로 제공한다.
- 사용자가 선택한 ETF 전략의 matrix만 버튼 실행한다.
- 결과는 session-only compact evidence table로 표시한다.
- Backtest Analysis 상단의 evidence / anchor panel 흐름 뒤에 UI를 연결한다.

## Out Of Scope

- registry / saved JSONL / run history rewrite
- strategy runtime behavior 변경
- DB schema 변경
- provider / FRED direct fetch
- Current candidate promotion write
- Practical Validation result write
- ETF provider snapshot generation
- live trading / broker order / auto rebalance 설계

## Completion Criteria

- service unit test가 Streamlit-free, read-only, injected runner execution, error capture를 검증한다.
- Backtest Analysis UI에서 matrix plan과 session-only run control이 보인다.
- Browser QA로 `/backtest` 화면에서 panel rendering을 확인한다.
- docs / task logs / root handoff가 4B 완료 상태로 sync된다.
- generated run history artifact는 커밋하지 않는다.
