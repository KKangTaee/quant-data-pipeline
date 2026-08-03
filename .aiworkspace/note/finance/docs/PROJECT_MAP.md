# Finance Project Map

Status: Active
Last Verified: 2026-08-03

## System At A Glance

`finance`는 Python domain/runtime과 Streamlit application shell, React +
TypeScript workbench를 결합한 DB-backed quant research workspace다.

```text
External Sources
  -> finance/data
  -> MySQL
  -> finance/loaders
  -> finance domain / app services / app runtime
  -> Streamlit route and command boundary
  -> React workbench or Streamlit fallback

Workflow decisions and reusable setup
  <-> append-only / preserved JSONL stores
```

핵심 방향은 `Ingestion -> DB -> Loader / Service -> Runtime -> UI`다. UI에서
provider를 직접 조회하지 않으며 React가 validation, Final Review decision이나
canonical persistence를 독자적으로 계산하지 않는다.

## Layer Ownership

| Layer | Main Path | Responsibility |
|---|---|---|
| Data collection | `finance/data/` | 외부 source adapter, 원천 정규화와 MySQL write |
| DB schema / client | `finance/data/db/` | MySQL schema와 connection / transaction helper |
| Loader | `finance/loaders/` | 기준일·coverage를 반영한 DB read path |
| Domain transform | `finance/transform.py` | signal, factor, ranking과 preprocessing |
| Strategy simulation | `finance/strategy.py` | portfolio simulation과 rebalance logic |
| Strategy orchestration | `finance/engine.py` | transform, strategy와 result 실행 orchestration |
| Performance | `finance/performance.py` | return, drawdown과 portfolio performance metric |
| App jobs | `app/jobs/` | ingestion과 bounded background / manual job orchestration |
| App services | `app/services/` | Streamlit-free use case, read model, command, evidence interpretation |
| App runtime | `app/runtime/` | backtest runner, result bundle과 workflow store boundary |
| Streamlit web | `app/web/` | navigation, page adapter, session, server command와 React bridge |
| React workbench | `app/web/streamlit_components/`, `app/web/components/` | local interaction, chart, responsive presentation과 explicit intent |
| Tests | `tests/` | domain, service, persistence와 UI-boundary regression contract |

### Repository Support Paths

| Path | Responsibility |
|---|---|
| `app/workspace_paths.py` | active worktree 기준 docs / registry / saved / artifact 경로 |
| `.aiworkspace/note/finance/docs/` | durable product, architecture, flow, data와 runbook |
| `.aiworkspace/note/finance/tasks/active/` | implementation / docs / QA task 기록 |
| `.aiworkspace/note/finance/phases/active/` | user-approved multi-task phase 통합 기록 |
| `.aiworkspace/note/finance/researches/active/` | product direction / benchmark / feature research |
| `.aiworkspace/note/finance/reports/backtests/` | 사람이 읽는 strategy / candidate / validation report |
| `.aiworkspace/note/finance/registries/` | append-only workflow records |
| `.aiworkspace/note/finance/saved/` | reusable user portfolio setup |

## Product Surface Entry Points

Top-level navigation과 route registration은 `app/web/streamlit_app.py`가 소유한다.

