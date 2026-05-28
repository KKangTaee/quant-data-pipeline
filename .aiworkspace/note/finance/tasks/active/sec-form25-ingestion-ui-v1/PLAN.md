# SEC Form 25 Ingestion UI V1 Plan

Status: Complete
Started: 2026-05-28
Completed: 2026-05-28

## 이걸 하는 이유?

SEC Form 25 delisting collector는 구현됐지만, 현재는 코드에서 직접 호출해야 한다.
검증용 delisting evidence는 실전 투자 가능성 판단에 필요한 DB-backed evidence이므로,
기존 `Workspace > Ingestion` 운영 화면에서 수동으로 실행할 수 있어야 한다.

## Scope

- `Workspace > Ingestion > Practical Validation Provider Snapshots`에 `Delisting Evidence` 탭을 추가한다.
- 탭은 SEC Form 25 / 25-NSE collector job wrapper를 실행한다.
- 입력은 symbol list, optional SEC user-agent override, archive file lookup option으로 제한한다.
- 수집 결과는 기존 ingestion job result surface를 사용한다.

## Out Of Scope

- 새 JSONL registry
- 사용자 메모 / comment 저장
- reusable preset 저장
- report file 자동 생성
- live approval, broker order, auto rebalance
- SEC collector logic 자체 변경

## Done Criteria

- Streamlit app import / py_compile가 통과한다.
- SEC Form 25 job wrapper service contract가 계속 통과한다.
- Browser로 Ingestion page가 열리고 `Delisting Evidence` 탭이 보인다.
- `.DS_Store`, run history, generated artifact는 stage하지 않는다.
