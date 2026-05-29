# Phase 11 Current Chapter TODO

Status: Active
Last Updated: 2026-05-29

## Current Position

- 11-0 `phase11-board-open`: Complete
- 11-1 `construction-risk-source-map-v1`: Complete
- 11-2 `concentration-overlap-exposure-contract-v1`: Complete
- 11-3 `correlation-risk-contribution-contract-v1`: Next

## Next Task

`correlation-risk-contribution-contract-v1`

Focus:

- 기존 component return correlation / volatility contribution proxy와 drop-one dependency evidence를 construction risk audit contract로 분리한다.
- average / max correlation, max risk contribution, component return matrix coverage, source strength를 compact row로 제공한다.
- component curve가 없으면 risk contribution을 `PASS`로 올리지 않는다.
- 새 JSONL registry, user memo, preset, approval, order, auto rebalance behavior는 추가하지 않는다.
