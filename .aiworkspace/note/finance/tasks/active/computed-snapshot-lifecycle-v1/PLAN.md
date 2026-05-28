# Computed Snapshot Lifecycle V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 8은 historical universe / survivorship evidence를 DB-backed로 강화하는 중이다.
현재 Nasdaq Symbol Directory, SEC CIK cross-check, NYSE listing snapshot은 모두 current snapshot evidence라서 단독으로 historical membership을 증명하지 못한다.

이 task는 repeated current snapshots가 쌓였을 때 그 관찰 구간을 `computed_from_snapshots` row로 요약하되, 부재나 사라짐을 delisting proof로 과대 해석하지 않도록 보수적 정책을 고정한다.

## Scope

포함한다.

- 기존 `nyse_symbol_lifecycle` current snapshot rows를 읽어 computed lifecycle row를 만든다.
- computed row는 같은 table에 `source=computed_snapshot_lifecycle`, `source_type=computed_from_snapshots`로 저장한다.
- source count, observation dates, observation span, pass eligibility를 compact `evidence_json`에 둔다.
- Data Coverage Audit이 computed row를 PASS 후보로 볼 수 있는 coverage 조건을 보수화한다.
- ingestion job wrapper와 service contract test를 추가한다.
- data docs / Phase 8 board / roadmap sync를 진행한다.

포함하지 않는다.

- 새 JSONL registry
- user memo / preset persistence
- absence from snapshot을 delisting proof로 해석
- current snapshot만으로 historical membership actual claim
- UI direct fetch
- live approval / broker order / auto rebalance

## Done Criteria

- computed row builder가 repeated snapshot evidence를 partial / review evidence로 요약한다.
- computed row가 current snapshot 부재만으로 delisted / inactive를 만들지 않는다.
- Data Coverage Audit은 `computed_from_snapshots`라도 `coverage_status=actual`이 아니면 survivorship PASS로 보지 않는다.
- compile, focused tests, full service contract, `git diff --check`가 통과한다.
