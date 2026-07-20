# Market Movers Chart Navigation Polish V1 Design

Status: Approved
Last Updated: 2026-07-21

## Problem

현재 재무 SVG는 `viewBox="0 0 720 250"`에 모든 point를 맞추므로 40개 분기가 좁게 압축된다. X축은 첫·마지막 `period_end`만 보여 중간 분기를 식별할 수 없고, 재무 chart에는 pointer active state와 tooltip이 없다. 가격 readout의 `is-primary`, `is-latest`, `is-high`, `is-low` CSS가 배경색과 좌측선을 만들어 텍스트 의미보다 장식이 강하다.

## Considered Approaches

1. **Intrinsic-width SVG inside a draggable scroll viewport — selected.** Point 수에 비례해 chart width를 늘리고 native horizontal scroll을 유지한다. pointer drag는 viewport의 `scrollLeft`를 변경하고, keyboard focus와 scrollbar도 함께 제공한다.
2. Fixed-width SVG with viewBox pan state. 화면은 일정하지만 visible domain, pan limit, overview indicator를 별도로 관리해야 한다.
3. Add a chart library. 기능은 충분하지만 현재 dependency-free custom SVG와 시각 체계를 바꾸고 bundle/dependency 비용이 생긴다.

## Selected Design

### Financial chart geometry

- 연간은 point당 최소 72px, 분기는 point당 최소 58px를 확보하고 전체 inner width는 viewport보다 작아지지 않게 한다.
- 좌우 plot inset을 포함한 실제 `chartWidth`를 기존 coordinate/bar helper에 전달한다.
- X축 tick은 각 point 중심에 둔다. 분기는 `YYYY Qn`, 연간은 `YYYY`로 표시한다.
- 겹침 방지를 위해 좁은 inner width에서는 label 간격을 유지하되, 모든 point의 정확한 `period_end`는 hover/focus tooltip에서 제공한다.

### Navigation and hover

- viewport는 `overflow-x: auto`, `cursor: grab`, `touch-action: pan-y`를 사용한다.
- primary pointer down/move/up 시 시작 clientX와 scrollLeft 차이만큼 이동한다. 클릭 임계치 이하에서는 hover를 유지한다.
- SVG pointer 위치로 가장 가까운 point index를 계산한다. 막대와 선이 같은 active guide, dot, tooltip contract를 사용한다.
- SVG focus 후 좌우 화살표로 active point를 이동하고 해당 point가 viewport 안에 오도록 scroll한다.
- tooltip은 결산일, 분기/연간 label, factor 값을 표시한다.

### Price readout

- readout row 배경은 모두 white/transparent로 통일한다.
- `is-primary` 좌측선과 `is-latest/is-high/is-low` 배경 규칙을 제거한다.
- 값의 `mm-return--positive`, `mm-return--negative`, `mm-return--neutral`만 유지한다.

## Error And Accessibility

- point가 없으면 기존 empty state를 유지한다.
- drag 중 pointer capture를 사용하고 pointer cancel/lost capture에서 상태를 정리한다.
- 차트는 focus 가능하며 `aria-label`에 factor와 주기를 포함한다.
- 터치 세로 스크롤은 유지하고 긴 차트의 가로 이동만 pointer gesture로 처리한다.

## Acceptance Criteria

1. 분기는 X축에 `YYYY Qn`, 연간은 `YYYY`가 표시된다.
2. 40개 분기 차트가 압축되지 않고 가로 overflow가 생긴다.
3. scrollbar와 pointer drag 모두 chart history를 이동한다.
4. 막대와 선 모두 pointer hover와 keyboard focus에서 정확한 `period_end`와 factor 값을 표시한다.
5. 가격 readout에는 배경 tint와 좌측 강조선이 없고 숫자 text tone만 남는다.
6. focused tests, production build, desktop/narrow Browser QA를 통과한다.
