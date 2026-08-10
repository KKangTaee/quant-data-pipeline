# Overview Futures Macro Intraday Nowcast V1 Design

Status: Written specification awaiting user review
Last Updated: 2026-08-11

## 승인된 제품 방향

사용자는 권장안 2를 승인했다.

- 거래 중인 선물은 최신 저장 intraday data로 현재 상태를 파악한다.
- 최근 1D / 5D / 20D는 모두 같은 장중 기준 시각으로 잠정 재계산한다.
- 미래 5D 검증과 과거 성능 평가는 마지막 완료 일봉만 사용한다.
- 비거래일에는 마지막 완료 일봉을 현재 기준으로 사용한다.

이 설계의 핵심은 `현재성`과 `검증 무결성` 중 하나를 포기하는 것이 아니라 두 read
model을 명시적으로 분리하는 것이다.

## 문제 정의

현재 화면은 pending daily session을 current pattern과 outlook에서 모두 제외한다.
이는 mutable Yahoo daily bar가 immutable history에 들어가는 것을 막지만 다음 사용자
문제를 만든다.

1. 거래 중 `일봉 갱신`을 눌러도 기준일이 전일에 머물러 갱신 실패처럼 보인다.
2. 화면의 `오늘의 재가격화`와 `단기 방향 진단`이라는 제품 약속이 장중 현실을 반영하지
   못한다.
3. 상단 observation rail은 1D / 5D / 20D인데 판단 카드는 1D / 5D / 미래 5D라서
   20D 배경과 미래 검증이 같은 흐름 안에서 뒤섞인다.
4. `방향 예측 근거 부족`은 충분한 표본에서 baseline을 이기지 못한 `NO_EDGE`도
   자료 누락처럼 들리게 한다.

## 제품 의미

### 장중 잠정 관측

사용자가 거래 중 `최신 데이터 갱신`을 실행하면 화면의 primary current state는 마지막
완료 일봉이 아니라 latest eligible stored 5m bar 기준 잠정 상태다.

- `1D 새 변화`: 현재 session-to-date 변화를 60일 변동성으로 표준화한 family 충격
- `5D 현재 방향`: 직전 4개 완료 거래일과 현재 잠정 session을 합친 단기 방향
- `20D 기존 배경`: 직전 19개 완료 거래일과 현재 잠정 session을 합친 배경 흐름

세 구간은 동일한 intraday cutoff를 사용한다. 서로 다른 symbol의 최신 시각을 섞지
않으며 필수 입력 중 가장 덜 따라온 symbol의 latest 완료 5분봉 시각을 common cutoff로
사용한다.

### 완료 관측

비거래 시간에는 마지막 완료 일봉 상태가 primary current state다. 거래 중에도 다음
secondary evidence를 항상 보존한다.

- 마지막 완료 기준일
- 완료 상태의 체제/전환 요약
- 장중 잠정 상태가 완료 상태에서 어떻게 달라졌는지

장중 source가 부적격하면 잠정값을 만들지 않고 완료 관측을 primary로 되돌린다.

### 미래 5D 검증

현재 `futures_macro_snapshot`과 immutable forecast history가 가진 완료 일봉 기준 5D
publication status를 그대로 사용한다. 장중 synthetic row는 다음 입력에 들어가지 않는다.

- analog episode selection
- current forecast probability / terminal coordinate / vector
- chronological evaluation
- Brier / log loss / calibration / bootstrap gate
- `futures_macro_forecast_history`

`NO_EDGE`의 primary copy는 `기본 빈도 대비 예측력 확인 안 됨`으로 바꾸고 다음 세 사실을
구분한다.

- 표본: 충분 또는 부족
- 성능: baseline 대비 우위 있음 또는 없음
- 사용 원칙: 현재 관측을 미래 방향으로 연장함 또는 연장하지 않음

## 데이터 흐름

