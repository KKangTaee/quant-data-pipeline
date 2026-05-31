# Design

## Contract

`liquidity_capacity_contract_v1` is a read-only Backtest Realism Audit contract.
It interprets existing Practical Validation provider operability context and does not fetch or store provider data.

## PASS Candidate

Backtest Realism Audit should pass liquidity / operability only when:

- provider operability diagnostic is `PASS`
- target-weight coverage is high enough
- provider snapshot freshness is fresh
- source / coverage provenance is strong enough, preferably official actual rows
- compact capacity metrics do not include review tickers

## Conservative Cases

- stale or unknown freshness: REVIEW
- partial coverage: REVIEW
- bridge/proxy-only evidence: REVIEW
- legacy `diagnostic_status=PASS` without provenance / capacity details: REVIEW
- missing provider context: NEEDS_INPUT
- explicit blocker/error: BLOCKED

## Storage Boundary

This task does not add a registry, memo, preset, or report persistence path.
It only extends compact evidence already flowing through provider context and Backtest Realism Audit.
