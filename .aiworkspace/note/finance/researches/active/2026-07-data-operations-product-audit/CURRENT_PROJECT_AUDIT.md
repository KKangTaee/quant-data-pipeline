# Current Project Audit — Data Operations

Status: Audit Complete
Last Updated: 2026-07-25

## Summary

현재 Data Operations의 가장 큰 문제는 수집 기능 부족이 아니다.
backend에는 가격, 재무제표, 선물, 심리, 일정, 기관 13F, ETF provider,
lifecycle evidence, 공식 파일 import와 진단 기능이 폭넓게 구현돼 있다.

문제는 활성 action 30개가 `일상 운영 / 검증 데이터`와
`수동 복구 / 진단` 두 선반에 거의 같은 위계로 노출된다는 점이다.
사용자는 “Market Research 자료를 준비한다” 또는
“Portfolio Lab의 가격을 최신화한다”가 아니라 collector와 table 관계를 이해한 뒤
개별 job을 골라야 한다.

권장 방향은 backend 기능 삭제가 아니라 다음 순서다.

1. 제품 첫 화면에서 개발자 정보와 저수준 진단을 제거한다.
2. 반복 작업을 consumer와 목적 기준의 짧은 workflow로 재조합한다.
3. 중복 수동 job은 진단 결과의 다음 행동 또는 Advanced Recovery로 내린다.
4. raw log / failure CSV / artifact path는 사용자 기본 화면에서 제거한다.
5. 장기 실행은 durable execution과 재시도 경계를 별도 차수에서 설계한다.

## Current Product Promise

Data Operations는 외부 provider와 공식 파일에서 데이터를 수집해 MySQL에 저장하고,
다른 제품 화면이 provider를 직접 호출하지 않도록 하는 write boundary다.

주요 consumer는 다음과 같다.

| Consumer | Data Operations가 준비하는 것 |
| --- | --- |
| Research > Market Research | 가격, 선물, 심리, 이벤트, S&P 500 실제 EPS |
| Research > Institutional Holdings | SEC 13F dataset과 identifier mapping |
| Portfolio > Portfolio Lab | 가격, EDGAR statement, statement shadow factor |
| Portfolio > Portfolio Monitoring | 활성 직접 주식·ETF 가격 최신화의 상세 기록 |
| Practical Validation | ETF operability / holdings / exposure, FRED, lifecycle evidence |

UI에서 provider / FRED를 직접 fetch하지 않고
`Ingestion -> DB -> Loader -> Service -> UI`를 유지하는 architecture boundary는 타당하다.

## Current Workflow

현재 화면 순서는 다음과 같다.

```text
Ingestion title
  -> Reference help
  -> Runtime / Build
  -> 운영 콘솔 설명
  -> 4단계 정적 workflow 설명
  -> 작업 영역
     -> 일상 운영 / 검증 데이터
     -> 수동 복구 / 진단
     -> 실행 기록 / 결과
```

`일상 운영 / 검증 데이터`에는 활성 action 22개,
`수동 복구 / 진단`에는 활성 action 8개가 있다.
호환성 action 4개는 UI에서 숨겨져 과거 replay 경로만 보존한다.

desktop 1280x720 실제 화면에서 첫 실행 버튼은 약 663px 지점에 걸쳐 있고,
기본 `일별 가격 업데이트 실행`은 약 2,125px 아래에 있다.
420x900 mobile에서는 Runtime / Build와 일반 설명만으로 첫 viewport가 끝나
실제 작업이 보이지 않는다.

## Implemented Capabilities

### Routine / Low-Frequency Collection

- NYSE 주식·ETF current listing universe refresh
- daily price / dividend / split refresh
- futures OHLCV
- CNN / AAII sentiment
- EDGAR statement + shadow refresh
- asset profile metadata
- FOMC, macro, market-structure, earnings calendar
- SEC 13F dataset + identifier mapping

### Official File Import

- BLS calendar `.ics`
- S&P 500 Index Earnings `.xlsx` with release date

### Practical Validation Data

- ETF official source discovery
- ETF operability
- ETF holdings / exposure
- FRED market context
- SEC Form 25, Nasdaq current listing, SEC ticker cross-check,
  repeated-observation lifecycle evidence

### Manual Recovery / Diagnostics

- bounded manual OHLCV
- manual asset profile
- raw statement collection
- statement shadow rebuild
- price stale diagnosis
- statement universe coverage QA
- statement coverage diagnosis
- statement PIT inspection

### Execution Evidence

- session-local recent results
- persistent run history
- full result JSON and artifact paths
- recent raw logs
- failure CSV preview

## Surface Role Classification

