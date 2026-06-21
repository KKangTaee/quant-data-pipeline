# Finance Project Map

Status: Active
Last Verified: 2026-06-21

## Project Summary

`finance`는 MySQL-backed data ingestion, market context dashboard, strategy backtest runtime, Practical Validation / Final Review evidence workflow, Operations Portfolio Monitoring을 함께 가진 quant research workspace다.

현재 merged product map은 네 경계를 특히 중요하게 본다.

- Data / macro / sentiment / futures는 `finance/data/* -> MySQL -> finance/loaders/*` 흐름을 유지한다.
- Backtest strategy engine과 daily swing research lane은 `finance/*`, `app/runtime/*`, `app/services/*`가 소유하고, Streamlit UI는 payload / render / session state에 집중한다.
- Practical Validation / Final Review / Portfolio Monitoring은 compact evidence와 read-only service model을 공유하되, approval / broker / auto rebalance 경계는 넘지 않는다.
- Overview의 Sentiment, Futures Monitor, Why It Moved는 context / investigation surface이며 validation gate나 monitoring signal을 만들지 않는다.

## Top-Level Structure

| Path | Responsibility |
|---|---|
| `finance/data/` | 외부 데이터 수집, ETF provider snapshot, FRED macro 수집 |
| `finance/data/db/` | MySQL schema definition과 DB helper |
| `finance/loaders/` | DB 데이터를 backtest / validation runtime 입력으로 읽는 loader |
| `finance/engine.py` | strategy orchestration |
| `finance/strategy.py` | portfolio simulation / rebalancing logic |
| `finance/swing.py` | short-term swing strategy simulation / scanner logic |
| `finance/transform.py` | signal, factor, ranking transform |
| `finance/performance.py` | 성과 요약과 portfolio performance metric |
| `finance/indicators.py` | reusable indicator helpers such as simple rolling ATR / True Range |
| `finance/swing_macro.py` | Risk-On Momentum 5D macro hard filter / ranking penalty evaluation |
| `finance/swing_analysis.py` | Risk-On Momentum 5D comparison, sensitivity, stability, trade-cause, quality warning analysis |
| `app/services/` | Streamlit-free application service boundary. UI에서 runtime / engine을 직접 호출하기 전에 use-case 단위 dispatch와 error normalization을 담당 |
| `app/runtime/` | Streamlit-free runtime / repository boundary. DB-backed backtest wrapper, JSONL registry / saved setup helper, selected portfolio runtime model |
| `app/workspace_paths.py` | active worktree root와 canonical `.aiworkspace/note/finance` JSONL / docs / artifact 경로 상수 |
| `app/web/` | Streamlit Finance Console 화면, form, session state, routing, user feedback |
| `app/jobs/` | Ingestion console에서 실행하는 job wrapper |
| `tests/` | service contract와 workflow helper 회귀 검증을 위한 focused Python tests |
| `.aiworkspace/` | AI / Codex 작업 문서와 plugin source의 top-level workspace |
| `.aiworkspace/note/finance/docs/` | 장기 프로젝트 지식 |
| `.aiworkspace/note/finance/researches/` | 제품 방향, 벤치마킹, 기능 후보 리서치 산출물 |
| `.aiworkspace/note/finance/reports/backtests/` | backtest 결과 report, 전략 hub, 후보 근거, validation report |
| `.aiworkspace/note/finance/tasks/active/` | 실행 task 기록과 retained completed work record. current active 판정은 `STATUS_MANIFEST.md` / README / roadmap을 먼저 본다 |
| `.aiworkspace/note/finance/phases/active/` | phase 단위 계획과 retained board 기록. current active phase 판정은 `STATUS_MANIFEST.md` / README / roadmap을 먼저 본다 |
| `.aiworkspace/note/finance/registries/` | workflow JSONL registry |
| `.aiworkspace/note/finance/saved/` | reusable saved portfolio setup |
| `.aiworkspace/plugins/quant-finance-workflow/` | repo-local finance Codex skill / helper script source |

## Main Entry Points

