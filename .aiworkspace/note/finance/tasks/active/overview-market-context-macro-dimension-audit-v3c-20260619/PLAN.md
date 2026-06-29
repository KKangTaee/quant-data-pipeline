# Plan

Status: Active
Last Updated: 2026-06-19

## 이걸 하는 이유?

3차-A/3차-B의 `Macro 조건 포함 pilot`은 sector relative strength, GLD price proxy, futures rate-pressure proxy를 실제 조건으로 사용했다.
3차-C는 사용자가 기대한 “금리 / 금 / 매크로 / 이벤트 / 심리까지 결합해서 과거 유사 맥락을 보고 싶다”는 흐름에서, 현재 어떤 차원이 실제 조건이고 어떤 차원은 참고 / 보류인지 화면 안에서 바로 구분하게 만든다.

## Tentative Roadmap

- 1차: source-action flow와 historical analog basis 표시 정리 완료.
- 2차: latest / selected as-of replay와 5D / 20D / monthly pattern window 완료.
- 3차-A: GLD price proxy 기반 `Macro 조건 포함 pilot` 완료.
- 3차-B: stored futures daily OHLCV 기반 Rate Pressure proxy 조건 추가 완료.
- 3차-C: 이번 작업. Macro dimension availability, regime preview, event / sentiment deferred reason을 compact read model과 UI로 추가한다.
- 이후 차수: 별도 승인 전까지 FRED hard conditioning, event / sentiment historical filtering, 새 collector / schema / provider, full PIT sector universe storage는 열지 않는다.

## Scope

- `macro_conditioned_analog` payload 아래에 `macro_dimension_audit` read model을 추가한다.
- Existing used conditions는 유지한다: sector ETF vs SPY relative strength, GLD price proxy, Rate Pressure futures proxy.
- Stored FRED macro series `T10Y3M`, `VIXCLS`, `BAA10Y`는 availability와 bucket preview만 표시한다.
- Events와 sentiment는 annotation / availability만 표시하고 hard historical condition으로 쓰지 않는다.
- UI는 `Macro 조건 포함 pilot` 안에 compact한 `맥락 차원 상태` 영역을 추가한다.

## Out Of Scope

- 새 FRED 수집, DGS2 / DGS10 / T10Y2Y 신규 collection, 새 DB schema, 새 loader, 새 provider.
- UI render 중 provider / FRED / yfinance 직접 fetch.
- FRED / events / sentiment를 broad anchor hard filter로 추가.
- Backtest Analysis, Practical Validation, Final Review, Operations core logic.
- trade signal, prediction, recommendation, validation gate, monitoring signal.
- registry / saved JSONL write 또는 generated artifact staging.

## Completion Conditions

- 기존 broad analog와 3B `Macro 조건 포함 pilot` 계산 결과가 유지된다.
- `T10Y3M`, `VIXCLS`, `BAA10Y`가 stored macro dimension 상태로 표시된다.
- 각 dimension은 기준일, 현재 값 / bucket, coverage, anchor preview count, hard condition 보류 이유를 가진다.
- Events와 sentiment는 hard condition이 아니라 annotation / deferred로 읽힌다.
- UI copy가 context-only 경계를 지키며 예측 / 추천 / 매매 신호처럼 읽히지 않는다.
- 검증과 Browser QA 결과를 `RUNS.md`에 기록한다.
