# Market Research Editorial Navigation V2 Notes

Status: Complete
Last Updated: 2026-07-23

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

## Implementation Notes

- family 설명은 visual chrome을 줄이기 위해 화면에서 숨겼지만 `aria-label="label: description"`으로 의미를 보존했다.
- desktop/760px에서는 header가 좌우 축을 유지하고 420px 이하에서만 stacked header로 전환한다.
- mobile family는 세 label을 축약하지 않고 같은 너비로 표시하며, view는 2열이고 단일 view는 전체 열을 차지한다.
- active family와 active view를 underline/fill로 다르게 표현해 목적과 현재 문서의 위계를 구분한다.
- dark/light theme variable, focus-visible outline, reduced-motion 계약을 유지했다.
