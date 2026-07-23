# Futures Macro On-Demand Daily Finalization Follow-up Design

Date: 2026-07-24
Status: User-approved design; written-spec review pending

## 이걸 하는 이유?

현재 Futures Macro의 같은 뉴욕 날짜 일봉은 `17:15–18:00 ET`에 수집됐을
때만 즉시 완료로 인정한다. `18:00 ET` 이후에는 Yahoo의 같은 날짜 일봉이
다음 저녁 세션 움직임으로 다시 변할 수 있어 pending 처리한다.

이 보호 로직은 다음 세션 혼입을 막지만, 사용자가 한국시간
`06:15–07:00`의 45분 안에 갱신하지 않으면 `13:00`까지 전일 기준일을
반영하지 못한다. 데이터 수집은 성공해도 화면 기준일이 바뀌지 않으므로
실사용에서는 갱신 실패처럼 보인다.

사용자가 승인한 성공 기준은 다음과 같다.

> 한국시간 오전 7시 이후 `일봉 갱신`을 누르면 다음 저녁 세션 가격을
> 섞지 않고도 직전 완료 미국 선물 세션을 즉시 반영한다.

## Current Root Cause

현재 경로는 mutable Yahoo `1d` row의 수집 시각만으로 finality를 판단한다.

```text
1d overlap download
  -> same-date row UPSERT
  -> 17:15–18:00 ET collection이면 FINAL
  -> 18:00 ET 이후 collection이면 IN_PROGRESS
  -> latest-good snapshot 재사용
```

`18:00 ET` 이후 같은 Yahoo 일봉을 그대로 FINAL로 바꾸는 것은 해결책이
아니다. 기존 actual 진단에서 해당 row의 OHLCV가 저녁 재개 후 계속
변하는 것이 확인됐기 때문이다.

## Considered Approaches

### 1. Session-bounded intraday reconstruction in the existing daily row — selected

Yahoo `5m` 데이터를 직전 완료 세션 구간으로 제한해 OHLCV를 재구성하고,
기존 `1d` row에 별도 `final_*` 값으로 보존한다.

- 장점: 요청 시점이 18:00 ET를 지났어도 직전 세션만 재구성할 수 있다.
- 장점: 다음 저녁 세션 데이터를 시간 구간으로 배제한다.
- 장점: 기존 일봉 row와 symbol/date key를 유지해 중복 source row가 없다.
- 비용: pending refresh에서 bounded `2d/5m` 다운로드가 한 번 추가된다.
- 비용: additive DB columns와 downstream final-value preference가 필요하다.

### 2. Separate finalized-daily shadow table

확정 일봉을 새 table에 저장하면 raw와 derived 의미는 가장 명확하지만,
새 writer/loader/join/source-of-truth 경계를 추가해야 한다. 현재 문제에
비해 변경 범위가 크므로 선택하지 않는다.

### 3. Accept the mutable Yahoo daily row after 18:00 ET

가장 작게 수정할 수 있지만 다음 세션 가격 혼입을 다시 허용한다.
point-in-time correctness와 기존 회귀 원인을 위반하므로 제외한다.

## Approved Data Contract

`finance_price.futures_ohlcv`의 기존 `1d/yfinance` row에 다음 nullable
column을 additive하게 추가한다.

| Column | Type | Meaning |
|---|---|---|
| `final_open` | `DOUBLE NULL` | session-bounded 5m first open |
| `final_high` | `DOUBLE NULL` | session-bounded 5m maximum high |
| `final_low` | `DOUBLE NULL` | session-bounded 5m minimum low |
| `final_close` | `DOUBLE NULL` | session-bounded 5m last close |
| `final_adj_close` | `DOUBLE NULL` | V1에서는 `final_close`와 동일 |
| `final_volume` | `DOUBLE NULL` | session-bounded 5m volume sum |
| `finalization_basis` | `VARCHAR(64) NULL` | `yfinance_5m_session_aggregate_v1` |
| `final_source_ref` | `VARCHAR(255) NULL` | source interval과 exact ET window |
| `finalized_at` | `TIMESTAMP NULL` | 확정 aggregate 저장 시각 |

기존 raw `open/high/low/close/volume/collected_at`은 provider 최신 상태를
계속 보존한다. 일반 `1d` UPSERT는 `final_*`, `finalization_basis`,
`final_source_ref`, `finalized_at`을 갱신하지 않는다. 한 번 저장된 확정
값은 이후 저녁 세션 raw refresh에 의해 덮어쓰이지 않는다.

