# Plan

Status: Completed
Last Verified: 2026-06-08

## Goal

Backtest 4차 4A로 GRS / Risk Parity Trend / Dual Momentum의 ETF current-anchor readiness를 실제 workflow artifact 기준으로 확인하는 read-only workbench를 Backtest Analysis에 추가한다.

## 이걸 하는 이유?

3D는 ETF evidence gap을 정리했지만, 사용자가 확인할 수 있는 기능은 아직 정적 방향 패널에 가까웠다.
4A는 현재 run history와 selection source 같은 로컬 workflow artifact를 읽어, 각 ETF 전략이 current anchor 후보로 설 수 있는지, 무엇이 비어 있는지, 다음에 어떤 실행이 필요한지를 화면에서 판단하게 한다.

## Scope

- Streamlit-free ETF current-anchor read model을 추가한다.
- Backtest run history와 portfolio selection source rows를 read-only로 해석한다.
- GRS / Risk Parity Trend / Dual Momentum 각각의 latest run evidence, source evidence, missing evidence, recommended next action을 표시한다.
- Backtest Analysis에 `ETF Current Anchor Workbench` panel을 추가한다.
- focused tests와 Browser QA를 수행한다.
- 관련 durable docs와 root handoff logs를 sync한다.

## Out Of Scope

- ETF strategy runtime behavior 변경.
- DB-backed rerun matrix 실행.
- Current candidate registry append / rewrite.
- saved JSONL / run history rewrite.
- Practical Validation result 저장.
- provider / FRED direct fetch.
- provider snapshot collection.
- 새 ETF strategy 추가.
- live trading / broker order / auto rebalance 설계.

## Completion Criteria

- read model이 Streamlit-free이고 세 ETF expansion target만 포함한다.
- run history / selection source가 있으면 strategy별 latest evidence로 연결된다.
- missing run/source/provider/cost/benchmark evidence가 pass로 오해되지 않고 gap으로 표시된다.
- panel이 read-only storage / route boundary를 명시한다.
- tests, py_compile, UI-engine boundary checker, diff check, Browser QA가 완료된다.
- docs / task records / root logs가 4A 상태와 맞는다.

## Result

- `app/services/backtest_etf_current_anchor.py` read model을 추가했다.
- Backtest Analysis에 `ETF Current Anchor Workbench` read-only panel을 추가했다.
- 기존 run history와 Practical Validation source handoff row를 읽어 GRS / Risk Parity Trend / Dual Momentum별 latest run / source evidence, missing evidence, recommended next action을 표시한다.
- registry / saved JSONL / run history / validation result / provider snapshot write와 rerun execution은 추가하지 않았다.
