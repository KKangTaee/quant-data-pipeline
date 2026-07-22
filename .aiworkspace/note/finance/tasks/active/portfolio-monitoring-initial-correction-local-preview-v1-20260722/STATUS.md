# Status

- 상태: 완료
- 전체 roadmap: 3/3차 완료
  - 1차: rerun 원인 확인과 local-preview 설계 확정
  - 2차: TDD로 명시적 `변경값 확인` interaction 구현
  - 3차: 전체 회귀, actual 달력 QA, 문서·commit
- 결과: 날짜·수량 입력은 React local state에만 머물고, 유효 입력에서 사용자가 `변경값 확인`을 누를 때만 기존 DB preview event를 보낸다.
- 저장 gate: READY projection의 item/date/quantity가 현재 draft와 모두 일치할 때만 저장이 활성화되며, 입력을 다시 바꾸면 이전 preview가 즉시 무효화된다.
- actual QA: AMD의 날짜를 `2024-06-15`, 수량을 `31`로 바꾸는 동안 dialog가 유지되고 저장이 비활성화됐다. 확인 뒤 적용일 `2024-06-17`, 종가 `$158.40`, 최초 투자금 `$4,910.40`이 표시되고 저장이 활성화됐다.
- 안전 경계: 실제 정정 저장은 실행하지 않았다. correction command, append-only revision, valuation, DB schema는 변경하지 않았다.
- 증빙: repository root의 generated `portfolio-monitoring-initial-correction-local-preview-qa.png`는 커밋하지 않는다.
