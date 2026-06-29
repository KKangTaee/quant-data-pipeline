# Plan

Status: Completed
Last Verified: 2026-06-08

## Goal

Backtest 3차 3D로 Global Relative Strength, Risk Parity Trend, Dual Momentum의 ETF evidence expansion 상태를 Backtest Analysis에서 read-only로 확인하게 한다.

## 이걸 하는 이유?

Strict annual 3종과 GTAA / Equal Weight는 3A / 3B에서 첫 evidence-mature group으로 정리됐다.
반면 Global Relative Strength, Risk Parity Trend, Dual Momentum은 실행과 replay 경로는 있지만 current anchor, weakness report, ETF operability / cost evidence가 얇다.
따라서 새 ETF strategy를 추가하거나 current candidate를 바로 만들기 전에, 세 전략의 current anchor / near miss / not-ready reason / required evidence를 같은 형식으로 정리한다.

## Scope

- Streamlit-free ETF evidence expansion read model을 추가한다.
- Backtest Analysis에 read-only `ETF Evidence Expansion` panel을 추가한다.
- GRS / Risk Parity Trend / Dual Momentum 각각의 current anchor, near miss, not-ready reason, required evidence, next workflow를 표시한다.
- GTAA / Equal Weight와의 차이를 baseline reference로 보여주되, bridge group을 재정의하지 않는다.
- focused tests와 Browser QA를 수행한다.
- 관련 durable docs와 root handoff logs를 sync한다.

## Out Of Scope

- ETF strategy runtime behavior 변경.
- DB-backed rerun matrix 실행.
- Current candidate registry append / rewrite.
- saved JSONL / run history rewrite.
- Practical Validation result 저장.
- provider / FRED direct fetch.
- 새 ETF strategy 추가.
- live trading / broker order / auto rebalance 설계.

## Completion Criteria

- ETF evidence expansion read model이 Streamlit-free이고 세 target strategy만 포함한다.
- 각 target strategy에 current anchor / near miss / not-ready reason / required evidence / next workflow가 있다.
- GRS가 first priority로 표시되고, Risk Parity / Dual Momentum은 lower evidence로 표시된다.
- panel이 read-only storage / route boundary를 명시한다.
- tests, py_compile, UI-engine boundary checker, diff check, Browser QA가 완료된다.
- docs / task records / root logs가 현재 3D 상태와 맞는다.

## Result

- `app/services/backtest_etf_evidence_expansion.py` read model을 추가했다.
- Backtest Analysis에 `ETF Evidence Expansion` read-only panel을 추가했다.
- GRS / Risk Parity Trend / Dual Momentum을 ETF evidence expansion target으로 표시했다.
- GTAA / Equal Weight는 baseline reference로만 남기고 mature bridge group은 재정의하지 않았다.
- registry / saved JSONL / run history / provider snapshot / validation result write는 추가하지 않았다.
