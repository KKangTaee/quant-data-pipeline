# Notes

- 현재 `US Statement Coverage 100 / 300 / 500 / 1000`은 이름과 달리 statement / price readiness를 보장하지 않는다.
- 실제 로딩 기준은 `finance_meta.nyse_asset_profile`, `kind=stock`, `country=United States`, `on_filter=True`, `order_by=market_cap_desc`이다.
- 따라서 첫 UI correction은 `Coverage`를 보장값처럼 설명하지 않고 `Base Universe` 후보군으로 설명하는 것이다.
- 1차에서는 내부 preset key를 바꾸지 않았다. saved payload / default key / replay compatibility를 유지하기 위해 display label만 `US Base Universe N`으로 바꿨다.
- 2차에서는 Data Trust가 `price_freshness.status=warning/error`일 때 `missing_symbols`, `stale_symbols`, `reason_counts`, `classification_rows`를 issue card로 변환한다. 따라서 excluded / malformed가 없어도 가격 최신성 경고가 있으면 하단 `1차 데이터 확인`이 비지 않는다.
