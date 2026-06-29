# Design

Status: Complete
Last Updated: 2026-06-18

## Existing Data Finding

- 기존 historical analog는 최신 `build_group_leadership_snapshot(... period="daily")`의 첫 sector row를 sector ETF proxy로 매핑했다.
- 이후 `finance_price.nyse_price_history`에서 sector ETF / SPY / comparison ETF 가격을 읽고, sector ETF의 SPY 대비 5D 상대강도 anchor를 찾아 5D / 20D / 60D forward distribution을 만들었다.
- 기존 `finance.loaders.price.load_price_history()`는 `end` 인자를 이미 지원하므로 가격 이력 as-of 절단은 새 loader 없이 가능하다.

## 2차 Implementation Direction

- `build_historical_analog_snapshot()`은 `as_of_date`와 `pattern_window`를 받는다.
- `pattern_window`는 5D / 20D / monthly를 `5 / 20 / 21` trading-day relative-strength condition으로 normalize한다.
- `build_group_leadership_snapshot()`의 date resolver는 `as_of_date` 이하의 eligible DB price date만 사용한다.
- analog용 leadership period는 5D는 weekly, 20D / monthly는 monthly group leadership window를 사용한다.
- price history는 `as_of_date` 이하로 다시 절단해 caller가 future rows를 넘겨도 계산에 쓰지 않는다.
- anchor forward return은 selected as-of 이하에 full horizon이 존재하는 anchor만 사용한다.

## As-Of Replay 판정

기존 DB / loader / service read model만으로 가능한 범위:

- 특정 기준일 이하의 가격 이력으로 sector leadership을 재계산한다.
- 같은 기준일 이하의 sector ETF / SPY relative-strength pattern으로 historical anchors를 찾는다.
- 선택 기준일 이후 가격은 anchor 탐색과 forward distribution에 사용하지 않는다.

기존 DB만으로 보장할 수 없는 범위:

- 특정 과거 기준일 당시의 S&P 500 membership, sector / industry classification, market-cap snapshot을 full PIT로 복원할 수 없다.
- 현재 구현은 current universe / current sector metadata와 DB 가격 이력을 사용한 bounded replay다.

## 승인 필요 후속

- full PIT sector leadership replay가 필요하면 historical universe membership, sector classification, market-cap snapshot의 as-of storage/read path가 필요하다.
- macro-conditioned analog pilot은 3차로 넘기며, 기존 distribution table을 유지한 context-only 확장으로만 설계한다.
