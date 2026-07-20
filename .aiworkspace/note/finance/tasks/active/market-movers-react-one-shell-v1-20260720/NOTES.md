# Notes

- 기존 `MarketMoversWorkbench`는 compact summary/action만 렌더링하고 실제 ranking/breadth/research는 별도 Streamlit surface다.
- 3차 `market_movers_decision_payload_v1`은 sector/industry × daily/weekly/monthly와 selected research boundary를 이미 제공한다.
- 실제 SP500 daily smoke에서 sector/industry flow와 bellwether rows가 준비되어 있다.
- selected TRV 표본은 연간 factor 중 매출·순이익·순이익률·ROE·부채비율이 있고, current TTM PER는 reported EPS 부족으로 unavailable이다.
- React component가 없을 때만 기존 Streamlit surface를 fallback으로 유지한다.