확정용 `2d/5m` provider row는 기존 `futures_ohlcv` table에
`interval_code=5m`, `source=yfinance`로 먼저 UPSERT한다. aggregate
writer는 provider response를 직접 이어받지 않고 저장된 5m row를 다시
읽어 exact window를 계산한다. 따라서 source 경계는
`Ingestion -> DB raw 5m -> finalized daily columns -> Loader -> UI`를
유지한다.

schema sync 전 DB에서도 Overview 첫 읽기가 깨지지 않도록 daily loader는
새 column 조회가 `unknown column`으로 실패하면 `NULL AS final_*`인 legacy
projection으로 한 번 fallback한다. 실제 `일봉 갱신` collection entry
point가 기존 schema sync를 실행해 additive migration을 적용한다.

## Session Reconstruction

### Trigger

기존 routine `1y/1d` 수집 뒤 아래 조건을 모두 만족할 때만 확정 재구성을
시도한다.

1. resolver가 same-date `pending_session`을 보고한다.
2. evaluation time이 해당 뉴욕 거래일 `17:15 ET` 이후다.
3. `pending_session`이 current evaluation New York date와 같다.

뉴욕 날짜가 이미 다음 날이면 기존 `session_date < evaluation_date`
규칙으로 raw daily row가 FINAL이므로 추가 5m 수집을 실행하지 않는다.
`17:15 ET` 이전에는 아직 완료 세션으로 간주하지 않는다.

### Window

pending session이 `D`라면 exact New York window는 다음과 같다.

```text
start = D-1 18:00:00 ET inclusive
end   = D   17:00:00 ET exclusive
```

Yahoo `2d/5m` frame에서 이 window만 선택한다. 따라서 `D 18:00 ET` 이후
시작된 다음 세션 bar는 aggregate에 들어갈 수 없다. `ZoneInfo`를 사용해
EDT/EST 전환을 하드코딩하지 않는다.

각 symbol의 aggregate는 다음처럼 만든다.

```text
open   = first non-null Open
high   = maximum non-null High
low    = minimum non-null Low
close  = last non-null Close
volume = sum of non-null Volume
```

Futures Macro score와 pattern model은 close return을 사용하지만 trace와
기존 daily schema 일관성을 위해 OHLCV 전체를 저장한다.

### Atomic coverage gate

17개 `DEFAULT_CORE_FUTURES_SYMBOLS` 모두에서 window row와 non-null close가
있을 때만 finalization을 저장한다.

- 17/17 complete: 하나의 DB transaction으로 17개 `1d/yfinance` row의
  final columns를 갱신한다.
- 16/17 이하: final column을 한 행도 쓰지 않고 latest-good snapshot을
  유지한다.
- partial provider failure를 현재 기준일로 오인하지 않는다.

## Resolver And Model Consumption

completed-session resolver는 동일 daily row에 유효한
`finalization_basis`와 `final_close`가 있으면 다음처럼 처리한다.

1. session status를 `FINAL`로 분류한다.
2. reason을 `explicit_session_aggregate`로 기록한다.
3. normalized row의 OHLCV를 `final_*` 값으로 교체한다.
4. `raw_candle_time_utc`와 raw provider fields는 DB에 그대로 남긴다.

explicit finalized row가 없는 기존 history는 현재 date/gap 규칙을
그대로 사용한다.

final input semantics가 바뀌므로 다음 version identity를 올린다.

- `FUTURES_DAILY_SESSION_VERSION`: `futures_daily_session_v3`
- `PATTERN_ALGORITHM_VERSION`: 새 finalized-aggregate identity

이 변경은 compatible snapshot을 한 번 다시 materialize하게 하지만,
historical forecast row를 삭제하거나 재작성하지 않는다.

## Refresh Flow

```text
일봉 갱신
  -> existing 17-symbol 1y/1d overlap
  -> completed-session probe
  -> pending + >=17:15 ET ?
       no  -> existing materialization path
       yes -> 17-symbol 2d/5m bounded download
              -> raw 5m rows UPSERT
              -> stored 5m exact-window reload
              -> exact session aggregate
              -> 17/17 atomic final columns write
  -> completed-session probe
  -> compact snapshot materialization
  -> DB-only rerun
```

성공하면 같은 클릭 안에서 기준일이 pending session으로 이동한다.
`다시 읽기`는 계속 provider fetch나 materialization을 실행하지 않는다.

## Error Handling

- 5m download 실패 또는 17/17 미달:
  - raw daily collection 성공은 보존한다.
  - snapshot은 latest-good 기준일을 유지한다.
  - action result는 `partial_success`와 finalization 사유를 반환한다.
- DB finalization transaction 실패:
  - 전체 rollback하고 partial final columns를 남기지 않는다.
  - snapshot materialization은 기존 latest-good 입력으로만 진행한다.
