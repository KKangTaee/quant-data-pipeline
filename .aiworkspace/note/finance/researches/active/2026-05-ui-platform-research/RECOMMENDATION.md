# Recommendation

## One-Line Recommendation

Streamlit은 내부 research / ops console로 유지하고, Python quant engine 앞에 service/API contract를 먼저 만든 뒤, Selected Portfolio Dashboard 또는 Final Review Evidence Viewer를 read-only Next.js pilot으로 분리한다.

## Why This Direction

현재 finance 프로젝트의 병목은 quant engine 자체보다 UI state와 product surface다. Streamlit은 빠른 개발에는 적합했지만, 현재 workflow는 candidate, validation, final decision, selected monitoring까지 이어지는 multi-stage product가 되었다. 이 상태에서 모든 화면을 Streamlit으로 계속 키우면 session state, rerun side effect, widget-bound logic이 계속 늘어난다.

반대로 full rewrite는 위험이 너무 크다. 이미 구현된 Backtest / Practical Validation / Final Review 흐름을 한 번에 React로 옮기면, 검증보다 migration 자체가 프로젝트를 잡아먹을 가능성이 높다.

따라서 가장 좋은 방향은 staged hybrid다.

```text
Python core stays:
finance/data, loaders, factor, strategy, engine, validation

Service boundary emerges:
Pydantic models + service functions + optional FastAPI

UI splits:
Streamlit = internal console
Next.js/React = product-grade read-only and chart-heavy surfaces
```

## Recommended Build Order

### Step 1. Contract First

목표:

- `BacktestRunResult`, `EvidencePack`, `SelectedPortfolioSnapshot`, `FinalReviewDecision` 같은 schema를 만든다.
- Streamlit helper가 직접 session state와 registry를 뒤섞는 부분을 service function으로 조금씩 이동한다.

좋은 첫 대상:

- `SelectedPortfolioSnapshot`
- `FinalReviewDecision read model`
- `EvidencePack`

완료 조건:

- Streamlit이 기존 화면을 유지하면서도 service function을 호출한다.
- 같은 result를 JSON으로 dump/load할 수 있다.
- 단위 테스트에서 Streamlit 없이 결과 contract를 검증할 수 있다.

### Step 2. Read-Only API

목표:

- FastAPI 또는 내부 API adapter로 read-only endpoint를 만든다.

추천 endpoint:

```text
GET /health
GET /selected-portfolios
GET /selected-portfolios/{selection_id}
GET /final-reviews/{decision_id}
GET /runs/{run_id}
```

주의:

- 처음부터 write API를 열지 않는다.
- registry write path는 기존 Streamlit workflow에 둔다.

### Step 3. Next.js Pilot

목표:

- Next.js로 selected portfolio dashboard를 read-only로 구현한다.

포함:

- selected portfolio picker
- snapshot summary
- performance recheck chart
- review signals
- why selected / evidence
- audit source link

제외:

- account connection
- broker order
- auto rebalance
- final decision write

완료 조건:

- 같은 selected decision을 Streamlit과 Next.js에서 같은 값으로 볼 수 있다.
- URL로 특정 selection을 다시 열 수 있다.
- chart/table UX가 Streamlit 대비 실제로 나아졌는지 비교 가능하다.

### Step 4. Job API

목표:

- backtest / validation replay / ingestion을 job model로 확장한다.

이 단계부터 필요한 것:

- job id
- status
- progress
- error kind
- artifact id
- retry/cancel semantics

### Step 5. Migration Decision

Step 3, 4 이후에 다음을 판단한다.

| Decision | Criteria |
| --- | --- |
| More Next.js screens | read-only pilot이 UX와 유지보수에서 분명히 이득 |
| Stay mostly Streamlit | 사용자가 내부 연구자 위주이고 product polish 요구가 낮음 |
| Dash Enterprise/Dash compare | Python-only production path가 비용 대비 매력적 |
| Full frontend migration | API contracts가 충분히 안정화되고 write workflow까지 옮길 근거가 생김 |

## Architecture Sketch

```text
External data
  -> ingestion
  -> DB
  -> loaders
  -> finance engine / validation
  -> service contracts
       -> Streamlit internal console
       -> FastAPI read/write boundary
            -> Next.js product UI
```

## Suggested Phase Plan

| Phase | Name | Output |
| --- | --- | --- |
| Phase A | Service Contract Foundation | Pydantic/read model, Streamlit-compatible service calls |
| Phase B | Read-Only API | FastAPI app with health and selected/final review endpoints |
| Phase C | Next.js Pilot | read-only selected dashboard |
| Phase D | Job Model | backtest/validation job API and status UI |
| Phase E | Product UI Expansion | final review report, run report, chart-heavy comparison |

## Decision Rules

Proceed with React/Next.js when:

- 화면이 shareable URL, rich chart, responsive layout, or external user polish를 요구한다.
- 같은 data contract를 여러 client가 읽어야 한다.
- UI state가 Streamlit session state를 넘어 persistent review state가 되어야 한다.

Keep Streamlit when:

- Python 개발자가 빠르게 실험하는 내부 도구다.
- provider/DB/admin/debug 기능이다.
- 화면 품질보다 iteration speed가 중요하다.

Avoid for now:

