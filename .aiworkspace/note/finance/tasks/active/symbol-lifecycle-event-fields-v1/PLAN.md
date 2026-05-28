# Symbol Lifecycle Event Fields V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 8은 survivorship / delisting / ticker lifecycle 근거를 강화하는 phase다.
현재 `nyse_symbol_lifecycle`은 source type과 coverage status는 갖고 있지만, row가 어떤 lifecycle event를 의미하는지 명시하는 필드는 부족하다.

이 task는 future ticker change / merger / historical membership ingestion을 넣기 전에 DB row contract를 먼저 안정화한다.

## Scope

포함한다.

- `nyse_symbol_lifecycle` event field 추가
- NYSE current listing snapshot row에 `listing_observed` event 명시
- SEC Form 25 row에 `delisting` event 명시
- loader가 event fields를 반환
- focused service contract 보강
- data docs / phase docs / roadmap sync

포함하지 않는다.

- 새로운 external source crawler
- 새 JSONL registry
- 사용자 메모 / preset 저장
- UI direct fetch
- broker order / live approval / auto rebalance

## Done Criteria

- Form 25 row가 delisting event로 테스트된다.
- current listing snapshot은 partial listing-observed event로 남는다.
- loader output이 event fields를 포함한다.
- docs가 event field 의미를 설명한다.
