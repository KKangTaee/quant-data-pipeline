# Data Operations Task-Oriented IA V1 Design

Status: Ready For User Review
Last Updated: 2026-07-25

## 1. Design Decision

Data Operations는 Streamlit 기반 내부 운영 도구 성격을 유지하되,
제품 첫 화면은 non-technical workflow language를 사용한다.

선택한 방향은 `Task-oriented Hybrid`다.

- primary: consumer별 데이터 준비 workflow
- secondary: 공식 파일 가져오기, 문제 복구, 간소화된 실행 이력
- advanced: 저수준 collector와 inspection
- hidden from default: runtime/build, raw logs, failure CSV, full JSON, absolute artifact paths

이 설계는 기존 action을 삭제하지 않고 노출 위치와 진입 순서를 재정의한다.

## 2. Assumptions

### Primary User

주 사용자는 finance workflow를 직접 운영하는 프로젝트 사용자다.
코드·DB를 전혀 모르는 public consumer는 아니지만,
일상 작업을 위해 내부 job id와 table name을 외울 필요는 없어야 한다.

### Execution Policy

- 모든 write action은 사용자 explicit click으로 시작한다.
- V1에서 workflow step을 자동 연속 실행하지 않는다.
- 한 job이 실행 중일 때 다른 실행을 막는 현재 contract를 유지한다.
- partial success와 failed source/symbol은 숨기지 않는다.
- scheduler와 background queue는 4차 후보다.

### Data Correctness

- current snapshot과 historical PIT evidence를 같은 `준비 완료`로 합치지 않는다.
- Form 25 부재, current listing, SEC identity row를 survivorship PASS로 표현하지 않는다.
- FRED current observation과 ALFRED vintage를 구분한다.
- current ETF holdings / operability를 historical truth로 표현하지 않는다.

## 3. Target User Flow

```text
Data > Data Operations
  -> 데이터 준비
     -> 목적 선택
        -> Market Research
        -> Portfolio Lab
        -> Institutional Holdings
        -> Practical Validation
     -> 필요한 step 확인
     -> 한 step의 범위 / preflight 확인
     -> explicit 실행
     -> 결과와 다음 step 또는 consumer 이동

  -> 공식 파일
     -> S&P 500 실제 EPS
     -> BLS 일정 .ics

  -> 문제 복구
     -> 진단 선택
     -> bounded diagnosis
     -> 추천된 recovery action 열기

  -> 실행 이력
     -> Data Operations action만 normalized summary로 확인

  -> 고급 도구
     -> 전체 active low-level action catalog
     -> PIT / provider / lifecycle caveat 확인
```

## 4. Page Identity

### Header

- H1: `Data Operations`
- Description:
  `Research와 Portfolio workflow가 읽는 데이터를 준비하고, 필요한 경우 누락 범위를 복구합니다.`
- contextual Reference는 유지하되 collapsed 상태로 둔다.

### Remove Above The Main Action

- `Runtime / Build`
- “외부 API / 공식 파일...” blue info block
- static Step 1~4 workflow cards
- `작업 영역` 중복 heading/caption

첫 viewport 안에는 H1, 한 줄 설명, primary section selector,
네 개의 준비 목적 중 최소 일부가 보여야 한다.

## 5. Primary Section IA

section selector는 다음 5개다.

1. `데이터 준비`
2. `공식 파일`
3. `문제 복구`
4. `실행 이력`
5. `고급 도구`

desktop은 compact horizontal selector,
420px에서는 두 줄 이내 wrapping 또는 vertical-safe control을 사용한다.
selector가 viewport 폭을 넘기지 않아야 한다.

### Default: 데이터 준비

네 개의 consumer card를 먼저 보여준다.

| Card | User question | Primary data |
| --- | --- | --- |
| Market Research | 시장·종목 리서치 자료를 갱신하려는가? | listing, price, futures, sentiment, calendars |
| Portfolio Lab | backtest / factor 입력을 준비하려는가? | price, EDGAR statement, metadata |
| Institutional Holdings | 기관 13F 탐색 자료를 갱신하려는가? | SEC 13F dataset, identifier mapping |
| Practical Validation | ETF·macro·lifecycle 근거를 보강하려는가? | ETF provider, FRED, lifecycle evidence |

