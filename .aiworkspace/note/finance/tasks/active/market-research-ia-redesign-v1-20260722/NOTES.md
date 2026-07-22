# Market Research IA Redesign V1 Notes

Status: Active
Last Updated: 2026-07-22

## Confirmed Decisions

- Today는 summary, Market Research는 deep research를 소유한다.
- 새 summary cockpit을 Market Research에 만들지 않는다.
- 3개 목적형 family를 한 `/overview` page 안에 둔다.
- 별도 Stock Research page는 V1 범위 밖이다.
- active module이 기준일, 자료상태, refresh action을 소유한다.
- full market-session banner와 Reference contextual help는 page-global top에서 제거한다.
- module data, service, loader, DB schema는 유지한다.

## Current Evidence

- `app/web/streamlit_app.py` page title은 Market Research이고 URL은 `/overview`다.
- `app/web/overview/page.py`는 아직 `Overview` title, contextual help, full session banner를 먼저 렌더링한다.
- `app/web/overview/navigation.py`는 다섯 bilingual label을 동급 pills로 렌더링한다.
- `app/web/overview/market_context.py`는 Economic Cycle, S&P 500, U.S. Stock을 다시 nested selector로 렌더링한다.
- Today는 Economic Cycle, S&P 500, Futures Macro, Sentiment, Events를 이미 compact projection한다.

## Preservation Notes

- dirty worktree의 registry, run history, 기존 research bundle, QA image는 task scope가 아니며 stage하지 않는다.
- legacy query/session key를 제거하기 전에 compatibility tests를 둔다.

## Spec Self-Review

- placeholder scan: 미정 표시와 미완성 section 없음.
- consistency: single-page 3-family IA, seven canonical views, `/overview` compatibility가 동일하게 정렬됨.
- scope: shell/navigation/handoff/header ownership으로 제한하고 module 계산·data pipeline·별도 Stock Research page는 제외함.
- ambiguity fixes: 420px primary layout을 3 equal columns로 확정하고, Market Context compatibility adapter 유지, Market Movers handoff event/validation, query-widget precedence를 명시함.
