# Plan

## Purpose

Market Movers Redesign V2 5차는 Why It Moved 흐름을 하단 부록이 아니라 선택 종목 조사 패널로 정리한다.

## Scope

- 기존 `why_it_moved` service/read model 경계를 유지한다.
- 선택 종목의 Symbol, Name, Sector, ranking context, return, volume, metadata status를 먼저 보이게 한다.
- 기존 identity/context/movement/peer detail table은 expander 안에 보존한다.
- 자동 원인 판정, AI 요약, 원인/거래 점수화, 원문 저장은 추가하지 않는다.

## Completion Criteria

- 사용자가 선택한 종목의 조사 시작 정보를 pane에서 먼저 확인할 수 있다.
- 원천 detail 표와 metadata tabs는 기존 기능을 유지한다.
- SP500 Daily/Weekly, NASDAQ empty state, 좁은 화면 QA가 통과한다.
- 공통 검증, Browser QA, coherent commit을 완료한다.