| Group / Surface | URL | Streamlit Entry | Primary Python Owner | React Presentation |
|---|---|---|---|---|
| Research / Today | `/` | `app/web/today_page.py` | `app/services/today.py`, `app/services/today_market_session.py`, `app/services/portfolio_monitoring/intraday_refresh.py` | `app/web/streamlit_components/today_workbench/` |
| Research / Market Research | `/overview` | `app/web/overview/page.py`, `app/web/overview/navigation.py` | `app/services/overview/`, related finance loaders and interpretation modules | `app/web/streamlit_components/market_research_navigation/` and view-owned workbenches |
| Research / Institutional Holdings | `/institutional-portfolios` | `app/web/institutional_portfolios.py` | `app/services/institutional_portfolios.py`, `finance/loaders/institutional_13f.py` | `app/web/streamlit_components/institutional_portfolios_workbench/` |
| Portfolio / Portfolio Lab | `/backtest` | `app/web/backtest_page.py`, `app/web/backtest_workflow_shell.py` | `app/services/backtest_workflow_shell.py`, `app/runtime/backtest/` and stage-owned services | `app/web/components/` under each Backtest stage |
| Portfolio / Portfolio Monitoring | `/selected-portfolio-dashboard` | `app/web/final_selected_portfolio_dashboard.py` | `app/services/portfolio_monitoring/`, `app/runtime/backtest/read_models/final_selected_portfolios.py` | `app/web/streamlit_components/portfolio_monitoring_workbench/` |
| Data / Data Operations | `/ingestion` | `app/web/ingestion_console.py`, `app/web/ingestion/` | `app/jobs/ingestion_jobs.py`, `app/services/ingestion_diagnostics.py`, `finance/data/` | Streamlit five-section task-oriented workbench; job results are Python-owned |
| Help / Reference Center | `/reference` | `app/web/reference_center.py` | `app/services/reference_center.py` | `app/web/streamlit_components/reference_center_workbench/` |

`app/web/overview_dashboard.py`와 일부 facade / fallback module은 기존 caller와 bundle
unavailable 상황을 위해 남아 있다. current 정상 화면의 owner는 위 표의 page,
service와 React workbench다.

## Workflow Ownership

### Inflation / Policy Yield Path (Functional Recovery Active)

```text
FRED/ALFRED + BEA + Federal Reserve SEP/FOMC + NY Fed ACM
  + verified FactSet Earnings Insight annual EPS vintages + stored ^GSPC prices
  -> app/jobs/inflation_policy_refresh.py
  -> finance_meta PIT tables
  -> finance/loaders/inflation_policy.py
  -> independent Core PCE / policy / yield / equity-stress engines
  -> inflation_policy_model_artifact / inflation_policy_snapshot
  -> app/services/overview/inflation_policy*.py
  -> Market Research > 경제 사이클 > 물가·정책 경로
```

- `finance/inflation_policy_catalog.py`와 `finance/data/fred_vintages.py`가 독립 26-series
  catalog와 공용 vintage transport를 소유한다.
- `finance/data/fomc_policy.py`, `bea_pce_components.py`,
  `nyfed_term_premium.py`가 익명 SEP/의결·선택 PCE breadth·기간 프리미엄 source를
  저장한다.
- `finance/data/spf_core_pce.py`는 Philadelphia Fed SPF current/next-year Core PCE
  Q4/Q4 확률 bin과 공식 release vintage를 저장하고, `finance/core_pce_q4.py`는 월간
  모델과 SPF를 chronological linear pool로 결합해 5상태·threshold 확률을 검증한다.
- `finance/data/factset_sp500_eps.py`는 FactSet 월별 보고서의 날짜·표 제목·연도·구조를
  fail-closed로 확인하고 current/next-calendar-year annual bottom-up EPS release vintage만
  저장한다. S&P 공식 actual quarterly workbook의 대체 source가 아니다.
- `finance/loaders/inflation_policy.py`는 `released_at <= as_of_at`인 DB row와 official
  macro row, 검증된 FactSet EPS release vintage, 저장된 `^GSPC` 가격을 DB에서만 읽고 과거 origin
  재구성에는 eligible 전체 vintage를 별도로 읽는다. 기존
  `economic_cycle_snapshot`/artifact/확률을 사용하지 않는다.
- `finance/inflation_policy_model.py`, `inflation_path.py`, `policy_path.py`,
  `policy_validation.py`, `joint_rate_paths.py`, `yield_resistance.py`,
  `inflation_policy_simulation.py`가 혼합형 Core PCE, 익명 SEP·실제 표결 policy marginal,
  시간순 정책 검증, empirical 공동 금리 경로, 동적 저항대와 순방향·역산 계산을 소유한다.
