# Plan

Status: Complete
Last Updated: 2026-06-18

## 이걸 하는 이유?

`Overview > Market Context > 참고: 과거 유사 맥락`의 기존 broad analog는 sector ETF가 SPY 대비 강했던 과거 anchor만 보여준다.
3차-A는 이를 예측 모델이나 매매 판단으로 확장하지 않고, stored data로 계산 가능한 macro 조건이 붙으면 표본이 어떻게 줄어드는지 별도 pilot 영역에서 보여준다.

## Tentative Roadmap

- 1차: source-action flow 정리. `next_checks`, source confidence, historical analog basis metadata를 표시했다.
- 2차: historical analog 기준 시점 / 패턴 기간 확장. `latest` / 과거 기준일과 5D / 20D / monthly window를 지원했다.
- 3차-A: 이번 작업. Macro 조건 포함 pilot framework와 최소 GLD 조건만 추가한다.
- 3차-B: 후속 제안. GLD coverage와 sample quality를 확인한 뒤, stored futures daily OHLCV 기반 rate pressure 또는 safe-haven 조건을 추가할지 결정한다.
- 이후 차수: 별도 승인 없이는 FRED rates, events, sentiment conditioning, full PIT sector universe storage/read path를 열지 않는다.

## Scope

- Preserve the existing broad historical analog result and median / positive rate / best / worst / sample table.
- Add a separate `Macro 조건 포함 pilot` payload and UI block under the historical analog section.
- Use the existing required sector ETF vs SPY relative strength condition.
- Add only one extra macro condition: GLD price proxy safe-haven / gold context from existing DB-backed price history already loaded by the analog service.
- Mark futures, FRED rates, events, and sentiment as deferred / disabled / insufficient instead of calculating them.

## Out Of Scope

- No new DB schema, provider, loader, registry, or saved setup.
- No provider, FRED, yfinance, or direct fetch from UI rendering.
- No events / sentiment historical conditioning.
- No 2Y / 10Y FRED collection.
- No trading recommendation, order, validation gate, monitoring signal, or prediction model.

## Completion Conditions

- Broad analog remains available as before.
- Macro-conditioned pilot is visually separate.
- Used, excluded, and insufficient conditions are visible.
- Sample reduction reason and sample quality are visible.
- Forbidden Market Context copy is not introduced.
- Required compile, pytest, Streamlit, and Browser QA checks are recorded in `RUNS.md`.
