# Backtest Symbol Resolver V1 Status

Status: Complete

## Current Step

- 2026-07-08: 1차~5차 개발 / QA / 문서 동기화 완료. 최종 closeout 커밋 준비 중.

## Next

- 후속 범위는 official corporate-action feed 신규 수집과 실제 old/new ticker price series stitching이다.

## Completed

- `codex/sub-dev` `4b698eb6`을 직접 merge하지 않고 Market Movers alias repair 흐름을 Backtest 공용 resolver로 재설계했다.
- `nyse_symbol_lifecycle`에 `resolution_status`, `confidence`를 추가하고 ticker-change candidate / active repair 의미를 문서화했다.
- `finance/loaders/symbol_resolver.py`와 `finance/data/symbol_resolver.py`를 추가했다.
- strict Factor Readiness pre-run / post-run model은 ticker-change 후보를 일반 price refresh / provider gap보다 우선 표시한다.
- Backtest price refresh plan은 active repair가 있으면 source ticker를 유지하고 collection ticker만 resolved symbol로 바꾼다.
- 2차에서 ticker-change candidate에 `evidence_factors`, `source_quality`, `review_note`, `recommended_action`을 붙였다.
- low-confidence candidate는 readiness 화면에 남기되 `apply_ticker_change_repair` 자동 반영 대상에서 제외하고 `review_symbol_identity` 수동 확인 action으로 표시한다.
- active repair 저장 시 source evidence factor payload를 `nyse_symbol_lifecycle.evidence_json`에 보존한다.
- 3차에서 active ticker repair에 `source_range`, `resolved_range`, `split_status`, `stitching_status=metadata_only`를 붙여 future PIT stitching이 읽을 수 있는 metadata contract를 만들었다.
- Backtest price refresh plan과 실행 result details는 동일한 `symbol_resolutions` split contract를 보존한다.
- 4차에서 Factor Readiness ticker-change diagnostics를 후보쌍 / 신뢰도 / 기간 경계 / 근거 / 다음 행동으로 분리했다.
- ticker-change repair action result는 `next_step=rerun_factor_readiness`와 Factor Readiness 재확인 / 백테스트 재실행 안내를 남긴다.
- Browser QA screenshot: `backtest-symbol-resolver-v4-browser-qa.png` (generated, not staged).
- 5차에서 durable docs, root handoff logs, active task status/runs를 closeout 기준으로 동기화했다.
