# Market Research IA Redesign V1 Status

Status: Complete
Roadmap: 4/4 implementation stages complete
Last Updated: 2026-07-22

## Completed

- current docs, navigation code, page shell, module ownership과 actual desktop Market Research 화면을 점검했다.
- Today와 Market Research의 역할 중복을 확인했다.
- minimal cleanup, single-page purpose groups, Market/Stock page split 세 접근을 비교했다.
- 사용자가 `시장 환경 | 지수 가치평가 | 종목 리서치` 단일 page 권장안을 승인했다.
- active task shell과 written design spec을 작성했다.
- placeholder, internal consistency, scope, ambiguity 자체 검토를 완료했다.
- 사용자가 written spec을 승인했다.
- six-task test-first implementation plan을 작성했다.
- canonical 3-family / 7-view navigation contract와 legacy query compatibility를 구현했다.
- page-global Reference / market-session banner를 제거하고 module-local header ownership으로 전환했다.
- Market Movers selected symbol을 U.S. Stock Research로 넘기는 inline handoff를 구현했다.
- Python·React·typecheck·build 회귀와 desktop·760px·420px actual Browser QA를 완료했다.

## Current

- 구현, QA, durable docs sync까지 완료했다.
- Today는 summary, Market Research는 deep research라는 제품 경계가 코드와 문서에 정렬됐다.

## Next

- 이 task의 남은 구현 차수는 없다.
- 다음 작업은 `codex/sub-dev` 변경의 통합 검토 또는 별도 승인된 후속 UX 범위에서 시작한다.
