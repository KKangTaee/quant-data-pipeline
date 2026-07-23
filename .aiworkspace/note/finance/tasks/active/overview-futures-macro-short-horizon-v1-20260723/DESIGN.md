# Overview Futures Macro Short-Horizon V1 Design

Status: User-approved visual direction; written spec review pending
Last Updated: 2026-07-23

## Approved Product Direction

사용자는 다음 구조를 승인했다.

1. 최근 1거래일 `새 충격`
2. 최근 5거래일 `단기 방향`
3. 향후 5거래일 `검증 결론`
4. 핵심 방향 정렬 4개
5. 확인 신호 2개
6. 다음 일봉에서 판단이 바뀌는 조건

관측창은 `최근 1 · 5 · 20거래일`로 통일한다. 최근 20거래일은 배경 흐름이며 primary future horizon이 아니다. 향후 20D 카드, 2D 상태지도, 검증되지 않은 확률·경로는 기본 화면에서 제거한다.

## Current Diagnosis

### Refresh latency

현재 `일봉 갱신`은 다음 순서로 동작한다.

```text
click
  -> 17 core futures × 10y/1d provider download
  -> full OHLCV normalize + UPSERT
  -> current macro rebuild
  -> full 5D/20D nested historical validation
  -> compact snapshot materialization
  -> rerun + DB-only render
```

10년 actual refresh는 약 42,500 rows를 다시 내려받아 UPSERT하며, 전망 계산도 전체 chronological history를 다시 평가한다. Overview first entry는 stored snapshot read라 빠르지만 명시적 refresh는 collection과 materialization 두 비용을 모두 지불한다. 40~50초는 UI 렌더링보다 이 두 단계가 원인이다.

### Data and presentation mismatch

- 현재 수집 preset: 17개 futures
- six-family score 직접 입력: 15개 futures
- 계산 family: risk-on, growth, rate pressure, dollar pressure, safe haven, inflation pressure
- 기존 active asset pathways: 5개이며 growth가 빠져 있다.
- 승인 전 4행 mockup은 safe haven까지 숨겨 실제 conflict 설명이 불완전했다.

`family 6/6`은 6개 행이 보인다는 뜻이 아니라 6개 family 모두 1D/5D/20D 계산 가능하다는 coverage다.

## Primary UX Contract

### Hero

Hero는 stored payload에서 동적으로 조립한다. mockup의 특정 날짜와 숫자를 hardcode하지 않는다.

- kicker: `단기 방향 진단`
- title: 현재 core alignment와 confirmation conflict를 한 문장으로 요약
- summary: 최근 5거래일 핵심 방향, confirmation 결과, 향후 5거래일 gate를 연결
- observation windows: `최근 1 · 5 · 20거래일`
- role labels: `새 충격 · 단기 방향 · 배경 흐름`

현재 actual처럼 주가지수 약화와 safe haven 약화가 동시에 나타나면 `전형적 방어 정렬은 아님`을 명시한다. 단순히 주식이 약하다는 이유만으로 `방어 압력 우세`를 출력하지 않는다.

### Three-step reading flow

1. `최근 1거래일 · 새 충격`
   - latest completed daily family values만 사용한다.
2. `최근 5거래일 · 단기 방향`
   - 핵심 4개 정렬과 material threshold를 요약한다.
3. `향후 5거래일 · 검증 결론`
   - future probability publication status를 사용자 언어로 번역한다.

내부 publication status는 보존하고 사용자 문구만 다음처럼 바꾼다.

| Internal | Primary copy | Supporting copy |
|---|---|---|
| `VERIFIED` | 검증된 5거래일 방향 우위 | 평소 결과 빈도보다 시간순 검증 성능이 높음 |
| `NO_EDGE` | 방향 예측 근거 부족 | 유사 국면 모델이 평소 5거래일 결과 빈도보다 정확하지 않음 |
| `PROVISIONAL` | 검증 중 · 방향 확정 보류 | 계산은 가능하지만 공개 검증 기준을 모두 충족하지 못함 |
| `UNAVAILABLE` | 검증 자료 부족 | 독립 표본 또는 시간순 평가가 부족함 |

`NO_EDGE`는 현재 관측 실패, 모델 실행 오류, 반대 방향 신호가 아니다. 관측된 5D 방향을 미래 5D로 연장할 추가 정확도가 없다는 뜻이다.

## Family Hierarchy

### Core directions

Primary matrix는 체제의 중심축 4개를 1/5/20거래일 열로 보여준다.

