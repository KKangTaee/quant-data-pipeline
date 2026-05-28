# Plan

## 이걸 하는 이유?

Events table now carries source validation and lifecycle metadata, but a flat table is still hard to scan. The Events tab should read like an operating calendar: near-term window, event type mix, and date groups first, raw table second.

## Scope

- Events에 window / source type / validation filter를 추가한다.
- Event count timeline chart를 추가한다.
- Events를 date group으로 묶어 calendar-like view로 보여준다.
- Table view는 보존한다.

## Done Criteria

- Events tab에서 날짜별 grouping을 볼 수 있다.
- window, source type, validation 기준으로 필터링할 수 있다.
- Browser smoke에서 Events calendar view가 렌더된다.
