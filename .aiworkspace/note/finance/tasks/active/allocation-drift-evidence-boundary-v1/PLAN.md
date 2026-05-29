# Allocation Drift Evidence Boundary V1 Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Actual Allocation check는 사용자가 직접 입력한 현재 비중, 평가금액, 보유 수량과 가격을 기준으로 target allocation 대비 drift를 확인하는 선택 점검이다.
이 기능은 선정 이후 검증 효력을 높이는 데 도움이 되지만, 저장 기능이나 broker / account 연결처럼 보이면 잘못된 운영 흐름을 만든다.

이 task의 목적은 Actual Allocation 결과를 수동 / session-only evidence로 명확히 고정하고, DB / registry / monitoring log 저장, alert persistence, account connection, broker sync, live approval, order instruction, auto rebalance가 모두 비활성이라는 계약을 코드와 UI, 테스트에 남기는 것이다.

## Scope

- current value / shares x price / current weight 기반 drift check의 execution boundary를 명시한다.
- drift alert preview가 alert 저장이나 주문 후보가 아니라 read-only review signal preview임을 명시한다.
- Selected Portfolio Dashboard에 Allocation evidence boundary 표를 추가한다.
- service contract test로 read-only / session-only boundary와 breach 상태를 고정한다.

## Out Of Scope

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- raw holding / price input persistence
- account holdings 자동 연결
- broker sync, live approval, order draft, auto rebalance
- UI direct provider / FRED / broker fetch