| Surface | Role | Finding |
| --- | --- | --- |
| Routine collection actions | Mixed / transitional | 실제 데이터 준비 가치가 있으나 collector 단위 UI다. |
| Official file imports | Internal operator tool with clear user task | 별도 목적 그룹으로 유지 가치가 높다. |
| Practical Validation data collection | Mixed / transitional | validation 목적은 분명하지만 다섯 provider tab과 네 lifecycle tab을 사용자가 직접 조합해야 한다. |
| Manual recovery / diagnostics | Internal ops console | 기본 사용자 흐름이 아니라 예외 복구 경로다. |
| Run history | Supporting operations | 감사·재시도 근거는 필요하지만 현재는 ingestion 외 실행까지 섞인다. |
| Raw log / failure CSV / artifact path | Developer diagnostics | 제품 사용자 기본 화면에는 불필요하다. |
| Runtime / Build | Developer diagnostics | code hot-reload 확인용이며 데이터 운영 업무가 아니다. |

전체 화면은 현재 user-facing data workspace라기보다
제품 기능과 내부 운영 콘솔이 섞인 `mixed/transitional` surface다.

## Strengths

- provider fetch와 UI read 경계가 분리되어 있다.
- action registry가 active / compatibility, write behavior, target table을 명시한다.
- 모든 registry action에 guide가 있어 source/consumer/caveat가 누락되지 않는다.
- 대량 입력 preflight와 atomic NYSE universe refresh guard가 있다.
- EDGAR, official file, provider snapshot의 PIT 한계를 반복적으로 설명한다.
- legacy broad yfinance action은 UI에서 숨기고 replay compatibility만 보존했다.
- 개별 action의 결과는 partial success와 failed symbol을 숨기지 않는다.
- Browser console error는 desktop/mobile 점검에서 발견되지 않았다.

## Weak Points

### 1. 첫 화면이 사용자 행동보다 개발 진단을 우선한다

`Runtime / Build`와 정적 4-step 설명이 실제 action보다 먼저 나온다.
이 정보는 개발 중 stale process를 찾는 데는 유용하지만 사용자가 데이터를 준비하는 데
직접 필요하지 않다.

### 2. 제품 IA와 화면 제목이 다르다

navigation은 `Data Operations`, H1은 `Ingestion`이다.
제품 개념과 내부 pipeline 용어가 첫 화면부터 충돌한다.

### 3. Action 수보다 action 선택 모델이 문제다

활성 action 30개가 job/collector 단위로 드러난다.
Market Research, Portfolio Lab, Institutional Holdings,
Practical Validation 중 무엇을 준비하려는지로 시작할 수 없다.

### 4. 기본 routine action의 위험과 비용이 크다

일별 가격 업데이트 기본값은 profile-filtered stock+ETF 10,738개다.
화면은 대량 실행이라고 경고하지만, 처음 방문한 사용자가
routine refresh와 full sweep의 차이를 이해해야 한다.

### 5. 운영 alias와 수동 job의 의미가 중복된다

- daily price update / manual OHLCV
- metadata refresh / manual asset profile
- EDGAR refresh / raw statement collection
- EDGAR refresh / shadow-only rebuild

backend 분리는 타당하지만 네 쌍을 모두 독립 도구처럼 노출하면 선택 비용이 커진다.

### 6. Consumer별 dependency가 화면에서 연결되지 않는다

- 13F dataset 뒤 identifier mapping
- listing universe 뒤 metadata / price
- ETF source map 뒤 operability / holdings
- raw statement 뒤 shadow rebuild
- calendar automatic fetch 실패 뒤 BLS file fallback

현재는 설명으로 관계를 말하지만 하나의 순서 있는 workflow로 실행하지 않는다.

### 7. 실행 기록이 제품 범위를 벗어난다

실제 화면에서 `portfolio_monitoring_price_refresh`가 Ingestion history 최상단에 나타났다.
또한 session result와 persistent history가 중복되고,
로컬 절대 경로, raw log tail, failure CSV, result JSON이 사용자에게 노출된다.

### 8. 물리적 모듈 분리는 됐지만 결합도는 여전히 높다

- `page.py`: 2,426 lines
- `sections.py`: 2,073 lines
- `ingestion_jobs.py`: 4,363 lines

`sections.py`의 `_bind_page_globals()`는 `page` module의 모든 이름을
runtime global에 주입한다. 이 구조는 순환 의존, 숨은 contract,
정적 분석과 단위 테스트의 어려움을 만든다.

### 9. Registry가 renderer를 생성하지 않는다

registry, guide, dispatcher는 action metadata를 갖지만
각 Streamlit form은 `sections.py`에 수동 구현돼 있다.
action이 추가될 때 registry/guide/dispatch/form/test 네 위치의 drift 위험이 있다.

### 10. 테스트가 현재 UI debt를 contract로 고정한다

