# Plan

## Purpose

Market Movers Polish V3 2차는 상단 `변동 종목` 요약과 `자료 신뢰 상태`의 중복을 하나의 결과 요약으로 통합한다.

## Scope

- 현재 coverage, period, sector, freshness, universe, returnable, missing, 보기 정보를 unified summary로 표시한다.
- 기존 command strip과 data trust strip은 호환용으로 남기되 실제 snapshot 첫 화면에서는 사용하지 않는다.
- Coverage trust raw/grouped diagnostics는 상세 expander에 보조 근거로 유지한다.
- 데이터 source, service/read model, provider boundary는 변경하지 않는다.

## Completion Criteria

- 첫 화면에서 coverage/period/freshness 정보가 반복 카드처럼 두 번 나오지 않는다.
- SP500 Daily/Weekly, NASDAQ empty state, 좁은 화면 Browser QA를 완료한다.
- context-only 경계와 coverage trust 상세 확인 경로는 유지된다.
