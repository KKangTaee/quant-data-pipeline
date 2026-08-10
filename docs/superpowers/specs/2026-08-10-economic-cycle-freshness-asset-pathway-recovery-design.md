# Economic Cycle Freshness and Asset Pathway Recovery Design

Status: User-selected; pending written-spec review
Date: 2026-08-10
Owner: Overview / Economic Cycle

## 이걸 하는 이유

경제사이클의 `Data Freshness` 수동 갱신은 최근 실제 실행에서 각각 96.836초와
75.616초가 걸렸다. 화면 조회가 느린 것이 아니라 17개 FRED/ALFRED series의 vintage
date와 observation을 series별로 순차 호출한 뒤 snapshot을 재계산하는 동기식 action이
원인이다. 현재 UI 문구도 1분 안팎을 정상 범위로 설명하지만, 사용자가 버튼을 누른 뒤
기다리는 상호작용으로는 지나치게 길다.

`자산별 확인 포인트`는 이 vintage pipeline과 다른 저장 경로를 사용한다. 2026-08-10
실제 DB를 확인한 결과 경제사이클 snapshot은 당일 기준으로 최신이지만 자산 경로의
DGS2, DGS10, DFII10, T10YIE, VIXCLS, BAA10Y와 일부 futures series는 5영업일 허용
범위를 넘었다. 이 때문에 충분한 과거 관측치가 저장되어 있어도 evaluator가
`STALE_SERIES`를 `자료 부족`과 동일하게 취급하고, 미국채 수익률·실질금리·금리차 등의
현재 값과 1개월·3개월 변화까지 모두 숨긴다.

사용자가 원하는 결과는 오래된 값을 최신값처럼 사용하는 것이 아니다. 원천 데이터를
지속적으로 최신화하고, 일시적인 수집 지연 때는 마지막 저장 측정치를 날짜와 함께
보여주되 현재 경기 판단의 유효 근거로는 사용하지 않는 것이다.

## 사용자 선택

검토한 대안은 다음과 같다.

1. 신선도 허용 기간만 늘린다.
   - 구현은 작지만 오래된 데이터를 최신 측정처럼 오해할 수 있어 제외한다.
2. 자산 데이터 수집만 수동 버튼에 추가한다.
   - 당장의 누락은 복구하지만 기존 75~97초 지연에 작업이 더해지고, provider 실패 시
     카드가 다시 모두 사라지는 문제가 남아 제외한다.
3. 수집 성능, 자산 데이터 자동 갱신, stale 표시 계약을 함께 개선한다.
   - 사용자가 3안을 선택했으며 이 문서는 해당 범위를 고정한다.

## 목표

- 경제사이클 vintage 수집의 네트워크 대기 시간을 제한된 병렬 처리로 줄인다.
- 기존 Overview automation에 자산 경로 전용 일일 갱신 job을 추가한다.
- 수동 Data Freshness action은 DB 상태를 먼저 확인하고 stale인 scope만 갱신한다.
- 저장 이력은 충분하지만 최근 관측이 지연된 경우 측정값과 기준일을 계속 표시한다.
- stale 측정값은 현재 신호, 방향 판단, transition support에는 사용하지 않는다.
- provider 일부 실패 시 마지막 정상 측정치와 경제사이클 snapshot을 보존한다.
- `자산별 확인 포인트`의 카드 구조, 자산 순서와 시각 디자인은 유지한다.

## Non-goals

- freshness 기준을 무조건 완화해 오래된 자료를 `최신`으로 판정하지 않는다.
- React 또는 Streamlit render 경로에서 provider를 직접 호출하지 않는다.
- raw job, row count, provider response 중심의 운영 진단 패널을 추가하지 않는다.
- 경제사이클 4국면 계산식이나 transition state machine을 변경하지 않는다.
- 자산별 확인 포인트를 투자 추천 또는 자동 매매 신호로 바꾸지 않는다.
- 새 DB schema를 만들거나 기존 append-only registry를 재작성하지 않는다.
- 새로운 OS scheduler, launchd 또는 외부 orchestration system을 도입하지 않는다.

## 핵심 상태 계약

자산 측정의 `자료 존재 여부`와 `현재 판단 사용 가능 여부`를 분리한다.

| 상태 | 저장 이력 | 최신성 | 화면 측정값 | 현재 신호 사용 |
|---|---:|---:|---:|---:|
| `READY` | 충분 | 통과 | 표시 | 사용 |
| `DELAYED` | 충분 | 실패 | 마지막 값과 기준일 표시 | 사용하지 않음 |
| `INSUFFICIENT` | 부족 | 무관 | 계산 가능한 항목만 표시 | 사용하지 않음 |
| `ERROR` | 확인 실패 | 확인 실패 | last-good가 있으면 표시 | 사용하지 않음 |

