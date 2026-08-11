# Economic Cycle Independent Reaudit

State: active
Date: 2026-08-03

## 이걸 하는 이유?

현재 경제사이클 화면은 현재 국면과 1·2개월 후 국면 확률을 보여주지만, 사용자가
실제 경제 상태와 전환 방향을 신뢰성 있게 파악하도록 돕지 못하고 있다. 과거 작업의
결론을 답으로 재사용하지 않고 현재 코드, 저장 데이터와 실행 결과에서 문제를 다시
재현한 뒤 더 적합한 제품 계약을 정한다.

## Scope

- 현재 국면 입력, 가공, 4분면 판정과 표시값의 일치 여부
- 1·2개월 모델의 시계열 검증, baseline 대비 성능과 공개 상태
- 과거 경로, 현재점과 미래점을 그리는 좌표 의미
- point-in-time, 발표 지연, NBER 후행 판정과 source freshness
- 향후 `현재 상태 -> 최근 변화 -> 조건부 전환 경로` 계약 후보
- 기존 `자산별 확인 포인트` 계산과 화면은 보존 대상

## Independence Rule

- `researches/active/2026-07-us-economic-cycle-regime-forecast/` 본문과 과거 QA
  이미지는 근거로 읽지 않는다.
- 현재 `HEAD` 코드, 현재 MySQL row, 현재 테스트와 공식 1차 출처만 사용한다.
- 과거 결과와 같은 결론이 나오더라도 이번 감사에서 재현된 근거로만 채택한다.

## Work Stages

1. 현행 데이터 흐름과 화면 의미를 재현한다. 완료.
2. 현재 국면과 과거 replay를 계산식과 대조한다. 완료.
3. 미래 지평 validation과 publication gate를 대조한다. 완료.
4. 대안 계약을 사용자와 합의한다. 완료 — next destination + transition imminence.
5. actual PIT sample gate를 구현·재현한다. 완료 — `NO_GO_DATA`.
6. RTDSM/ADS data expansion 여부를 사용자 결정 뒤 별도 task로 수행한다.

## Stop Condition

sample gate가 실패하면 model, DB serving schema와 React probability UI를 변경하지
않는다. 신규 provider ingestion은 별도 승인 전까지 시작하지 않는다.
