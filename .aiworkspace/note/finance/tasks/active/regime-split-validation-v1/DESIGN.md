# Regime Split Validation V1 Design

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Contract

`app/services/backtest_temporal_validation.py`에 `build_regime_split_validation()`을 추가한다.

입력은 기존 Practical Validation의 portfolio curve / benchmark curve와 `finance.loaders.macro.load_macro_series_observations()`가 읽은 DB-backed macro observation history다.
출력은 workflow registry나 memo 저장이 아니라 Practical Validation result에 포함되는 compact evidence dict다.

## Regime Buckets

초기 bucket은 FRED 3개 series로 분류한다.

- `VIXCLS`: volatility stress
- `T10Y3M`: yield curve stress
- `BAA10Y`: credit spread stress

Bucket rule:

- `risk_off`: `VIX >= 30`, yield curve inversion, or `BAA10Y >= 3`
- `caution`: `VIX >= 20`, yield curve below `0.5`, or `BAA10Y >= 2.5`
- `neutral`: above thresholds not triggered

## Rows

Regime evidence는 아래 row를 만든다.

- `Regime aligned history`: portfolio / benchmark / macro history가 같은 월 단위로 결합되는지 확인한다.
- `Regime bucket coverage`: neutral 외 caution / risk-off bucket sample이 충분한지 확인한다.
- `Worst regime excess return`: 가장 약한 bucket에서도 benchmark 대비 성과가 유지되는지 확인한다.
- `Worst regime drawdown gap`: 나쁜 bucket에서 strategy drawdown이 benchmark보다 과도하게 깊은지 확인한다.
- `Regime source strength`: runtime / embedded curve와 DB-backed macro observation source strength를 확인한다.

## Storage Boundary

- `db_write=False`
- `registry_write=False`
- `memo_persistence=False`
- live approval / order / auto rebalance 없음

Full macro series와 raw curve는 DB / runtime source에 두고, Practical Validation result에는 compact row와 metrics만 포함한다.
