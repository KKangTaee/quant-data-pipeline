# Today U.S. Market Session Status V1 Notes

## Decisions

- 정규장만 표시한다. 프리마켓·애프터마켓은 제외한다.
- 정규장 기준은 09:30–16:00 ET다.
- 사용자에게 필요한 상태는 `개장 전 / 장 진행 중 / 정규장 마감 / 휴장`이다.
- 장 상태는 시장 방향 또는 매매 신호가 아니므로 Today evidence readiness에 합산하지 않는다.
- 현재 시각과 countdown은 React local timer로 갱신하되 calendar 의미는 Python payload가 소유한다.

## Existing Context

- Today payload owner: `app/services/today.py`
- Today page adapter: `app/web/today_page.py`
- React owner: `app/web/streamlit_components/today_workbench/src/`
- official holiday / early-close persistence: `market_event_calendar`
- 기존 Today의 `next_event`는 FOMC 중심 snapshot이므로 session calendar는 별도 좁은 loader boundary가 필요하다.