focused test는 module ownership과 문자열 존재를 잘 검사하지만,
사용자 완료 경로보다 source substring을 주로 확인한다.
일부 test는 recent results, history, raw logs, failure CSV가 모두 있어야 한다고 강제해
개선 시 의도적으로 다시 설계해야 한다.

## Remove From Default Product UI

다음은 backend data나 artifact를 삭제하자는 뜻이 아니라
기본 제품 화면에서 제거할 후보이다.

| Candidate | Decision | Preservation |
| --- | --- | --- |
| Runtime / Build card | Remove | run metadata 또는 developer details에 보존 |
| 4-step static workflow cards | Remove | action별 필요한 preflight만 유지 |
| 내부 job id / target table 반복 노출 | Hide | Advanced details와 docs에 보존 |
| session-local recent results | Merge/remove | persistent normalized history로 충분 |
| raw recent log viewer | Remove | local log file은 backend/debugging에 보존 |
| failure CSV preview | Remove | artifact 생성은 보존, 사용자 재시도 대상으로 변환 |
| full result JSON / absolute artifact path | Hide | developer details에서만 접근 |
| manual alias cards의 독립 primary placement | Demote | diagnosis next action / Advanced Recovery에서 보존 |
| broad Practical Validation provider workbench의 primary placement | Demote | validation 문맥 handoff + Advanced Data에서 보존 |

현재 호출되지 않는 `_render_runtime_build_indicator()`는
별도 dead-code 제거 후보이고,
사용 중인 `_render_ingestion_runtime_build_indicator()`와 혼동을 만든다.

## Keep And Improve

| Capability | Direction |
| --- | --- |
| NYSE listing refresh | low-frequency market baseline workflow의 선행 단계 |
| daily price update | bounded routine refresh와 explicit full sweep를 분리 |
| EDGAR statement refresh | Portfolio Lab data preparation의 primary path |
| futures / sentiment / event collection | Market Research data preparation으로 묶음 |
| 13F dataset / mapping | 순서 있는 Institutional Holdings refresh로 결합 |
| official file imports | `공식 파일 가져오기`로 분리 |
| ETF / macro / lifecycle evidence | Practical Validation에서 필요한 항목만 context handoff |
| read-only diagnostics | 예외 발생 뒤 Advanced Recovery에서 접근 |
| run metadata and artifacts | backend audit trail로 보존 |

## Missing Product Capabilities

### P0 — Purpose-Based Entry

첫 화면에서 collector 목록 대신 사용자가 끝내려는 일을 고른다.

- Market Research 데이터 준비
- Portfolio Lab 데이터 준비
- Institutional Holdings 데이터 준비
- Practical Validation 데이터 보강
- 특정 누락 복구
- 공식 파일 가져오기

### P0 — Dependency-Aware Workflow

각 목적 안에서 prerequisite, 현재 선택 범위, 실행 순서,
완료 후 이동 화면을 한 흐름으로 보여준다.
저수준 job은 workflow step으로 남고 제품 navigation item이 되지 않는다.

### P0 — Safer Scope Defaults

10,738-symbol full routine run을 첫 기본값으로 두지 않는다.
routine bounded scope와 explicit broad sweep를 분리하고,
대상·기간·예상 부담을 실행 전에 한 문장으로 확정한다.

### P1 — Actionable Result

row count 중심 결과를 consumer-ready / partial / blocked와
누락 범위, 바로 가능한 다음 행동으로 변환한다.
raw log와 artifact path는 기본 결과에서 제거한다.

### P1 — Contextual Handoff

Research / Portfolio / Validation 화면의 실제 missing-data 상태에서
Data Operations의 정확한 workflow와 입력값으로 이동하고,
완료 후 원래 consumer로 돌아갈 수 있어야 한다.

### P1 — Durable Long-Run Execution

동기 rerun에만 의존하는 10k-symbol 작업은
재접속 후 상태 복원, 실패 subset 재시도, 취소/중단 정책이 부족하다.
background worker 또는 durable queue는 별도 architecture 차수로 설계해야 한다.

### P2 — Scheduling Policy

daily / weekly / quarterly source를 모두 수동으로 기억하게 하지 않는다.
다만 자동 실행은 provider rate limit, official release timing,
partial-success policy를 먼저 확정한 뒤 도입한다.

## Recommended Information Architecture

권장안은 `task-oriented hybrid`다.

```text
Data Operations
  -> 지금 필요한 데이터 작업
     -> consumer별 준비 workflow
  -> 공식 파일 가져오기
  -> 문제 복구
     -> diagnosis가 추천한 bounded action
  -> 실행 이력
     -> normalized result와 재시도만
  -> Advanced Data Tools
     -> low-level collector / PIT inspection / developer evidence
```

첫 화면은 raw run count나 저장 row dashboard가 아니라
“어느 제품 기능을 준비하려는가”와 “다음 행동이 무엇인가”를 중심으로 한다.

