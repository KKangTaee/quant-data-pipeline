# Strategy Evidence Inventory / Direction Panel 2026-06-08

Status: Completed
Last Verified: 2026-06-08

## Purpose

Backtest 3차 개발의 3A scope로, Backtest Analysis에서 전략별 maturity / evidence / next action을 read-only로 확인할 수 있게 한다.

## 이걸 하는 이유?

2차 product direction research는 현재 Backtest 전략 실행 범위가 넓지만 evidence maturity가 전략마다 다르다고 결론냈다.
새 strategy runtime, registry write, governance 연결을 늘리기 전에 사용자가 어떤 전략이 evidence-mature인지, 무엇이 prototype인지, 다음 작업이 무엇인지 한 화면에서 구분해야 한다.

## Tentative 3차 Roadmap

| 차수 | 목적 | 바뀔 범위 | 완료 조건 | 다음 차수 연결 |
| --- | --- | --- | --- | --- |
| 3A | Strategy evidence inventory / direction panel | Streamlit-free read model, Backtest Analysis read-only UI, docs | 모든 catalog strategy row와 maturity / evidence / next action 표시, tests, Browser QA | 3B bridge 후보군 선택 근거 |
| 3B | Strict annual + GTAA / Equal Weight portfolio bridge | Practical Validation-ready bridge display / handoff | evidence-mature group의 component role / validation gap 정리 | validation workflow 연결 |
| 3C | Risk-On Momentum governance design | Daily swing governance plan, possible validation/monitoring module | research lane을 governance로 승격할지 별도 승인 | Backtest Analysis와 monitoring 경계 유지 |
| 3D | ETF evidence expansion | GRS / Risk Parity / Dual Momentum evidence hub | current candidate anchor와 weakness report 보강 | ETF family maturity 개선 |

현재 진행 차수는 3A다.
이번 차수에서는 3B bridge 실행, Risk-On Momentum governance 구현, quarterly maturation, ETF current-candidate rerun은 하지 않는다.

## Scope

- Backtest 전략별 maturity / evidence / next action read-only inventory를 만든다.
- 모든 catalog strategy가 포함되게 한다.
- Risk-On Momentum 5D는 Backtest Analysis research lane이며 governance deferred로 표시한다.
- Strict quarterly prototypes는 prototype / contract-smoke maturity로 표시한다.
- Strict annual 3종과 GTAA / Equal Weight는 첫 evidence-mature candidate group으로 표시한다.
- Streamlit-free read model부터 만들고 test를 붙인다.
- UI 변경 후 가능한 범위에서 Browser QA를 수행한다.

## Not In Scope

- registry / saved JSONL / run history rewrite.
- strategy runtime behavior 변경.
- DB schema 변경.
- provider / FRED direct fetch.
- Risk-On Momentum governance 구현.
- quarterly maturation 구현.
- ETF current-candidate rerun.
- live trading / broker order / auto rebalance 설계.

## Stop Condition

- Read model tests가 strategy coverage와 special labels를 검증한다.
- Backtest Analysis UI에서 direction panel이 read-only로 보인다.
- 관련 docs / task log가 갱신된다.
- focused verification과 Browser QA 결과가 RUNS에 기록된다.

## Closeout

3A is complete.
3B / 3C / 3D remain future scopes and were not implemented in this task.
