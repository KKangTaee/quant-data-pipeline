# Notes

## Decisions

- 화면별 정보량을 같게 만들지 않는다.
- 공통 대상은 shell, 타이포, 정보 순서, fact card, meta chip, responsive layout이다.
- 사실 카드의 좌측 컬러 테두리는 사용하지 않는다.
- 의미 색상은 상태값 내부 점과 상태 문구에만 적용한다.
- 일정의 다음 이벤트는 공통 fact slot으로 이동하지만, 상세 일정 workflow는 유지한다.

## Existing Ownership

- 경제사이클: `economic_cycle_workbench`
- 선물매크로: `futures_macro_workbench`
- 심리: `sentiment_workbench`
- 일정: `events_workbench`

네 화면은 독립 Vite bundle이므로 공통 헤더 source가 각 bundle에 정상 포함되는지 구현 단계에서 네 build를 모두 검증해야 한다.

## Visual Review

- Direction comparison: `.superpowers/brainstorm/21928-1784980870/content/market-research-header-directions.html`
- Direction A detail: `.superpowers/brainstorm/21928-1784980870/content/market-research-header-a-detail.html`
- Status treatment V2: `.superpowers/brainstorm/21928-1784980870/content/market-research-header-a-status-v2.html`

`.superpowers/`는 generated local artifact이며 commit 대상이 아니다.

## Implemented Contract

- 공통 source: `app/web/streamlit_components/market_research_header/ResearchHeader.tsx`
- 공통 shell은 eyebrow, action, kicker, title, transition, summary, detail, fact, notice, meta의 선택 slot을 제공한다.
- 데스크톱 제목은 34px, 모바일 제목은 28px이며 화면별 정보량이 적으면 빈 slot 자체를 렌더링하지 않는다.
- fact box는 네 방향이 같은 중립 1px border를 사용한다. 의미 색상은 `showIndicator`가 명시된 상태 fact의 6px 점과 상태 문구에만 적용한다.
- 경제사이클과 선물매크로는 기존 hero adapter를 교체했고, 심리와 일정은 `SentimentHero`, `EventsHero` adapter로 공통 계약에 연결했다.
- 기존 refresh action id, Streamlit event dispatch, payload 의미와 본문 순서는 유지했다.

## Plan Adjustment

- 구현 계획의 source-string 중심 예시는 실제 React DOM test로 대체했다.
- 일정의 기존 `.events-workbench h2` 규칙이 공통 34px 제목을 덮어쓰는 회귀를 제거했다.
- 심리·일정의 사용하지 않는 legacy hero CSS와 좌측 강조선 규칙을 제거했다.
