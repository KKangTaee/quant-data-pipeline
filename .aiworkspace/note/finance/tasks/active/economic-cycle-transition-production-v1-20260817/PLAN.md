# Plan

## 이걸 하는 이유?

1~3차 검증이 actual DB 기준 `GO`가 되었으므로, 검증된 역할 분리를 제품에 연결한다.
현재 국면은 confirmed RTDSM state가 소유하고, 전환압력은 extended driver model,
다음 국면 분포는 compact core model이 소유한다.

## Whole Roadmap Position

- 1차 제품·모델 계약: 완료
- 2차 PIT 데이터 적합성: 완료
- 3차 chronological forecast 검증: 완료 (`GO`)
- 4차 persistence/service: 이번 task
- 5차 순환 경로 UI와 Browser QA: 이번 task

## Scope

1. `GO`를 전제한 production artifact와 current forecast 생성
2. 기존 artifact/snapshot 테이블에 versioned forecast contract 저장
3. Overview DB-only service에서 명시적 forecast contract만 해석
4. 순환 경로에 모든 대안 국면 비교, 전환압력, 조건별 driver 설명 표시
5. 자산별 확인 포인트 계산·디자인 무변경 검증

## Completion Conditions

- 현재 국면과 예측 국면이 서로 다른 소유 모델로 표시된다.
- 전환압력은 “가까운 3개 usable release 안의 전환 가능성”으로 정의된다.
- 목적지는 “전환이 발생할 경우 다음 confirmed phase”로 정의된다.
- 고정 순환 순서가 예측값을 대체하지 않는다.
- refresh가 새 snapshot을 저장하고 실패 시 기존 last-good을 보존한다.
- Python/React tests와 actual DB materialization, Browser QA가 통과한다.

## Out Of Scope

- 특정 달(1개월/2개월/3개월 후)의 국면 예측
- fiscal driver 추가
- 자산별 확인 포인트 계산 또는 디자인 변경
