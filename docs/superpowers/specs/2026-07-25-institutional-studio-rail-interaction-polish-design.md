# Institutional Studio Rail Interaction Polish Design

Date: 2026-07-25
Status: Approved

## 이걸 하는 이유?

`C · Modular Research Studio`의 왼쪽 탐색은 선택 항목을 둥근 카드와 왼쪽 inset bar로 표시한다. 이 표현은 사용자가 원하는 편집형 research rail보다 pill/card에 가깝다. 기관 목록은 250px 높이의 기본 세로 스크롤 영역이라 탐색 가능한 항목 수가 적고, 밝은 브라우저 스크롤바가 어두운 rail의 시각 흐름을 끊는다.

## Approved Direction

사용자가 선택한 `A · 플랫 강조형`을 적용한다.

- 선택 항목의 둥근 배경, 외곽선, 왼쪽 inset bar를 제거한다.
- 선택된 번호와 제목의 명도·색상 대비를 높인다.
- 제목 영역 아래에 짧은 수평 직선 강조선을 둔다.
- hover는 약한 텍스트·배경 변화만 사용하며 선택 상태와 혼동되지 않게 한다.

## Manager List Interaction

기관 / 투자 대가 목록은 순서 재배치가 아니라 grab-to-scroll 탐색 영역으로 동작한다.

- desktop 목록 높이를 약 360px로 늘려 한 번에 더 많은 기관을 보여준다.
- 기본 스크롤바는 시각적으로 숨기되 wheel, trackpad, touch, keyboard scrolling은 유지한다.
- pointer down 후 목록을 위아래로 끌면 `scrollTop`을 반대 방향으로 이동한다.
- drag threshold를 넘은 경우 이어지는 click을 취소해 의도하지 않은 기관 선택을 막는다.
- pointer capture를 사용해 목록 밖으로 포인터가 잠시 나가도 드래그를 유지한다.
- `grab` / `grabbing` cursor와 `data-dragging` 상태로 조작 가능성을 피드백한다.
- mobile drawer에서는 native touch scrolling을 우선하며 custom pointer drag가 터치 기본 동작을 방해하지 않게 한다.

## Component Boundary

- `InstitutionalStudioShell.tsx`: 탐색 선택 표현의 semantic class와 기존 `aria-current`를 유지한다.
- `InstitutionalPortfoliosWorkbench.tsx`: manager rail pointer interaction, drag threshold, accidental-click suppression을 소유한다.
- `style.css`: flat active state, manager viewport height, hidden scrollbar, grab cursor를 소유한다.
- Python payload, Streamlit event, DB loader, 기관 순서는 변경하지 않는다.

## Accessibility And Failure Behavior

- 탐색 버튼과 기관 버튼은 기존 keyboard focus와 Enter/Space 선택을 유지한다.
- 기관 목록은 focus 가능한 scroll region으로 만들고 설명 가능한 Korean `aria-label`을 제공한다.
- custom drag가 지원되지 않거나 pointer event가 중단되어도 native scroll과 버튼 선택은 계속 가능하다.
- pending server event 동안 기존 disabled 상태를 유지한다.

## Verification

- React test에서 drag threshold 전 click 허용, threshold 이후 click 차단, scroll delta 계산을 검증한다.
- 전체 React test, typecheck, production build를 실행한다.
- actual Browser QA에서 선택 항목이 둥근 카드/왼쪽 bar 없이 표시되는지 확인한다.
- actual Browser QA에서 목록 높이, 숨겨진 scrollbar, mouse drag, wheel, 기관 선택, 420px drawer의 touch-compatible layout을 확인한다.

## Out Of Scope

- 기관 목록 순서 재배치 또는 저장
- drag inertia / momentum 구현
- rail 전체 너비나 main canvas 구조 변경
- SEC 13F payload, ingestion, mapping, ranking 기능 변경
