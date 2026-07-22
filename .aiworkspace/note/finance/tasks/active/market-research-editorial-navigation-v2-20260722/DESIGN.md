# Market Research Editorial Navigation V2 Design

Status: Approved Mockup
Last Updated: 2026-07-22

## User-Approved Direction

사용자는 비교 시안 A인 `Editorial Tabs`를 선택하고 desktop/mobile 최종 시안으로 진행을 승인했다. B `Research Command Bar`도 비교했지만 최종 선택은 A다.

## Problem Diagnosis

- 현재 최대 55px title이 module보다 상단을 과도하게 지배한다.
- active family는 filled card+underline, inactive family는 배경 없는 text라 세 항목이 하나의 navigation system처럼 보이지 않는다.
- family row와 별도의 bordered view surface가 form control을 두 줄 쌓은 인상을 만든다.
- navigation은 820px로 제한되지만 module은 page content 폭을 사용해 왼쪽 시작점만 같고 오른쪽 시각축이 끊긴다.
- family 설명의 10px low-contrast text는 목적 설명보다 장식처럼 보인다.

## Approved Desktop Design

- Header는 같은 행에서 왼쪽 `RESEARCH + Market Research`, 오른쪽 한 줄 설명을 배치한다.
- title은 desktop 30px, 480px 이하 26px로 낮춰 module보다 크되 page를 지배하지 않게 한다.
- family는 별도 카드 배경 없이 3개의 text tab으로 표시한다.
- family group 아래 1px neutral divider를 두고 active family만 2px underline, stronger text, `aria-pressed=true`로 표시한다.
- family 목적 설명은 visual row에서 제거한다. payload compatibility를 위해 데이터는 유지해도 presentation에는 반복하지 않는다.
- local views는 외곽 border/background 없이 다음 줄에 wrap한다.
- active view만 compact filled pill과 `aria-current="page"`로 표시하고 inactive view는 text-only hover target이다.
- navigation은 820px 제한을 제거하고 iframe/page content width를 사용해 선택 module과 정렬한다.
- module과 navigation 사이 여백은 현재보다 줄여 조사 본문이 빨리 시작되게 한다.

## Approved Mobile Design

- Header는 세로로 쌓고 설명은 title 아래 왼쪽 정렬한다.
- family는 full label을 유지한 equal 3-column tab이다.
- view는 equal 2-column layout이며 active fill만 사용한다.
- horizontal scroll, clipped label, hidden essential text를 허용하지 않는다.

## Architecture And State Boundary

`app/web/overview/navigation.py`, `market_research_navigation_react_component.py`, payload schema와 event envelope는 변경하지 않는다. React는 기존 payload를 그대로 읽고 `select_view` intent만 반환한다. Python은 query/session/legacy slug와 selected renderer를 계속 소유하며 changed-view rerun과 Streamlit fallback도 유지한다.

Primary implementation files:

- `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.tsx`
- `app/web/streamlit_components/market_research_navigation/src/style.css`
- `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.test.tsx`
- generated canonical `component_static/`

## Accessibility

- 실제 `<h1>`, 두 navigation의 aria label, family `aria-pressed`, view `aria-current`를 유지한다.
- focus-visible outline은 underline/pill과 구분되는 2px 이상 ring을 유지한다.
- active state는 color만이 아니라 underline, fill, weight로 함께 표현한다.
- reduced-motion 계약을 유지한다.

## Test And QA Contract

- React: header semantics, family/view event, active aria state, no payload fallback 회귀
- Structural/CSS: family card-specific active surface와 view container chrome가 재도입되지 않도록 style contract 검토
- Static: Vitest, TypeScript, production build
- Python: Market Research/Today/fallback/changed-view rerun 회귀
- Browser: 3 family·7 view, URL/selected module sync, 1280·760·420px frame/page overflow 0, focus outline, console

## Tradeoffs

- family 설명을 화면에서 제거하면 최초 의미 설명은 줄지만, 명확한 세 family label과 Today→Research 맥락으로 충분하고 상단 밀도가 크게 개선된다.
- underline tabs는 card보다 클릭 영역이 작아지므로 button 자체 padding과 focus target은 충분히 유지한다.
- navigation width가 넓어져 desktop에서 빈 공간이 생길 수 있으나, 얇은 editorial line은 빈 공간을 layout rhythm으로 사용하고 본문 축 정렬을 우선한다.
