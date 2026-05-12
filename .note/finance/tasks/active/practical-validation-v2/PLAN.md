# PLAN - Practical Validation V2

Status: Active
Created: 2026-05-12

## Goal

Backtest Analysis에서 만든 후보 source를 실전 투입 전 관점으로 검증하는 Practical Validation V2를 완성한다.

핵심 목표는 12개 진단 중 proxy / `NOT_RUN` / 설명 부족으로 남아 있던 항목을 실제 provider data, DB bridge, macro context, stress / sensitivity 해석으로 정상화하는 것이다.

## Current Scope

현재 active scope는 P2 closeout과 이후 P3 준비다.

| Step | Meaning | Current Status |
|---|---|---|
| P2-0 | 12개 진단 중 P2 대상 항목 확정 | completed |
| P2-1 | 각 항목에 필요한 데이터 목록 / schema 계약 확정 | completed |
| P2-2 | ETF operability / cost / liquidity 수집 / 저장 기반 | completed |
| P2-3 | ETF holdings / exposure 수집 / 저장 기반 | completed |
| P2-4 | macro / sentiment market context 수집 / 저장 기반 | completed |
| P2-5 | Practical Validation 12개 진단에 provider context 연결 | completed |
| P2-6 | stress / sensitivity 해석 보강 | completed |
| P2-7 | proxy / NOT_RUN 항목 QA와 closeout 판단 | pending |

## P2 Target Diagnostics

P2는 아래 진단을 중심으로 정상화한다.

| No | Diagnostic |
|---:|---|
| 2 | Asset Allocation Fit |
| 3 | Concentration / Overlap / Exposure |
| 5 | Regime / Macro Suitability |
| 6 | Sentiment / Risk-On-Off Overlay |
| 7 | Stress / Scenario Diagnostics |
| 9 | Leveraged / Inverse ETF Suitability |
| 10 | Operability / Cost / Liquidity |
| 11 | Robustness / Sensitivity / Overfit |

## Completion Criteria

P2는 아래를 만족하면 closeout할 수 있다.

- provider data가 있는 항목은 actual / bridge evidence를 표시한다.
- 데이터가 부족한 항목은 어떤 ETF / series / diagnostic이 부족한지 보여준다.
- `NOT_RUN`은 pass처럼 보이지 않는다.
- Practical Validation Result JSONL에는 compact evidence만 저장한다.
- Final Review에서 사용자가 어떤 진단이 충분하고 어떤 진단이 부족한지 판단할 수 있다.

## Out Of Scope

- 모든 ETF issuer 완전 지원
- broker order, live approval, auto rebalance
- account holding 자동 연결
- 모든 stress scenario의 strategy-specific runtime replay
- dashboard monitoring snapshot 자동 저장
