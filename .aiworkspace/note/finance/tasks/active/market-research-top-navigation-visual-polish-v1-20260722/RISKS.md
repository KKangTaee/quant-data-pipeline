# Market Research Top Navigation Visual Polish V1 Risks

Status: Complete
Last Updated: 2026-07-22

## Resolved Risks

1. actual DOM selector를 keyed scope와 structural test로 고정했고 Browser QA에서 active underline을 확인했다.
2. selected navigation은 blue-gray underline/pill과 font weight로 표시해 red/warning tone과 color-only 상태를 제거했다.
3. single-view `지수 가치평가`도 같은 bounded local surface에서 `S&P 500` pill을 유지한다.
4. 1280/760/420px에서 desktop content-width와 mobile equal-column contract, overflow 0을 확인했다.
5. header/local CSS는 `market_research_*` keyed class와 `mr-market-research-*` class로 scope했다.
6. 경제 사이클, S&P 500, Market Movers, U.S. Stock 전환과 module 시작 간격을 실제 화면에서 확인했다.

## Deferred

- sticky top rail
- left drawer/off-canvas
- watchlist, recent research, saved research navigation
- module body redesign

## Remaining Watch

- Streamlit upgrade로 native button testid가 바뀌면 structural test와 actual Browser QA를 함께 갱신한다.
