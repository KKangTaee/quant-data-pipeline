# Market Research IA Redesign V1 Notes

Status: Complete
Last Updated: 2026-07-22

## Confirmed Decisions

- Today는 summary, Market Research는 deep research를 소유한다.
- 새 summary cockpit을 Market Research에 만들지 않는다.
- 3개 목적형 family를 한 `/overview` page 안에 둔다.
- 별도 Stock Research page는 V1 범위 밖이다.
- active module이 기준일, 자료상태, refresh action을 소유한다.
- full market-session banner와 Reference contextual help는 page-global top에서 제거한다.
- module data, service, loader, DB schema는 유지한다.

## Final Implementation

- `app/web/streamlit_app.py` page title은 Market Research이고 URL은 `/overview`다.
- `app/web/overview/page.py`는 `Market Research` title과 짧은 설명 뒤 목적형 selector를 바로 렌더링하며 page-global Reference, market-session banner, 운영 진단 패널을 두지 않는다.
- `app/web/overview/navigation.py`는 `시장 환경 | 지수 가치평가 | 종목 리서치` 3개 family와 7개 canonical view를 소유한다.
- 시장 환경은 `경제 사이클 | 선물 매크로 | 심리 | 일정`, 지수 가치평가는 `S&P 500`, 종목 리서치는 `변동 종목 | 개별 종목`으로 구성한다.
- active module만 lazy render하며 기준일, 자료 상태, refresh action은 각 module이 소유한다.
- Market Movers의 `개별 종목 분석`은 현재 선택 symbol을 검증해 U.S. Stock view로 넘기며 provider fetch나 write를 실행하지 않는다.
- legacy `market-context` query/session 입력은 `economic-cycle`로 canonicalize하며 기존 deep link를 보존한다.
- Today는 Economic Cycle, S&P 500, Futures Macro, Sentiment, Events를 compact projection하는 summary owner로 유지한다.

## Preservation Notes

- dirty worktree의 registry, run history, 기존 research bundle, QA image는 task scope가 아니며 stage하지 않는다.
- legacy query/session key를 제거하기 전에 compatibility tests를 둔다.

## Spec Self-Review

- placeholder scan: 미정 표시와 미완성 section 없음.
- consistency: single-page 3-family IA, seven canonical views, `/overview` compatibility가 동일하게 정렬됨.
- scope: shell/navigation/handoff/header ownership으로 제한하고 module 계산·data pipeline·별도 Stock Research page는 제외함.
- ambiguity fixes: 420px primary layout을 3 equal columns로 확정하고, Market Context compatibility adapter 유지, Market Movers handoff event/validation, query-widget precedence를 명시함.
