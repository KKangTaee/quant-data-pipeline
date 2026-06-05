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

## Interpretation Layer

`app.services.overview_market_intelligence.build_market_sentiment_snapshot()`은 원천 row와 trend 외에 `analysis` dict를 함께 만든다.

- `phase` / `phase_label` / `headline`: CNN Fear & Greed, AAII bearish, bull-bear spread, CNN component split을 조합한 현재 시장 심리 문맥.
- `data_confidence`: CNN / AAII freshness, missing, stale 상태를 먼저 보여주는 신뢰도 요약.
- `analysis_steps`: `지금 결론 -> 왜 이렇게 보나 -> 강한 신호 -> 약한 신호 -> 그래서 어떻게 보나 -> 다음 확인` 순서의 6단계 학습형 읽기 경로.
- `driver_groups`: CNN component를 greed / fear / neutral로 나눠 headline 뒤의 내부 엇갈림을 한국어 label로 요약한다.
- `component_explanations`: CNN 7개 component가 무엇을 보는지와 현재 점수가 어떤 의미인지 학습 카드로 설명한다.
- `next_checks`: sentiment만으로 결론 내리지 않도록 Market Movers, Futures Macro Thermometer, Events calendar로 이어지는 확인 이유와 볼 항목.

`app.web.overview_dashboard`는 Sentiment 탭 상단을 `시장 심리 컨텍스트` band로 열고, 그 아래에 `시장 심리 읽기 - 6단계`, 데이터 카드, 드라이버 분해, CNN 구성요소 학습 노트, 다음 확인, 추세 / 구성 / 원천 근거 탭을 순서대로 배치한다.

## Source Risk

CNN JSON endpoint는 CNN page referer와 browser-like user agent가 필요하다. AAII는 공식 historical page table을 우선 파싱하고, Excel download는 차단 가능성이 있어 1차에서는 fallback 후보로만 둔다.
