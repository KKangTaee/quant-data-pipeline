# Economic Cycle Intramonth Nowcast Design

Status: Approved
Date: 2026-07-21
Owner: Overview / Market Context

## Context

`Workspace > Overview > Market Context > 경제 사이클`은 현재 마지막 월말
`economic_cycle_snapshot`을 읽는다. 2026-07-21 현재 화면의 canonical 월말 원점은
2026-06-30이다. 이 원점은 그날까지 공개된 FRED/ALFRED vintage만 사용하므로
point-in-time 의미는 정확하지만, 7월에 새로 공개된 고용·금융·정책 자료가 월말
모델과 자산 관측 사이에 반영되지 않는다.

사용자는 과거 월말 데이터를 훼손하지 않으면서 현월의 최신 공개정보가 경제사이클
추정을 어느 방향으로 움직였는지 보고 싶다. 월말과 월중 모두 모델 추정이며,
월중 결과는 불완전한 release mix를 사용하는 `잠정 계산`이다.

## Goals

- 기존 `current`와 `historical_replay` 월말 snapshot을 수정하거나 재작성하지 않는다.
- 같은 17-series PIT catalog에서 최신 공개 vintage만 증분 수집한다.
- 최근 월말 모델 artifact로 날짜별 월중 nowcast를 별도 materialize한다.
- 월이 바뀌면 종료된 직전 월의 canonical 월말 snapshot을 한 번 append한 뒤 새 현월
  nowcast의 baseline으로 사용한다.
- Overview에 월말 기준점과 최신 월중점의 변화, 계산일, 수집일, 원천 최신일을 함께 표시한다.
- 매 평일 한 번 backend automation으로 갱신한다.
- 수집 또는 계산 실패 시 마지막 정상 월중 결과를 유지한다.

## Non-goals

- 월중 값을 NBER 공식 판정이나 확정 경기국면으로 표시하지 않는다.
- 공개되지 않은 월간 지표를 보간하거나 합성하지 않는다.
- 월중 결과로 기존 60개월 ribbon 또는 historical replay를 채우지 않는다.
- 화면 render나 `browser_safe` profile에서 provider를 호출하지 않는다.
- validation threshold를 낮추거나 `LIMITED` artifact를 `READY`로 바꾸지 않는다.
- 일별 모델 재학습, 매매 신호, 목표가격을 만들지 않는다.

## Considered Approaches

### 1. Daily overwrite of `current`

구현은 단순하지만 월말 원점과 월중 원점의 의미가 섞이고 과거 기준점이 사라진다.
보존 요구와 맞지 않아 제외한다.

### 2. Live computation during Overview render

항상 최신 결과를 계산할 수 있지만 UI의 DB-only 계약을 위반하고 현재 full PIT panel
계산에 약 25초가 걸린다. Provider/fit/write를 UI에서 분리한다는 프로젝트 경계와 맞지
않아 제외한다.

### 3. Separate persisted intramonth snapshot

월말 원점을 보존하고 월중 결과만 독립적으로 실패 격리할 수 있다. 자동화가 성공한
경우에만 compact row를 저장하고 Overview는 저장 결과만 읽는다. 이 접근을 채택한다.

## Architecture

### A. Incremental vintage collection

`finance/data/economic_cycle_vintages.py`에 series별 최신 `realtime_start`를 읽는 DB
경계를 추가한다. 첫 실행 또는 coverage가 없으면 기존 full bootstrap을 사용한다.
이후 실행은 각 series의 마지막 알려진 vintage date를 overlap 시작점으로 사용한다.

FRED `series/vintagedates`와 observations 요청은 이 overlap부터 open end까지만 조회한다.
마지막 기존 interval을 다시 받기 때문에 새 release가 생겼을 때 이전 open-ended
`realtime_end`가 닫히고 새 interval이 추가된다. Business key
`(series_id, observation_date, realtime_start, source)`와 UPSERT 계약은 유지한다.

17개 series 중 하나라도 provider 수집에 실패하면 combined refresh는 실패로 끝내고
새 nowcast를 저장하지 않는다. 이미 저장된 raw vintage와 마지막 정상 nowcast는
그대로 유지한다.

### B. Intramonth materialization

`economic_cycle_snapshot.run_kind`에 `intramonth_nowcast`를 추가한다. 기존 unique key
`(as_of_date, model_version, run_kind)`를 그대로 사용하므로 날짜별 row가 보존되고 같은
날짜 재실행은 idempotent UPSERT다.

월중 materializer는 다음 순서로 동작한다.

1. `as_of_date`보다 이전 또는 같은 최신 `current` 월말 snapshot을 읽는다.
2. 그 snapshot의 exact `model_version` artifact를 읽는다.
3. 전체 PIT history의 month-end origins 뒤에 `as_of_date` 원점을 하나 추가한다.
4. 공개되지 않은 값을 채우지 않고 origin-eligible observation만으로 factor를 계산한다.
5. 기존 provisional scoring contract로 h0/h1/h2를 계산하되 UI 월중 브리지는 h0만 사용한다.
6. 모든 계산과 compact metadata 생성이 성공한 뒤 한 row를 UPSERT한다.

월중 row에는 기존 snapshot 필드와 함께 다음 compact metadata를 둔다.

- `source_collected_at`: 사용한 raw vintage의 마지막 실제 수집시각
- `source_coverage_json`: series별 최신 관측일, staleness, coverage status
- `baseline_as_of_date`: 비교한 월말 snapshot 원점

역사 월말 row에는 새 필드가 `NULL`이어도 된다. 기존 row를 backfill하지 않는다.

### C. Scheduled refresh

`app/jobs/overview_automation.py`에 economic-cycle combined runner를 등록한다.

