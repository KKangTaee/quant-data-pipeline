# Overview Market Context Nasdaq-100 Coverage Repair Action V1 Design

Status: Approved in Conversation — Awaiting Written Spec Review
Last Updated: 2026-07-13

## Decision Summary

Nasdaq-100 · QQQ proxy coverage blocker 안에 `60개월 가치평가 자료 보강` action을 추가한다. action은 현재 job을 무조건 반복하지 않고, DB에 저장된 최근 60개월 holdings/EPS/price를 먼저 진단해 실제 gap만 수집한다. 사용자는 같은 화면에서 완료까지 기다리며, 수집 후 60개월 materialization과 valuation cache refresh가 자동으로 이어진다.

기존 품질 계약은 유지한다. 실제 분기 diluted EPS와 가격으로 설명되는 월별 보유 비중이 95% 미만이면 그래프를 표시하지 않는다. 해외 issuer의 FY-only 수치, 상장폐지 종목의 미확인 가격, 식별 불가 보유를 임의 대체하거나 보간하지 않는다.

## Approaches Considered

### A. Targeted Synchronous Coverage Closure — Selected

- 현재 DB를 읽어 누락 symbol/month/reason을 먼저 계산한다.
- 필요한 SEC statement와 EOD range만 기존 ingestion으로 수집한다.
- 화면에서 단계별 진행 상태를 보며 완료까지 기다린다.
- 종목 단위 UPSERT로 중단 후 이어받는다.

장점은 불필요한 provider 요청을 줄이고 기존 Python action facade/DB 경계를 재사용한다는 점이다. 단점은 과거 편입·퇴출 종목이 많으면 실행 시간이 길고, 무료 원천에 없는 자료는 여전히 blocker로 남는다는 점이다.

### B. Blind Full Refresh — Rejected

현재 Nasdaq valuation job 전체를 매번 다시 실행하는 방식은 단순하지만, 이 job은 QQQ holdings와 QQQ EOD 위주이며 누락 constituent EPS/price를 적극 보강하지 않는다. 이미 확보한 자료도 반복 요청하고 동일 gap이 그대로 남을 수 있다.

### C. Background Queue — Deferred

브라우저를 떠나도 계속되는 durable worker는 장시간 backfill에 유리하지만 현재 앱에 공통 queue/runtime가 없다. 이번 범위를 벗어나는 운영 인프라를 새로 만들지 않고 사용자가 승인한 synchronous flow를 따른다.

## User Flow

```text
Nasdaq coverage blocker
  -> 60개월 가치평가 자료 보강
  -> 대상 확인
  -> EPS 보강
  -> 가격 이력 보강
  -> 60개월 가치평가 재계산
  -> valuation cache clear + rerun
  -> READY graph 또는 갱신된 blocker
```

버튼은 EPS만이 아니라 holdings identity, constituent/QQQ EOD, monthly materialization까지 다루므로 `EPS 수집` 대신 `60개월 가치평가 자료 보강`으로 표시한다. 첫 화면에는 사용자 진행 단계와 결과만 표시한다. symbol별 raw job row와 stack trace는 기본 화면의 주인공으로 만들지 않는다.

## Architecture And Ownership

```text
MarketContextValuation.tsx
  -> Streamlit component event {id, nonce}
  -> market_context_helpers.py event consume/dedup
  -> overview_actions.py Nasdaq coverage repair facade
  -> ingestion_jobs.py statement/EOD/materialization pipeline
  -> finance/data/nasdaq100_valuation.py repair plan + monthly reconstruction
  -> finance_* DB schemas
  -> loader/service read model
  -> cache clear + Streamlit rerun
```

### Coverage Repair Planner

`finance/data/nasdaq100_valuation.py`가 DB-independent 진단 계산과 DB-backed input load를 소유한다. planner는 최근 60개 observation month에 사용되는 historical holdings universe를 기준으로 다음을 반환한다.

```python
{
  "window": {"start_month": "...", "end_month": "...", "months": 60},
  "targets": [
    {
      "symbol": "...",
      "issuer_cik": "...",
      "needs": ["quarterly_diluted_eps", "eod_price"],
      "start_date": "...",
      "end_date": "...",
      "affected_months": 0,
      "max_weight_pct": 0.0,
    }
  ],
  "unsupported": [...],
  "before": {"ready_months": 0, "blocked_months": 60},
}
```

진단 reason은 최소 `missing_quarterly_eps`, `missing_price_history`, `missing_identity`, `non_equity`, `unsupported_free_source`로 구분한다. 현금, 통화, index future, synthetic cash는 equity coverage denominator에서 제외하고 equity weight를 다시 정규화한다.

### Ingestion Orchestration

`app/jobs/ingestion_jobs.py`는 planner target을 작은 batch로 실행한다. EPS는 canonical SEC EDGAR statement ingestion을 거쳐 `finance_fundamental.nyse_financial_statement_values`에 저장하고, 가격은 existing OHLCV ingestion을 거쳐 `finance_price.nyse_price_history`에 저장한다. Nasdaq module이나 React가 provider를 직접 호출하지 않는다.

진행 callback contract는 사용자 단계와 수치만 제공한다.

```python
{
  "event": "stage_progress",
  "stage": "eps" | "prices" | "materialize",
  "completed": 0,
  "total": 0,
  "message": "...",
}
```

