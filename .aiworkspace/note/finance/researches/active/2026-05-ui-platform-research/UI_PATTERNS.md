# UI And Workflow Patterns

## Pattern 1. Keep Python Engine, Add API Contract

현재 구조에서 가장 중요한 패턴은 engine과 UI를 분리하는 것이다.

```text
Current:
Streamlit UI -> app/web helpers/runtime -> finance engine/loaders/DB

Recommended:
Streamlit internal console -> service contract -> finance engine/loaders/DB
Next.js product UI      -> service contract -> finance engine/loaders/DB
```

API contract는 처음부터 public REST product일 필요가 없다. 먼저 Python 내부 service function과 Pydantic model로 시작하고, 그 위에 FastAPI를 얹을 수 있게 만든다.

## Pattern 2. Read-Only Product Surface First

처음부터 Backtest Analysis 전체를 Next.js로 다시 만들면 위험이 크다. 더 좋은 pilot은 read-only 또는 low-write 화면이다.

후보:

| Candidate screen | Why good as pilot |
| --- | --- |
| Selected Portfolio Dashboard | Final Review 결과를 읽고 monitoring view를 보여주는 성격이라 write risk가 낮다 |
| Final Review Evidence Viewer | validation evidence, robustness, decision history를 보기 좋게 표현할 수 있다 |
| Backtest Run Report Viewer | run artifact를 chart/table로 보여주는 read-only product surface다 |

## Pattern 3. Job-Oriented UX

Backtest, ingestion, practical validation replay는 job으로 표현하는 것이 제품적으로 자연스럽다.

필요한 상태:

| State | Meaning |
| --- | --- |
| queued | 요청은 접수됐지만 아직 실행 전 |
| running | 실행 중, progress/log summary 표시 |
| succeeded | artifact / result id 생성 |
| failed | error kind, retry 가능 여부, missing data 표시 |
| cancelled | 사용자가 중단 |
| stale | source data나 parameter가 바뀌어 결과 재검증 필요 |

Streamlit에서도 일부 흉내낼 수 있지만, API + frontend로 분리하면 job status polling, progress panel, notification, retry UI를 훨씬 안정적으로 만들 수 있다.

## Pattern 4. Evidence Object As First-Class UI Model

현재 프로젝트의 차별점은 evidence-first다. 이것을 화면별 ad hoc display가 아니라 공통 evidence object로 만들면 API와 React UI 모두에 도움이 된다.

예시 contract:

```text
EvidencePack
  source
  run_id
  strategy_snapshot
  validation_summary
  robustness_summary
  practical_constraints
  decision_context
  warnings
  links_to_artifacts
```

이 contract는 Final Review, Selected Dashboard, reports/backtests, future frontend가 함께 사용할 수 있다.

## Pattern 5. Strategy Builder Is Visual, Engine Is Strict

Composer류 제품은 strategy logic을 visual/no-code 형태로 보여준다. finance 프로젝트가 이 영역을 따라가려면 engine logic은 엄격하게 유지하고, UI에는 다음을 보여주는 식이 적합하다.

| UI object | User-facing meaning |
| --- | --- |
| universe | 어떤 후보군에서 고르는가 |
| signal / factor | 어떤 기준으로 순위를 매기는가 |
| weighting | 동일비중, inverse volatility, custom weight 등 |
| guardrail | trend filter, drawdown guardrail, liquidity filter 등 |
| rebalance | 언제 다시 구성하는가 |
| evidence | 이 설정이 왜 통과/보류/거절됐는가 |

## Pattern 6. Streamlit As Control Plane

Streamlit은 없애는 것이 아니라 control plane으로 남기는 편이 좋다.

Streamlit에 남길 화면:

- ingestion/admin 상태
- registry inspection
- research-only strategy trial
- internal QA / debug page
- ops review

React/Next.js로 옮길 화면:

- external-facing selected portfolio review
- shareable final decision report
- polished backtest report
- chart-heavy comparison view
- future collaboration/review screen

## Pattern 7. Chart Component Layer

금융 UI는 chart와 table 품질이 전체 인상을 결정한다. Next.js/React 도입 시 chart library를 한 번에 결정하기보다 data contract를 먼저 만든다.

필요한 contract:

