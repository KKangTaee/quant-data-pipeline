# Plan

## 이걸 하는 이유?

RTDSM 원시 4분면은 의미·개정·표본 검증을 통과했지만 한 달짜리 국면 비중이 높았다.
임계값을 사후 완화하지 않고 원시 신호와 공식 국면을 분리해야 현재 국면과 향후 전환
확률이 같은 Point-in-Time 의미를 갖는다.

## Goal

2회 연속 확인 국면을 canonical state로 재정의하고, 실제 DB state/model gate가 통과한
경우에만 기존 순환 경로 UI로 연결한다.

## Whole Roadmap

1. confirmation-based core state와 audit
2. actual RTDSM state checkpoint
3. 통과 시 actual transition model OOS checkpoint
4. 최종 READY 시 persistence/service/route UI와 Browser QA

## Stop Conditions

- confirmed state gate 실패 시 actual model fitting과 3~4차 중단
- model publication gate 실패 시 persistence/service/UI 중단
- actual result를 본 뒤 threshold, feature, confirmation count 변경 금지
- four-quadrant UI 복원 금지
- `자산별 확인 포인트` 계산·payload·markup·CSS 변경 금지