```text
사용자 `최신 데이터 갱신`
  -> 기존 1Y/1D overlap refresh
  -> latest daily session resolver
  -> pending session 없음
       -> last completed snapshot 사용
  -> pending session 있음
       -> core 17 symbols bounded 2d/5m 한 번 수집
       -> finance_price.futures_ohlcv 저장
       -> session window 안의 closed 5m bars만 DB에서 read
       -> direct family input의 common cutoff / freshness / coverage 확인
       -> 장중 session-to-date OHLCV aggregate
       -> completed daily history + synthetic pending row
       -> provisional thermometer / pattern 1D·5D·20D 계산
  -> settlement-stable cutoff 이후
       -> 같은 stored 5m evidence로 기존 17/17 atomic finalization
       -> completed snapshot / immutable history materialize
  -> Python payload
       -> React는 잠정/확정/검증을 표시만 함
```

UI는 provider를 직접 호출하지 않는다. 사용자가 명시적으로 갱신한 뒤 collector가 DB에
저장하고 service가 DB row를 읽는 기존 `Ingestion -> DB -> Service -> UI` 경계를 유지한다.

## 장중 입력 적격성

### Session window

기존 `futures_session_window_utc(session_date)`의 DST-safe session start/end를 재사용한다.
현재 시각이 end 이전이면 end 대신 latest closed 5m common cutoff까지만 집계한다.
session date는 latest daily row의 기존 resolver 결과를 사용하므로 Sunday evening의
Monday trade date도 유지한다.

### Closed 5m bar

현재 형성 중인 5분봉은 제외한다. provider bar timestamp와 평가 시각을 기준으로 완전히
끝난 5분 구간만 eligible하게 만든다. 장중 화면은 tick realtime이 아니라 latest completed
5m observation이다.

### Common cutoff

먼저 `SCORE_DEFINITIONS` member가 모두 latest eligible bar를 가진 family를 찾는다. 적격
family member 합집합에서 가장 이른 latest timestamp를 common cutoff로 선택하고, 해당
family의 모든 symbol aggregate를 그 시각까지만 계산한다. 이후 bar가 더 있는 symbol도
잘라서 같은 시각의 시장 상태를 비교한다. 이 순서로 4~5개 family만 가능한 partial 상태도
missing member를 0 또는 전일값으로 채우지 않고 같은 시각 기준을 유지한다.

### Coverage

- 한 family는 `SCORE_DEFINITIONS`의 모든 member가 current session aggregate를 가질 때만
  잠정 score를 계산한다. missing member를 0 또는 전일값으로 채우지 않는다.
- 6개 family 모두 계산 가능하면 `INTRADAY_READY`다.
- 4~5개 family만 가능하면 `INTRADAY_PARTIAL`로 표시하고 누락 family를 숨기지 않는다.
- 4개 미만이면 전체 장중 체제 headline을 만들지 않고 마지막 완료 관측으로 fallback한다.
- DXY shared context와 silver raw-only 역할은 기존대로 유지하며 family 입력으로 승격하지
  않는다.

### Freshness

common cutoff가 평가 시각보다 30분 넘게 오래되면 장중 상태는 stale이다. stale 값을
현재처럼 표시하지 않고 마지막 완료 관측으로 fallback하며 마지막 intraday 기준 시각과
지연 사유를 짧게 보여준다. 30분은 free provider의 지연 가능성을 허용하면서 거래 중
오래된 상태를 current로 오인하지 않게 하는 제품 threshold다.

## 계산 경계

기존 수식을 재사용한다.

1. 완료 일봉 close matrix를 불러온다.
2. pending session별 5m aggregate close를 synthetic daily close로 추가한다.
3. `build_pattern_feature_frame()`으로 1D / 5D / 20D family z-score를 계산한다.
4. `build_current_pattern_snapshot()`으로 provisional regime / transition / family matrix를
   계산한다.

별도 장중 threshold나 family weight를 만들지 않는다. 다만 산출물에는 다음 provenance를
반드시 붙인다.

- `observation_mode`: `INTRADAY_PROVISIONAL | COMPLETED`
- `observed_at_utc`
- `observed_at_et`
- `session_date`
- `completed_as_of_date`
- `freshness_minutes`
- `available_family_count / required_family_count`
- `fallback_reason`

이 provenance는 compact product evidence이며 실행 job/row 진단 패널이 아니다.

## 저장 정책

장중 synthetic row와 provisional pattern은 다음 위치에 저장하지 않는다.

- `finance_meta.futures_macro_snapshot`
- `finance_meta.futures_macro_forecast_history`
- workflow registry JSONL
- saved portfolio JSONL

