# Overview Market Movers Period Refresh V1

## Goal

Overview > Market Movers에서 Period가 Weekly / Monthly / Yearly일 때도 사용자가 EOD 가격 이력을 수동 갱신할 수 있는 행동 경로를 제공한다.

## 이걸 하는 이유?

Daily는 일중 quote snapshot 갱신과 자동 갱신이 보이지만, non-daily period는 저장된 `finance_price.nyse_price_history` 기반으로 계산되면서 같은 화면에 가격 이력 갱신 경로가 없다. 사용자는 기간을 바꿨을 때 해당 기간 데이터도 갱신할 수 있어야 한다.

## Scope

- `Workspace > Overview > Market Movers` period refresh UX only.
- Daily의 기존 일중 스냅샷 갱신, 자동 갱신, 유니버스 갱신, 화면 새로고침 유지.
- Weekly / Monthly / Yearly에는 EOD 가격 이력 수동 갱신 버튼만 추가.
- 기존 OHLCV 수집 boundary를 통해 `finance_price.nyse_price_history` 갱신.
- job result는 기존 보조 expander 흐름으로만 노출.

## Non-Goals

- Market Context, Futures, Events, Backtest, Operations, historical analog 변경 없음.
- 새 provider, DB schema, registry / saved JSONL write 없음.
- Weekly / Monthly / Yearly 자동 분당 갱신 없음.
- 대량 Top1000 / Top2000 실제 provider 수집을 QA에서 강제 실행하지 않음.

## Stop Condition

- Focused tests 또는 대체 검증이 non-daily refresh action / UI contract를 확인한다.
- Browser QA에서 Daily 기존 UI와 Weekly / Monthly / Yearly 수동 EOD refresh UI를 확인한다.
- coherent commit을 만든다.
