# Risks

- Bounded overlap reduces each symbol's requested history, but provider fetch still covers the full selected universe. The actual S&P 500 weekly refresh took 138.11 seconds for 503 symbols, so the user can still perceive a long blocking action.
- Monthly bounded behavior is covered by calendar-boundary and service contract tests; a second 503-symbol live Monthly provider run was not performed.
- Browser automation confirmed the financial scroller has a 2,260px content width inside a 702px viewport and the pointer-drag handlers remain in the built component. The automation backend did not change `scrollLeft` with its synthetic drag gesture, so physical mouse drag remains a small manual QA gap.
- New listings remain eligible for shorter periods when their first stored price precedes that period's required start; they are excluded only from periods whose start predates their first stored price.
- Sector conditional outlook remains out of this task and must not be published without historical/OOS evidence.
- rolling 1Y는 선택 종목 조사 시 기존 단일 DB 조회 범위를 1월 1일에서 최근 1년으로 넓힌다. 추가 query는 없지만 종목별 반환 행 수는 증가한다.
- 기존 session cache에 `price_series`가 없을 때는 YTD `series`의 원시 가격을 fallback으로 사용하므로, 새 서버 payload를 받기 전에는 1Y가 YTD 범위까지만 표시될 수 있다.
