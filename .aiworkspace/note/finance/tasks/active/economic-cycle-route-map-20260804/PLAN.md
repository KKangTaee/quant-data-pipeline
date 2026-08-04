# Economic Cycle Route Map Plan

## 이걸 하는 이유?

4분면의 겹치는 과거 좌표를 제거하고, 현재 관측 국면과 구조적 다음 확인 방향을 더
빠르게 이해할 수 있는 순환 경로 지도로 교체한다.

## Scope

- React cycle map view와 관련 CSS/test/source contract
- production component bundle
- Browser QA와 task closeout

## Frozen Scope

- service payload와 DB/domain 계산
- `현재 관측과 전환 기준` 상세 조건 의미
- `최근 12개월 국면 흐름`
- `자산별 확인 포인트` 전체

## Roadmap

1. 설계와 구현 계획: complete
2. route helper와 UI 구현: active
3. integrated verification와 Browser QA: pending

## Stop Condition

순환 경로 지도, 상태별 arc, 과거 요약이 검증되고 기존 리본·자산 surface가 유지되면
완료한다.