- `finance/inflation_policy_validation.py`와 `inflation_policy_pipeline.py`는 component별
  rolling-origin gate, exact-cutoff replay와 compact artifact/snapshot을 소유한다.
  1개월 Core PCE와 `core_pce_q4_linear_pool` artifact, 5개 다음 발표 scenario,
  정책·돌파·역산·equity 상태를 독립적으로 보존한다.
- `finance/inflation_policy_equity_stress.py`는 당시 공개된 annual 차년도 EPS, 가격·금리로
  year-end EPS×multiple panel을 만들고 label 공개시각 rolling-origin ridge, 세 baseline·
  과거 OOS 잔차 interval coverage 비교, paired residual과 사용자 AI EPS
  uplift/지수 수준 시나리오를 소유한다. production runner와 command는 versioned equity
  artifact와 별도 `joint_macro_paths`의 독립 `READY`를 함께 요구한다. model artifact에는
  불변 모델만, 현재 지수·EPS·시작금리는 snapshot `equity_json`에 두며, 검증된 EPS
  release vintage나 joint path가 없으면 Shiller로 대체하지 않고 equity만 `NOT_AVAILABLE`로 닫는다.
- `app/services/overview/inflation_policy.py`는 저장 snapshot과 PIT definition을
  `inflation_policy_v1` read model로 변환하고, `inflation_policy_commands.py`는
  USER 기준 저장과 exact READY artifact의 bounded rate/equity scenario만 실행한다.
- `app/web/overview/market_context_helpers.py`는 기존 cycle과 독립 payload를 렌더 직전에만
  합성하고 별도 nonce/cache를 소유한다. command result는 component transport 전에 다시
  JSON-safe하게 정규화한다. React workbench는 순방향·역산·조건부 S&P 500 stress·근거
  UI와 component별 `READY/LIMITED/NOT_AVAILABLE` 표현만 맡는다.

### Research Evidence

```text
Data Operations
  -> MySQL market / macro / statement / provider / 13F data
  -> finance loaders
  -> app/services/overview or app/services/institutional_portfolios.py
  -> Research surfaces
```

- Today는 저장된 Research evidence와 대표 Portfolio Monitoring projection을
  compact하게 조합한다.
- Market Research의 canonical 7-view normalization은
  `app/web/overview/navigation.py`가, 각 view 계산과 read model은 owning service가
  담당한다.
- Institutional Holdings의 SEC dataset과 identifier resolution은
  `finance/data/institutional_13f.py`와
  `finance/data/institutional_13f_mapping.py`가 저장하고 loader/service가 읽는다.
- Research context는 validation gate, trading signal이나 monitoring decision을
  만들지 않는다.

### Portfolio Selection

```text
Backtest Analysis
  -> candidate source
  -> Practical Validation
  -> Final Review decision
  -> Portfolio Monitoring handoff
```

| Stage | Main Owner |
|---|---|
| Backtest Analysis | `app/web/backtest_analysis.py`, `app/services/backtest_execution.py`, `app/runtime/backtest/` |
| Practical Validation | `app/web/backtest_practical_validation/`, `app/services/backtest_practical_validation_workspace.py`, `app/services/backtest_practical_validation_replay.py` |
| Final Review | `app/web/backtest_final_review/`, `app/services/backtest_final_review_policy.py`, `app/services/backtest_final_review_decision_brief.py` |
| Monitoring handoff | `app/runtime/backtest/stores/final_selection_decisions.py`, `app/services/portfolio_monitoring/decision_lifecycle.py` |

Practical Validation은 자료 보강을 pass로 간주하지 않고 재검증과 새 result를 요구한다.
Final Review에는 현재 gate를 충족한 validation만 selected-route 후보로 전달한다.
decision은 append-only record이며 broker order나 live approval이 아니다.

