# Practical Validation Flow4 Action Center V1 Plan

Status: Completed
Date: 2026-07-09

## 이걸 하는 이유?

Flow4의 `카테고리별 검증 결과`, `데이터 보강 대상`, `Provider 보강 액션`은 내부 역할은 다르지만 사용자에게는 비슷한 보강 영역처럼 보인다. 특히 `Provider`가 무엇을 뜻하는지 모르는 사용자는 어떤 버튼이 무엇을 수집하는지 판단하기 어렵다.

이번 작업은 Flow4를 `판정 -> 데이터 보강 / 수집 실행 -> 상세 근거 / 원자료` 흐름으로 정리해, 사용자가 지금 해결할 수 있는 데이터 보강과 버튼의 실제 의미를 먼저 이해하게 만든다.

## Goal

Flow4에서 `데이터 보강 대상`과 기존 Python 수집 버튼을 사용자-facing `데이터 보강 / 수집 실행` 액션 센터로 묶고, raw provider / 작업 상세는 보조 원자료로 낮춘다.

## Scope

- `app/web/backtest_practical_validation/page.py`
  - visible section title / description 정리
  - `Provider 보강 액션` standalone header 제거 또는 하향
  - 버튼 주변에 `수집하는 것 / 하지 않는 것 / 실행 후 다음 단계` 설명 추가
  - `보강 작업 상세 테이블`은 first-read action center 밖으로 낮춤
- `app/services/backtest_practical_validation_workspace.py`
  - `data_action_board` copy를 사용자-facing 용어로 정리
  - criteria collection action의 위치 문구를 새 액션 센터명에 맞춤
- `app/web/components/practical_validation_data_action_board/frontend/src/PracticalValidationDataActionBoard.tsx`
  - board title / summary copy를 새 action-center 의미와 맞춤
  - React는 props 표시만 유지
- `tests/test_service_contracts.py`
  - Flow4 action center contract test를 먼저 추가

## Out Of Scope

- 새 수집 엔진, DB schema, provider fetch path 생성
- React fetch / 실행 / validation / storage 추가
- Final Review gate policy 변경
- registry / saved JSONL rewrite
- live approval, broker order, auto rebalance 의미 추가

## Implementation Plan

1. Failing tests
   - Flow4 page source가 standalone `Provider 보강 액션` section을 노출하지 않음을 검증한다.
   - action center에 `수집하는 것`, `하지 않는 것`, `실행 후 다음 단계` 설명이 있음을 검증한다.
   - `보강 작업 상세 테이블`은 provider action body가 아니라 `상세 근거 / 원자료` 쪽으로 낮아졌음을 검증한다.
   - React component가 `데이터 보강 / 수집 실행` copy를 쓰고 fetch / provider execution을 하지 않음을 검증한다.
2. Minimal implementation
   - Python action section title을 `수집 실행` 하위 블록으로 바꾸고, first-read card grid 중복을 줄인다.
   - 버튼 바로 위에 수집 범위 / 비범위 / 다음 단계 설명을 추가한다.
   - 작업 상세 table을 `상세 근거 / 원자료` 안에서만 볼 수 있게 이동하거나 label을 raw detail로 낮춘다.
   - service read model copy와 criteria link location을 `Flow4 > 데이터 보강 / 수집 실행`으로 맞춘다.
   - React title / summary copy를 액션 센터에 맞춘다.
3. Verification
   - focused unittest
   - py_compile
   - npm build for the component
   - git diff --check
   - Browser QA screenshot
4. Documentation / commit
   - task docs, flow docs, roadmap/index/root handoff log를 필요한 만큼만 sync한다.
   - generated screenshot / run history는 stage하지 않는다.
   - 한국어 commit을 만든다.

## Stop Condition

Browser QA에서 Flow4가 `카테고리별 검증 결과 -> 데이터 보강 / 수집 실행 -> 상세 근거 / 원자료`로 읽히고, 사용자가 수집 버튼이 무엇을 수집하고 무엇을 하지 않는지 바로 알 수 있으면 완료한다.
