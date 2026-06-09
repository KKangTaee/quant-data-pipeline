# Risk Parity / Dual Momentum 5B Plan

## 이걸 하는 이유?

5A에서 Global Relative Strength는 전략 row와 runtime meta만으로 top-N, cash proxy, benchmark, exclusion, concentration을 설명할 수 있게 됐다.
5B는 같은 방식을 Risk Parity Trend와 Dual Momentum에 적용해 새 Backtest Analysis 패널 없이 기존 result display와 Selection History에서 전략 판단 근거를 확인하게 만든다.

## Scope

- Risk Parity Trend result row/meta contract hardening
- Dual Momentum result row/meta contract hardening
- Existing Selection History renderer reuse
- Streamlit-free focused tests first
- Korean-first user-facing interpretation copy

## Out Of Scope

- 새 evidence / log / workbench / Backtest Analysis panel
- registry / saved JSONL / run_history / generated artifact write
- provider / FRED direct fetch
- Practical Validation / Final Review / Monitoring behavior changes

## Tentative Roadmap

1. 1차: RED tests로 Risk Parity / Dual Momentum row와 runtime meta 계약을 고정한다.
2. 2차: `finance/strategy.py`에서 전략별 row diagnostics를 추가한다.
3. 3차: `app/runtime/backtest.py`에서 compact meta summary를 추가한다.
4. 4차: 기존 Selection History renderer가 두 ETF 전략을 읽도록 최소 UI copy를 조정한다.
5. 5차: durable docs, task logs, verification, commit으로 closeout한다.
