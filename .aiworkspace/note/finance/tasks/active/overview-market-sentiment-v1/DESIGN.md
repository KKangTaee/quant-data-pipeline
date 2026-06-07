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

## Practical Validation 2차 / Downstream 3차 Overlay

2차에서는 Overview의 DB-backed sentiment snapshot을 `app.services.backtest_practical_validation.build_market_sentiment_context_overlay()`가 Practical Validation용 read model로 변환한다.

```text
finance_meta.macro_series_observation
  -> finance.loaders.sentiment
  -> app.services.overview_market_intelligence.build_market_sentiment_snapshot
  -> app.services.backtest_practical_validation.build_market_sentiment_context_overlay
  -> app.web.backtest_practical_validation
  -> app.web.backtest_final_review
  -> app.web.final_selected_portfolio_dashboard
```

Overlay는 `risk-on / neutral / risk-off` 해석, CNN / AAII 핵심 수치, data confidence, stale / missing warning을 보여준다. 단, `boundary.context_only=true`, `gate_effect=none`, `affects_pass_blocker=false`, `registry_write=false`, `saved_setup_write=false`, `monitoring_signal=false`를 명시해 Final Review Gate, selected-route preflight, validation module status, registry save, saved setup, monitoring signal, live approval / order / auto rebalance와 분리한다.

3차에서는 같은 read model을 `surface` label과 함께 Final Review Decision Desk 아래, Portfolio Monitoring 진입부에 표시한다. Final Review에서는 Candidate Board priority나 selected-route save readiness를 바꾸지 않고, Portfolio Monitoring에서는 Monitoring Scenario / Review Signals / portfolio saved setup을 바꾸지 않는다.

## Source Risk

CNN JSON endpoint는 CNN page referer와 browser-like user agent가 필요하다. AAII는 공식 historical page table을 우선 파싱하고, Excel download는 차단 가능성이 있어 1차에서는 fallback 후보로만 둔다.
