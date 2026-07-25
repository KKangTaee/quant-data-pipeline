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
