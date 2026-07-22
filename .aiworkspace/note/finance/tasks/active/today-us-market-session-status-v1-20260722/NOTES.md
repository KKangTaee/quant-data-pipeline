# Today U.S. Market Session Status V1 Notes

## Decisions

- 정규장만 표시한다. 프리마켓·애프터마켓은 제외한다.
- 정규장 기준은 09:30–16:00 ET다.
- 사용자에게 필요한 상태는 `개장 전 / 장 진행 중 / 정규장 마감 / 휴장`이다.
- 장 상태는 시장 방향 또는 매매 신호가 아니므로 Today evidence readiness에 합산하지 않는다.
- 현재 시각과 countdown은 React local timer로 갱신하되 calendar 의미는 Python payload가 소유한다.
- Today schema는 `today_home_v3`이며 market-session payload는 evidence readiness와 독립이다.
- 공식 `MARKET_HOLIDAY`와 `EARLY_CLOSE`는 현재·다음 연도를 좁게 읽고, 기존 FOMC `next_event` query는 그대로 유지한다.
- UI는 Python이 제공한 UTC open/close schedule만 해석하며 휴일 규칙을 다시 구현하지 않는다.
- holiday/early-close loader 중 하나라도 비정상이거나 calendar quality가 `LIMITED`면 React는 정규장 phase와 countdown을 계산하지 않고 `일정 자료 부족`으로 닫는다.

## Existing Context

- Today payload owner: `app/services/today.py`
- Today page adapter: `app/web/today_page.py`
- React owner: `app/web/streamlit_components/today_workbench/src/`
- official holiday / early-close persistence: `market_event_calendar`
- 기존 Today의 `next_event`는 FOMC 중심 snapshot이므로 session calendar는 별도 좁은 loader boundary가 필요하다.

## Actual Behavior

- 2026-07-22 실제 화면은 09:30 ET 경계 전 `개장 전`, 경계 후 `장 진행 중`으로 자동 전환됐다.
- ET 09:30–16:00은 KST 22:30–익일 05:00으로 표시됐다.
- 휴장·조기폐장 공식 일정 row가 있어 calendar-quality 경고는 표시되지 않았다.
