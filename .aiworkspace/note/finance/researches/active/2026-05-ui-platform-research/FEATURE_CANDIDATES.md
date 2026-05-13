# Feature Candidates

Scoring: 1 low, 5 high. `Priority`는 지금 시작할 순서다.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | API/service contract extraction | 5 | 3 | 3 | 5 | 5 | 바로 시작 |
| P0 | Streamlit retained as internal console | 4 | 1 | 1 | 5 | 5 | 정책으로 확정 |
| P1 | Read-only Next.js pilot for Selected Portfolio Dashboard | 4 | 4 | 3 | 4 | 5 | API contract 이후 |
| P1 | EvidencePack / RunArtifact schema | 5 | 3 | 3 | 4 | 5 | API와 함께 |
| P2 | Job-oriented backtest/validation execution API | 4 | 4 | 4 | 4 | 4 | pilot 이후 |
| P2 | Chart-ready data contracts | 4 | 3 | 3 | 4 | 4 | dashboard pilot과 병행 |
| P2 | Final Review shareable report viewer | 4 | 3 | 2 | 4 | 5 | read-only surface로 좋음 |
| P3 | Strategy visual editor | 4 | 5 | 4 | 3 | 3 | 나중 |
| P3 | Auth / multi-user review workflow | 4 | 5 | 4 | 3 | 3 | productization 시점 |
| Park | Full Streamlit rewrite to Next.js | 5 | 5 | 5 | 3 | 2 | 지금은 하지 않음 |
| Park | Live trading / broker order UI | 5 | 5 | 5 | 5 | 1 | scope 밖 |

## P0. API / Service Contract Extraction

Goal:

- 기존 Streamlit 화면이 호출하는 runtime/helper logic을 UI-independent service contract로 정리한다.
- Python engine은 그대로 두고 request/response schema를 만든다.

First contract candidates:

| Contract | Existing source candidate |
| --- | --- |
| BacktestRunRequest / BacktestRunResult | `app/web/runtime/backtest.py` |
| PracticalValidationRequest / PracticalValidationResult | `app/web/backtest_practical_validation_helpers.py`, runtime replay modules |
| FinalReviewDecision | `app/web/runtime/final_selection_decisions.py` |
| SelectedPortfolioSnapshot | `app/web/runtime/final_selected_portfolios.py` |
| RegistryReadModel | `app/web/runtime/*`, `.aiworkspace/note/finance/registries/*.jsonl` |

Why now:

- UI migration의 전제 조건이다.
- Streamlit 유지에도 이득이 있다. session state와 helper call이 줄고 test가 쉬워진다.

Success criteria:

- Streamlit page가 service function을 통해 결과를 받는다.
- 같은 service function을 CLI/test/FastAPI에서 호출할 수 있다.
- 최소 1개 read-only result contract가 JSON 직렬화 가능하다.

## P0. Streamlit Internal Console Policy

Goal:

- Streamlit을 폐기하지 않고 내부 연구/운영 콘솔로 명확히 정의한다.

Keep in Streamlit:

- ingestion status
- DB/provider admin
- internal backtest experiment
- registry inspection
- operations review
- debugging panels

Move candidates:

- selected portfolio dashboard
- final review report viewer
- polished backtest run report
- chart-heavy comparison screen

Why now:

- "React로 갈까?"를 rewrite 논쟁이 아니라 화면별 역할 분리로 바꾼다.

## P1. Read-Only Next.js Pilot

Recommended pilot:

1. `Selected Portfolio Dashboard` read-only view
2. Alternative: `Final Review Evidence Viewer`

Why Selected Portfolio Dashboard:

- Final Review 이후 결과를 읽는 화면이라 write risk가 낮다.
- product-facing dashboard 느낌을 가장 잘 검증할 수 있다.
- live trading / broker order와 명확히 분리되어 있다.

Minimum pilot:

- Next.js page 하나
- FastAPI endpoint 또는 local JSON mock
- selected decision list
- selected portfolio snapshot
- performance recheck chart
- monitoring signals
- source/evidence link

Out of scope for pilot:

- login
- account connection
- broker order
- auto rebalance
- all Streamlit page migration

## P1. EvidencePack / RunArtifact Schema

Goal:

- Final Review, Selected Dashboard, report viewer가 같은 evidence object를 읽게 한다.

Fields:

- ids: run_id, validation_id, decision_id, selection_id
- source: strategy name, universe, timeframe, data source freshness
- performance: CAGR, Sharpe, drawdown, benchmark spread
- practical validation: liquidity, holdings, macro/stress/sensitivity, missing data
- decision: select/hold/reject/re-review and reason
- warnings: bias risk, stale data, incomplete evidence
- artifacts: report path, registry row reference, chart series ids

Why now:

- 이 프로젝트의 차별점인 evidence-first를 API/UI 공통 언어로 승격한다.

## P2. Job-Oriented Execution API

Goal:

- backtest, ingestion, validation replay를 job으로 모델링한다.

Potential endpoints:

```text
POST /jobs/backtests
POST /jobs/validations
GET /jobs/{job_id}
GET /runs/{run_id}
GET /validations/{validation_id}
```

Why later:

- job queue는 service contract 이후에 넣어야 한다.
- 먼저 read-only surface로 API shape를 검증하는 편이 안전하다.

## P2. Chart-Ready Data Contracts

Goal:

- frontend chart library와 무관한 series contract를 만든다.

Contracts:

- time series: date, value, label
- drawdown series
- allocation timeline
- benchmark comparison
- event markers
- diagnostics table

Why:

- TradingView, Plotly, ECharts, Recharts 중 무엇을 쓰든 backend contract가 안정적이면 교체 가능하다.

## P2. Final Review Shareable Report Viewer

Goal:

- Final Review 결과를 공유 가능한 read-only report로 만든다.

Why:

- 이 프로젝트는 "왜 이 후보를 골랐는가"가 핵심이다.
- report viewer는 상용 UI polish 효과가 크고 write 위험이 낮다.

## P3. Strategy Visual Editor

Goal:

- Composer류처럼 universe, factor, condition, weighting, guardrail을 시각적으로 편집한다.

Why later:

- 현재 strategy/input model을 먼저 계약화해야 한다.
- 시각 편집기는 UX scope가 크고 engine assumptions를 쉽게 깨뜨릴 수 있다.

## Parking Lot. Full Rewrite

Full Streamlit rewrite는 지금 추천하지 않는다.

Reasons:

- 현재 workflow가 넓고 registry/state 경계가 복잡하다.
- read-only surface로 충분히 learning을 얻을 수 있다.
- full rewrite는 quant 기능 개발을 장기간 멈추게 만들 가능성이 높다.

## Parking Lot. Live Trading

live trading, broker order, auto rebalance는 현재 product direction과 문서 규칙상 scope 밖이다. UI가 좋아져도 Final Review와 Selected Dashboard는 decision support와 monitoring으로 유지한다.
