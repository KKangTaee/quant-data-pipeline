# Plan

## Purpose

Market Movers Polish V3 1차는 상단 조건 control을 모두 같은 조작 언어로 정리한다.

## Scope

- Coverage, Period, Sector, Top N, 랭킹 기준을 select/list style control로 통일한다.
- Top N은 number input 대신 preset list로 바꾼다.
- 랭킹 기준은 segmented button 대신 selectbox로 바꾼다.
- 데이터 source, service/read model, provider boundary는 변경하지 않는다.

## Completion Criteria

- 상단 control이 혼합 버튼/stepper UI처럼 보이지 않는다.
- 기존 session state가 invalid option으로 깨지지 않는다.
- SP500 Daily/Weekly, NASDAQ 상태, 좁은 화면 Browser QA를 완료한다.
