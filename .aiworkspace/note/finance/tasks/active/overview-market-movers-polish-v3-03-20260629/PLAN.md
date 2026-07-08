# Plan

## Purpose

Market Movers Polish V3 3차는 데이터 갱신 영역을 큰 운영 패널이 아니라 compact action row로 정리한다.

## Scope

- 갱신 상태를 `데이터 갱신` 블록 제목 대신 inline rail로 표시한다.
- 갱신 방식은 버튼/segmented control 대신 selectbox로 정리한다.
- 수동 실행 버튼은 기존 Overview action facade를 그대로 사용한다.
- 내부 action label이 화면에 영어로 노출되지 않도록 표시 문구를 번역한다.

## Completion Criteria

- Daily refresh 영역이 상태 rail + 방식 selectbox + 실행 버튼 묶음으로 보인다.
- Weekly/monthly EOD refresh도 같은 rail 언어를 쓴다.
- NASDAQ empty state에서도 갱신 영역이 깨지지 않는다.
- Provider, DB schema, action facade boundary는 변경하지 않는다.
