# Plan

## 이걸 하는 이유?

기존 1~3차 검증은 현재 RTDSM 상태가 한 관측치 결측으로 장기간 끊기고, 최근 3년만
제공되는 고수익 OAS와 2011년 이후 ANFCI를 모든 모델 원점에서 동시에 요구해
`NO_GO`가 됐다. 임계값을 낮추지 않고 현재 국면 연속성과 장기 Point-in-Time 입력
계약을 복구한 뒤, 전환압력과 다음 국면을 서로 다른 예측 과제로 검증해야 한다.

## Goal

1. RTDSM의 한 달 관측 공백이 6개월 상태 공백으로 확산되지 않게 한다.
2. 장기 신용 입력을 DB-backed `BAA10Y`로 교체하고 제한된 BAML/ANFCI는 보조 근거로 둔다.
3. 전환압력과 다음 국면의 feature 계약을 분리해 동일 chronological gate로 재검증한다.
4. 최종 `GO`일 때만 4차 persistence/service와 5차 UI를 후속 진행한다.

## Scope

- `finance/economic_cycle_realtime_history.py`
- `finance/economic_cycle_transition_dataset.py`
- `finance/economic_cycle_transition_drivers.py`
- `finance/economic_cycle_transition_comparison.py`
- `finance/economic_cycle_state_transition_experiment.py`
- 관련 focused tests와 task/durable docs

## Out Of Scope

- 검증 전 production snapshot/service/UI 연결
- 자산별 확인 포인트 계산·디자인 변경
- publication threshold 완화
- BAML/ANFCI 값을 과거로 임의 보간

## Stop Conditions

- exact current confirmed phase가 없으면 3차 모델 검증 중단
- required driver coverage가 기존 기준을 통과하지 못하면 모델 fitting 중단
- 전환압력 또는 다음 국면의 지정 OOS gate가 실패하면 4·5차 중단
- 결과를 본 뒤 feature·threshold를 다시 바꿔 같은 holdout을 반복 최적화하지 않음

## Whole Roadmap

1. NO_GO 원인 재현과 수정 계약 확정
2. 현재 국면·driver·task-specific model 구현
3. 동일 1~3차 actual DB 재검증
4. GO 범위 persistence/service
5. 순환 경로 UI와 Browser QA, 자산별 확인 포인트 유지
