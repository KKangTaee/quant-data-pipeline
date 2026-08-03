# UI Patterns

Date: 2026-08-03
Status: design hypothesis, not approved

## Keep

- `자산별 확인 포인트` 전체 구조와 asset-specific interpretation
- source 기준일, freshness와 limitation disclosure
- 회복 / 확장 / 둔화 / 위축의 2x2 mental model

## Remove Or Replace

- 현재 / +1M / +2M 네 국면 확률 카드
- probability distribution을 level / momentum 좌표로 그린 월별 path
- LIMITED 결과를 dominant future phase처럼 표시하는 ribbon

## Candidate First-Read Flow

```text
현재 국면과 기준일
  -> 최근 1 / 3 / 6개월에 실제로 변한 것
  -> 현재 국면 유지 근거와 전환 감시 조건
  -> actual level / momentum의 과거 anchor와 현재점
  -> 자산별 확인 포인트 (현행 유지)
  -> 방법론 / 데이터 상세
```

## Candidate Graph Contract

- 좌표: actual composite level과 robust momentum
- 과거: 6개월 전, 3개월 전, 현재 anchor 또는 smoothed short trail
- 현재: boundary distance와 data state를 함께 표시
- 미래: terminal point를 찍지 않는다.
- 전환: 조건이 누적될 때만 현재점에서 다음 인접 국면 방향으로 pressure arrow / band를
  표시하고 `예측 경로가 아님`을 명시한다.