| Contract | Purpose |
| --- | --- |
| equity curve series | performance chart |
| drawdown series | risk chart |
| holdings timeline | allocation history |
| benchmark comparison | relative performance |
| validation diagnostic table | Practical Validation summary |
| event marks | rebalance, guardrail breach, validation fail |

TradingView Advanced Charts는 price/technical analysis에는 강하지만, portfolio/evidence chart는 Plotly/Recharts/ECharts 등과 비교가 필요하다. 이 리서치에서는 library 확정이 아니라 JS chart-ready contract를 우선 추천한다.

## Pattern 8. Deep Links And Stable Review URLs

상용화에 가까운 workflow에서는 사용자가 특정 결과를 다시 열 수 있어야 한다.

필요한 URL model:

```text
/runs/{run_id}
/candidates/{candidate_id}
/validations/{validation_id}
/final-reviews/{decision_id}
/selected-portfolios/{selection_id}
```

Streamlit session state 중심 구조에서는 이 패턴이 약하다. API + Next.js route는 이 부분을 자연스럽게 해결한다.

## Pattern 9. Agent-Oriented Ownership Boundary

이번 refocus에서 가장 중요한 패턴은 "화면과 엔진을 다른 agent가 안전하게 수정할 수 있는 경계"다. 같은 Python 안에서도 아래처럼 소유권을 나누면 된다.

```text
Agent A: UI / product surface
  app/web/*.py
  future frontend/*

Agent B: engine / data / backtest logic
  finance/*
  finance/loaders/*
  finance/data/*
  app/jobs/*

Shared contract / integration owner:
  app/services/*
  app/api/*
  versioned schemas and read models
```

이 경계가 의미 있으려면 규칙이 필요하다.

| Rule | Why |
| --- | --- |
| UI renderer files do not call `finance.*` directly except through approved service functions | UI agent가 engine internals를 몰라도 화면을 바꿀 수 있다 |
| `app/services/*` has no `streamlit` import | engine/API/test/Next.js가 같은 service를 쓸 수 있다 |
| Strategy runtime dispatch lives outside Streamlit runners | 새 strategy 추가 시 UI switch문을 계속 늘리지 않는다 |
| Registry read/write is wrapped by versioned read models | JSONL source-of-truth는 유지하되 UI별 ad hoc parsing을 줄인다 |
| Session state stores UI convenience only, not canonical product state | reload/deep link/API/replay가 가능해진다 |

## Pattern 10. Service First, API Later

FastAPI는 좋은 후보지만, 첫 단계에서 서버를 띄울 필요는 없다. 먼저 Python service function이 Streamlit 없이 호출되고 JSON 직렬화 가능한 결과를 반환해야 한다.

권장 순서:

```text
1. app/services/backtest_service.py
   - BacktestRunRequest
   - BacktestRunResult
   - run_backtest(request)

2. app/services/selection_service.py
   - SelectedPortfolioSnapshot
   - EvidencePack
   - load_selected_snapshot(selection_id)

3. app/api/*
   - FastAPI read-only endpoints
   - service layer를 얇게 감싸는 HTTP boundary

4. frontend/*
   - Next.js / React read-only pilot
```

이렇게 가면 UI agent는 Streamlit 또는 React 화면을 맡고, engine agent는 `finance/*`와 service implementation을 맡으며, main/integration은 schema change와 compatibility를 확인할 수 있다.

## Pattern 11. Contract Tests As The Working Agreement

멀티에이전트 개발에서 가장 중요한 산출물은 문서만이 아니라 contract test다.

필요한 테스트:

| Contract | Test |
| --- | --- |
| BacktestRunRequest / Result | minimal payload가 Streamlit 없이 실행되거나, 데이터 부족 시 typed error로 실패한다 |
| EvidencePack | Final Review / Practical Validation / Selected Dashboard가 같은 id와 evidence summary를 읽는다 |
| Registry read model | append-only JSONL의 old row와 new row를 모두 읽는다 |
| Chart series contract | equity curve / drawdown / benchmark series가 JSON 직렬화된다 |

이 테스트가 있으면 A agent가 UI를 바꿔도 B agent의 engine 계약을 깨뜨렸는지 바로 확인할 수 있다.
