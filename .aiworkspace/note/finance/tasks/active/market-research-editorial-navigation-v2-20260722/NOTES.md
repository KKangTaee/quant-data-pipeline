# Market Research Editorial Navigation V2 Notes

Status: Design
Last Updated: 2026-07-22

## Decisions

- A Editorial Tabs를 채택한다.
- family는 text+underline, local view만 compact active pill을 사용한다.
- header 크기와 상단 높이를 줄이고 module width와 정렬한다.
- mobile full family label, 3-column/2-column 계약을 유지한다.
- 기존 payload/event/Python state/fallback은 변경하지 않는다.

## Preservation

- V1의 React component architecture와 state synchronization fix를 보존한다.
- registry, research bundle, run history, generated QA images는 stage하지 않는다.
- visual companion `.superpowers/`는 generated brainstorming artifact로 commit하지 않는다.
