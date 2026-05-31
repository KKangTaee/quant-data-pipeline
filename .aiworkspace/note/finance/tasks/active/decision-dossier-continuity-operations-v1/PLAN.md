# Decision Dossier Continuity Operations V1 Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Selected Portfolio Dashboard는 Final Review에서 선정된 row를 운영 확인 대상으로 읽는다.
하지만 Decision Dossier, Continuity, Timeline, Review Signals가 서로 다른 source identity나 session-state evidence를 참조하는 것처럼 보이면, 선정 이후 검증 결과가 durable monitoring history처럼 오해될 수 있다.

이 task의 목적은 새 저장 기능을 만들지 않고, 네 surface가 같은 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2` decision row를 기준으로 읽는다는 source consistency 계약을 코드, UI, 테스트에 명시하는 것이다.

## Scope

- Timeline / Continuity / Review Signals / Decision Dossier에 selected decision source contract를 추가한다.
- Continuity가 timeline source contract mismatch를 blocked continuity issue로 표시하게 한다.
- Decision Dossier markdown에 source contract와 read-only execution boundary를 표시한다.
- Selected Portfolio Dashboard에 source contract table을 추가한다.
- service contract tests로 source consistency, mismatch, read-only boundary를 고정한다.

## Out Of Scope

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- report 파일 자동 저장
- account holdings 자동 연결
- broker sync, live approval, order draft, auto rebalance