기존 evaluator의 `STALE_SERIES`는 service adapter에서 `DELAYED`로 표현한다. 최근값,
1개월 변화와 3개월 변화를 계산할 충분한 저장 이력이 있으면 measurement payload를
보존한다. 다만 `supports_current_signal=false`를 명시하고 pathway direction 집계에서는
제외한다.

진짜 관측치 부족과 수집 지연을 더 이상 같은 `자료 부족` 문구로 합치지 않는다.

- `DELAYED`: `갱신 지연 · 마지막 확인 YYYY-MM-DD`
- `INSUFFICIENT`: `자료 부족`
- `ERROR`: `자료 확인 실패 · 마지막 정상값 유지`

daily FRED series는 기존 5영업일 기준을 유지한다. EIA weekly series는 주간 발표
주기를 반영한 별도 freshness 기준을 사용한다. S&P 500 actual EPS는 분기 자료이므로
일별 series와 같은 staleness 기준을 적용하지 않고 기존 완료 분기 계약을 유지한다.

## 수집 아키텍처

### 1. Economic-cycle vintage 수집 성능

현재 incremental collector는 17개 series를 차례대로 처리하며 각 series에서 vintage
date와 observation 요청을 다시 수행한다. 이를 다음 두 단계로 나눈다.

```text
latest stored realtime boundary 조회
  -> 최대 4 worker로 series별 provider page fetch
  -> series별 normalize 결과 수집
  -> 단일 DB connection에서 순차 UPSERT
  -> closed-month rollover
  -> intramonth snapshot materialization
```

provider fetch만 병렬화하고 DB write는 기존처럼 한 connection에서 순차 수행한다.
worker 수는 기본 4로 제한해 FRED rate limit과 로컬 자원 사용을 통제한다. 결과 순서는
catalog 순서로 다시 정렬하고, series별 실패·missing 판정과 last-good 보존 규칙은
유지한다.

collector에는 순수 fetch helper와 batch write 경계를 두어 thread 내부에서 공유 DB
connection을 사용하지 않게 한다. 테스트에서는 worker 수와 무관하게 동일한 normalized
rows, coverage, missing, failed 결과가 나와야 한다.

### 2. 자산 경로 일일 갱신

기존 ingestion job을 조합하는 `economic_cycle_asset_pathways` automation job을 추가한다.
새 collector를 UI에 만들지 않는다.

```text
FRED market context
  DGS2, DGS10, DFII10, T10YIE, VIXCLS, BAA10Y

EIA weekly petroleum
  WCESTUS1, WCRFPUS2, WRPUPUS2

daily market prices
  GC=F, DX-Y.NYB, CL=F, HG=F
  ^GSPC, SPY
```

- FRED와 EIA는 `run_collect_macro_market_context`를 재사용한다.
- futures는 필요한 네 symbol에 한정한 daily OHLCV refresh를 재사용한다.
- S&P 500은 기존 bounded SPX/SPY price refresh를 재사용한다.
- S&P 500 actual TTM EPS는 자동 추정하지 않으며 기존 공식 workbook 등록 경계를
  유지한다. 따라서 주식 카드의 가격 경로는 복구할 수 있지만 EPS는 실제 등록 자료가
  없으면 계속 명시적으로 제한된다.

이 job은 기존 Overview automation의 weekday daily cadence에 포함한다. 브라우저 render는
계속 DB-only이며, automation이 실행되지 않은 환경에서는 수동 action이 같은 bounded
job을 호출할 수 있다.

### 3. Scope-aware Data Freshness action

페이지 freshness read model은 최소한 두 scope를 구분한다.

```text
data_freshness
  cycle_snapshot
  asset_pathways
  overall_status
  refresh_required_scopes
```

버튼을 누르면 모든 source를 무조건 다시 받지 않는다.

1. 저장된 cycle snapshot 기준일과 asset pathway별 latest observation을 읽는다.
2. `refresh_required_scopes`만 실행 계획에 넣는다.
3. cycle scope가 stale이면 최적화된 vintage refresh와 materialization을 실행한다.
4. asset scope가 stale이면 bounded asset pathway refresh를 실행한다.
5. 두 scope를 DB에서 다시 읽어 postcondition을 확인한다.
6. 실제 최신성이 개선된 scope가 하나 이상일 때만 관련 cache를 비운다.

