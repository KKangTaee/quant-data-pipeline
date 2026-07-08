# Backtest Symbol Resolver V1 Status

Status: Phase 2 complete, phase 3 pending

## Current Step

- 2026-07-08: 2차 Source Evidence Scoring 구현 및 focused QA 통과. 커밋 준비 중.

## Next

- 3차 PIT effective-date split 계약: old/source ticker 구간과 resolved ticker 구간 metadata를 refresh plan/details에 노출한다.

## Completed

- `codex/sub-dev` `4b698eb6`을 직접 merge하지 않고 Market Movers alias repair 흐름을 Backtest 공용 resolver로 재설계했다.
- `nyse_symbol_lifecycle`에 `resolution_status`, `confidence`를 추가하고 ticker-change candidate / active repair 의미를 문서화했다.
- `finance/loaders/symbol_resolver.py`와 `finance/data/symbol_resolver.py`를 추가했다.
- strict Factor Readiness pre-run / post-run model은 ticker-change 후보를 일반 price refresh / provider gap보다 우선 표시한다.
- Backtest price refresh plan은 active repair가 있으면 source ticker를 유지하고 collection ticker만 resolved symbol로 바꾼다.
- 2차에서 ticker-change candidate에 `evidence_factors`, `source_quality`, `review_note`, `recommended_action`을 붙였다.
- low-confidence candidate는 readiness 화면에 남기되 `apply_ticker_change_repair` 자동 반영 대상에서 제외하고 `review_symbol_identity` 수동 확인 action으로 표시한다.
- active repair 저장 시 source evidence factor payload를 `nyse_symbol_lifecycle.evidence_json`에 보존한다.
