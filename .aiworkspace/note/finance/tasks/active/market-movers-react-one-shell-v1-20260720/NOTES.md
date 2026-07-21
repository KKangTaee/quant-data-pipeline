# Notes

- 기존 `MarketMoversWorkbench`는 compact summary/action만 렌더링하고 실제 ranking/breadth/research는 별도 Streamlit surface다.
- 3차 `market_movers_decision_payload_v1`은 sector/industry × daily/weekly/monthly와 selected research boundary를 이미 제공한다.
- 실제 SP500 daily smoke에서 sector/industry flow와 bellwether rows가 준비되어 있다.
- selected TRV 표본은 연간 factor 중 매출·순이익·순이익률·ROE·부채비율이 있고, current TTM PER는 reported EPS 부족으로 unavailable이다.
- React component가 없을 때만 기존 Streamlit surface를 fallback으로 유지한다.
- 1180px breakpoint는 Streamlit iframe의 실제 989px 폭에서도 one-shell을 1열로 만들었다. 결정 화면만 900px breakpoint로 분리해 일반 desktop에서는 62/38을 유지하고 sector legacy lane 규칙은 1180px에 남겼다.
- group mode/period, 상세 tab, 재무 frequency/group/factor는 React local state다. coverage/period/ranking/top-N과 ranking-selected symbol만 bounded Streamlit event로 보낸다.
- YTD 가격 series와 financial factor series는 DB-backed research payload만 사용한다. React가 provider 또는 DB를 직접 읽지 않는다.
