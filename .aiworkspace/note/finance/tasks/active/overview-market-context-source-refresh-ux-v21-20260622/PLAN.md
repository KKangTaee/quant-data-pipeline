# Overview Market Context Source / Refresh UX V21

Status: Completed
Started: 2026-06-22

## 이걸 하는 이유?

`Overview > Market Context`의 `근거: 자료 기준 / 출처 상태`와 `필요 자료 보강`은 기능적으로는 맞지만, 현재 화면은 긴 진단 표와 큰 보강 박스처럼 보여 사용자가 어떤 자료가 정상이고 어떤 자료가 실제 보강 대상인지 다시 해석해야 한다.

## Scope

- 자료 기준 / 출처 상태를 `요약 -> 브리프 직접 자료 -> 참고 / 관리 자료 -> 보강 판단` 흐름으로 재정리한다.
- Events / Data Health가 보강 필요한 문제처럼 보이지 않게 참고 / 관리 자료로 낮춘다.
- 보강 대상이 없을 때는 큰 disabled 버튼 대신 작은 상태 요약과 보조 전체 갱신 action만 남긴다.
- 보강 대상이 있을 때는 실행 대상 자료 rows를 먼저 보여주고 `현재 이슈만 보강`을 primary action으로 유지한다.

## Out of Scope

- Market Context progressive loading.
- 데이터 계산 로직, provider / DB schema / loader 변경.
- refresh action id, registry / saved JSONL, run history persistence 변경.
- Backtest / Practical Validation / Final Review / Operations core logic 변경.

## Steps

1. RED: source confidence와 refresh panel UI 계약 테스트를 추가한다. Done.
2. GREEN: source confidence HTML/CSS와 refresh expander 내부 UX를 개편한다. Done.
3. Verify: focused tests, full service contracts, py_compile, diff check, Browser QA. Done.
4. Docs: task docs / manifest / root logs를 V21로 동기화한다. Done.