1. 주가지수 위험선호 (`risk_on`)
2. 채권·금리 압력 (`rate_pressure`)
3. 달러 압력 (`dollar_pressure`)
4. 원자재·물가 압력 (`inflation_pressure`)

### Confirmation signals

두 confirmation은 core와 동등한 체제축처럼 보이지 않도록 별도 영역에 둔다.

1. 경기민감 성장 (`growth`)
   - 장기 성장 배경과 단기 core pressure의 일치·불일치를 설명한다.
2. 안전자산 선호 (`safe_haven`)
   - risk-off를 확인하거나 전형적 방어 정렬을 반박하는 신호다.

각 confirmation card도 최근 1/5/20거래일 상태를 유지하며, 한 문장 해석은 family 값과 threshold에서 deterministic하게 생성한다.

## Calculation Scope Disclosure

첫 화면의 판단 흐름을 방해하지 않는 secondary block으로 둔다.

```text
17개 선물 수집 · 15개 family 산식 반영 · family 6/6
달러인덱스는 경제 사이클 공유 · 은은 원본 관찰 전용
```

숫자는 하드코딩하지 않는다.

- collected count: selected/core futures와 latest coverage에서 계산
- direct family input count: `SCORE_DEFINITIONS` member union에서 계산
- family coverage: current pattern coverage에서 계산
- symbol role: explicit product mapping을 사용

이번 작업은 산식 변경 없이 역할만 투명하게 공개한다.

| Role | Symbols | Behavior |
|---|---|---|
| direct family input | `SCORE_DEFINITIONS`의 15개 union | current family와 pattern feature 계산에 사용 |
| shared context | `DX-Y.NYB` | Futures Macro family에는 넣지 않고 Economic Cycle stored price로 유지 |
| raw observation | `SI=F` | raw trace/monitoring에는 유지하고 family 산식에는 넣지 않음 |

DXY와 은을 family에 추가하면 historical feature와 OOS gate가 바뀌므로 별도 model revision 없이는 추가하지 않는다.

## Payload Boundary

Python이 계산과 사용자 의미를 소유하고 React는 표시와 action event만 소유한다.

권장 payload shape:

```text
short_horizon_decision
  observation_windows
  current_summary
  one_day_shock
  five_day_direction
  future_five_day_validation
  core_directions[4]
  confirmation_signals[2]
  change_conditions
  calculation_scope
```

React가 raw z-score를 재분류하거나 market conclusion을 추론하지 않는다. Python adapter가 기존 stored `pattern`, `pattern_outlook`, `coverage`, `SCORE_DEFINITIONS`를 위 payload로 변환한다.

## Default Render Changes

Default active render에서 제거한다.

- future 20D horizon card
- `PatternMapSection` 2D observed/conditional path
- conditional terminal regions and direction vector visualization
- repeated asset-level future 5D/20D status rows

60D regime ribbon은 삭제하지 않는다. above-the-fold 판단 흐름에서는 제외하되 하단 `최근 체제 이력` secondary section 또는 disclosure로 유지한다. 관련 backend calculation, stored snapshot fields, immutable forecast history도 삭제하지 않는다.

## Refresh Performance Design

### Bootstrap versus routine refresh

`10y/1d`는 bootstrap 또는 explicit repair에만 사용한다. routine `최신 일봉 반영`은 17개 core symbols에 bounded `1y/1d` overlap을 요청한다.

1년 overlap은 신규 완료 일봉뿐 아니라 최근 roll/adjustment correction을 다시 UPSERT할 여지를 남기면서 rows를 약 10분의 1로 줄인다. 기존 DB의 더 오래된 rows는 삭제하거나 재작성하지 않는다.

10년 backfill이 필요한 경우:

- symbol daily rows가 전혀 없음
- pattern minimum history를 충족하지 못함
- explicit repair/bootstrap entry point가 호출됨

부분 이력 symbol만 10년 backfill하고, 나머지 symbols는 routine overlap을 사용한다. UI primary action은 routine refresh이며 full repair 운영 action을 새 primary panel로 추가하지 않는다.

### Unchanged-input fast path

routine refresh 전후에 model input에 필요한 bounded daily rows의 canonical fingerprint를 계산한다.

- fingerprint unchanged: compatible stored snapshot을 재사용하고 full pattern outlook 계산을 건너뛴다.
- fingerprint changed: stored full history를 읽어 current pattern과 5D/20D backend outlook을 materialize한다.
- incompatible algorithm/schema: fingerprint와 무관하게 rebuild한다.