현재처럼 cycle snapshot이 이미 오늘 기준이고 asset만 stale이면 17-series vintage job은
다시 실행하지 않고 자산 자료만 갱신한다. 반대로 자산이 최신이면 기존 cycle refresh만
수행한다.

## 화면 동작

자산별 확인 포인트의 레이아웃, 카드 순서, 측정 항목과 펼침 구조는 유지한다. 변경은
status와 설명 문구에 한정한다.

- 최신 자료: 기존 측정값과 해석을 그대로 표시한다.
- 갱신 지연: 마지막 값, 1개월·3개월 변화와 마지막 관측일을 표시하고 카드 상단에
  `갱신 지연`을 표시한다.
- 진짜 자료 부족: 현재와 동일하게 `자료 부족`을 표시한다.
- 일부 경로만 최신: 최신 경로로만 현재 해석을 만들고 delayed 경로는 참고 측정으로
  분리한다.

Data Freshness 영역은 운영 상세 대신 다음만 보여준다.

- 전체 최신 여부
- 경제사이클 계산 기준일
- 자산 경로 마지막 확인일 또는 갱신 필요 개수
- `최신 데이터 반영` action
- 실행 중인 사용자 단계: `경기 지표 확인`, `자산 경로 확인`, `화면 다시 계산`

provider request 수, 저장 row 수와 stack trace는 run history에만 남긴다.

## 오류와 last-good 처리

- FRED/ALFRED 일부 실패: 새 cycle snapshot을 성공 처리하지 않고 기존 snapshot 유지
- 자산 source 일부 실패: 성공한 source만 UPSERT하고 실패 source의 마지막 저장값 유지
- stale history 존재: `DELAYED` 측정값 표시, 현재 신호에서는 제외
- history 자체 부족: `INSUFFICIENT` 유지
- postcondition 실패: cache를 비우지 않고 재시도 가능한 freshness 상태 유지
- 같은 날짜 재실행: 기존 business key UPSERT로 idempotent
- 중복 component event: 기존 nonce 소비 계약으로 한 번만 실행
- 자동 갱신 job 실패: 다음 automation cadence 또는 수동 action에서 재시도

## 변경 가능성이 있는 파일

- `finance/data/economic_cycle_vintages.py`
  - bounded concurrent fetch와 sequential write 경계
- `app/jobs/economic_cycle_refresh.py`
  - 최적화된 collector 결과와 실패 계약 유지
- `app/jobs/ingestion_jobs.py`
  - 자산 경로 bounded ingestion 조합 또는 기존 job 재사용 helper
- `app/jobs/overview_automation.py`
  - weekday asset-pathway daily job 등록
- `app/jobs/overview_actions.py`
  - scope-aware manual refresh와 postcondition
- `finance/economic_cycle_asset_pathways.py`
  - stale measurement 보존과 signal eligibility 분리
- `app/services/overview/economic_cycle.py`
  - cycle/asset freshness read model과 UI adapter
- `app/web/overview/market_context_helpers.py`
  - action 실행, cache invalidation과 단계 상태 연결
- `app/web/streamlit_components/economic_cycle_workbench/src/`
  - 기존 레이아웃을 유지한 freshness/status copy
- 관련 Python/React tests와 production component bundle

실제 구현 중 기존 helper로 충분한 파일은 수정하지 않는다. DB schema 변경은 없다.

## 테스트 전략

### Collector

- 여러 series fetch가 제한된 worker pool에서 실행된다.
- DB writer는 호출 thread에서 catalog 순서대로 실행된다.
- parallel과 serial fixture 결과가 동일하다.
- 한 series timeout이 다른 series 결과를 잃게 하지 않는다.
- retries, missing, failed와 coverage 집계가 유지된다.

### Refresh orchestration

- cycle만 stale이면 asset job을 실행하지 않는다.
- asset만 stale이면 17-series cycle job을 실행하지 않는다.
- 두 scope가 stale이면 둘 다 실행하고 각각 postcondition을 확인한다.
- 이미 최신이면 provider 호출 없이 success/no-op을 반환한다.
- partial failure는 성공 scope만 cache invalidation 대상으로 반환한다.
- automation profile에서 weekday daily asset job이 선택되고 cadence를 지킨다.

### Asset pathway contract

- fresh + sufficient history는 `READY`와 기존 측정값을 반환한다.
- stale + sufficient history는 `DELAYED`, 마지막 날짜와 측정값을 반환한다.
- `DELAYED` measurement는 방향 집계와 current support에서 제외된다.
- insufficient history는 여전히 `INSUFFICIENT`다.
- weekly EIA와 quarterly EPS freshness가 daily threshold로 오판되지 않는다.