- profiles: `safe`, `standard`, `broad`
- cadence: 24시간
- calendar: 평일만 실행
- excluded profile: `browser_safe`
- required credential: `FRED_API_KEY`

runner는 `incremental collection -> closed-month rollover -> intramonth materialization`을
순서대로 실행한다.

`closed-month rollover`는 오늘보다 이전인 가장 최근 calendar month-end를 구한다. 그
날짜의 `current` snapshot이 없을 때만 기존 계약대로 직전 month-end까지 학습·검증하고
새 canonical month-end row를 append한다. 같은 key 재실행은 idempotent하며 이전 월말
row를 다시 계산하거나 수정하지 않는다. 예를 들어 8월 첫 평일에는 7/31 월말 row가
없을 때만 이를 만든 뒤 8월 월중 nowcast를 계산한다. 당일이 월말이면 아직 종료된 달로
승격하지 않고 다음 달 첫 평일 rollover에 맡긴다.

수집이 partial/failed이거나 materialization이 계산 불가로 종료되면 전체 job을 실패로
기록하고 snapshot write를 수행하지 않는다. 기존 run history를 사용하며 새로운 사용자
진단 패널은 만들지 않는다.

### D. Loader and service contract

`finance/loaders/economic_cycle.py`는 latest `intramonth_nowcast`를 요청일 이하에서 읽되,
baseline 월말보다 오래된 row는 반환하지 않는다.

`app/services/overview/economic_cycle.py`의 기존 top-level 월말 payload는 호환성을 위해
그대로 유지한다. 선택적 `intramonth` object를 추가한다.

```text
intramonth
  as_of_date
  source_collected_at
  baseline_as_of_date
  estimate_status = PROVISIONAL | UNAVAILABLE
  current_horizon
  factor_evidence
  factor_deltas
  probability_deltas
  source_coverage
```

월중 row가 없거나 baseline보다 오래되었으면 `intramonth`는 `null`이다. 월말 화면은
기존과 동일하게 정상 렌더링된다.

### E. Overview presentation

기존 월말 h0/h1/h2 카드와 60개월 ribbon은 바꾸지 않는다. 월말 확률 카드 다음,
Cycle Map 전에 `월중 흐름` 블록을 추가한다.

- 왼쪽: `YYYY-MM-DD 월말 추정`
- 가운데: 확률과 네 factor 변화 방향
- 오른쪽: `YYYY-MM-DD 현재 입수정보 기반 잠정 계산`
- 보조 문구: `계산 기준일`, `마지막 수집`, 주요 원천 최신일

Cycle Map은 월말 h0에서 월중 h0로 이어지는 별도 점선 segment와 접근 가능한 tooltip을
추가한다. 월중점은 history 실선, +1M/+2M forecast 점선과 다른 class/legend를 사용한다.
두 원점 사이에 존재하지 않는 일별 점을 보간하지 않는다.

월중 값은 항상 `현재 입수정보 기반 잠정 계산`으로 표시한다. Artifact가 READY여도
intramonth origin 자체가 별도 validation을 통과하기 전에는 `VERIFIED`로 승격하지 않는다.

## Error Handling

- API key 없음: job failed, last-good nowcast 유지
- provider series 일부 실패: 새 nowcast 미기록, last-good 유지
- 신규 release 없음: overlap fetch와 idempotent UPSERT 후 현재 cutoff로 계산 가능
- exact artifact 없음: 새 nowcast 미기록
- PIT input 또는 parameter 불완전: 해당 계산 실패, 월말 payload 유지
- service read 실패: `intramonth=null`, 기존 월말 화면 유지
- stale monthly inputs: nowcast는 `PROVISIONAL/LIMITED`로 표시하고 coverage 근거 노출

## Testing

### Data and pipeline

- first-run full bootstrap과 subsequent overlap start
- 새 release가 이전 open interval을 닫는 UPSERT
- multiple missed release dates의 증분 수집
- partial provider failure가 nowcast write를 막는지
- same-day rerun idempotence
- current/historical rows가 변경되지 않는지
- 새 달 첫 평일에 누락된 직전 month-end만 append하고 같은 rollover를 반복하지 않는지
- calendar month-end 당일에는 canonical rollover를 조기 실행하지 않는지
- partial origin이 미래 vintage를 읽지 않는지
- last monthly artifact를 exact version으로 재사용하는지

### Scheduler and service

- weekday daily due / weekend skip / 24-hour cadence
- safe/standard/broad 포함, browser_safe 제외
- latest valid nowcast와 baseline pairing
- missing/stale nowcast fallback
- source date와 collected-at 분리

### UI and actual QA

- legacy payload에서 기존 화면 회귀 없음
- monthly-to-intramonth bridge, labels, deltas, tooltip
- ribbon에 intramonth row가 섞이지 않는지
- React typecheck/test/build와 tracked `component_static` rebuild
- desktop 및 420px Browser QA, overflow/console/page errors 0
- generated screenshot은 커밋하지 않음

## Completion Criteria

- 구현 전 존재하던 월말 날짜 범위의 row count와 checksum 표본이 구현 전후 동일하다.
- 기존 과거 월말 row는 불변이고, 새로 종료된 달의 canonical row와 신규 날짜별
  `intramonth_nowcast`만 추가된다.
- 자동 job 실패 시 마지막 정상 월중 화면이 유지된다.
- Overview가 월말과 월중의 계산일·수집일·원천 최신일을 구분한다.
- 7/21 actual local data에서 월말→월중 브리지가 렌더링되고 `잠정 계산`으로 표시된다.
- focused tests, Python compile, React build, Browser QA가 통과한다.
