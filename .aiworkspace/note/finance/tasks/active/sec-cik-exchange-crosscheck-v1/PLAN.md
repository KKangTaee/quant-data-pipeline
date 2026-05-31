# SEC CIK Exchange Crosscheck V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 8은 symbol lifecycle evidence를 강화하는 중이다.
Nasdaq Symbol Directory는 current listing snapshot coverage를 넓히지만, CIK / entity continuity를 직접 제공하지 않는다.

SEC `company_tickers_exchange.json`는 current CIK / company name / ticker / exchange association을 제공하므로 ticker identity를 보조하는 DB evidence로 적합하다.
단, 이것도 historical membership proof가 아니다.

## Scope

포함한다.

- SEC company ticker exchange file parser 추가
- `nyse_symbol_lifecycle`에 current `listing_observed` partial evidence로 저장
- `related_cik`와 compact `evidence_json`에 CIK / exchange context 저장
- ingestion job wrapper 추가
- focused service contract test 추가
- data docs / Phase 8 board / roadmap sync

포함하지 않는다.

- complete historical membership PASS 처리
- SEC association을 delisting / ticker action proof로 해석
- 새 JSONL registry
- user memo / preset persistence
- live approval / broker order / auto rebalance

## Done Criteria

- SEC current association row가 lifecycle evidence로 normalize된다.
- DB write summary가 registry / memo / preset side effect 없음으로 고정된다.
- current association rows remain partial evidence.
- `git diff --check`, compile, focused tests pass.