각 batch 실패는 전체 DB transaction을 rollback하지 않는다. 성공한 batch는 유지하고 failed symbol/reason을 `JobResult.details`에 compact evidence로 남긴다. 다음 실행의 planner가 이미 충족된 target을 제거한다. full-window 가격 수집 뒤에도 이력이 부족한 종목은 기존 `finance_meta.market_data_issue`의 `limited_price_history` evidence를 재사용해 같은 provider 요청을 반복하지 않는다. foreign/FY-only EPS처럼 source contract상 지원되지 않는 항목은 issuer/form 분류에서 결정적으로 `unsupported_free_source`로 분류한다. 별도 checkpoint table은 이번 범위에 추가하지 않는다.

### Rematerialization And Quality

수집 뒤 `materialize_and_store_nasdaq100_monthly`를 최근 60개월 window로 실행한다. 기존 point-in-time `available_at`, latest eligible holdings snapshot, weight drift, four-discrete-quarter TTM, 95% weighted coverage, calibration 계약을 그대로 사용한다.

결과는 다음을 구분한다.

- `READY`: 최근 60개월 graph contract가 모두 충족됨
- `PARTIAL_SUCCESS`: 일부 자료가 추가됐지만 하나 이상의 월이 95% 미만임
- `FAILED`: planner/ingestion/materialization 자체가 실행되지 못함

부분 성공을 READY로 포장하지 않는다. repair result에는 before/after ready month count, latest/minimum coverage, remaining reason count만 first-class summary로 둔다.

### Action Facade And React Event

`app/jobs/overview_actions.py`는 `run_overview_nasdaq100_valuation_repair` facade를 제공하고 run history 기록에 필요한 표준 `JobResult`를 반환한다. React는 `{event: {id: "repair_nasdaq100_60m", nonce}}`만 전달한다.

`market_context_helpers.py`는 session state에 마지막 event token을 저장해 중복 실행을 막고, `st.status`/progress를 이용해 synchronous execution을 표시한다. 완료 뒤 다음 cache를 clear하고 `st.rerun()`한다.

- `load_market_context_valuation_model`
- repair 실행에 사용된 관련 DB-backed cached loaders

실행 결과 summary는 session state에 보관해 rerun 뒤 READY graph 상단의 성공 notice 또는 blocker 하단의 partial/failed notice로 한 번 표시한다.

### React Surface

coverage blocker의 reason 아래에 action 영역을 둔다.

- primary label: `60개월 가치평가 자료 보강`
- helper: `누락된 구성 종목 EPS와 가격 이력을 보강한 뒤 다시 계산합니다.`
- pending label: `자료 보강을 시작하는 중`
- partial label: `일부 자료를 보강했지만 기준에 아직 못 미칩니다.`
- retry label: `남은 자료 다시 보강`

React local pending state는 event 전달 직후 double click을 막는 보조 수단이다. 실제 중복 방지는 Python nonce consumption이 소유한다. 420px에서도 action copy와 button이 수평 overflow를 만들지 않아야 한다.

## Error Handling

- planner failure: 수집을 시작하지 않고 기존 blocker를 유지한다.
- individual EPS/price failure: 성공 batch를 유지하고 materialization은 가능한 입력으로 계속한다.
- materialization failure: cache를 clear하지 않고 기존 read model을 유지한다.
- cache/rerun failure: 저장은 완료된 상태이므로 사용자가 화면 새로고침으로 복구할 수 있는 안내를 남긴다.
- provider unsupported: 반복 가능한 failure로 계속 요청하지 않고 `unsupported_free_source`로 표시한다.

오류가 있어도 coverage threshold를 낮추거나 missing earnings를 0/sector median/annual proxy로 채우지 않는다.

## Test Strategy

### Pure / DB Contract

- 60개월 universe와 target date range 계산
- non-equity exclusion and renormalization
- EPS/price/identity/unsupported reason classification
- already-complete target exclusion
- repeated planner determinism
- repeat UPSERT idempotency

### Job / Service

- EPS and price batch partial failure
- progress callback ordering
- successful batch persistence after later failure
- rematerialization always follows usable partial collection
- before/after/remaining summary
- 60/60 READY and partial-success contracts

### UI Contract

- blocker-only action visibility
- React event nonce emission
- Python duplicate event suppression
- synchronous progress and result reflection
- valuation cache clear and rerun
- successful graph transition and failed blocker retention
- narrow layout overflow regression

### Actual QA

- actual DB repair plan dry diagnostic
- bounded real collection smoke before full run
- full 60-month synchronous run
- desktop and 420px Browser QA
- console errors, horizontal overflow, retry behavior

## Success Criteria

- 사용자는 coverage blocker에서 한 번의 클릭으로 60개월 자료 보강과 재계산을 시작할 수 있다.
- action은 UI/provider direct fetch 없이 ingestion -> DB -> loader/service 경계를 따른다.
- 중간 실패 후 재실행이 완료된 자료를 재사용한다.
- 통과 시 같은 화면에서 자동으로 graph가 표시된다.
- 미통과 시 갱신된 coverage와 남은 무료 원천 한계를 명확히 보여준다.
- unrelated untracked files, generated screenshots, run history artifact는 commit하지 않는다.