원천 5m row만 기존 `finance_price.futures_ohlcv`에 idempotent UPSERT한다. provisional read
model은 명시 갱신 직후 또는 저장 row 다시 읽기에서 재구성할 수 있다. 완료 cutoff와 17/17
atomic finalization을 통과한 뒤에만 기존 completed snapshot/history가 전진한다.

## Job orchestration

`app/jobs/overview_actions.py`가 수동 action을 소유한다.

1. 기존 routine daily overlap과 deficient-symbol bootstrap을 실행한다.
2. latest session state를 확인한다.
3. pending session이 있으면 bounded `2d/5m`을 한 번 실행한다.
4. settlement-stable cutoff 전이면 stored rows를 장중 nowcast가 읽도록 남긴다.
5. cutoff 이후면 같은 stored rows로 기존 finalization을 시도해 중복 provider 호출을 막는다.
6. 완료 snapshot materialization은 기존 fingerprint/compatibility 경계를 유지한다.

상세 collection timing과 failure는 backend job result에 남길 수 있지만 기본 Futures Macro
화면에 운영 진단 패널을 추가하지 않는다.

## 서비스와 파일 소유권

### 신규 focused service

`app/services/futures_macro_intraday.py`

- pending session resolution 결과를 입력으로 받는다.
- stored 5m rows의 eligible closed bar와 common cutoff를 고른다.
- session-to-date synthetic rows를 만든다.
- 완료 이력에 synthetic row를 결합해 provisional macro/pattern을 계산한다.
- Streamlit과 provider 호출을 포함하지 않는다.

### 기존 파일

- `app/jobs/overview_actions.py`
  - manual refresh의 one-time 5m collection과 finalization reuse orchestration
- `app/jobs/futures_macro_daily_finalization.py`
  - pre-collected 5m evidence를 재사용할 수 있는 narrow handoff
- `finance/data/futures_session_finalization.py`
  - stored session-window 5m reader와 aggregate primitive 재사용 또는 focused 확장
- `app/web/overview/futures_macro_helpers.py`
  - completed snapshot과 provisional observation을 결합한 payload, copy, action result clear
- `app/web/streamlit_components/futures_macro_workbench/src/`
  - 장중/확정 provenance와 observation/forecast 분리 표시
- focused Python/React contract tests와 production `component_static/` bundle

DB schema는 바꾸지 않는다.

## 화면 설계

### Header

- action label: `최신 데이터 갱신`
- 장중 primary fact: `관측 상태 · 장중 잠정`
- 기준 시각: `최근 완료 5분봉 · YYYY-MM-DD HH:mm ET`
- secondary fact: `마지막 확정 · YYYY-MM-DD`
- 비거래일: `관측 상태 · 확정`, `기준일 · YYYY-MM-DD`
- stale/partial fallback: 완료 상태를 primary로 보여주고 장중 자료 제한을 notice로 표시

### 현재 관측

기존 observation rail과 decision cards를 하나의 일관된 3단계로 합친다.

1. `1D · 지금 새로 생긴 변화`
2. `5D · 현재 단기 방향`
3. `20D · 기존 배경과의 관계`

각 카드에는 관측인지 예측인지 반복해서 쓰지 않고 section 제목과 상태 badge로 한 번만
구분한다. 20D는 5D와 같은 방향이면 `기존 흐름 지속`, 반대면 `단기 전환 시도`, 모두
threshold 안이면 `방향 확정 전`처럼 사용자 판단 문장으로 번역한다.

### Family matrix

generic `강화 / 약화`만 표시하지 않는다. family 의미에 맞춘 compact wording을 사용한다.

- 위험선호: `위험선호 강화 / 약화`
- 금리 압력: `금리 부담 확대 / 완화`
- 달러 압력: `달러 압력 확대 / 완화`
- 원자재·물가: `물가 압력 확대 / 완화`
- 경기민감 성장: `성장 기대 강화 / 약화`
- 안전자산: `방어 수요 강화 / 약화`

### 미래 검증

현재 관측 section과 분리된 gate로 둔다.

- 질문: `현재 흐름을 향후 5거래일로 연장할 수 있는가?`
- 기준: `마지막 완료 일봉 YYYY-MM-DD`
- `NO_EDGE`: `기본 빈도 대비 예측력 확인 안 됨`
- detail: `표본은 충분하지만 단순 기준보다 정확하지 않아 현재 흐름을 미래 방향으로
  연장하지 않습니다.`
