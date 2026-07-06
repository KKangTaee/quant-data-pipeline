# Practical Validation Category Results V1

Status: Completed
Date: 2026-07-06

## 이걸 하는 이유?

사용자는 Practical Validation Flow 4에서 `Final Review로 넘기기 전 확인 기준`이 먼저 보이면 실제로 무엇을 검증했고 무엇이 부족한지 알기 어렵다고 지적했다.

이번 작업은 Flow 4를 Final Review route 기준판이 아니라 카테고리별 검증 결과로 읽게 하고, 후보 특성과 무관한 검증이 이동 차단처럼 보이는 문제를 줄이는 것이다.

## Scope

- Flow 4 workspace read model을 category-first grouping으로 변경
- selected-route preflight를 검증 category에서 분리하고 handoff summary로 유지
- stress / robustness missing evidence는 기본 review로 낮춤
- construction risk는 ETF-like 또는 weighted mix 후보에만 적용
- sentiment risk-on/off overlay는 macro gate status에서 제외하고 context로만 유지
- Flow 4 / React Fix Queue copy를 `카테고리별 검증 결과` 중심으로 변경

## Non-Goals

- Provider 수집 실행
- JSONL registry rewrite
- Final Review selected-route 저장 정책 변경
- live approval / broker order / auto rebalance 의미 추가
