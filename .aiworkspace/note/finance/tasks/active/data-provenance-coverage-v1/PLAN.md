# Data Provenance Coverage V1 Plan

Status: Complete
Created: 2026-05-28
Owner: finance-db-pipeline + finance-backtest-web-workflow

## 이걸 하는 이유?

`storage-governance-audit-v1`에서 새 JSONL을 늘리지 않는 기준은 정리했다.
다음 문제는 기존 DB-backed provider / macro evidence가 Final Review에서 "실전 검토에 충분한 근거인지"를 판단할 만큼 출처와 freshness를 명확히 보여주느냐다.

이번 task는 새 저장소를 만들지 않고, 이미 DB loader가 읽는 provider snapshot metadata를 compact provenance / freshness / coverage read model로 바꿔 Practical Validation과 Final Review가 더 엄격하게 해석하게 만드는 작업이다.

## Scope

- ETF operability / holdings / exposure / macro loader 결과의 source / source_type / as_of_date / collected_at / coverage_status를 compact provenance summary로 변환
- provider snapshot이 오래됐을 때 PASS로 숨기지 않고 REVIEW로 낮추는 policy 추가
- Practical Validation result의 provider coverage display row에 source mix / freshness / as-of range를 표시
- Final Review packet에 연결되는 provider coverage status가 stale / partial / bridge / proxy를 반영하도록 유지
- service contract test 추가
- 관련 data / phase / roadmap 문서 동기화

## Out Of Scope

- 새 JSONL registry
- registry rewrite
- 새 DB table 또는 schema migration
- 새 remote provider / crawler 추가
- UI에서 provider / FRED 직접 fetch
- holdings 2차 look-through expansion
- report export / dossier 생성

## Completion Criteria

- provider context에 area별 `provenance` summary가 포함된다.
- stale provider snapshot은 해당 diagnostic status를 `REVIEW`로 낮춘다.
- display row에서 source mix와 freshness를 확인할 수 있다.
- `tests/test_service_contracts.py`에 provider provenance contract가 추가된다.
- `git diff --check`, focused py_compile, service contract test, boundary check가 통과한다.
