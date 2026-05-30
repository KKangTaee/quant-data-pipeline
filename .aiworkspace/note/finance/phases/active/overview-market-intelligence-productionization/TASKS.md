# Overview Market Intelligence Productionization Tasks

## Development Stages

| Stage | Task | Status | Owner | Why |
|---|---|---|---|---|
| 2차 | Refresh State And Diagnostics Baseline | Complete | `sub-dev` | 정식 기능의 첫 조건은 최신성 / 부분 실패 / missing reason을 사용자가 바로 읽는 것이다. |
| 2차 | Event Read Model Hardening | Complete | `sub-dev` | FOMC와 earnings가 섞인 Events table에서 source confidence와 stale estimate를 분명히 보여준다. |
| 2차 | QA And Acceptance Checklist | Complete | `sub-dev` | prototype 완료가 아니라 정식화 gate를 통과했는지 확인하는 checklist를 만든다. |
| 3차 | Earnings Source Validation | Complete | `sub-dev` | yfinance estimate를 official/company source 또는 alternate free source와 비교하는 경로를 만든다. |
| 3차 | Earnings Lifecycle Cleanup | Complete | `sub-dev` | 날짜 변경으로 생기는 older estimate row를 superseded/stale로 정리한다. |
| 3차 | Low-Frequency Wider Collection | Complete | `sub-dev` | Top movers 외에 broader universe를 안전하게 저빈도 수집한다. |
| 4차 | Market Intelligence Visuals | Complete | `sub-dev` | heatmap/treemap 또는 dense chart로 sector/industry/movers 비교 경험을 높인다. |
| 4차 | Calendar UX Polish | Complete | `sub-dev` | Events를 calendar-like view, filters, source labels로 읽기 쉽게 만든다. |
| 4차 | Production Closeout | Complete | `sub-dev` | runbook, docs, browser QA, handoff를 정리하고 다음 phase로 넘긴다. |

## Task Details

### Task 2-01. Refresh State And Diagnostics Baseline

Files likely to change:

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/jobs/ingestion_jobs.py`
- `tests/test_service_contracts.py`

Work:

- Market Movers daily refresh state를 `fresh / due / stale / failed / partial`로 명확히 계산한다.
- 5분 refresh UX를 버튼 활성/상태 배지/next refresh text로 정리한다.
- missing diagnostics에 recommended action을 추가한다.
- latest snapshot source, snapshot age, failed symbol count를 status card에 더 명확히 노출한다.

Done:

- 사용자가 “지금 refresh가 필요한가?”를 버튼 주변에서 바로 판단할 수 있다.
- partial/fail일 때 어떤 symbol/reason/action인지 확인할 수 있다.
- service contract tests와 Browser smoke가 통과한다.

### Task 2-02. Event Read Model Hardening

Files likely to change:

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `finance/data/market_intelligence.py`
- `tests/test_service_contracts.py`

Work:

- Events read model에 source confidence, official vs estimate, collected age를 추가한다.
- Earnings row의 stale estimate 기준을 정의한다.
- All / FOMC / Earnings filter를 유지하되 table columns와 status cards를 event type에 맞게 조정한다.

Done:

- FOMC official row와 earnings estimate row가 화면에서 명확히 구분된다.
- earnings가 오래된 estimate이면 warning이 보인다.

### Task 2-03. QA And Acceptance Checklist

Files likely to change:

- `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`

Work:

- 2차 완료 기준 checklist를 작성한다.
- manual QA route: Overview Market Movers, Sector / Industry, Events, Ingestion refresh를 정리한다.
- closeout 전 필수 command를 phase docs에 고정한다.

Done:

- 구현자가 다음 task를 마쳐도 무엇을 확인해야 하는지 문서만 보고 알 수 있다.

### Task 3-01. Earnings Source Validation

Work:

- 무료 source 후보를 비교한다: yfinance calendar, company IR page parsing 후보, Nasdaq/Yahoo web page parsing 후보.
- 공식 source가 가능한 ticker와 estimate-only ticker를 구분한다.
- source confidence와 fallback order를 문서화하고 collector에 반영한다.

Done:

- earnings row가 `official / provider_estimate / unknown` 신뢰도로 분류된다.

### Task 3-02. Earnings Lifecycle Cleanup

Work:

- 같은 symbol의 earnings estimate가 날짜 변경될 때 older row 처리 방식을 구현한다.
- 먼저 read model에서 stale/superseded 판정, 필요 시 schema column 추가를 검토한다.
- cleanup job은 idempotent해야 한다.

Done:

- Events table이 오래된 estimate row로 사용자를 혼동시키지 않는다.

### Task 3-03. Low-Frequency Wider Collection

Work:

- Coverage 1000/2000 전체 장중 수집이 아니라 scheduled/low-frequency collection을 설계한다.
- 기본 대상은 S&P 500, 이후 Top1000 일부 batch로 확장한다.
- rate-limit, retry, cooldown, progress 표시를 둔다.

Done:

- broad earnings 수집이 운영 버튼 실수로 앱을 멈추게 하지 않는다.

### Task 4-01. Market Intelligence Visuals

Work:

- Sector / Industry leadership에 heatmap 또는 treemap을 추가한다.
- Market Movers ranking chart를 dense하고 비교 가능한 형태로 개선한다.
- 색상은 과도한 단일 hue를 피하고, operational dashboard 톤을 유지한다.

Done:

- 사용자가 table을 읽기 전에 강한 sector/industry를 빠르게 파악할 수 있다.
- Market Movers는 Rank chart와 Sector Pulse chart를 탭으로 제공한다.
- Sector / Industry leadership은 Equal Weight, Cap Weighted, Top Symbol return을 heatmap으로 비교한다.

### Task 4-02. Calendar UX Polish

Work:

- Events를 날짜 중심으로 묶어 보여준다.
- event type, source, confidence, symbol filters를 정리한다.
- near-term events와 stale estimates를 분리한다.

Done:

- Events 탭이 단순 DB table이 아니라 운영 calendar로 읽힌다.
- Events는 Window, Source Type, Validation filter를 제공한다.
- Calendar view는 날짜별 event group과 timeline chart를 보여주고, Table view는 기존 row inspection을 유지한다.

### Task 4-03. Production Closeout

Work:

- runbook, data docs, architecture docs, root logs를 최종 정렬한다.
- Browser smoke와 acceptance checklist를 완료한다.
- 남은 work를 다음 phase 후보로 분리한다.

Done:

- Overview Market Intelligence를 정식 feature로 부를 수 있는 상태와 남은 한계를 문서화한다.
- Phase 2차, 3차, 4차 task를 모두 완료했고 runbook / root handoff / acceptance checklist를 최신 상태로 맞춘다.
