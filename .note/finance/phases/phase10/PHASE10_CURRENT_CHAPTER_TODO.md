# Phase 10 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 10 상위 계획 문서 작성
  - `PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
- `completed` current static preset vs dynamic PIT mode 역할 분리 방향 고정
- `completed` Phase 10 active phase 전환
  - real-money validation 우선순위에 맞춰 productization보다 먼저 dynamic PIT 구현 phase로 전환

## 2. Dynamic Universe Contract

- `completed` rebalance-date membership contract first pass 정의
  - annual strict single-strategy form에 `Universe Contract` selector 추가
  - `Static Managed Research Universe`
  - `Historical Dynamic PIT Universe`
- `completed` listing / delisting / symbol continuity rule second pass
  - price-window continuity 진단 추가
  - asset-profile 상태 진단 추가
  - candidate status row persistence 추가
- `completed` static mode와 dynamic mode 차이 문구 first pass 고정
- `completed` first-pass baseline 방향 고정
  - annual strict family부터 시작
  - current static mode는 유지
  - rebalance-date approximate PIT market-cap universe를 first-pass contract로 사용

## 3. PIT Source Inventory

- `completed` historical market-cap reconstruction source inventory 초안
- `completed` listing / delisting metadata source inventory 초안
- `completed` missing metadata fallback rule 초안
  - `PHASE10_PIT_SOURCE_AND_SCHEMA_GAP_ANALYSIS.md`

## 4. Annual Strict First Pass

- `completed` annual strict family dynamic mode scope 정의
- `completed` dynamic annual runtime first pass 설계 초안
- `completed` strict annual single-strategy dynamic runtime first pass 구현
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- `completed` static vs dynamic comparison output contract first pass
  - result row에 `Universe Membership Count`, `Universe Contract` 기록
  - bundle meta에 `universe_contract`, `dynamic_candidate_count`, `dynamic_target_size`, `universe_debug` 기록
- `completed` annual strict compare mode dynamic PIT first pass 확장
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
  - compare override에서 `Universe Contract` / `dynamic_candidate_tickers` / `dynamic_target_size` 전달

## 5. Validation Surface

- `completed` universe drift readout first pass
  - `Execution Context`에 dynamic candidate pool / membership summary 노출
  - `Runtime Metadata`에 `universe_debug` JSON 유지
- `completed` candidate drift / membership drift 해석 first pass
- `completed` dynamic mode help / caution 문구 first pass
- `completed` static vs dynamic compare readout 확장
  - compare highlight table에 `Universe Contract`, `Dynamic Candidate Pool`, `Membership Avg`, `Membership Range` 추가
  - dynamic compare run일 때 compare-level info 문구 추가
- `completed` history snapshot persistence first pass
  - dynamic run history context에 `dynamic_universe_artifact` / `dynamic_universe_preview_rows` 기록
  - snapshot json artifact 저장

## 6. Quarterly Dynamic Expansion

- `completed` quarterly strict prototype dynamic PIT first pass 확장
  - quarterly strict single-strategy form에 `Universe Contract` selector 추가
  - quarterly runtime / compare / history artifact 연동
  - `Quality / Value / Quality+Value Snapshot (Strict Quarterly Prototype)` 지원

## 7. Documentation And Validation

- `completed` Phase 10 reference docs 추가
- `completed` Phase 10 test checklist first-pass refresh
- `completed` Phase 10 second-pass hardening 문서 추가
- `completed` roadmap / index / comprehensive analysis sync second pass
- `completed` roadmap / index / progress sync first pass
- `completed` practical closeout / later batch checklist review 방향 고정
  - user-side batch QA는 계속 가능하지만,
    current phase 목표 기준으로는 closeout 가능한 상태로 정리

## 현재 메모

- current strict preset은 계속 `managed static research universe`로 유지한다.
- Phase 10의 목적은 current mode를 대체하는 것이 아니라,
  **실전형 검증용 dynamic PIT mode를 추가하는 것**이다.
- first implementation target은 annual strict family가 맞았고, 그 다음 pass에서 quarterly strict prototype까지 확장되었다.
- 현재 구현된 범위는 annual strict + quarterly strict prototype **single strategy + compare first pass**이다.
- history artifact persistence와 candidate continuity diagnostics도 현재 surface에 포함된다.
- 다만 perfect constituent-history source는 아직 없고, current-source 기반 approximate PIT + diagnostics contract로 읽는 것이 맞다.
- stronger listing / delisting source 같은 더 강한 PIT reinforcement는 long-term backlog로 남지만,
  current chapter closeout의 blocker는 아니다.
- `Phase 11`은 validation contract를 더 엄격하게 만드는 phase가 아니라,
  현재 확보한 validation contract 위에 portfolio workflow를 제품화하는 phase다.
