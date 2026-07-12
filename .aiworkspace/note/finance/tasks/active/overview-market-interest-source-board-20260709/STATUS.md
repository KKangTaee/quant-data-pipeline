# Status

- 2026-07-09: 작업 시작. 목표는 애널리스트 관심을 링크 묶음 expander에서 출처별 상태 보드 중심으로 개선하는 것이다.
- 2026-07-09: 완료. `build_market_interest_read_model`에 analyst `source_cards`를 추가하고, Streamlit `애널리스트 관심` 영역에서 `출처별 확인 상태` 보드를 항상 보여주도록 변경했다.
- 2026-07-09: MarketWatch / WSJ Markets / Nasdaq.com은 자동 수집이 아니라 `원문 교차확인` 상태로 표시한다. Yahoo/yfinance는 세션 전용 구조화 단서로만 표시한다.
