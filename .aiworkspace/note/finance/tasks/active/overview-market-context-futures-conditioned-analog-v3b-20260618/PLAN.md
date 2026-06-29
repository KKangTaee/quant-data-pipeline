# Plan

Status: Complete
Last Updated: 2026-06-18

## 이걸 하는 이유?

3차-A의 `Macro 조건 포함 pilot`은 broad historical analog에 GLD price proxy context를 더했을 때 표본이 얼마나 줄어드는지 별도 영역으로 보여줬다.
3차-B는 같은 context-only 구조를 유지하면서, 저장된 futures daily OHLCV만으로 계산 가능한 Rate Pressure context를 하나 더 붙여 broad anchor 중 futures macro context가 비슷한 과거 anchor가 얼마나 남는지 확인한다.

## Tentative Roadmap

- 1차: source-action flow와 historical analog basis 표시 정리 완료.
- 2차: latest / selected as-of와 5D / 20D / monthly pattern window 완료.
- 3차-A: GLD price proxy 기반 `Macro 조건 포함 pilot` 완료.
- 3차-B: 이번 작업. stored futures daily OHLCV 기반 Rate Pressure context 1개를 GLD pilot에 추가한다.
- 이후 차수: 별도 승인 전까지 FRED rates, events, sentiment, 새 provider, 새 DB schema, 새 loader, full PIT universe storage는 열지 않는다.

## Scope

- 기존 broad historical analog와 GLD conditioned pilot을 유지한다.
- `finance/loaders/futures.py::load_futures_ohlcv()`로 selected as-of date 이하 stored futures daily rows만 읽는다.
- futures condition은 `ZN=F` / `ZB=F` price move 기반 Rate Pressure futures proxy 1개만 추가한다.
- futures coverage가 부족하면 계산하지 않고 `insufficient_conditions`에 남긴다.
- UI는 GLD condition과 futures condition을 구분해 표시한다.

## Out Of Scope

- FRED 2Y / 10Y 수집 또는 조건화.
- Events / sentiment historical conditioning.
- 새 provider, 새 DB schema, 새 loader.
- UI render 중 provider / FRED / yfinance 직접 fetch.
- Backtest Analysis, Practical Validation, Final Review, Operations core logic.
- trade signal, broker order, auto rebalance, validation gate, monitoring signal.

## Completion Conditions

- GLD conditioned pilot이 깨지지 않는다.
- stored futures daily OHLCV Rate Pressure condition이 사용되거나, 데이터 부족 시 명확한 insufficient condition으로 표시된다.
- broad analog와 macro-conditioned analog가 계속 구분된다.
- selected as-of / pattern window 기준 이후 futures rows를 조건 계산에 쓰지 않는다.
- sample quality와 sample reduction reason이 유지된다.
- Market Context 본문에 금지 copy가 추가되지 않는다.
- service contract tests, compile, Streamlit run, Browser QA를 기록한다.
