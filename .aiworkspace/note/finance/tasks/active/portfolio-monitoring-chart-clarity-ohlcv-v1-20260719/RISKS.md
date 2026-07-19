# Risks

- DB에 선택 종목의 완전한 OHLC row가 없으면 가격 차트는 MISSING 상태를 표시한다.
- V1은 최신 120거래일 고정이며 intraday/zoom/indicator를 지원하지 않는다.
- 브라우저 QA는 로컬 DB availability와 실행 중인 Streamlit 상태에 영향을 받을 수 있다.