### Strategy Runtime

| Responsibility | Owner |
|---|---|
| runner catalog and compatibility facade | `app/runtime/backtest/runner_catalog.py`, `app/runtime/backtest/facade.py` |
| strategy-specific runtime adapters | `app/runtime/backtest/runners/` |
| result bundle | `app/runtime/backtest/result_bundle.py` |
| strategy transforms / simulation | `finance/transform.py`, `finance/strategy.py`, `finance/engine.py` |
| performance metrics | `finance/performance.py` |
| price / factor / statement inputs | `finance/loaders/price.py`, `finance/loaders/factors.py`, `finance/loaders/financial_statements.py` |

### Portfolio Monitoring

`app/services/portfolio_monitoring/`가 group/item command, position event, DB persistence,
cashflow-aware valuation, exposure, diagnosis, history, market chart와 read model을
분리해 소유한다. React는 group/item 선택, chart navigation과 form draft 같은 local
interaction을 담당하고 server write는 explicit command event로만 요청한다.

Today의 장중 대표 포트폴리오 overlay도 이 service의 DB-backed intraday refresh
경계를 재사용한다. historical EOD curve나 monitoring canonical state를 React가
변경하지 않는다.

### Data Operations

`app/web/ingestion_console.py`는 compatibility facade이며 active page body는
`app/web/ingestion/`에 있다. 사용자는 `데이터 준비 / 공식 파일 / 문제 복구 /
실행 이력 / 고급 도구` 순으로 진입하고, 기본 준비 화면은 Market Research,
Portfolio Lab, Institutional Holdings, Practical Validation 네 consumer workflow를
소유한다.

기존 active action 30개의 form과 dispatcher는 한 벌로 유지된다. 모든 write는
explicit click으로 시작하고 `app/jobs/ingestion_jobs.py`가 visible job boundary를,
collector와 DB persistence는 `finance/data/`가 소유한다. 실행 이력은 Data
Operations action의 상태·범위·결과·다음 행동만 요약하며 raw log, failure CSV,
full payload와 artifact path는 backend artifact로 보존하고 기본 제품 화면에서는
렌더링하지 않는다.

재무제표 active source는 EDGAR detailed statement와 statement shadow path다.
broader legacy yfinance fundamentals / factors action은 old replay compatibility
범위이며 current canonical financial statement refresh가 아니다.

## Data And Storage Boundaries

| Data | Canonical Location | Policy |
|---|---|---|
| universe, asset profile, macro, provider, event, 13F metadata | MySQL `finance_meta` | ingestion / loader boundary를 통해 사용 |
| price and volume history | MySQL `finance_price` | backtest와 monitoring의 canonical price source |
| raw filing, statement and derived factor | MySQL `finance_fundamental` | EDGAR statement shadow가 active financial source |
| candidate / validation / Final Review decision | `.aiworkspace/note/finance/registries/*.jsonl` | append-only workflow record |
| reusable portfolio / monitoring setup | `.aiworkspace/note/finance/saved/*.jsonl` | 사용자 설정으로 보존 |
| local run history | `.aiworkspace/note/finance/run_history/*.jsonl` | generated runtime record, 보통 commit하지 않음 |
| human-readable backtest evidence | `.aiworkspace/note/finance/reports/backtests/` | registry / saved source-of-truth를 대체하지 않음 |
| local job artifact | task별 local generated artifact directory | generated artifact, 보통 commit하지 않음 |

Full holdings, macro series와 raw provider response는 DB에 두고 workflow JSONL에는
compact evidence와 identity만 저장한다. 자세한 규칙은
[Storage Governance](./data/STORAGE_GOVERNANCE.md)를 따른다.

## Where To Start By Change Type

