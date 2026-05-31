# Backtest Analysis UX Checkpoint V1 Plan

Status: Active
Created: 2026-05-30

## 이걸 하는 이유?

Backtest Analysis는 후보를 만드는 첫 화면인데, 현재 결과 영역에는 개발자 payload, Data Trust, Practical Validation handoff, Real-Money next-step 문구가 같은 위계로 섞여 있다.
사용자가 백테스트 결과를 해석할 때 제품 단계와 검증 기준을 혼동하지 않도록, 화면 언어를 `Stage`와 `검증 체크포인트`로 분리한다.

## Scope

- Runtime payload를 기본 접힘 developer detail로 낮춘다.
- Latest Backtest Run 상단을 checkpoint / availability 중심으로 재정리한다.
- Data Trust Summary를 result integrity 상태 중심으로 개선한다.
- Practical Validation handoff를 검증 항목이 아니라 Next Action으로 분리한다.
- Real-Money의 legacy `4단계 / 5단계 Compare` 문구를 현재 4-stage flow와 충돌하지 않는 용어로 바꾼다.
- Backtest flow docs에 Stage / Checkpoint 용어 기준을 반영한다.

## Out Of Scope

- 새 JSONL registry 추가
- 사용자 메모 / preset 저장 기능
- DB schema / ingestion 변경
- broker order, live approval, auto rebalance