fingerprint는 row order, collection timestamp, run id가 아니라 provider symbol, completed session time, OHLCV 값으로 계산한다. incomplete daily session은 기존 resolver를 그대로 사용한다.

### Stage timing

backend job result와 test evidence에는 다음 duration을 남긴다.

- collection duration
- normalize/UPSERT duration
- input comparison duration
- materialization duration

이 timing은 성능 검증과 run log에 사용하며 첫 사용자 화면에 운영 진단 패널로 추가하지 않는다.

## Data Integrity And Error Handling

- routine partial provider failure는 성공한 symbols만 UPSERT하고 기존 실패 symbol rows를 삭제하지 않는다.
- 6개 family 중 4개 미만이 current completed session을 만들 수 없으면 latest-good snapshot을 유지한다.
- DXY는 Economic Cycle 공유 source이므로 global preset에서 임의 제거하지 않는다.
- raw-only 은을 family에 억지로 편입하거나, 성능만을 위해 dependency 확인 없이 삭제하지 않는다.
- point-in-time feature, completed-session resolver, purged chronological validation, immutable forecast history를 보존한다.
- `NO_EDGE` probability/coordinate/vector suppression 계약을 유지한다.

## File Ownership

Primary implementation candidates:

- `app/web/overview/futures_macro_helpers.py`
  - short-horizon payload adapter, status copy, calculation scope, action dispatch
- `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
  - approved reading order
- new or revised React section files for decision flow and core/confirmation matrix
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`
  - desktop/mobile hierarchy
- `app/jobs/overview_actions.py`
  - routine daily refresh request contract
- `app/jobs/ingestion_jobs.py`
  - stage result and conditional materialization handoff
- `finance/data/futures_market.py`
  - per-symbol bootstrap/routine period routing and input timing
- `app/services/futures_macro_snapshot.py`
  - pre-materialization compatible/fingerprint fast path
- existing Futures Macro and service contract tests
- canonical `component_static/` production bundle

No provider or DB access moves into React/Streamlit render code.

## Testing Contract

### Python

- 4 core + 2 confirmation ordering and labels
- 1/5/20 observation versus future 5 distinction
- `VERIFIED/NO_EDGE/PROVISIONAL/UNAVAILABLE` copy and suppression
- 17 collected / 15 direct / 6 family scope derivation
- DXY shared and silver raw-only role
- routine refresh requests bounded overlap rather than 10y for complete symbols
- deficient symbol gets full bootstrap without forcing all symbols to 10y
- unchanged input skips outlook builder
- changed input and incompatible version rebuild
- partial failure preserves latest-good data/snapshot

### React

- hero and three-step flow render from payload
- core 4 and confirmation 2 semantics/order
- calculation scope remains secondary
- refresh action event remains idempotent
- future 20D와 2D map은 default render에서 빠지고 60D ribbon은 secondary history로 유지
- keyboard/focus and narrow layout

### Browser QA

- actual stored snapshot at desktop and 420px
- no horizontal overflow or clipped family labels
- core and confirmation hierarchy is visually distinct
- refresh/reload action state remains usable
- no console errors
- QA screenshot 1장, generated artifact로 보존하고 명시 요청 없이는 커밋하지 않음

### Performance verification

- before/after provider requested periods and returned rows
- unchanged refresh total duration and skipped materialization evidence
- changed-session refresh collection/materialization breakdown
- no claim of a fixed latency target until local actual measurements are recorded

## Tradeoffs

- 4+2 layout is slightly taller than four equal rows, but it preserves why a core direction is confirmed or contradicted.
- 1-year overlap downloads more than a minimal 5~20-day delta, but better absorbs provider correction and roll-adjustment changes while still sharply reducing the current 10-year transfer.
- backend 20D outlook remains calculated for compatibility even though it is hidden from the primary UI. Removing it is a separate model/storage change.
- unchanged-input fingerprint adds a DB read/hash step, but this is bounded and substantially cheaper than full nested validation.

## Approval Record

- User selected short-horizon direction B: primary focus on recent 1D/5D and future 5D validation.
- User selected B3 factor matrix mixed with B1 decision flow.
- User approved `최근 1 · 5 · 20거래일` wording and removal of the redundant 20D future-warning copy.
- User approved `방향 예측 근거 부족` for `NO_EDGE`.
- User approved final `핵심 4 + 확인 2` visual direction in the visual companion.
