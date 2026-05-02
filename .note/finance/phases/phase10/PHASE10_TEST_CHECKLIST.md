# Phase 10 Test Checklist

## 목적

- `historical dynamic PIT universe` mode가
  current static preset과 구분되는 실전형 validation contract로 동작하는지 확인한다.

## 1. mode contract disclosure

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

각 single-strategy form의 `Advanced Inputs` 안에
`Universe Contract` selector가 보이는지 확인

- `Static Managed Research Universe`
- `Historical Dynamic PIT Universe`

두 mode의 의미가 UI caption / info 문구에서 분명히 구분되는지 확인

## 2. annual strict dynamic first pass execution

- 위 3개 annual strict single-strategy form에서
  `Historical Dynamic PIT Universe`를 선택하고 실행
- 결과 bundle이 정상적으로 반환되는지 확인
- large candidate pool에서도 late listing / no-history candidate 때문에 hard-fail 하지 않는지 확인

## 3. dynamic candidate pool semantics

- preset mode에서 dynamic PIT를 선택하면
  `US Statement Coverage 1000` managed candidate pool을 기반으로
  target membership를 다시 계산한다는 설명이 보이는지 확인
- manual mode에서는 current manual ticker set이
  candidate pool로 사용된다는 점이 자연스럽게 읽히는지 확인
- `dynamic_candidate_count`와 `universe_debug.candidate_pool_count`가 다를 수 있다는 점이
  설명/메타에서 자연스럽게 해석되는지 확인

## 4. rebalance-date membership readout

- result table에 아래 컬럼이 추가되는지 확인
  - `Universe Membership Count`
  - `Universe Contract`
- `Execution Context`에서 아래가 보이는지 확인
  - `Universe Contract`
  - `Dynamic Candidate Pool`
  - membership summary
- `Runtime Metadata`에 `universe_debug`가 유지되는지 확인

## 5. history / prefill contract

- 여기서 `dynamic run`은 `Universe Contract = Historical Dynamic PIT Universe`로 annual strict 전략을 실행한 경우를 뜻한다
- annual strict dynamic run을 history에 남긴 뒤
  `Load Into Form`을 실행
- 해당 annual strict form에서 `Universe Contract`가
  이전 run 값으로 다시 채워지는지 확인

## 6. static vs dynamic comparison smoke

- 같은 annual strict strategy / 같은 기간 / 같은 preset에서
  `static`과 `dynamic PIT`를 각각 실행
- 결과 차이 또는 membership count 차이가 읽히는지 확인

## 7. annual strict compare dynamic mode

- `Compare & Portfolio Builder`에서 아래 annual strict 전략을 선택한다
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- 각 strategy block 안에 `Universe Contract` selector가 보이는지 확인
- `Historical Dynamic PIT Universe`를 선택해 compare run이 정상 완료되는지 확인
- `Strategy Highlights`에서 아래 컬럼이 보이는지 확인
  - `Universe Contract`
  - `Dynamic Candidate Pool`
  - `Membership Avg`
  - `Membership Range`

## 8. quarterly strict dynamic first pass

- 아래 3개 quarterly prototype form에서도 `Universe Contract` selector가 보이는지 확인
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- `Historical Dynamic PIT Universe`를 선택하고 실행했을 때 run이 정상 완료되는지 확인
- result/meta에서 아래가 annual과 같은 방식으로 유지되는지 확인
  - `Universe Membership Count`
  - `Universe Contract`
  - `universe_debug`
  - `dynamic_universe_snapshot_rows`
  - `dynamic_candidate_status_rows`

## 9. continuity / delisting diagnostics

- dynamic run의 `Runtime Metadata > universe_debug` 안에 아래 continuity 항목이 보이는지 확인
  - `continuity_ready_count`
  - `pre_listing_excluded_count`
  - `post_last_price_excluded_count`
  - `asset_profile_delisted_count`
  - `asset_profile_issue_count`
- 의미:
  - `continuity_ready_count`: 해당 날짜를 가격 이력상 자연스럽게 커버하는 후보 수
  - `pre_listing_excluded_count`: 아직 상장 전이라 제외된 후보 수
  - `post_last_price_excluded_count`: 마지막 가격 이후라 제외된 후보 수
  - `asset_profile_delisted_count` / `asset_profile_issue_count`: profile 기준 continuity 힌트
- `Execution Context` 또는 history artifact preview에서 continuity / profile 진단이 자연스럽게 해석되는지 확인

## 10. history artifact persistence

- dynamic annual 또는 quarterly run을 history에 남긴다
- history drilldown에서 아래가 보이는지 확인
  - `dynamic_universe_preview_rows`
  - `dynamic_universe_artifact`
- artifact 경로가 실제 파일로 존재하는지 확인
- 의미:
  - `dynamic_universe_preview_rows`: history에 같이 저장하는 날짜별 membership 미리보기
  - `dynamic_universe_artifact`: 별도 저장 JSON 산출물 메타데이터
  - `snapshot_json` path: 실제 저장된 JSON 파일 경로

## 11. PIT caution messaging

- dynamic mode가 실전형 validation에 더 가깝다는 점
- 하지만 아직 perfect constituent-history는 아니라는 점
- 현재 static mode는 여전히 연구용 contract라는 점

이 세 가지가 과장 없이 설명되는지 확인

## 12. compare dynamic quarterly smoke

- `Compare & Portfolio Builder`에서 아래 quarterly prototype 전략을 선택한다
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- 각 strategy block에서 `Historical Dynamic PIT Universe`를 고를 수 있는지 확인
- compare run이 정상 완료되고 dynamic membership 관련 readout이 유지되는지 확인

## 13. later handoff

- perfect constituent-history source reinforcement는 아직 later pass라는 점이 문서와 구현에서 일관적인지 확인
- current contract가 `approximate PIT + diagnostics`라는 점이 분명한지 확인
- 이후 Phase 11 productization으로 자연스럽게 이어질 수 있는지 확인

## closeout 판단 기준

아래가 모두 만족되면
Phase 10은 first-pass dynamic PIT universe closeout 후보로 볼 수 있다.

1. annual strict single-strategy family가 dynamic mode로 실행된다
2. quarterly strict prototype family도 dynamic mode로 실행된다
3. `Universe Contract` / `Universe Membership Count` / `universe_debug` / history artifact가 노출된다
4. static vs dynamic 차이를 읽을 수 있다
5. current static mode와 dynamic mode 계약이 혼동되지 않는다
6. perfect constituent-history가 아니라는 점이 명확히 드러난다
