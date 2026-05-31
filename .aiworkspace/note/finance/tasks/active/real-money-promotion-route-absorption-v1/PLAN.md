# Real-Money Promotion Route Absorption V1 Plan

Status: Implementation complete
Created: 2026-05-30

## 이걸 하는 이유?

Real-Money 탭에서 `Shortlist`가 `Promotion`과 나란히 표시되면 별도 검증 단계처럼 보인다.
하지만 현재 구현상 Shortlist는 Promotion 결과를 받아 `Hold / Watchlist / Paper Probation / Small Capital Trial` 같은 추천 경로를 붙이는 보조 분류다.
따라서 Shortlist를 독립 검증처럼 보이게 하지 않고 Promotion의 추천 경로로 흡수한다.

## Scope

- Real-Money 상단 카드에서 `Shortlist` 독립 카드를 제거한다.
- Promotion 카드와 Promotion 상세 섹션에 `Suggested Route`를 함께 표시한다.
- 기존 `shortlist_status`, `shortlist_next_step`, `shortlist_rationale` metadata는 재사용한다.
- 저장 구조, runtime 계산, JSONL registry는 변경하지 않는다.
- 관련 flow / glossary 문서를 현재 UI 의미에 맞게 정리한다.

## Out Of Scope

- Promotion / Shortlist 계산 로직 변경
- 새 저장소 또는 사용자 메모 저장
- Practical Validation / Final Review gate 정책 변경
- broker order, live approval, account sync, auto rebalance