- 전체 Streamlit UI rewrite
- Streamlit custom component에 product frontend를 과도하게 넣는 방식
- broker/live trading UI
- auth/multi-user부터 시작하는 방식

## Final Recommendation

2단계 리서치의 결론은 React/Next.js 도입 가능성이 높다는 것이다. 다만 즉시 "UI를 React로 갈아엎기"가 아니라, "Python engine과 Streamlit workflow에서 API-ready contract를 추출하고 read-only product surface로 검증하기"가 맞다.

가장 먼저 만들 기능은 `API/service contract extraction + Selected Portfolio Dashboard read-only pilot`이다. 이 조합은 현재 프로젝트 강점인 Final Review / Selected Dashboard를 살리면서도, 상용화 UI로 갈 수 있는지 가장 작고 현실적인 단위로 검증한다.

## 2026-05-19 Refocused Recommendation

### Updated One-Line Recommendation

다음 개발 방향은 `Next.js 도입`이 아니라 `UI-engine service boundary 확립`이다. Streamlit은 내부 console로 유지하고, `app/services`에 Streamlit 없는 backtest / validation / selected portfolio contract를 먼저 만든 뒤, 그 contract 위에서 Streamlit UI와 future API/Next.js UI를 나란히 붙인다.

### Why This Is The Right First Move

사용자가 말한 문제의 핵심은 "UI와 엔진이 모두 Python으로 되어 있다"가 아니다. 문제는 `app/web` 안에서 화면 렌더링, `st.session_state`, runtime dispatch, registry write/read, validation 계산 일부가 같은 파일 흐름으로 움직인다는 점이다.

현재 구조는 full rewrite보다 boundary extraction에 적합하다.

```text
Now:
app/web Streamlit screen
  -> app/web helper/runtime
  -> finance loaders/engine/strategy/performance
  -> JSONL registry/session state

Target:
app/web Streamlit screen
  -> app/services contract layer
  -> finance loaders/engine/strategy/performance
  -> versioned read/write models

Optional later:
app/api FastAPI
  -> app/services contract layer

frontend Next.js
  -> app/api or local JSON fixture
```

### Recommended Immediate Build: Boundary Phase A

Phase A should be a narrow implementation task, not a frontend migration.

| Step | Build | Owner Skill | Output |
| --- | --- | --- | --- |
| A1 | Backtest execution service extraction | `finance-backtest-web-workflow` + integration review | `app/services/backtest_execution.py`, service result object, Streamlit runner calls service |
| A2 | Minimal contract tests | `finance-integration-review` for closeout | service imports without Streamlit, error categories stable, result JSON-compatible |
| A3 | Practical Validation helper split plan | `finance-backtest-web-workflow` | identify pure diagnostics vs UI handoff functions |
| A4 | Selected Portfolio read model contract | `finance-backtest-web-workflow` | selected snapshot/evidence object usable by Streamlit and future API |

### First Implementation Slice

Start with `Backtest execution service extraction`.

Why:

- It directly addresses the user's "백테스트 로직과 UI를 분리" goal.
- It avoids starting with React/Next.js before the backend contract exists.
- It gives future A/B agent split a real contract:
  - A agent can change Streamlit/React screen behavior.
  - B agent can change backtest runtime internals.
  - Integration owner checks service tests and schema compatibility.

The first slice should not change product behavior. It should only move responsibility.

```text
Before:
app/web/backtest_single_runner.py
  - renders payload
  - opens spinner
  - dispatches strategy runtime
  - normalizes errors
  - writes st.session_state
  - appends history

After:
app/services/backtest_execution.py
  - dispatches strategy runtime
  - normalizes errors
  - returns BacktestExecutionResult

app/web/backtest_single_runner.py
  - renders payload/spinner
  - calls service
  - writes session state
  - appends history for now
```

History append can move later. Moving everything at once would make the first step too large.

### Development Direction After Phase A

| Order | Direction | Rationale |
| --- | --- | --- |
| 1 | Service contract foundation | 멀티에이전트 개발 경계의 기반 |
| 2 | Validation/read model cleanup | Practical Validation과 Final Review evidence를 공통 object로 만들기 |
| 3 | Read-only FastAPI endpoints | HTTP boundary는 service가 안정된 뒤 얇게 추가 |
| 4 | Read-only product UI pilot | Selected Portfolio Dashboard 또는 Final Review Evidence Viewer |
| 5 | Job model | ingestion/backtest/validation replay의 progress/retry/cancel 모델 |

### What To Avoid Now

- Full Streamlit rewrite.
- Next.js project부터 만들기.
- FastAPI server부터 만들고 내부 service contract를 나중에 생각하기.
- `app/web/runtime/backtest.py`를 곧바로 public API처럼 노출하기.
- live trading, broker order, auto rebalance scope 추가.

### Decision To Ask The Human Next

다음 구현으로 승인받을 범위는 아래 하나가 가장 적절하다.

```text
UI-Engine Boundary Phase A:
Backtest single-run dispatch를 app/services/backtest_execution.py로 분리하고,
Streamlit 화면 동작은 유지한 채 service contract와 최소 테스트를 만든다.
```

이 작업이 끝나면 이후 멀티에이전트 분담이 훨씬 명확해진다.
