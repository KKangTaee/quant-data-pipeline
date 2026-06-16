# Design

## Current Root Cause

`app/web/overview_dashboard.py`의 `_render_market_movers_refresh_bar`가 `period != "daily"`이면 즉시 return한다. 서비스는 `app/services/overview_market_intelligence.py`에서 `VALID_PERIODS = daily / weekly / monthly / yearly`를 지원하며, non-daily는 `finance_price.nyse_price_history`의 EOD `1d` row로 계산한다.

## Implementation Direction

1. Daily refresh bar와 non-daily EOD refresh bar를 분리한다.
   - Daily helper는 기존 일중 스냅샷 / 자동 갱신 / 유니버스 갱신을 유지한다.
   - EOD helper는 `가격 이력 갱신` button, period 설명, large coverage warning, 화면 새로고침, 기존 job result expander만 렌더링한다.
2. Overview action facade에 Market Movers EOD 가격 이력 wrapper를 추가한다.
   - Universe는 기존 S&P 500 member 또는 market-cap ranked asset profile 기준을 재사용한다.
   - OHLCV write는 기존 `run_collect_ohlcv(..., execution_profile="managed_safe")`만 호출한다.
   - target table metadata는 `finance_price.nyse_price_history`로 남긴다.
3. Period별 collection window는 helper로 명시한다.
   - Weekly: `3mo`
   - Monthly: `1y`
   - Yearly: `3y`
   - Yearly는 current 252 거래일과 previous-period context까지 충분히 읽을 수 있는 window를 우선한다.
4. Rerun / reload 흐름은 button action 후 `st.rerun()`으로 snapshot을 다시 읽게 한다.

## Tradeoff

Top1000 / Top2000는 버튼 한 번이 많은 yfinance OHLCV 요청으로 이어질 수 있다. 이번 작업에서는 실행 자체를 막지 않고, 화면 설명과 button help로 비용을 명확히 알린다. 별도 queue / scheduler / chunk UI는 이번 범위가 아니다.
