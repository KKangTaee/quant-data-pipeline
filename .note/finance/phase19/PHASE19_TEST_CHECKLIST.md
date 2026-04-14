# Phase 19 Test Checklist

## 목적

- Phase 19에서 정리한 strict annual contract language가
  UI / history / interpretation / 문서에서 일관되게 다시 읽히는지 확인한다.
- 이번 checklist는
  "새 구조 옵션이 추가됐는가"보다
  **그 옵션의 뜻을 사용자가 다시 읽고 이해할 수 있는가**
  를 보는 데 초점을 둔다.

## 추천 실행 순서

1. strict annual single strategy에서 contract UI 확인
2. compare / history / load-into-form 흐름 확인
3. interpretation summary / selection history 문구 확인
4. phase closeout 문서와 index 확인

## 1. strict annual single strategy contract UI 확인

- 확인 위치:
  - `Backtest > Single Strategy > Quality / Value / Quality + Value > Strict Annual`
  - `Advanced Inputs > Overlay & Defensive Rules`
- 확인:
  - `Overlay & Defensive Rules` 안에
    - `Rejected Slot Handling Contract`
    - `Weighting Contract`
    - `Risk-Off Contract`
    가 같이 보이는지
  - 각 contract 아래에
    - "위치 / 역할" 설명
    - 현재 선택이 무슨 뜻인지 보여주는 짧은 설명
    이 같이 보이는지
  - `Rejected Slot Handling Contract`가 보이는지
  - 아래 mode를 고를 수 있는지
    - `Reweight Survivors`
    - `Retain Unfilled Slots As Cash`
    - `Fill Then Reweight Survivors`
    - `Fill Then Retain Unfilled Slots As Cash`
  - 각 option이
    - 생존 종목 재배분인지
    - 현금 유지인지
    - 먼저 다음 순위 종목으로 채우는지
    를 설명하는 도움말/현재 선택 설명과 함께 읽히는지
  - `Weighting Contract`에서
    - `Equal Weight`
    - `Rank-Tapered`
    를 고를 수 있는지
  - `Weighting Contract`가 최종 선택 종목의 비중 규칙을 뜻한다는 설명이 보이는지
  - `Risk-Off Contract`에서
    - `Cash Only`
    - `Defensive Sleeve Preference`
    를 고를 수 있는지
  - `Risk-Off Contract`가
    - partial trend rejection이 아니라
    - `Market Regime` 또는 guardrail 때문에 전체 포트폴리오가 risk-off일 때 쓰인다는 설명이 보이는지
  - `Defensive Sleeve Tickers`가
    - `Defensive Sleeve Preference`일 때만 쓰이는 방어 ETF 목록
    이라는 설명과 함께 보이는지

## 2. compare / history / load-into-form 흐름 확인

- 확인 위치:
  - `Backtest > Compare > strict annual family override`
  - `Backtest > History`
- 확인:
  - strict annual compare override에서도 위 contract가 같은 이름으로 보이는지
  - history run을 다시 열었을 때
    - `Rejected Slot Handling`
    - `Weighting Contract`
    - `Risk-Off Contract`
    값이 자연스럽게 복원되는지
  - `Load Into Form` 이후 single/compare 폼에서도 같은 설정이 다시 보이는지

## 3. interpretation summary / selection history 문구 확인

- 확인 위치:
  - `Backtest > History > strict annual run > Selection History / Interpretation`
- 확인:
  - history 표에
    - `Rejected Slot Handling`
    - `Weighting Contract`
    - `Risk-Off Contract`
    - `Risk-Off Reasons`
    - `Filled Count`
    같은 컬럼이 읽기 쉬운 이름으로 보이는지
  - interpretation summary에
    - `Rejected Slot Handling`
    - `Weighting Contract`
    - `Risk-Off Contract`
    - `Filled Events`
    - `Cash-Retained Events`
    - `Defensive Sleeve Activations`
    가 보이는지
  - row-level interpretation 문구가
    - trend rejection 처리
    - full cash risk-off
    - defensive sleeve rotation
    - final weighting contract
    를 구분해서 설명하는지

## 4. phase closeout 문서와 index 확인

- 확인 문서:
  - [PHASE19_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase19/PHASE19_CURRENT_CHAPTER_TODO.md)
  - [PHASE19_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase19/PHASE19_COMPLETION_SUMMARY.md)
  - [PHASE19_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase19/PHASE19_NEXT_PHASE_PREPARATION.md)
  - [PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase19/PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md)
  - [PHASE_PLAN_TEMPLATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/PHASE_PLAN_TEMPLATE.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
- 확인:
  - Phase 19 상태가 closeout 기준으로 보이는지
  - new slice / closeout / checklist 문서가 index에서 바로 찾히는지
  - roadmap에 Phase 19가 closeout 기준으로 반영됐는지
  - 앞으로 phase plan 문서 template가 안내 문서로 보이는지

## 한 줄 판단 기준

- 이번 checklist는
  “strict annual 구조 옵션이 추가됐는가”보다,
  **그 옵션을 사용자가 다시 읽고 이해하고 비교할 수 있게 정리됐는가**
  를 확인하는 checklist다.
