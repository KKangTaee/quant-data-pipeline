# Overview Market Sentiment V1 Design

## Architecture

```text
CNN official page JSON / AAII official survey HTML
  -> finance.data.sentiment
  -> finance_meta.macro_series_observation
  -> finance.loaders.sentiment
  -> app.services.overview_market_intelligence
  -> app.web.overview_dashboard
```

## Series

- `CNN_FEAR_GREED`
- `CNN_FNG_MARKET_MOMENTUM_SP500`
- `CNN_FNG_STOCK_PRICE_STRENGTH`
- `CNN_FNG_STOCK_PRICE_BREADTH`
- `CNN_FNG_PUT_CALL_OPTIONS`
- `CNN_FNG_MARKET_VOLATILITY_VIX`
- `CNN_FNG_JUNK_BOND_DEMAND`
- `CNN_FNG_SAFE_HAVEN_DEMAND`
- `AAII_BULLISH`
- `AAII_NEUTRAL`
- `AAII_BEARISH`
- `AAII_BULL_BEAR_SPREAD`

## UI Placement

`Overview` top tabs에 `Sentiment`를 `Futures Monitor` 다음에 추가한다. Sentiment는 market context screen이며, Backtest / Practical Validation의 판단 저장 흐름이 아니다.

## Source Risk

CNN JSON endpoint는 CNN page referer와 browser-like user agent가 필요하다. AAII는 공식 historical page table을 우선 파싱하고, Excel download는 차단 가능성이 있어 1차에서는 fallback 후보로만 둔다.
