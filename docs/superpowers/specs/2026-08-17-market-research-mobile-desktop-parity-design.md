# Market Research Mobile/Desktop Navigation Parity Design

Status: Approved
Date: 2026-08-17
Supersedes: the mobile-only visual rules in `2026-08-17-market-research-flat-navigation-design.md`

## 이걸 하는 이유?

평탄화된 Market Research 구조 자체는 유지하되, 모바일 전용으로 만든 얇은 가로
스와이프 rail이 PC와 다른 제품처럼 보이고 선택 상태도 지나치게 약하다. 사용자는
모바일에서도 별도 축약형 UI가 아니라 PC에서 본 것과 같은 탭 디자인을 원한다.

## Considered Approaches

1. **상·하단 탭 모두 PC와 완전 동일하게 표시 — 채택**
   - 같은 정렬, 간격, pill, 선택 색상과 자연스러운 줄바꿈을 사용한다.
   - 기기별로 다른 탐색 규칙을 기억할 필요가 없다.
2. 서브탭만 PC와 동일하게 표시
   - 변경은 작지만 상단 family 탭은 여전히 모바일 전용 균등 분할이라 시각 언어가
     완전히 통일되지 않는다.
3. 현재 compact horizontal swipe 유지
   - 세로 공간은 가장 적게 쓰지만 사용자가 거부한 모바일 전용 표현을 유지한다.

## Approved Visual Contract

- 상단 `시장 환경 | 지수 가치평가 | 종목 리서치`는 모든 화면 폭에서 PC와 같은
  왼쪽 정렬, content-width, underline 선택 상태를 사용한다.
- 하단 view는 모든 화면 폭에서 PC와 같은 rounded pill, quiet text, filled selected
  state를 사용한다.
- 모바일에서도 view가 한 줄에 맞지 않으면 PC의 `flex-wrap` 규칙대로 다음 줄로
  자연스럽게 내려간다.
- 모바일 전용 equal-width family grid, 축소 font/padding, square-like view tab,
  horizontal swipe, hidden scrollbar를 제거한다.
- horizontal overflow가 없어지므로 active view `scrollIntoView` 보정도 제거한다.
- 모바일 header의 제목/설명 재배치는 유지한다. 이번 parity 범위는 navigation tab
  두 층이며 Market Research header와 각 본문 레이아웃은 대상이 아니다.

## Runtime And State Contract

- 기존 3-family / 8-view 정보 구조와 URL slug는 변경하지 않는다.
- `economic-cycle`과 `inflation-policy` direct route 및 controlled renderer 계약을
  변경하지 않는다.
- React navigation event와 Streamlit fallback state ownership도 변경하지 않는다.
- 변경은 navigation presentation CSS와 overflow 보정 코드에 한정한다.

## Files

- `app/web/streamlit_components/market_research_navigation/src/style.css`
- `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.tsx`
- `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.test.tsx`
- `app/web/overview/navigation.py`
- `tests/test_market_research_navigation.py`
- `tests/test_service_contracts.py`
- generated navigation component bundle and affected durable/task docs

## Verification

- CSS contract tests prove mobile blocks do not redefine family/view navigation styling.
- React tests prove selection/event behavior remains intact and no overflow scroll correction
  runs.
- Vitest, TypeScript typecheck and Vite production build pass.
- Focused Python navigation and Overview contract tests pass.
- Browser QA at desktop and 360px confirms the same family underline and view pill styling,
  natural wrapping, no page-level horizontal overflow and correct direct-route selection.

## Non-goals

- Market Research information architecture or copy changes
- economic-cycle / inflation-policy body redesign
- header typography parity between desktop and mobile
- provider, DB, model, refresh or command behavior changes
