# Plan

## Purpose

Market Movers Redesign V2 3차는 기존 차트 영역을 단순 보조 그래프가 아니라 선택된 탐색 모드의 가격 / 거래량 워크스페이스로 정리한다.

## Scope

- 기존 snapshot/read model만 사용한다.
- 선택된 탐색 모드의 metric label, row count, top symbol, metric range를 화면 상단에 붙인다.
- 기존 Altair chart는 유지하되 차트가 무엇을 보여주는지 먼저 알 수 있게 한다.
- context-only 경계를 유지하고 매수/매도 신호, 자동 원인 판정, 외부 provider fetch는 추가하지 않는다.

## Completion Criteria

- Market Movers 화면에서 board 다음 흐름으로 chart workspace가 보인다.
- SP500 daily/weekly와 NASDAQ empty state가 깨지지 않는다.
- 좁은 화면에서 chart facts와 chart가 겹치지 않는다.
- 공통 검증, Browser QA, coherent commit을 완료한다.