## Alternatives

### A. Copy / Layout Cleanup Only

30개 action을 유지하고 순서, 문구, expander를 정리한다.

- 장점: 변경 위험과 effort가 낮다.
- 단점: 사용자가 collector 관계를 이해해야 하는 근본 문제가 남는다.

### B. Task-Oriented Hybrid — Recommended

consumer workflow를 primary로 만들고 저수준 action은 Advanced로 내린다.

- 장점: backend 재사용이 높고 실제 완료 경로가 짧아진다.
- 단점: readiness read model과 action handoff contract가 필요하다.

### C. Automated Data Control Plane

scheduler, durable queue, dependency graph, retry policy를 중심으로 재구축한다.

- 장점: 반복 운영 부담을 가장 많이 줄인다.
- 단점: provider policy, concurrency, recovery, deployment 운영 범위가 크게 늘어난다.

현재는 B를 먼저 하고, 실제 반복 사용 근거가 쌓인 뒤 C 일부를 도입하는 편이 적합하다.

## Code And Ownership Implications

변경 가능성이 큰 파일:

- `app/web/ingestion/page.py`
- `app/web/ingestion/sections.py`
- `app/web/ingestion/registry.py`
- `app/web/ingestion/guides.py`
- `app/web/ingestion/results.py`
- `app/web/ingestion/dispatcher.py`
- `app/services/ingestion_diagnostics.py`
- `app/web/streamlit_app.py`
- 관련 `tests/test_ingestion_module_split_contracts.py`
- 관련 `tests/test_service_contracts.py`

collector / DB semantics가 바뀌지 않는 1차 UI 개편에서는
`finance/data/*`, `finance/data/db/schema.py`, registry/saved JSONL을 건드리지 않는다.
durable execution 차수에서만 `app/jobs/*`와 persistence contract를 다시 검토한다.

## Data And Validation Risks

- current listing, asset profile, ETF holdings는 historical PIT truth가 아니다.
- FRED current observation은 ALFRED vintage가 아니다.
- current ETF operability는 historical transaction cost proof가 아니다.
- Form 25 부재, current SEC identity, repeated current snapshot은
  active historical membership PASS 근거가 아니다.
- UI 개편 중 current snapshot과 PIT evidence를 같은 `ready`로 합치면 안 된다.
- purpose-based workflow가 여러 job을 묶더라도 partial success와 source별 실패를 숨기면 안 된다.
- full sweep default를 줄일 때 backtest universe coverage를 조용히 축소하면 안 된다.

## Documentation Or Handoff Drift

- docs 일부는 여전히 `Workspace > Ingestion`, 화면 navigation은
  `Data > Data Operations`, H1은 `Ingestion`을 사용한다.
- 기존 Operations 연구는 2026-07-19 이후 Portfolio Monitoring 단일 화면 결론으로 갱신됐으나,
  Data Operations 자체의 mixed surface 문제는 별도 audit이 필요했다.
- 이전 closeout은 raw log / failure CSV를 Ingestion에 보존했지만,
  이번 실제 사용성 감사에서는 기본 사용자 화면에서 다시 제거 후보로 분류한다.
  artifact backend 보존과 사용자 UI 노출을 구분해야 한다.

## Benchmark Questions

다음 차수에서 외부 benchmark가 필요하다면 아래 질문만 조사한다.

- mature data products는 routine refresh와 advanced repair를 어떻게 분리하는가?
- long-running data job의 scope confirmation, retry, resume를 어떻게 보여주는가?
- consumer readiness를 raw row count 없이 어떻게 action으로 연결하는가?
- operator audit trail과 일반 사용자 결과 화면을 어떻게 분리하는가?

## Open Questions

1. Data Operations의 주 사용자는 단일 개발자/운영자인가,
   아니면 finance workflow를 쓰는 비개발 사용자까지 포함하는가?
2. routine data collection은 계속 explicit manual action이어야 하는가,
   아니면 일부 source는 scheduler 대상인가?
3. persistent run history는 제품 UI에서 얼마나 보존해야 하는가?
4. Portfolio Monitoring refresh처럼 consumer 화면에서 직접 실행한 job도
   Data Operations history에 보여야 하는가?
5. full universe price refresh의 실제 권장 cadence와 허용 실행 시간은 얼마인가?

## Audit Conclusion

현재 Data Operations는 backend capability는 강하지만 제품 workflow는 약하다.
30개 action을 더 잘 꾸미는 것만으로는 충분하지 않다.

가장 먼저 해야 할 일은
`collector catalog -> purpose-based data workflow` 전환이다.
삭제는 backend 기능보다 기본 UI의 개발자 정보, raw diagnostics,
중복 alias placement를 대상으로 해야 한다.
durable background execution과 scheduling은 그 다음 차수다.
