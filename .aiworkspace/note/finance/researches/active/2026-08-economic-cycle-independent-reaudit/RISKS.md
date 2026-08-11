# Risks And Open Questions

Date: 2026-08-12

## Open Decision

- RTDSM/ADS 공식 realtime history를 신규 provider로 추가하는 data expansion scope를
  진행할지 사용자 결정이 필요하다.

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

- RTDSM variable별 첫 vintage, known-at date와 missing-vintage contract
- existing PIT observed-state와 RTDSM-based long history의 common-period parity
- data expansion 뒤 usable origin / destination / holdout event gate 재실행
- sample gate 통과 뒤 destination와 imminence model의 episode-block OOS / calibration

## Confirmed Stop Risk

- 현재 DB만 사용하면 usable origin 148, independent event 32로 `NO_GO_DATA`다.
- 최근 holdout의 expansion/slowdown destination support가 0이므로 4-class probability를
  공개할 수 없다.
- monthly origin을 독립 표본처럼 세거나 revised history를 predictor로 소급하는 방식은
  허용하지 않는다.
