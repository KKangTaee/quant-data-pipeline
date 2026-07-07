# Backtest Symbol Resolver V1 Status

Status: Implementation complete, verification in progress

## Current Step

- 2026-07-08: Symbol Resolver V1 구현 완료. focused contract tests와 py_compile 통과.

## Next

- diff check, Browser QA 가능성 판단, docs/root log final sync, commit.

## Completed

- `codex/sub-dev` `4b698eb6`을 직접 merge하지 않고 Market Movers alias repair 흐름을 Backtest 공용 resolver로 재설계했다.
- `nyse_symbol_lifecycle`에 `resolution_status`, `confidence`를 추가하고 ticker-change candidate / active repair 의미를 문서화했다.
- `finance/loaders/symbol_resolver.py`와 `finance/data/symbol_resolver.py`를 추가했다.
- strict Factor Readiness pre-run / post-run model은 ticker-change 후보를 일반 price refresh / provider gap보다 우선 표시한다.
- Backtest price refresh plan은 active repair가 있으면 source ticker를 유지하고 collection ticker만 resolved symbol로 바꾼다.
