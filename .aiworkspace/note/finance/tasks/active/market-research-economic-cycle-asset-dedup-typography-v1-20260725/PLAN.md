# Economic Cycle Asset Dedup Typography V1 Plan

Status: Complete
Last Updated: 2026-07-25

## 이걸 하는 이유?

금·달러 카드가 같은 공통 경제 배경과 전체 narrative를 여러 위치에서 반복해 실제 가격과
측정 경로를 빠르게 읽기 어렵다. 자산별 영역의 작은 글자도 함께 개선해 판단 경로를
짧고 읽기 쉽게 만든다.

## Goal

금·달러의 공통 경제 배경 중복을 제거하고 자산 고유 해석을 분리하며, 자산별 확인 포인트
영역의 표시 글자를 모두 `1px` 키운다.

## Scope

- 금·달러 summary/current interpretation 의미 분리
- React fallback과 자산별 section ownership
- scoped `+1px` typography
- focused regression, production build, desktop/420px Browser QA
- 관련 durable docs/root handoff 동기화

## Non-Goals

- 모델·데이터·가격 산식 변경
- 채권·주식·원자재 전면 재설계
- 전역 Economic Cycle typography 변경
- provider 수집 또는 DB write

## Stop Condition

- 사용자 승인 설계와 구현 계획이 확정된다.
- 금·달러 중복 제거와 자산별 typography가 test-first로 구현된다.
- actual desktop/420px Browser QA와 focused regression을 통과한다.
- generated artifact와 unrelated dirty files를 제외하고 commit한다.

## Roadmap

### 1차 — 의미 분리

- [x] 금·달러 summary에서 common economic state 제거
- [x] 금·달러 current interpretation 명시
- [x] legacy fallback 유지

### 2차 — typography와 QA

- [x] 자산별 section 전체 글자 `+1px`
- [x] focused Python/React/build 검증
- [x] desktop/420px Browser QA와 docs closeout

## Current Step

전체 roadmap `2/2차`를 완료했다. 금·달러의 공통 경제 배경은 전용 블록 한 곳에만
남기고 자산별 summary/current interpretation을 분리했다. 기존
`.market-implications` scope 안의 표시 글자를 `+1px` 조정하고 desktop/420px actual
Browser QA까지 닫았다.

## Canonical Design

`docs/superpowers/specs/2026-07-25-economic-cycle-asset-dedup-typography-design.md`

## Implementation Plan

`docs/superpowers/plans/2026-07-25-economic-cycle-asset-dedup-typography.md`
