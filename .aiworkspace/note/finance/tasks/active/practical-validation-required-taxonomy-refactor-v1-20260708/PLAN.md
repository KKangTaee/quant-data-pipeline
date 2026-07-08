# Practical Validation Required Taxonomy Refactor V1

## 이걸 하는 이유?

Practical Validation의 1차 필수 검증에서 같은 증거가 여러 모듈에 중복 배치되어 사용자가 “무엇이 부족하고 어디서 해결해야 하는지”를 구분하기 어렵다. 이번 작업은 검증 모듈별 소유권을 분리해 Flow3는 결론을 짧게 보여주고, Flow4는 원인과 보강 액션을 카테고리별로 확인하도록 정리한다.

## 차수

- 2차: `validation_efficacy`를 검증 방법론 강도 전용으로 축소한다.
- 3차: module planner / board registry / workspace의 모듈 taxonomy를 새 소유권에 맞춘다.
- 4차: Flow3 / Flow4 표시 문구와 카테고리 UI 라벨을 사용자 언어로 정리한다.
- 5차: Final Review gate 회귀 테스트를 보강한다.
- 6차: Browser QA와 문서 closeout을 수행한다.

