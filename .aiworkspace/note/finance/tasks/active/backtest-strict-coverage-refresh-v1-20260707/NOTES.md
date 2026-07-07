# Notes

- 현재 `US Statement Coverage 100 / 300 / 500 / 1000`은 이름과 달리 statement / price readiness를 보장하지 않는다.
- 실제 로딩 기준은 `finance_meta.nyse_asset_profile`, `kind=stock`, `country=United States`, `on_filter=True`, `order_by=market_cap_desc`이다.
- 따라서 첫 UI correction은 `Coverage`를 보장값처럼 설명하지 않고 `Base Universe` 후보군으로 설명하는 것이다.
- 1차에서는 내부 preset key를 바꾸지 않았다. saved payload / default key / replay compatibility를 유지하기 위해 display label만 `US Base Universe N`으로 바꿨다.
- 2차에서는 Data Trust가 `price_freshness.status=warning/error`일 때 `missing_symbols`, `stale_symbols`, `reason_counts`, `classification_rows`를 issue card로 변환한다. 따라서 excluded / malformed가 없어도 가격 최신성 경고가 있으면 하단 `1차 데이터 확인`이 비지 않는다.
- 3차에서는 기존 price refresh action을 Coverage 최신화로 바꿨다. plan은 `refresh_symbols_all`이 있으면 stale/missing 대상만 수집하고, missing symbol이 있으면 백테스트 시작일에서 수집을 시작한다. 실행 후 inspector가 남은 `refresh_symbols_all`을 다시 읽어 unresolved count를 result details/message에 보존한다.
- 4차에서는 `Universe Contract = Historical Dynamic PIT Universe`일 때 `US Base Universe 300`은 target 300을 유지하되 후보 pool은 최대 600개까지, 500은 최대 1000개까지 확장한다. Dynamic PIT membership이 최신 실행일에 target을 채우면 candidate-pool stale/missing은 `candidate_pool_price_freshness`에 보존하고, Data Trust의 effective `price_freshness`는 runnable coverage OK로 바꾼다.
- 5차에서는 20D 거래대금 기준을 `liquidity_layer_v1`로 표준화했다. 이 기준은 Base Universe 선별이 아니라 Base Universe / Dynamic PIT membership 이후 각 리밸런싱 날짜 후보를 거르는 optional layer이며, DB OHLCV `close * volume` rolling 20 trading days 기준이다.