card는 raw run count, saved rows, failure count를 표시하지 않는다.
목적, 포함 데이터, 예상 빈도, `열기` action만 보여준다.

## 6. Workflow Detail Design

workflow를 선택하면 page 안에서 해당 workflow만 렌더한다.
모든 step을 동시에 expanded form으로 보여주지 않는다.

각 step은 다음 contract를 갖는다.

```text
step title
  -> 왜 필요한가
  -> 언제 실행하는가
  -> 현재 선택 범위
  -> data-quality caveat
  -> 설정 열기
  -> preflight
  -> explicit 실행
  -> normalized result
  -> next step / consumer handoff
```

step state는 `선택 가능 / 실행 중 / 최근 실행 결과 있음` 정도만 사용한다.
source freshness를 새 global dashboard로 계산하지 않는다.

### 6.1 Market Research

| Order | Step | Existing action | Placement |
| ---: | --- | --- | --- |
| 1 | 미국 주식·ETF 기준 목록 | `refresh_nyse_listing_universe` | 저빈도 준비 |
| 2 | 일별 가격 | `daily_market_update` | routine primary |
| 3 | 종목 메타데이터 | `metadata_refresh` | 필요 시 |
| 4 | 선물 데이터 | `collect_futures_ohlcv` | Futures Macro |
| 5 | 시장 심리 | `collect_market_sentiment` | Sentiment |
| 6 | FOMC 일정 | `collect_fomc_calendar` | Events |
| 7 | 공식 매크로 일정 | `collect_macro_calendar` | Events |
| 8 | 시장 구조 일정 | `collect_market_structure_calendar` | Events |
| 9 | 실적 예상 일정 | `collect_earnings_calendar` | Events |

S&P 500 actual EPS와 BLS `.ics`는 수집 action이 아니라
사용자 파일 import이므로 `공식 파일`에 둔다.

일별 가격의 기본 UI는 다음 두 scope를 분리한다.

- `일상 갱신`: managed universe, short daily window
- `전체 범위 다시 수집`: 명시적 Advanced 선택

현재 10,738-symbol managed scope를 조용히 줄이지 않는다.
대상 수와 execution profile을 확인한 뒤 실행하게 하되,
full raw NYSE sweep는 기본 선택으로 두지 않는다.

### 6.2 Portfolio Lab

| Order | Step | Existing action | Placement |
| ---: | --- | --- | --- |
| 1 | 가격 준비 | `daily_market_update` | shared routine |
| 2 | EDGAR 재무제표 | `extended_statement_refresh` | primary |
| 3 | 종목 메타데이터 | `metadata_refresh` | universe filter 보강 |

다음 저수준 action은 기본 step으로 노출하지 않는다.

- `collect_financial_statements`
- `rebuild_statement_shadow`

이 둘은 statement diagnosis 결과에 따라 `문제 복구`에서 연다.

### 6.3 Institutional Holdings

| Order | Step | Existing action | Placement |
| ---: | --- | --- | --- |
| 1 | SEC 13F dataset | `collect_sec_13f_dataset` | primary |
| 2 | ticker identity 연결 | `collect_sec_13f_identifier_mappings` | dataset 이후 |

두 action을 한 버튼으로 자동 연속 실행하지 않는다.
dataset 결과 뒤 `ticker 연결 보강으로 이동`을 제공한다.
완료 뒤 `Institutional Holdings 열기` handoff를 제공한다.

### 6.4 Practical Validation

| Group | Step | Existing action |
| --- | --- | --- |
| ETF source | 공식 source mapping | `discover_etf_provider_source_map` |
| ETF operability | 비용·규모·유동성 | `collect_etf_operability_provider` |
| ETF composition | holdings / exposure | `collect_etf_holdings_exposure` |
| Macro | FRED market context | `collect_macro_market_context` |
| Lifecycle | SEC Form 25 | `collect_sec_form25_delistings` |
| Lifecycle | Nasdaq current listing | `collect_symbol_directory_snapshots` |
| Lifecycle | SEC ticker identity | `collect_sec_company_ticker_crosscheck` |
| Lifecycle | repeated snapshot summary | `collect_computed_snapshot_lifecycle` |

