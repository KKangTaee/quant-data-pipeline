# Inflation Policy Workbench Risks

- actual snapshot의 `LIMITED` 수치를 READY처럼 노출하면 검증 경계를 훼손한다.
- reverse joint paths가 저장되지 않은 상태에서 25bp 매핑이나 fixture로 결과를 채우면 안 된다.
- 같은 model version의 다른 cutoff artifact를 허용하면 과거 replay에 look-ahead가 생긴다.
- AUTO criterion을 수정 가능하게 만들면 시점별 알고리즘 기준과 사용자 가정이 섞인다.
- 기존 cycle payload와 같은 transport를 쓰더라도 service 입력이나 fallback으로 재사용하면 안 된다.
- UI command가 provider refresh를 암묵적으로 실행하면 DB-only workflow를 위반한다.
- 사용자 소유 dirty/untracked 파일과 generated QA 파일은 stage하지 않는다.

## Closeout

- 위 7개 항목은 구현 테스트와 Browser QA로 guardrail이 유지됨을 확인했다.
- 실제 reverse joint path 부족은 결함을 숨긴 것이 아니라 의도된
  `NOT_AVAILABLE` publication 상태다.
- 4차 주가 스트레스와 5차 침체 모델은 이 task에서 구현하지 않았으며 phase risk로
  계속 추적한다.
- 저장소 전체 `pytest -q`는 Streamlit 전역 singleton의 순차 실행 격리 문제로
  green이 아니다. 전체 실행에서 실패한 대표 테스트가 새 프로세스에서는 통과했고
  task focused 122건은 green이지만, 이를 full-suite pass로 해석하지 않는다.
