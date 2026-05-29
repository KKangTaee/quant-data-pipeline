# Phase 10 Current Chapter TODO

Status: Active
Last Updated: 2026-05-29

## Current Position

- 10-1 `walkforward-oos-source-map-v1`: Complete
- 10-2 `walkforward-split-contract-v1`: Complete
- 10-3 `oos-holdout-validation-contract-v1`: Complete
- 10-4 `regime-split-validation-v1`: Next

## Next Task

`regime-split-validation-v1`

Focus:

- 확인 가능한 DB / macro loader source를 먼저 점검한다.
- historical regime bucket별 portfolio / benchmark evidence를 compact row로 설계한다.
- missing macro source, short regime coverage, proxy-only evidence는 `PASS`로 처리하지 않는다.
- 새 JSONL registry, user memo, preset, approval, order, auto rebalance behavior는 추가하지 않는다.
