# 설계

`persistent_source_gap_or_symbol_issue`는 날짜 차이만으로 생성된 heuristic이므로 `backtest_price_refresh`의 공급처 차단 marker에서 제거한다. 공급처 no-data 및 종목 상태 관련 기존 제외, ticker resolution, 명시적 수집/재실행 흐름은 유지한다. 특정 ETF whitelist를 추가하지 않는다.

회귀 조건: 혼합 lag universe와 장기 stale만 남은 universe 모두 수집 가능. 실제 provider_no_data 제외는 보존. 운영 검증은 전체 8종목의 DB 최신일과 GTAA 실제 종료일로 수행한다.
