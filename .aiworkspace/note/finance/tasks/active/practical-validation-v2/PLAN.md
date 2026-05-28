# PLAN - Practical Validation V2

Status: Active
Created: 2026-05-12

## Goal

Backtest Analysis에서 만든 후보 source를 실전 투입 전 관점으로 검증하는 Practical Validation V2를 완성한다.

핵심 목표는 12개 진단 중 proxy / `NOT_RUN` / 설명 부족으로 남아 있던 항목을 실제 provider data, DB bridge, macro context, stress / sensitivity 해석으로 정상화하는 것이다.

## Current Scope

현재 active scope는 P2 closeout 완료 후 P3 준비다.

| Step | Meaning | Current Status |
|---|---|---|
| P2-0 | 12개 진단 중 P2 대상 항목 확정 | completed |
| P2-1 | 각 항목에 필요한 데이터 목록 / schema 계약 확정 | completed |
| P2-2 | ETF operability / cost / liquidity 수집 / 저장 기반 | completed |
| P2-3 | ETF holdings / exposure 수집 / 저장 기반 | completed |
| P2-4 | macro / sentiment market context 수집 / 저장 기반 | completed |
| P2-5 | Practical Validation 12개 진단에 provider context 연결 | completed |
| P2-6 | stress / sensitivity 해석 보강 | completed |
| P2-7 | proxy / NOT_RUN 항목 QA와 closeout 판단 | completed |

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

## P2 Closeout

Status: Completed on 2026-05-28

Closeout 기준:

- provider / macro / holdings snapshot은 DB / loader / provider context를 통해 읽는다.
- Practical Validation result에는 provider coverage, look-through board, robustness lab 같은 compact evidence만 남긴다.
- full holdings row, full macro series, raw provider payload, raw perturbation artifact는 JSONL에 저장하지 않는다.
- provider table이 비어 있거나 stale이면 `NOT_RUN` / `REVIEW` reason으로 남긴다.
- Final Review는 provider gap, stress gap, sensitivity gap을 investability evidence로 읽을 수 있다.

P3는 새 실전 승인 기능이 아니라 Final Review handoff와 Selected Portfolio Dashboard monitoring 연결을 정리하는 후속 단계다. 현재 continuity check, recheck comparison, recheck readiness, symbol freshness, selected provider evidence slice가 완료됐다.

## Detailed Task Docs

| Document | Role |
|---|---|
| `DESIGN.md` | Practical Validation V2의 diagnostic domain, UI / JSON contract, stage ownership 설계 |
| `IMPLEMENTATION_PLAN.md` | P0~P3 구현 범위와 완료 / 남은 항목 정리 |
| `CONNECTOR_AND_STRESS_PLAN.md` | P2 대상 진단, provider / macro / stress 해석 정상화 작업 순서 |
| `PROVIDER_CONNECTORS.md` | ETF operability, holdings / exposure, macro series 수집 / 저장 / loader 계약 |

## Out Of Scope

- 모든 ETF issuer 완전 지원
- broker order, live approval, auto rebalance
- account holding 자동 연결
- 모든 stress scenario의 strategy-specific runtime replay
- dashboard monitoring snapshot 자동 저장
