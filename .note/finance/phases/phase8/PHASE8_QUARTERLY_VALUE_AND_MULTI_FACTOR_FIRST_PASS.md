# Phase 8 Quarterly Value And Multi-Factor First Pass

## 구현 범위

이번 first pass에서 추가된 quarterly strict prototype 전략은 아래와 같다.

- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

## runtime

추가된 runtime wrapper:

- `run_value_snapshot_strict_quarterly_prototype_backtest_from_db(...)`
- `run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(...)`

위 wrapper들은 다음 공통 semantics를 가진다.

- `statement_freq = quarterly`
- `snapshot_mode = strict_statement_quarterly`
- `snapshot_source = shadow_factors`
- `factor_freq = quarterly`
- trend filter overlay 지원
- market regime overlay 지원
- strict price freshness preflight 결과를 bundle meta에 남김

## sample/runtime 연결

재사용한 sample/runtime path:

- `get_statement_value_snapshot_shadow_from_db(..., statement_freq="quarterly")`
- `get_statement_quality_value_snapshot_shadow_from_db(..., statement_freq="quarterly")`

즉 이번 구현은 새 알고리즘을 따로 만들기보다,
이미 복구된 quarterly shadow factor path를 product surface에 올린 작업이다.

## single strategy UI

추가된 single strategy form:

- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

공통 입력:

- universe mode:
  - `Preset`
  - `Manual`
- 기본 preset:
  - `US Statement Coverage 100`
- start / end
- top N
- rebalance interval
- factor inputs
- trend filter overlay
- market regime overlay

공통 진단:

- strict price freshness preflight
- statement shadow coverage preview

## compare / history / interpretation

이번 first pass에서 quarterly family 3종은 아래 surface까지 같이 연결됐다.

- compare strategy selection
- compare strategy-specific advanced inputs
- focused strategy selection interpretation
- history payload rerun
- load-into-form prefill
- latest run selection history

## current behavior summary

- quarterly value / quality+value path는 실행 가능하다.
- active start는 universe에 따라 다르다.
  - manual `AAPL/MSFT/GOOG`:
    - value quarterly = `2017-05-31`
    - quality+value quarterly = `2017-05-31`
  - `US Statement Coverage 100`:
    - value quarterly = `2016-01-29`
    - quality+value quarterly = `2016-01-29`

## current limitation

- 여전히 `research-only`
- annual strict family처럼 public candidate로 승격된 상태가 아님
- wider quarterly universes에서 active start와 factor availability는 아직 더 검증이 필요함
