# Notes

- 현재 코드 기준 Top1000 / Top2000 live loader는 `nyse_asset_profile.market_cap`을 사용한다.
- 개선 목표는 live ranking을 매 화면 조회에서 반복하지 않고, 명시적 `유니버스 기준 갱신`에서 materialized membership을 계산/저장한 뒤 Market Movers가 그 결과를 읽는 구조다.
