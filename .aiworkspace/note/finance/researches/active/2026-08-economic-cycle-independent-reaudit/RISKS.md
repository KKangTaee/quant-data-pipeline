# Risks And Open Questions

Date: 2026-08-03

## Open Decision

- 4분면을 상대 성장순환으로 정의하고 `침체` 대신 `위축`을 쓸지 사용자 승인이 필요하다.

## Method Risks

- 현행 score를 그대로 쓸지, dynamic factor current-state index로 교체할지는 shadow
  validation 뒤 결정해야 한다.
- 0 경계의 guard band, minimum duration과 breadth threshold를 sample에 맞춰 과최적화할
  수 있다.
- NBER chronology는 ex-post benchmark로 유용하지만 current-state 정답은 아니다.
- COVID 같은 abrupt shock은 일반 hysteresis보다 빠른 override가 필요할 수 있다.
- monthly source의 발표 지연과 revision 때문에 `current` 기준일을 observation month,
  information date, materialization date로 분리해야 한다.

## Product Risks

- probability를 제거하면서도 condition path를 확정 예측처럼 보이게 만들 수 있다.
- asset checkpoints가 새 phase vocabulary를 implicit recommendation으로 해석할 수 있다.
- transition condition을 너무 많이 노출하면 기존 확률 카드와 같은 판단 부담이 재발한다.

## Verification Gaps Before Implementation

- PIT current-state candidate의 historical replay와 revision matrix
- transition condition 후보별 false alarm / missed turn / median lead / detection delay
- current vs intramonth 기준일 선택과 stale fallback contract
- 420px / desktop graph와 condition cards visual prototype
