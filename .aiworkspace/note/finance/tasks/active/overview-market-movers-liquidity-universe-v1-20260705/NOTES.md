# Notes

- 현재 코드 기준 Top1000 / Top2000 live loader는 `nyse_asset_profile.market_cap`을 사용한다.
- 개선 목표는 live ranking을 매 화면 조회에서 반복하지 않고, 명시적 `유니버스 기준 갱신`에서 materialized membership을 계산/저장한 뒤 Market Movers가 그 결과를 읽는 구조다.
- 최종 구현은 legacy profile fallback을 두지 않는다. listing source 후보가 없으면 `유니버스 기준 갱신` 결과가 실패 / 확인 필요로 남고, 사용자는 listing source refresh를 먼저 해야 한다.
- `nyse_asset_profile.market_cap`은 Top universe ranking source가 아니라 company name, sector, industry, market cap display 같은 보조 metadata join으로만 남는다.
- Browser QA 중 service label에 `Top 2000 by market cap`이 남아 있음을 발견했고, Market Movers / Why It Moved / statement diagnostics label을 `Top N by 20D avg dollar volume`로 정렬했다.
