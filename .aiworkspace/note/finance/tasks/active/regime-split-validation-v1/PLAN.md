# Regime Split Validation V1 Plan

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## 이걸 하는 이유?

Phase 10의 10-2 / 10-3에서 walk-forward와 OOS evidence는 생겼지만, 시장 국면별로 전략 성과가 유지되는지는 아직 current macro snapshot 중심이었다.
이 task의 목적은 DB에 저장된 FRED macro observation history를 이용해 neutral / caution / risk-off bucket별 portfolio / benchmark 성과를 compact evidence로 확인하는 것이다.

새 JSONL registry, 사용자 메모, preset 저장, 승인, 주문, 자동 리밸런싱을 추가하지 않는다.

## Scope

포함한다.

- DB-backed `macro_series_observation` history를 loader로 읽는 read-only 경로 연결
- `VIXCLS`, `T10Y3M`, `BAA10Y` 기반 월별 regime bucket 분류
- portfolio / benchmark 월별 수익률을 regime bucket별로 집계하는 compact contract 추가
- Practical Validation result payload에 `regime_split_validation` evidence 연결
- Validation Efficacy Audit에 `Regime split validation` row 추가
- service contract tests 추가
- Project Map / script map / roadmap / phase handoff sync

포함하지 않는다.

- 새 DB schema
- 새 macro collector
- 새 JSONL registry
- raw macro series 또는 raw split curve artifact 저장
- user memo / preset persistence
- broker order / live approval / auto rebalance

## Done Criteria

- missing macro history는 `PASS`가 아니다.
- short shared history는 `NEEDS_INPUT`이다.
- proxy / bridge macro source 또는 proxy curve source는 강한 `PASS`가 아니라 `REVIEW`로 남는다.
- 충분한 official actual macro history, portfolio curve, benchmark parity가 있으면 regime rows가 `PASS` 또는 `REVIEW`로 계산된다.
- Validation Efficacy Audit이 regime split row를 읽고 route에 반영한다.
- compile, service contract, boundary, hygiene, diff check가 통과한다.