기존 5-tab 안의 4개 lifecycle sub-tab 구조를 없애고
`ETF 근거 / Macro 근거 / Lifecycle 근거` 세 group으로 줄인다.

각 group은 “현재 snapshot인지”, “PIT PASS에 사용할 수 있는지”를
group header에서 한 번 설명한다.

## 7. Official File Design

`공식 파일`에는 두 action만 둔다.

### S&P 500 실제 EPS

- existing `import_sp500_index_earnings_xlsx`
- release date와 workbook 선택
- actual As-Reported 완료 분기 조건 유지
- 완료 뒤 Market Research의 S&P 500 / Economic Cycle handoff

### BLS 일정

- existing `import_bls_macro_calendar_ics`
- 자동 macro calendar 수집이 BLS source에서 실패했을 때 쓰는 fallback임을 먼저 표시
- source year / event coverage caveat 유지
- 완료 뒤 Market Research Events handoff

## 8. Recovery Design

`문제 복구`의 첫 화면에는 네 진단만 둔다.

| Diagnosis | Existing action | Possible next action |
| --- | --- | --- |
| 가격 stale 원인 | `diagnose_price_stale` | `collect_ohlcv` |
| statement universe coverage | `diagnose_statement_universe_coverage` | EDGAR refresh / shadow rebuild |
| statement symbol coverage | `diagnose_statement_coverage` | raw statement / shadow rebuild |
| statement PIT inspection | `inspect_statement_pit` | source / factor boundary review |

수동 write action은 독립 primary card가 아니라
diagnosis result의 next action 또는 Advanced에서 연다.

- `collect_ohlcv`
- `collect_asset_profiles`
- `collect_financial_statements`
- `rebuild_statement_shadow`

diagnosis 없이도 Advanced에서 직접 접근할 수 있으므로
전문 사용자의 복구 자유도는 유지한다.

## 9. History Design

### Keep

- persistent run history backend
- run metadata
- standardized JSON / failure CSV artifact generation
- job status, duration, requested scope, partial / failed symbol summary

### Default UI

Data Operations registry의 active/compatibility action만 기본 history 대상이다.
Portfolio Monitoring 같은 consumer-origin job은 기본 목록에서 제외하고
원래 consumer 화면에서 확인한다.

한 row의 visible 정보:

- 실행 시각
- 사용자-facing action name
- 목적 workflow
- 성공 / 부분 성공 / 실패
- 요청 범위
- 결과 해석
- 다음 행동

### Remove From Default UI

- session-local recent results section
- absolute history file path
- full result JSON
- raw log tail
- raw failure CSV table
- artifact absolute path
- generic non-Data job

V1은 history row의 즉시 재실행 버튼을 만들지 않는다.
대신 `해당 workflow 열기`를 제공해 현재 preflight를 다시 통과시킨다.

## 10. Advanced Data Tools

Advanced는 active action의 안전한 escape hatch다.

### Contents

- 모든 active action catalog
- action domain / write behavior / consumer / caveat
- low-level manual forms
- statement PIT inspection
- explicit full-universe price sweep
- developer-only runtime metadata

### Exclusions

- raw log browser
- raw failure CSV browser
- arbitrary JSON editor
- hidden compatibility action의 active execution

compatibility action 4개는 run-history replay/dispatcher compatibility로만 유지한다.

## 11. Action Inventory Contract

활성 action은 다음 화면 배치를 갖는다.

| Ownership | Visible placement count |
| --- | ---: |
| Market Research | 9 |
| Portfolio Lab shared/primary | 3 |
| Institutional Holdings | 2 |
| Practical Validation | 8 |
| Official File | 2 |
| Recovery / Advanced manual | 4 |
| Recovery diagnosis | 4 |

화면 배치 합계는 32개다.
`daily_market_update`와 `metadata_refresh`가
Market Research와 Portfolio Lab에 각각 한 번씩 공유 배치되기 때문이다.
이 둘의 shared placement 중복을 제거한 registry unique count는 30이어야 한다.
`daily_market_update`와 `metadata_refresh`는 여러 consumer가 쓰지만
form/dispatcher는 하나만 유지한다.