- 이미 같은 `finalization_basis`로 17/17 완료:
  - 5m 다운로드와 DB write를 생략하고 기존 확정값을 재사용한다.
- schema migration 전 read:
  - legacy projection fallback으로 기존 화면을 유지한다.

새 run/job/row 진단 패널은 UI에 추가하지 않는다. 기존 action feedback과
pending disclosure만 사용한다.

## Actual Feasibility Evidence

2026-07-24 KST read-only probe에서 Yahoo `2d/5m`를 17개 core symbol에
요청했다.

- download duration: 약 4.2초
- downloaded frame: 507 rows × 102 columns
- target session: `2026-07-22 18:00 ET` inclusive부터
  `2026-07-23 17:00 ET` exclusive
- symbol coverage: 17/17
- 각 symbol target rows: 276
- 마지막 target timestamp: 2026-07-23 16:55 ET

따라서 다음 18:00 ET 이후 데이터 없이 7/23 완료 세션 close를 현재
provider로 재구성할 수 있음을 확인했다. 이 probe는 DB write를 실행하지
않았다.

## File Ownership

Primary implementation candidates:

- `finance/data/db/schema.py`
  - additive final columns
- `finance/data/futures_market.py`
  - 2d/5m collection reuse, session aggregation, transactional final writer
- `app/jobs/overview_actions.py`
  - pending-only finalization orchestration and result contract
- `app/services/futures_macro_sessions.py`
  - explicit finalized value preference and resolver version
- `app/services/futures_macro_thermometer.py`
  - final columns projection with legacy fallback
- `app/services/futures_macro_validation.py`
  - validation/pattern daily projection alignment
- `app/services/futures_macro_pattern_validation.py`
  - algorithm identity update
- focused Futures Macro session, refresh, snapshot, and DB-pipeline tests
- active task and durable data/architecture docs

React component와 payload shape는 변경하지 않는다.

## Testing Contract

### Unit

- 18:00 ET 이후 raw same-date daily row는 계속 pending이다.
- explicit finalized row는 수집 시각과 무관하게 FINAL이다.
- normalized model row는 raw close가 아니라 `final_close`를 사용한다.
- exact ET window가 다음 세션 18:00 이후 bar를 제외한다.
- EDT와 EST 날짜에서 window가 각각 올바른 UTC instant로 변환된다.
- missing symbol이 하나라도 있으면 aggregate write가 0건이다.
- 17/17 aggregate write는 transaction 단위로 commit된다.
- 일반 daily UPSERT가 기존 final columns를 덮어쓰지 않는다.
- legacy schema projection fallback이 기존 daily row를 읽는다.

### Integration

- `07:02 KST / 18:02 ET` refresh 시나리오에서 7/23이 같은 클릭 안에
  `latest_final_session`과 snapshot `as_of_date`가 된다.
- 다음 세션 18:00 ET 이후 5m 가격을 크게 바꿔도 7/23 final aggregate와
  input fingerprint가 변하지 않는다.
- finalization 16/17이면 snapshot이 7/22 latest-good을 유지한다.
- 13:00 KST 이후 raw prior-date final path는 추가 5m 수집 없이 동작한다.
- unchanged finalized input은 nested materialization fast path를 유지한다.

### Browser QA

- actual `일봉 갱신` 후 command detail과 hero 기준일이 같은 새 날짜다.
- 성공 후 pending banner가 사라진다.
- 실패 fixture에서는 latest-good 날짜와 pending 안내가 유지된다.
- desktop과 420px layout, console warning/error, horizontal overflow를
  재확인한다.

## Tradeoffs

- pending refresh에 약 4초 수준의 provider 요청과 5m aggregate 비용이
  추가될 수 있다. 대신 기존 40~50초 nested rebuild 문제를 다시 만들지
  않도록 2d/5m로 제한하고 unchanged-input fast path를 유지한다.
- `futures_ohlcv`가 raw와 canonical final fields를 함께 갖게 되지만,
  duplicate source row와 downstream join drift를 피할 수 있다.
- reconstructed close는 Yahoo 5m 기준의 completed session close이며
  거래소 공식 settlement price라고 주장하지 않는다.

## Scope Review

- Placeholder: 없음
- Ambiguity: “오전 7시 이후”는 current July EDT뿐 아니라
  `ZoneInfo("America/New_York")`의 `17:15 ET 이후`로 정의한다.
- Scope: Futures Macro manual daily refresh와 completed-session input에 한정한다.
- Compatibility: React payload, family 산식, forecast history, registry, saved
  setup은 변경하지 않는다.
- Data integrity: next-session exclusion, all-or-nothing coverage, transactional
  final write, latest-good fallback을 명시했다.
