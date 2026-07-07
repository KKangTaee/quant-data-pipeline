# Backtest Symbol Resolver V1 Design

## Commit Comparison

`codex/sub-dev` `4b698eb6 Market Movers 티커 변경 복구 흐름 추가`는 Market Movers 안에서 `market_symbol_alias` table, quote-missing 후보 감지, `티커 변경 복구 적용` 버튼, active alias quote lookup을 추가했다.

재사용할 점:

- candidate와 active repair를 분리한다.
- active repair 이후 provider lookup ticker만 resolved symbol로 바꾸고 source universe symbol은 유지한다.
- 버튼을 누르기 전에는 자동 적용하지 않는다.

재사용하지 않을 점:

- `market_symbol_alias` 새 테이블.
- Market Movers 전용 UI / intraday snapshot 결합.
- yfinance search 중심 candidate 로직을 Backtest runtime에 직접 넣는 구조.

## 1차 Implementation Direction

- `finance/loaders/symbol_resolver.py`: read-only symbol identity diagnosis와 active lifecycle resolver를 둔다.
- `finance/data/symbol_resolver.py`: user-approved ticker-change repair를 `nyse_symbol_lifecycle`에 idempotent UPSERT한다.
- `app/services/backtest_price_refresh.py`: active resolver가 있으면 collection ticker를 resolved symbol로 바꾸되 plan에는 `source_symbol` / `resolved_symbol` metadata를 남긴다.
- `app/web/backtest_common.py` / `app/web/backtest_result_display.py`: Factor Readiness action model에 symbol identity issue check와 apply action을 연결한다.

## Boundary

- UI는 외부 provider를 직접 호출하지 않는다.
- 후보 탐지와 active alias read는 DB-backed loader/service 경계에서 수행한다.
- 1차는 official source ingestion 확장이나 full PIT ticker split을 구현하지 않는다.