| Change | Start Here | Then Read |
|---|---|---|
| top navigation / route | `app/web/streamlit_app.py` | [Flows](./flows/README.md) |
| Today | `app/web/today_page.py`, `app/services/today.py` | [Today Intraday Flow](./flows/TODAY_PORTFOLIO_INTRADAY_FLOW.md) |
| Market Research | `app/web/overview/page.py`, `app/web/overview/navigation.py` | view owner under `app/services/overview/` |
| economic cycle / valuation | owning module under `finance/`, `finance/loaders/`, `app/services/overview/` | [Data Quality And PIT](./data/DATA_QUALITY_AND_PIT_NOTES.md) |
| inflation / policy / yield / equity stress | `app/jobs/inflation_policy_refresh.py`, `finance/loaders/inflation_policy.py`, `finance/inflation_policy_model.py`, `finance/inflation_policy_equity_stress.py`, `finance/inflation_policy_pipeline.py`, `app/services/overview/inflation_policy*.py` | [Inflation / Policy Engine Flow](./architecture/INFLATION_POLICY_ENGINE_FLOW.md), [Inflation / Policy Data Refresh](./runbooks/INFLATION_POLICY_DATA_REFRESH.md) |
| Institutional Holdings / 13F | `app/web/institutional_portfolios.py`, `app/services/institutional_portfolios.py` | [Institutional Flow](./flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md) |
| Backtest Analysis / strategy | `app/web/backtest_analysis.py`, `app/runtime/backtest/` | [Backtest Runtime](./architecture/BACKTEST_RUNTIME_FLOW.md), [Strategy Flow](./architecture/STRATEGY_IMPLEMENTATION_FLOW.md) |
| Practical Validation | `app/web/backtest_practical_validation/` | [Backtest UI Flow](./flows/BACKTEST_UI_FLOW.md) |
| Final Review | `app/web/backtest_final_review/` | [Portfolio Selection Flow](./flows/PORTFOLIO_SELECTION_FLOW.md) |
| Portfolio Monitoring | `app/services/portfolio_monitoring/` | [Command Center Architecture](./architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md), [Data Contract](./data/PORTFOLIO_MONITORING_DATA_CONTRACT.md) |
| ingestion / DB schema / loader | `app/jobs/ingestion_jobs.py`, `finance/data/db/schema.py` | [Data DB Pipeline](./architecture/DATA_DB_PIPELINE_FLOW.md), [DB Schema Map](./data/DB_SCHEMA_MAP.md) |
| Data Operations UI / action routing | `app/web/ingestion/` | [Finance Flows](./flows/README.md), [Runbooks](./runbooks/README.md) |
| Reference Center | `app/services/reference_center.py`, `app/web/reference_center.py` | [Glossary](./GLOSSARY.md) |
| automated / repeated operation | `app/jobs/` | [Runbooks](./runbooks/README.md) |

## Detailed Documentation

| Need | Document |
|---|---|
| layer / storage / product surface boundary | [System Boundaries](./architecture/SYSTEM_BOUNDARIES.md) |
| script-level responsibility | [Script Structure Map](./architecture/SCRIPT_STRUCTURE_MAP.md) |
| Backtest payload / runtime / result flow | [Backtest Runtime Flow](./architecture/BACKTEST_RUNTIME_FLOW.md) |
| ingestion / persistence / loader flow | [Data DB Pipeline Flow](./architecture/DATA_DB_PIPELINE_FLOW.md) |
| Core PCE / FOMC / dynamic-yield model and publication flow | [Inflation / Policy Engine Flow](./architecture/INFLATION_POLICY_ENGINE_FLOW.md) |
| top-level and detailed user flow | [Finance Flows](./flows/README.md) |
| Backtest stages and handoff | [Backtest UI Flow](./flows/BACKTEST_UI_FLOW.md) |
| portfolio selection lifecycle | [Portfolio Selection Flow](./flows/PORTFOLIO_SELECTION_FLOW.md) |
| data meaning and persistence | [Data Documentation](./data/README.md) |
| commands, ingestion and QA procedures | [Runbooks](./runbooks/README.md) |