| Area | Entry Point |
|---|---|
| Finance Console shell / navigation | `app/web/streamlit_app.py` |
| Workspace > Ingestion console | `app/web/ingestion_console.py` |
| Workspace > Ingestion read-only diagnostics service | `app/services/ingestion_diagnostics.py` |
| Finance workspace path constants | `app/workspace_paths.py` |
| Backtest page | `app/web/pages/backtest.py` |
| Single Backtest execution service | `app/services/backtest_execution.py` |
| Manual Compare execution service | `app/services/backtest_compare_execution.py` |
| Compare runner catalog service | `app/services/backtest_compare_catalog.py` |
| Backtest result read model service | `app/services/backtest_result_read_model.py` |
| Weighted portfolio builder service | `app/services/backtest_weighted_portfolio.py` |
| Saved portfolio replay service | `app/services/backtest_saved_portfolio_replay.py` |
| Reference contextual help service | `app/services/reference_contextual_help.py` |
| Reference contextual help renderer | `app/web/reference_contextual_help.py` |
| Backtest Compare visual components | `app/web/backtest_compare_components.py` |
| Practical Validation service | `app/services/backtest_practical_validation.py`; includes Practical Validation result build wrapper, source/result registry append, provider gap collection orchestration, and surface-aware read-only CNN / AAII market sentiment context overlay |
| Practical Validation source/profile/selection-history service helper | `app/services/backtest_practical_validation_source.py` |
| Practical Validation curve service helper | `app/services/backtest_practical_validation_curve.py` |
| Practical Validation curve context service helper | `app/services/backtest_practical_validation_curve_context.py` |
| Practical Validation stress/sensitivity service helper | `app/services/backtest_practical_validation_stress_sensitivity.py` |
| Backtest temporal validation service | `app/services/backtest_temporal_validation.py` |
| Practical Validation provider context service helper | `app/services/backtest_practical_validation_provider_context.py` |
| Practical Validation module gate service | `app/services/backtest_practical_validation_modules.py` |
| Practical Validation board map service | `app/services/backtest_practical_validation_board_registry.py` |
| Construction risk audit service | `app/services/backtest_construction_risk_audit.py` |
| Risk contribution audit service | `app/services/backtest_risk_contribution_audit.py` |
| Component role / weight audit service | `app/services/backtest_component_role_weight_audit.py` |
| Practical Validation efficacy audit service | `app/services/backtest_validation_efficacy.py` |
| Data coverage audit service | `app/services/backtest_data_coverage_audit.py` |
| Backtest realism audit service | `app/services/backtest_realism_audit.py` |
| Backtest evidence read model service | `app/services/backtest_evidence_read_model.py` |
| Overview market intelligence service | `app/services/overview_market_intelligence.py` |
| Overview historical analog service | `app/services/overview_market_context_analog.py`; sector leadership -> sector ETF proxy -> SPY-relative historical distribution read model. Supports selected as-of bounded replay and 5D / 20D / monthly pattern windows using existing DB prices plus current universe / sector metadata. Latest mode can receive the visible Market Context daily sector leadership snapshot from `app/web/overview_dashboard_helpers.py`, so the analog anchor sector matches the sector pressure map; selected as-of still loads a selected-date daily sector snapshot. `pattern_window` changes the similarity window, not the sector leadership source. The read model exposes requested vs effective as-of alignment, limiting symbols, basis warnings, and a bounded `overview_historical_analog_ohlcv` repair action when common daily price coverage is older than the selected date. `app/web/overview_dashboard.py` places historical analog controls immediately before the analog analysis flow and renders stale-basis / insufficient-coverage repair actions through the existing Overview action facade. `app/web/overview_ui_components.py` renders the broad result as compact basis summary, collapsed calculation-boundary detail, method line, summary strip, and a core 5D / 20D / 60D matrix across sector ETF / SPY / QQQ / TLT / GLD, with raw detail tables collapsed; matrix cell color intensity follows median return direction and magnitude. Default guide blocks such as `먼저 볼 점`, `주의할 점`, and separate market-background summary should not be reintroduced. Macro comparison remains a separate compact section and is hidden when broad analog rows are unavailable. The Macro section separates `Sector ETF vs SPY relative strength` as the broad basis from additional GLD / Rate Pressure futures conditions, then shows broad-vs-conditioned deltas, current Macro backdrop, and collapsed raw detail. 3차-A adds an additive `macro_conditioned_analog` pilot using GLD price proxy context; 3차-B adds one stored futures daily OHLCV Rate Pressure proxy condition using `ZN=F` / `ZB=F`; 3차-C adds `macro_dimension_audit` for stored FRED `T10Y3M` / `VIXCLS` / `BAA10Y` current backdrop / bucket preview and event / sentiment annotation or deferred status. FRED rates / events / sentiment hard conditioning remain disabled or excluded |
| Overview Macro Context Cockpit read model | `app/services/overview_market_intelligence.py` via `build_overview_macro_context_cockpit`; rendered by `app/web/overview_ui_components.py` and loaded through `app/web/overview_dashboard_helpers.py`. `brief_rows` is the user-facing Market Context brief sequence for movement, breadth, and Futures/Macro backdrop, with an optional `market_session` basis payload supplied by `app/web/overview_dashboard.py` from the existing NYSE session helper. During open trading the brief can be `오늘의 시장 브리프`; during weekends / holidays it becomes `마지막 거래일 시장 브리프` and uses the previous trading date as basis. The sector pressure map normalizes provider sector aliases into the canonical 11 display sectors and should render all 11 as equal tiles; value and color, not tile size or omission, communicate pressure. Sector pressure return values render with two decimals. Events remain in event timeline / source evidence / compatibility findings unless a future approved cause-analysis dimension changes that boundary. `refresh_plan` maps current resolvable or partially resolvable data issues to bounded Overview action ids, while non-actionable caveats and closed-session intraday elapsed-age stale states stay excluded; full Market Context refresh remains a secondary fallback. Top `자료 상태` should count actionable refresh items, not Events reference caveats or Data Health management meta. `context_findings` / `next_checks` remain compatibility payloads and should not be rendered as a default user-facing action checklist |
| Overview Events / Macro Week read model | `app/services/overview_market_intelligence.py` via `build_market_events_snapshot` and `build_overview_macro_week_lane`; rendered by `app/web/overview_dashboard.py` and `app/web/overview_ui_components.py`. Event context reads recent 7D plus upcoming rows and prioritizes FOMC / CPI / PPI / Employment / GDP over earnings for scan surfaces |
| Overview Data Health Ingestion Handoff read model | `app/services/overview_market_intelligence.py` via `build_overview_data_health_ingestion_handoff`; rendered by `app/web/overview_ui_components.py` and loaded through `app/web/overview_dashboard_helpers.py` for `Workspace > Overview > Data Health` |
| Overview Source Confidence Catalog read model | `app/services/overview_market_intelligence.py` via `build_overview_source_confidence_catalog`; embedded in the macro cockpit model and rendered by `app/web/overview_ui_components.py`. It exposes `source_role`, `actionability`, and `counts_for_status` so direct brief sources, reference limitations, and management meta are separated. Events estimate caveats are `참고 제한`; Data Health is `관리 메타`; only actionable source rows count as unresolved `자료 확인 필요` |
| Overview IA Closeout guide | `app/web/overview_dashboard_helpers.py` via `load_overview_ia_closeout_model`; rendered by `app/web/overview_ui_components.py` inside the first `Workspace > Overview > Market Context` tab with the cockpit |
| Overview futures monitor service | `app/services/futures_market_monitoring.py` |
| Overview futures macro thermometer service | `app/services/futures_macro_thermometer.py` |
| Overview futures macro historical validation service | `app/services/futures_macro_validation.py` |
| Overview market intelligence ingestion | `finance/data/market_intelligence.py` |
| Overview futures monitor ingestion | `finance/data/futures_market.py` |
| Overview market sentiment ingestion | `finance/data/sentiment.py` |
| Overview bounded refresh action facade | `app/jobs/overview_actions.py` |
| Backtest Analysis | `app/web/backtest_analysis.py`; includes contextual Reference help entry point |
| Practical Validation | `app/web/backtest_practical_validation.py`; includes contextual Reference help entry point |
| Practical Validation UI components | `app/web/backtest_practical_validation_components.py` |
| Final Review | `app/web/backtest_final_review.py`; includes contextual Reference help entry point |
| Final Review UI components | `app/web/backtest_final_review_components.py` |
| Operations Overview | `app/web/operations_overview.py`; includes contextual Reference help entry point |
| Operations > Portfolio Monitoring | `app/web/final_selected_portfolio_dashboard.py` legacy implementation route; includes contextual Reference help entry point |
| Ingestion jobs | `app/jobs/ingestion_jobs.py` |
| Overview scheduled refresh automation | `app/jobs/overview_automation.py` |
| DB schema | `finance/data/db/schema.py` |
| SEC Form 25 delisting collector | `finance/data/sec_delisting.py` |
| SEC CIK / ticker exchange crosscheck collector | `finance/data/sec_company_tickers.py` |
| Nasdaq Symbol Directory snapshot collector | `finance/data/symbol_directory.py` |
| Computed snapshot lifecycle collector | `finance/data/computed_lifecycle.py` |
| ETF provider ingestion | `finance/data/etf_provider.py` |
| Macro ingestion | `finance/data/macro.py` |
| Market sentiment loader | `finance/loaders/sentiment.py` |
| Futures OHLCV loader | `finance/loaders/futures.py` |
| Risk-On Momentum 5D strategy core | `finance/swing.py`, `finance/indicators.py`, `finance/swing_macro.py`, `finance/swing_analysis.py` |
| Risk-On Momentum 5D DB runtime | `app/runtime/backtest_risk_on_momentum.py`; compatibility export remains in `app/runtime/backtest.py` |
| Backtest real-money / readiness runtime helpers | `app/runtime/backtest_real_money.py`; compatibility exports remain in `app/runtime/backtest.py` |
| Backtest strict quality / value runtime wrappers | `app/runtime/backtest_strict.py`; compatibility exports remain in `app/runtime/backtest.py` |
| Backtest result bundle runtime helper | `app/runtime/backtest_result_bundle.py` |
| Service contract tests | `tests/test_service_contracts.py` |

