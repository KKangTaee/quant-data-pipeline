# Merge Review Fixes 2026-06-08

Status: Completed
Last Verified: 2026-06-08

## Purpose

sub-dev / main-dev master merge 후 리뷰에서 확인된 Reference link, task status, contract-test coverage 문제를 바로잡는다.

## 이걸 하는 이유?

병합 자체는 큰 충돌 marker 없이 정리됐지만, Reference contextual help의 internal markdown link가 Streamlit direct route에서 깨지고, 완료된 Reference V4 task plan이 In Progress로 남아 있었으며, Reference Guides catalog 테스트의 required-key assertion 방향이 느슨했다.
이 작업은 새 제품 기능을 추가하지 않고 병합 후 안전성을 회복하는 소규모 fix다.

## Scope

- Reference contextual help internal links를 Streamlit page target 기반으로 렌더한다.
- `reference-contextual-links-v4-20260608/PLAN.md` 상태를 Completed로 맞춘다.
- Reference Guides catalog test의 required task key assertion 방향을 바로잡는다.
- Focused tests, service contract, UI boundary, Browser QA를 실행한다.

## Not In Scope

- Reference 전체 UX 재설계.
- URL query deep-linking.
- Ingestion / Overview Reference help surface 추가.
- DB / registry / saved JSONL 변경.