구현 test는 모든 active action이 최소 하나의 workflow/advanced ownership을 갖고,
unknown active action이 생기면 실패해야 한다.

## 12. Result Design

기존 result payload를 유지하고 presentation만 바꾼다.

visible summary 순서:

1. 사용자-facing 결과 문장
2. 성공 / 부분 성공 / 실패
3. 요청 범위 대비 처리 / 누락
4. data-quality implication
5. next action

`rows_written`은 domain-specific 보조 근거이며 headline이 아니다.

Advanced details에서도 V1은 raw log viewer를 복원하지 않는다.
필요하면 runtime metadata와 compact diagnostic fields만 표시한다.

## 13. Code Structure

### Existing Boundary To Preserve

- `app/jobs/ingestion_jobs.py`: job orchestration
- `app/web/ingestion/dispatcher.py`: action dispatch
- `app/web/ingestion/registry.py`: action inventory
- `app/services/ingestion_diagnostics.py`: read-only diagnosis facade
- `finance/data/*`: collector / DB write

### Target UI Modules

```text
app/web/ingestion/
  page.py                 # page shell, session state, scheduling boundary
  registry.py             # action metadata + workflow ownership
  workflows.py            # pure workflow definitions and inventory validation
  dispatcher.py           # existing dispatch boundary
  results.py              # pure normalized result summaries
  views/
    preparation.py        # four consumer workflows
    imports.py            # official file imports
    recovery.py           # diagnosis and recommended manual action
    history.py            # normalized Data Operations history
    advanced.py           # low-level active action catalog
  forms/
    market.py             # listing, price, futures, sentiment, events
    statements.py         # EDGAR and manual statement actions
    institutional.py      # 13F
    validation.py         # ETF / macro / lifecycle
    common.py             # symbol source, preflight, execution contract
```

V1 implementation may split modules incrementally,
but `sections.py`의 `_bind_page_globals()`를 최종 상태로 유지하지 않는다.
명시적 dependency object 또는 direct import로 교체한다.

### Functions To Remove Or Replace

- remove unused `_render_runtime_build_indicator`
- remove `_render_ingestion_runtime_build_indicator` from default page
- remove `_render_ingestion_workflow_overview`
- replace `_render_ingestion_collection_section_selector`
- replace `_render_ingestion_operational_section`
- replace `_render_ingestion_manual_section`
- replace `_render_ingestion_records_section`
- remove `_render_recent_results`
- remove `_render_recent_logs`
- remove `_render_failure_csv_preview`
- replace `_render_persistent_run_history` with normalized history view

### Functions / Contracts To Preserve

- `init_ingestion_state`
- `promote_pending_job`
- `apply_pending_ingestion_prefill`
- `_schedule_job`
- `_run_scheduled_job`
- `_dispatch_job`
- progress callbacks
- `write_run_artifacts`
- `append_run_history`
- active / compatibility action registry

public compatibility import
`app.web.ingestion_console.render_ingestion_page`는 유지한다.

## 14. Session And Navigation Contract

기존 pending prefill target은 유지한다.

- `extended_statement_refresh`
- `statement_shadow_rebuild`
- `statement_coverage_diagnosis`

prefill request에 workflow target을 추가할 수 있지만
기존 session key를 재작성하지 않는다.

consumer handoff는 allow-listed route만 사용한다.

- Market Research -> `/overview`
- Institutional Holdings -> `/institutional-portfolios`
- Portfolio Lab -> `/backtest`
- Practical Validation -> existing Backtest workflow route/state

외부 URL, provider fetch, DB write는 navigation action에서 실행하지 않는다.

## 15. Error Handling

- DB read/preflight 실패: 해당 step만 blocked로 표시하고 다른 workflow는 유지
- provider partial success: 성공 row를 보존하고 누락 범위와 next action 표시
- file parse failure: 기존 DB last-good를 유지하고 import result에서 원인 표시
- running job: 현재 workflow/step을 유지하고 다른 실행 button 비활성화
- stale session/prefill: known workflow/action으로 normalize하고 unknown target은 무시
- history payload drift: known compact fields만 표시하고 raw fallback을 기본 UI에 노출하지 않음