### UI와 실제 QA

- 미국 2년·10년 국채 수익률, 10년-2년 금리차, 실질금리, 기대인플레이션이
  최신 갱신 후 실제 값과 1개월·3개월 변화로 표시된다.
- stale fixture에서는 값과 날짜가 보이지만 `갱신 지연`으로 명확히 구분된다.
- 자산별 확인 포인트의 기존 카드 레이아웃과 순서는 변하지 않는다.
- raw run/job 진단 패널이 추가되지 않는다.
- Python focused tests, React tests/typecheck/build와 production bundle rebuild가 통과한다.
- 실제 DB refresh 후 source별 최신 관측일과 last-good 불변성을 확인한다.
- 데스크톱과 좁은 화면 Browser QA를 수행하고 스크린샷 한 장을 생성하되 커밋하지 않는다.

## 성능 검증

현재 실제 기준선은 96.836초와 75.616초다. 같은 로컬 환경에서 다음을 별도로 측정한다.

- 17-series incremental provider fetch + write
- cycle materialization
- asset-only bounded refresh
- 이미 최신인 no-op action

provider가 정상 응답하는 실제 실행에서 17-series refresh가 두 기준선보다 모두 짧아야
한다. 목표는 45초 이내지만 외부 provider 응답 편차 때문에 시간을 하드코딩된 성공
조건으로 사용하지 않는다. 대신 요청 구조가 serial 17-series에서 최대 4-worker bounded
fetch로 바뀌었는지와 실제 개선 측정값을 함께 기록한다. 이미 최신인 scope는 provider
호출 없이 즉시 종료해야 한다.

## 구현 Roadmap

### 1차 — 수집 계약과 성능 개선

vintage fetch/write를 분리하고 제한된 병렬 수집을 적용한다. 기존 결과 동등성, 실패
격리와 DB 순차 write를 테스트한다. 완료 조건은 serial 네트워크 병목이 제거되고 기존
PIT/vintage 저장 계약이 유지되는 것이다.

### 2차 — 자산 데이터 복구와 표시 계약

자산 경로 bounded refresh, automation 등록, scope-aware action과 `DELAYED` 측정 표시를
구현한다. 완료 조건은 현재 DB의 stale 금리·실질금리·스프레드가 갱신되고, provider
지연 시에도 마지막 측정값이 날짜와 함께 보이는 것이다.

### 3차 — 실측, Browser QA와 문서 정렬

실제 provider/DB refresh를 실행해 성능과 최신 관측일을 확인하고, React production
bundle과 Browser QA를 완료한다. 완료 조건은 기존 UI 구조를 유지한 화면에서 자산
측정값이 복구되고, regression test와 durable documentation이 정렬되는 것이다.

## 중요한 Trade-off

- 제한된 병렬 fetch는 대기 시간을 줄이지만 provider rate limit 위험이 있어 worker를
  4개로 제한하고 기존 retry 정책을 유지한다.
- stale 측정값을 보여주면 정보는 보존되지만 현재 신호로 오해할 수 있다. 상태 배지,
  기준일과 signal 제외를 함께 적용한다.
- 자산 경로 자동 갱신은 데이터 신뢰도를 높이지만 Overview automation 실행 환경에
  의존한다. 수동 action을 동일 pipeline의 fallback으로 둔다.
- actual TTM EPS는 자동 추정하지 않으므로 다른 주식 경로가 복구되어도 공식 EPS가
  없으면 해당 항목의 제한은 남는다.

## 완료 기준

1. 17-series vintage fetch가 bounded concurrent network stage와 sequential DB write로
   동작한다.
2. cycle과 asset scope freshness가 분리되어 stale scope만 갱신한다.
3. DGS2, DGS10, DFII10, T10YIE, VIXCLS와 BAA10Y 최신 자료가 자산 카드에 반영된다.
4. gold, dollar, WTI, copper와 SPX/SPY bounded refresh가 같은 자산 경로를 지원한다.
5. stale history는 `갱신 지연`으로 값과 기준일을 표시하지만 현재 신호에는 사용하지
   않는다.
6. 기존 자산별 확인 포인트 UI 구조와 경제사이클 국면 계산은 유지된다.
7. last-good snapshot과 과거 월말 이력은 provider 실패에도 보존된다.
8. 실제 성능 개선값, source별 최신일, focused tests와 Browser QA 근거가 남는다.
