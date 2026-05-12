# Phase 35 Doc Sync And QA Fourth Work Unit

## 목적

네 번째 작업은 코드와 문서를 모두 새 흐름에 맞추고,
사용자가 manual QA로 확인할 checklist를 정리하는 것이다.

## 쉽게 말하면

문서 어디에서도 현재 기능처럼 별도 후속 가이드를 안내하지 않게 만들고,
사용자는 Final Review까지만 확인하면 된다.

## 왜 필요한가

- UI는 바뀌었는데 문서가 예전 흐름을 말하면 QA가 흔들린다.
- Phase35는 사용 흐름을 단순화한 phase이므로 checklist도 "새 탭 확인"이 아니라 "새 탭이 없는지" 확인해야 한다.

## 구현한 내용

- Phase35 plan / TODO / work unit / completion / next preparation / checklist를 새 방향으로 고쳤다.
- `BACKTEST_UI_FLOW.md`와 `SCRIPT_STRUCTURE_MAP.md`에서 삭제된 module 참조를 제거했다.
- operations guide에서 final decision registry가 최종 판단 원본임을 명확히 했다.
- README와 상위 finance 문서에서 workflow를 `Portfolio Proposal -> Final Review -> 최종 판단 완료`로 맞췄다.

## 결과

Phase35는 implementation_complete / manual_qa_pending 상태다.
사용자는 `PHASE35_TEST_CHECKLIST.md`로 QA를 진행하면 된다.