- compact evidence: 독립 표본, evaluation count, model/baseline Brier의 rounded comparison

확률, 좌표, vector suppression은 기존 publication status 계약을 유지한다.

## 오류와 fallback

| 상황 | 사용자 결과 | 저장/검증 결과 |
|---|---|---|
| 비거래일, pending session 없음 | 최신 완료 관측 | 변경 없음 |
| 장중 5m 6/6 family ready, fresh | 장중 잠정 관측 | raw 5m만 저장 |
| 장중 4~5 family ready, fresh | 장중 잠정·부분 관측 | raw 5m만 저장 |
| 장중 family 4개 미만 | 마지막 완료 관측 + 장중 자료 부족 | completed snapshot 유지 |
| common cutoff 30분 초과 | 마지막 완료 관측 + 최신 자료 지연 | completed snapshot 유지 |
| 5m provider collection 실패 | 마지막 완료 관측 + 갱신 제한 | 기존 5m/1d 삭제 없음 |
| cutoff 이후 17/17 finalization 성공 | 완료 관측으로 승격 | snapshot/history 전진 |
| cutoff 이후 finalization 실패 | 장 마감 후 확정 대기 + 잠정 evidence | latest-good completed 유지 |

장중 실패는 완료 snapshot을 `partial`로 덮지 않는다. 성공한 raw rows도 기존 row를
삭제하지 않으며 stable unique key UPSERT를 유지한다.

## 테스트 계약

### Python service

- 현재 형성 중인 5분봉 제외
- 적격 full-member family 합집합의 common cutoff 선택
- DST 전후 exact session window
- Sunday evening의 Monday trade date
- completed daily history + synthetic current row의 1D/5D/20D 계산
- family member missing 시 해당 family fail-closed
- 6/6 ready, 4~5 partial, 4 미만 fallback
- 30분 freshness boundary
- provisional row가 completed fingerprint/history에 들어가지 않음

### Job

- active pending session에서 `2d/5m` 한 번만 수집
- 비거래일은 intraday 수집 생략
- cutoff 전 nowcast-only
- cutoff 이후 pre-collected rows로 17/17 finalization
- partial provider failure가 latest-good snapshot을 보존

### Payload / React

- header의 장중 잠정 시각과 마지막 확정일
- 1D / 5D / 20D current observation 순서
- future 5D gate의 별도 completed 기준
- family semantic wording
- `NO_EDGE` 표본 충분/성능 부족/사용 원칙 분리
- stale/partial/fallback copy
- desktop/mobile keyboard와 overflow

### Verification

- focused pytest와 py_compile
- React unit/contract test와 Vite production build
- `git diff --check`
- 실제 stored data desktop 및 420px Browser QA
- 콘솔 warning/error와 horizontal overflow 확인
- 최종 응답에 QA screenshot 1장 첨부, generated artifact는 커밋하지 않음

## Tradeoffs

- 5분봉 nowcast는 tick realtime보다 늦지만 free provider와 기존 DB 경계에서 안정적으로
  현재성을 높인다.
- common cutoff는 가장 빠른 symbol의 최신값을 일부 버리지만 cross-asset 비교 시각을
  일치시킨다.
- 30분 freshness gate는 일시적인 provider delay를 허용하지만 그 이상 오래된 값이 현재처럼
  보이는 것을 막는다.
- 장중 상태와 미래 검증의 기준일이 다를 수 있으므로 화면 높이가 조금 늘어나지만, 현재
  관측과 검증된 예측을 혼동하지 않는 편이 더 중요하다.
- provisional read model을 별도 snapshot으로 저장하지 않아 첫 계산 비용이 생기지만 2일치
  5분봉과 기존 일봉 feature 계산 범위이며 immutable forecast 오염을 피한다.

## 승인 기록

- 2026-08-11: 사용자는 거래 중인 선물은 최신 수집 데이터로 파악해야 한다고 제품 의미를
  정정했다.
- 2026-08-11: 사용자는 `1D / 5D / 20D를 모두 장중 잠정값으로 재계산하고 미래 검증만
  완료 일봉 기준으로 분리`하는 권장안 2를 승인했다.