## 16. Responsive Design

### Desktop 1280px

- H1과 section selector 뒤에 consumer cards가 첫 viewport에 진입
- 네 consumer card는 2x2 또는 4-column
- workflow detail은 single main column
- form inputs는 최대 2-column

### Mobile 420px

- consumer card 1-column
- section selector는 wrapping 또는 vertical-safe
- stat/meta grid는 1-column
- table보다 stacked summary를 우선
- absolute path와 long internal id를 노출하지 않아 horizontal overflow 방지

QA 기준:

- horizontal overflow 0
- console error 0
- primary action을 찾기 위해 Runtime/Build 또는 static guide를 지나지 않음
- touch target과 button label truncation 없음

## 17. Test Design

### Pure Contract Tests

- active action unique count 30
- 모든 active action이 workflow 또는 Advanced ownership을 가짐
- compatibility action은 primary workflow에 없음
- shared action은 form/dispatcher ownership이 하나임
- official imports와 diagnosis write behavior가 맞음

### UI Source / Render Contracts

- page H1 is `Data Operations`
- default section is `데이터 준비`
- Runtime / Build와 static 4-step renderer가 default entrypoint에 없음
- raw log / failure CSV / full JSON renderer가 default history에 없음
- five section views are explicit modules
- `_bind_page_globals()` 제거

### Existing Regression

- dispatcher action coverage
- diagnostic facade
- NYSE universe refresh
- 13F dataset / mapping
- S&P EPS import
- futures / sentiment / event jobs
- statement refresh / diagnosis
- run history append and artifact generation

### Browser QA

- 1280x720 first viewport
- 420x900 first viewport
- four workflow entries
- each secondary section
- one bounded read-only diagnosis
- no write action in QA unless a task-specific safe smoke is approved

## 18. Tradeoffs

### Benefits

- 사용자가 consumer 목적에서 시작한다.
- backend action을 재사용해 data correctness risk를 낮춘다.
- low-level freedom을 Advanced에서 보존한다.
- raw diagnostics를 제거해 제품/개발자 경계를 명확히 한다.
- workflow/action mapping을 testable contract로 만든다.

### Costs

- existing source-string tests를 의도적으로 다시 작성해야 한다.
- `sections.py` 분리는 UI 변경과 module refactor를 함께 요구한다.
- V1은 global freshness dashboard나 자동 orchestration을 제공하지 않는다.
- 전문 사용자는 low-level action을 한 단계 더 들어가야 한다.

### Why Not Automate In V1

provider rate limit, official release date, source별 partial success,
10k-symbol duration, Streamlit session lifetime이 아직 하나의 durable execution policy로
정리되지 않았다.

자동화보다 먼저 task-oriented manual flow를 실제로 사용해
반복 빈도와 실패 패턴을 수집하는 편이 안전하다.

## 19. Implementation Approval Boundary

이 문서 승인 후 3차 구현에 들어간다.

3차에서 변경하지 않는 것:

- collector semantics
- DB schema
- provider source
- registry / saved JSONL content
- background queue / scheduler
- live trading boundary

구현 중 action 삭제 필요성이 새로 발견되면
backend 삭제와 UI removal을 구분해 다시 사용자 확인을 받는다.

## 20. Follow-up — Contextual Reference Help Removal

2026-07-26 사용자 확인에 따라 Data Operations 상단의
`Reference help · Ingestion` contextual panel은 제거한다.

- 제거 범위는 `render_ingestion_page()`의 renderer 호출과 전용 import뿐이다.
- canonical Reference Center, Ingestion catalog item, destination과 related journey는
  유지한다.
- 목적 카드, section navigation, action form, dispatcher, collector, DB와 loader는
  변경하지 않는다.
- source contract test로 Data Operations page가 contextual help를 다시 호출하지
  않도록 고정한다.
- desktop/mobile Browser QA에서 제목 다음에 section navigation과 목적 카드가
  바로 이어지는지 확인한다.
