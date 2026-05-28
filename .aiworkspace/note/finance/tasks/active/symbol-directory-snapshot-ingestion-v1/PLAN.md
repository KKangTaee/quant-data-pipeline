# Symbol Directory Snapshot Ingestion V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 8 source review 결과, 무료 / 공식 source 중 바로 구현 가능한 다음 단계는 Nasdaq public Symbol Directory current snapshot이다.
이 source는 complete historical membership이 아니지만, NYSE-only current snapshot보다 넓은 current listing evidence를 DB에 쌓을 수 있다.

이 task는 future computed lifecycle evidence를 만들기 위한 기반으로 public current snapshot을 `nyse_symbol_lifecycle`에 보수적으로 적재한다.

## Scope

포함한다.

- `finance/data/symbol_directory.py` collector 추가
- `nasdaqlisted.txt`, `otherlisted.txt` parser 추가
- lifecycle row를 `current_listing_snapshot` / `listing_observed` / `partial` evidence로 저장
- ingestion job wrapper 추가
- service contract test 추가
- data docs / Phase 8 board / roadmap sync

포함하지 않는다.

- complete historical membership PASS 처리
- missing-from-current-file delisting 추론
- 새 JSONL registry
- user memo / preset persistence
- UI direct fetch
- live approval / broker order / auto rebalance

## Done Criteria

- Nasdaq public symbol directory text가 lifecycle rows로 normalize된다.
- DB write summary가 registry / memo / preset side effect 없음으로 고정된다.
- current snapshot rows remain partial evidence.
- `git diff --check`, compile, focused tests pass.
