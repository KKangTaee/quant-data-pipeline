# Risks

- DB에 선택 종목의 완전한 OHLC row가 없으면 가격 차트는 MISSING 상태를 표시한다.
- V1은 최신 120거래일 고정이며 intraday/zoom/indicator를 지원하지 않는다.
- 브라우저 QA는 로컬 DB availability와 실행 중인 Streamlit 상태에 영향을 받을 수 있다.
- 실제 Streamlit DB에는 QA 시점에 active item이 없어 populated 가격 차트는 동일 production bundle과 deterministic fixture로 시각 검증했다. DB selection/compaction/error 경계는 Python 계약 테스트가 담당한다.
- standalone fixture harness의 Streamlit parent protocol 부재로 `MutationObserver.observe` console message가 발생했지만, 실제 Streamlit route에서는 console error가 없었다.
- volume 결측은 price chart를 막지 않지만 tooltip 거래량은 `자료 없음`으로 표시한다. 불완전하거나 비논리적인 OHLC row는 projection에서 제외한다.
