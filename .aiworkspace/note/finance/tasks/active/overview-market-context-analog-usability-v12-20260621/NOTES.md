# Overview Market Context Analog Usability V12 Notes

## User Issues Captured

- `실제 계산 기준일`이 2026-05-29로 고정되어 보일 때, 이것이 DB price basis 한계인지, 보강으로 해결 가능한지 화면에서 연결되지 않는다.
- `참고: 과거 유사 맥락` 상단이 같은 정보를 여러 줄과 여러 박스에서 반복한다.
- 핵심 / 보조 자산 통계 표는 숫자는 맞지만, 사용자가 먼저 읽을 결론과 비교 구조가 약하다.

## Design Decisions

- Price basis freshness is actionable only through the existing bounded OHLCV collection facade, not from UI direct fetch.
- Broad analog remains the primary sample; Macro conditioned comparison remains separate and does not replace broad rows.
- Detailed raw statistics stay available, but primary read path should be matrix / insight / support summary first.