## Practical Validation Core Files

| File | Responsibility |
|---|---|
| `app/services/backtest_practical_validation.py` | Streamlit-free Practical Validation result build wrapper, source/result registry append, Practical Validation / Final Review handoff contract, provider gap row / collection plan / ingestion job orchestration, and surface-aware read-only CNN / AAII sentiment overlay read model for Practical Validation, Final Review, and Portfolio Monitoring. The sentiment overlay is market context only and does not affect gate / PASS-BLOCKER / monitoring signal / registry / saved setup / live trading boundaries |
| `app/services/backtest_practical_validation_source.py` | Streamlit-free validation profile / selection source builder / source component table / compact selection history helper |
| `app/services/backtest_practical_validation_curve_context.py` | Streamlit-free compact curve snapshot, result curve normalize, DB price proxy curve, component curve combination, window perturbation / monthly returns helper |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | Streamlit-free rolling validation, stress window, baseline challenge, sensitivity interpretation, correlation risk, market context, overfit audit, Robustness Lab board helper |
| `app/services/backtest_temporal_validation.py` | Streamlit-free benchmark-aligned temporal validation helper. Walk-forward rolling excess return, OOS holdout excess / deterioration, macro regime split excess / drawdown gap, curve / macro source strength, and compact storage boundary evidence를 만든다 |
| `app/services/backtest_practical_validation_diagnostics.py` | Streamlit-free Practical Validation diagnostics orchestration, component context assembly, 12개 diagnostic result 생성, public compatibility export |
| `app/services/backtest_practical_validation_replay.py` | Streamlit-free Practical Validation replay service. source를 최신 DB 데이터 기준으로 다시 실행하거나 저장 기간 그대로 재현해 component / portfolio curve evidence와 replay selection history snapshot을 생성 |
| `app/services/backtest_practical_validation_curve.py` | Streamlit-free curve normalize, provenance, benchmark parity helper |
| `app/services/backtest_practical_validation_provider_context.py` | Streamlit-free provider / macro loader output to compact coverage, provenance, freshness, diagnostic evidence, and look-through board context adapter |
| `app/services/backtest_practical_validation_modules.py` | Streamlit-free source traits / validation module planner. source kind, component mix, strategy keys, profile, input checks, diagnostics, and audit rows를 읽어 필수 / 조건부 / 후속 참고 module, gate effect, gate reason, Final Review 이동 gate를 만들고 evidence board mapping을 붙인다 |
| `app/services/backtest_practical_validation_board_registry.py` | Streamlit-free Practical Validation board registry. `Final Review Gate`, audit board, provider board, Robustness Lab 같은 화면 보드를 validation module과 연결하고 적용 / 비적용 board map을 만든다 |
| `app/services/backtest_construction_risk_audit.py` | Streamlit-free construction risk audit read model. Existing component weight, provider look-through coverage, top holding, holdings overlap, dominant asset, and unknown exposure evidence를 읽어 concentration / overlap / exposure risk를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_risk_contribution_audit.py` | Streamlit-free risk contribution audit read model. Existing component return matrix, pairwise correlation, max risk contribution proxy, drop-one dependency, and storage boundary evidence를 읽어 risk contribution construction risk를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_component_role_weight_audit.py` | Streamlit-free component role / weight audit read model. Existing proposal role, target weight, validation profile, role concentration, profile intent, weight reason, and storage boundary evidence를 읽어 role / weight discipline risk를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_validation_efficacy.py` | Streamlit-free validation efficacy audit read model. Existing compact evidence를 읽어 runtime replay, period coverage, benchmark parity, walk-forward temporal validation, OOS holdout validation, regime split validation, provider freshness, robustness, PIT / look-ahead, survivorship / universe, execution / storage boundary gap을 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_data_coverage_audit.py` | Streamlit-free data coverage audit read model. DB price window summary, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 compact `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_realism_audit.py` | Streamlit-free backtest realism audit read model. Existing result metadata와 compact validation evidence를 읽어 transaction cost, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary gap을 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/web/backtest_practical_validation.py` | Practical Validation UI render, Step 1 source strategy / construction / selection history display, profile input, latest replay button, current-session replay display policy, 7-step boundary, Control Center, CNN / AAII market sentiment context overlay, Fix Queue, summary-first evidence workspace, look-through board, Robustness Lab board, Provider Action Center, save-only audit copy, provider gap / replay service result session state handoff |
| `app/web/backtest_practical_validation_components.py` | Practical Validation 전용 product shell / CSS helper. Command Center, section header, card grid, step rail, alert panel을 담당하며 검증 로직이나 저장 계약은 포함하지 않는다 |
| `finance/data/etf_provider.py` | ETF source map discovery, operability / holdings / exposure snapshot 수집과 저장 |
| `finance/loaders/provider.py` | ETF provider snapshot read path |
| `finance/data/macro.py` | FRED macro series 수집 |
| `finance/loaders/macro.py` | macro market-context read path |
| `finance/data/sentiment.py` | CNN Fear & Greed / AAII sentiment 수집 |
| `finance/loaders/sentiment.py` | Overview market sentiment read path |

## Final Review / Selected Portfolio Evidence Files

| File | Responsibility |
|---|---|
| `app/services/backtest_evidence_read_model.py` | Streamlit-free final decision status, Final Review candidate board priority / decision cockpit / decision record guide / saved decision review read models, investability evidence packet / profile-aware gate policy snapshot / selected-route gate, saved decision table rows, shared evidence check rows, decision dossier markdown read model and selected decision source consistency contract. Validation Efficacy row-level walk-forward / OOS / regime gaps and Construction Risk / Risk Contribution / Component Role / Weight non-PASS rows feed selected-route gate evidence |
| `app/web/backtest_final_review.py` | Final Review screen render, Decision Desk command center / flow ordering, read-only CNN / AAII market sentiment context overlay, Practical Validation Gate-passed Candidate Board with review priority / queue / primary reason, selected-source Decision Cockpit, hidden blocked validation count, selection-only final decision input with decision record checklist / selected-route guide, Evidence Appendix for investability packet / look-through / Robustness Lab / previous validation evidence, saved final decision review ledger with route filter and detail tabs, Selected Dashboard handoff summary, decision dossier download |
| `app/web/backtest_final_review_components.py` | Final Review 전용 visual shell. Command center, flow rail, section header, lane grid, action panel CSS / HTML helper를 제공하며 service/gate/persistence 로직은 포함하지 않는다 |
| `app/web/backtest_final_review_helpers.py` | Final Review source eligibility filter, validation reuse, paper observation snapshot, investability packet wiring, selection-only official save row construction |
| `app/web/operations_overview.py` | Operations Console landing page render와 Streamlit-free read model. selected dashboard summary, monitoring portfolio setup, run health를 읽어 Portfolio Monitoring Status summary, Evidence Health mini strip, priority / evidence ordered review queue, Portfolio Monitoring / System Data Health primary lane, no-live boundary를 표시 |
| `app/web/final_selected_portfolio_dashboard.py` | `Operations > Portfolio Monitoring` screen render. Legacy file name은 Selected Portfolio Dashboard를 유지한다. Read-only CNN / AAII market sentiment context overlay를 화면 진입부에 표시하고, Active Portfolio Monitoring Scenario hero / empty-not-configured-run state handling / value curve / strategy performance / rebalance summary를 먼저 보여준다. Portfolio card shelf 생성 / 선택 / collapsed portfolio management soft delete / portfolio name-description edit / Final Review selected strategy slot compact board / 설정 적용 / 제거 / strategy-board 아래 pending-stale scenario update를 관리한다. 선택한 1개 전략의 lazy Monitoring Scenario detail, continuity / Monitoring Signals / Open Issues / optional preflight / allocation monitoring / Decision Dossier / 하단 evidence detail을 read-only로 렌더링한다 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Dashboard portfolio / selected strategy pool / strategy slot / strategy comparison table, Selected Dashboard handoff table, component / continuity / timeline / recheck preflight / recheck readiness / symbol freshness / provider evidence policy / review signal policy / open issue follow-up / deployment readiness / recheck comparison / drift / alert / allocation boundary / source contract display helpers |
| `app/runtime/final_selected_portfolios.py` | Read-only selected portfolio dashboard runtime model, dashboard portfolio saved state and backward-compatible strategy slot helper, Final Review -> Selected Dashboard handoff review and continuity check, selected decision source consistency contract, open issue follow-up, deployment readiness preflight, performance recheck operations preflight, readiness, symbol freshness, selected provider evidence staleness / coverage policy, review signal policy, performance recheck, recheck comparison, drift check, alert preview, allocation drift evidence boundary, monitoring timeline |

## Backtest Workflow Boundary

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

역할:

- Backtest Analysis는 후보 source를 만든다.
- Practical Validation은 source를 실전 투입 전 조건으로 검증하고 source traits 기반 module planner로 필수 / 조건부 / 후속 참고 검증과 Final Review 이동 gate를 만든다. Step 1은 source의 단일 / mix 구성, component 전략, target weight, 원래 result table, monthly selection / holdings history를 먼저 확인하게 한다. 화면의 `Final Review Gate`, audit board, provider board, Robustness Lab은 board registry를 통해 어떤 module의 evidence인지 표시하며, 후보 특성상 적용되지 않는 조건부 board는 비적용으로 분리한다. `검증 결과 저장(기록용)`은 audit trail만 남기고, Gate 미통과 result는 Final Review 후보가 아니다.
- Final Review는 Practical Validation Gate를 통과한 result만 source picker에 표시한다. Provider / Look-through / Robustness Lab / Construction Risk / Risk Contribution / Component Role Weight / Validation Efficacy / Data Coverage / Backtest Realism 근거와 investability packet을 읽어 profile-aware gate policy로 selected-route 가능 여부를 판정한다. Validation Efficacy의 walk-forward / OOS / regime non-PASS row와 Construction Risk / Risk Contribution / Component Role / Weight non-PASS row도 selected-route blocker 또는 review-required 근거로 표시하고, selected-route gate까지 통과한 후보만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 정식 저장한다. 보류 / 거절 / 재검토는 새 저장 row가 아니라 상태 안내이며, 저장된 선정 기록은 read-only dossier와 Selected Dashboard handoff summary로 다시 보여준다.
- Operations Console은 Operations의 입구로, Portfolio Monitoring Status summary와 Evidence Health mini strip을 먼저 보여준 뒤 priority / evidence / metric 기반 review queue와 Portfolio Monitoring / System Data Health primary lane을 둔다. Summary는 active portfolio, assigned strategy, stale / pending scenario metadata, blocked / missing / incomplete slot, open review, target snapshot, next review를 읽기 전용으로 요약한다. Evidence Health는 scenario freshness, selected evidence readiness, open review, system run health를 이미 로드된 selected dashboard / monitoring portfolio setup / run history payload에서만 요약하며 provider DB 세부 조회나 새 수집을 실행하지 않는다. Review queue는 setup blocker, system run failure, scenario freshness, open review, routine monitoring, no-selected-row guidance를 sort rank로 정렬하지만 job 실행 / registry write / scenario replay는 만들지 않는다. Archive / development-history decision table은 운영 화면에 노출하지 않으며, Backtest Run History / Candidate Library 데이터와 helper code 삭제는 별도 audit 전까지 하지 않는다. 기존 Selected Portfolio Dashboard route는 `Portfolio Monitoring` navigation label 아래 유지된다. Portfolio Monitoring 화면은 Active Portfolio Monitoring Scenario를 상단 hero로 먼저 보여주며, active portfolio가 없으면 생성 안내를, portfolio가 있지만 전략이 없으면 strategy board 안내를, 전략은 있지만 scenario가 없으면 아래 `포트폴리오 시나리오 업데이트` 실행 안내를 보여준다. Scenario 결과가 있으면 portfolio-wide 현재 가치 / 손익 / 수익률 / CAGR / MDD / 기준일 / session update timestamp / value curve / 전략별 성과 / target snapshot을 상단에서 확인한다. Portfolio card shelf는 hero 아래 active selector로 두고, portfolio 이름 / 설명 edit, Final Review selected strategy slot board, start / latest-end mode / balance / memo 저장, pending-stale scenario update action은 그 아래 관리 영역에 둔다. Scenario 결과는 portfolio / slot / selected decision / start / end / balance signature가 맞을 때만 합산한다. 리밸런싱 표는 `Target Snapshot Date`, `Next Review Date`, `Current Target Snapshot`으로 표시되며 주문 지시나 자동 리밸런싱이 아니다. 개별 strategy Monitoring Scenario와 read-only recheck readiness / symbol freshness / provider evidence / continuity / timeline / review signal / open issue / optional deployment preflight / allocation boundary는 사용자가 선택한 1개 전략 상세를 열 때만 렌더링한다. Deployment Readiness preflight도 승인 / 주문 / broker-account 연동 / 자동 리밸런싱을 만들지 않는다.

## Data Boundary

| Data | Location | Commit Policy |
|---|---|---|
| Current / candidate / final decision registries | `.aiworkspace/note/finance/registries/*.jsonl` | 명시 요청 없이는 새 runtime 생성물 커밋 금지. 저장 경계는 `docs/data/STORAGE_GOVERNANCE.md` 기준 |
| Saved portfolio setup | `.aiworkspace/note/finance/saved/*.jsonl` | 보존 대상. validation / approval record가 아니라 reusable setup. `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`은 Operations > Portfolio Monitoring의 사용자 monitoring portfolio setup이며 legacy dashboard file name을 유지한다 |
| Backtest result reports | `.aiworkspace/note/finance/reports/backtests/` | 사람이 읽는 결과/근거 문서. JSONL source-of-truth 대체 금지 |
| Backtest run history | `.aiworkspace/note/finance/run_history/*.jsonl` | local runtime artifact, 보통 커밋 금지 |
| Backtest generated artifacts | `.aiworkspace/note/finance/backtest_artifacts/` | full scanner / trade detail 같은 generated artifact, 보통 커밋 금지 |
| Run artifacts | `.aiworkspace/note/finance/run_artifacts/` | local runtime artifact, 보통 커밋 금지 |
| Playwright output | `.playwright-mcp/` | generated artifact, 커밋 금지 |

Code resolves these paths through `app/workspace_paths.py`; app/runtime and app/jobs should not recreate legacy `.note/finance` paths directly.

## Where To Look

| Situation | Start Here |
|---|---|
| Overview macro context cockpit / historical analog / market movers / Why It Moved / sector leadership / futures monitor / sentiment 수정 | `app/jobs/overview_actions.py`, `app/services/overview_market_intelligence.py`, `app/services/overview_market_context_analog.py`, `app/services/futures_market_monitoring.py`, `app/services/futures_macro_thermometer.py`, `app/services/futures_macro_validation.py`, `finance/data/sentiment.py`, `finance/loaders/sentiment.py`, `app/web/overview_dashboard.py`, `app/web/overview_dashboard_helpers.py`, `app/web/overview_ui_components.py` |
| S&P 500 / Nasdaq-listed universe, intraday snapshot, market event calendar 수정 | `finance/data/market_intelligence.py`, `finance/data/symbol_directory.py`, `finance/data/db/schema.py`, `app/jobs/ingestion_jobs.py`, `app/jobs/overview_actions.py`, `app/services/overview_market_intelligence.py` |
| Overview 자동 수집 cadence / cron / launchd runner 수정 | `app/jobs/overview_automation.py`, `app/jobs/overview_actions.py`, `app/jobs/run_history.py`, `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` |
| Backtest UI 수정 | `app/web/pages/backtest.py`, 관련 `app/web/backtest_*.py`; Compare visual shell은 `app/web/backtest_compare_components.py` |
| Risk-On Momentum 5D 수정 | `finance/swing.py`, `finance/indicators.py`, `finance/swing_macro.py`, `finance/swing_analysis.py`, `finance/transform.py`, `finance/loaders/futures.py`, `app/runtime/backtest_risk_on_momentum.py`, `app/runtime/backtest.py` compatibility facade, `app/web/backtest_single_forms.py`, `app/web/backtest_result_display.py` |
| Backtest real-money / guardrail / deployment readiness helper 수정 | `app/runtime/backtest_real_money.py`, `app/runtime/backtest.py` compatibility facade, `app/web/backtest_common.py`, `app/web/backtest_result_display.py`, `app/web/backtest_history_helpers.py`, related `app/services/backtest_*` replay / execution callers |
| Strict quality / value / quality-value runtime wrapper 수정 | `app/runtime/backtest_strict.py`, `app/runtime/backtest.py` compatibility facade, `finance/loaders/factors.py`, `finance/loaders/financial_statements.py`, `app/services/backtest_execution.py`, `app/services/backtest_compare_catalog.py`, `app/web/backtest_single_forms.py` |
| UI-engine boundary 수정 | `app/services/*`, 호출하는 `app/web/backtest_*.py`, 관련 `app/runtime/*` |
| Service contract 회귀 검증 | `tests/test_service_contracts.py`, `.aiworkspace/note/finance/docs/runbooks/README.md` |
| Practical Validation P2 수정 | `app/web/backtest_practical_validation*.py`, `finance/data/etf_provider.py`, `finance/loaders/provider.py`, `finance/data/macro.py`, `finance/loaders/macro.py` |
| DB schema 변경 | `finance/data/db/schema.py` |
| Ingestion page / job UI 변경 | `app/web/ingestion_console.py`, `app/services/ingestion_diagnostics.py`, `app/jobs/ingestion_jobs.py`, `finance/data/*` |
| Strategy runtime 변경 | `finance/engine.py`, `finance/strategy.py`, `finance/transform.py`, `finance/performance.py` |
| 제품 방향 / 벤치마킹 리서치 | `.aiworkspace/note/finance/researches/README.md`, `.aiworkspace/note/finance/researches/active/<research-id>/` |
| Backtest report 작성 / 정리 | `.aiworkspace/note/finance/reports/backtests/INDEX.md` |
| 문서 / AI workspace 체계 변경 | `.aiworkspace/note/finance/tasks/active/doc-system-rebuild/`, `.aiworkspace/note/finance/tasks/active/ai-workspace-migration/` |

## Detailed Documentation Maps

| Need | Start Here |
|---|---|
| layer / storage / UI-engine 경계 판정 | `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md` |
| script별 책임 지도 | `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` |
| backtest runtime / result bundle 흐름 | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` |
| data / DB / loader 코드 흐름 | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` |
| Backtest UI / Final Review / Portfolio Monitoring 화면 흐름 | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` |
| Portfolio Selection 사용자 흐름 | `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` |
| helper script / automation 사용법 | `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md` |
