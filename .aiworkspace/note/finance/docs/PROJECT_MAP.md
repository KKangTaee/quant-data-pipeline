# Finance Project Map

Status: Active
Last Verified: 2026-05-29

## Project Summary

`finance`는 MySQL-backed data ingestion, strategy backtest runtime, Streamlit finance console, Practical Validation workflow를 함께 가진 quant research workspace다.

## Top-Level Structure

| Path | Responsibility |
|---|---|
| `finance/data/` | 외부 데이터 수집, ETF provider snapshot, FRED macro 수집 |
| `finance/data/db/` | MySQL schema definition과 DB helper |
| `finance/loaders/` | DB 데이터를 backtest / validation runtime 입력으로 읽는 loader |
| `finance/engine.py` | strategy orchestration |
| `finance/strategy.py` | portfolio simulation / rebalancing logic |
| `finance/transform.py` | signal, factor, ranking transform |
| `finance/performance.py` | 성과 요약과 portfolio performance metric |
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
| `.aiworkspace/note/finance/tasks/active/` | 현재 실행 task 기록 |
| `.aiworkspace/note/finance/phases/active/` | phase 단위 계획과 통합 기록 |
| `.aiworkspace/note/finance/registries/` | workflow JSONL registry |
| `.aiworkspace/note/finance/saved/` | reusable saved portfolio setup |
| `.aiworkspace/plugins/quant-finance-workflow/` | repo-local finance Codex skill / helper script source |

## Main Entry Points

| Area | Entry Point |
|---|---|
| Finance Console | `app/web/streamlit_app.py` |
| Finance workspace path constants | `app/workspace_paths.py` |
| Backtest page | `app/web/pages/backtest.py` |
| Single Backtest execution service | `app/services/backtest_execution.py` |
| Manual Compare execution service | `app/services/backtest_compare_execution.py` |
| Compare runner catalog service | `app/services/backtest_compare_catalog.py` |
| Backtest result read model service | `app/services/backtest_result_read_model.py` |
| Weighted portfolio builder service | `app/services/backtest_weighted_portfolio.py` |
| Saved portfolio replay service | `app/services/backtest_saved_portfolio_replay.py` |
| Practical Validation service | `app/services/backtest_practical_validation.py` |
| Practical Validation source/profile service helper | `app/services/backtest_practical_validation_source.py` |
| Practical Validation curve service helper | `app/services/backtest_practical_validation_curve.py` |
| Practical Validation curve context service helper | `app/services/backtest_practical_validation_curve_context.py` |
| Practical Validation stress/sensitivity service helper | `app/services/backtest_practical_validation_stress_sensitivity.py` |
| Backtest temporal validation service | `app/services/backtest_temporal_validation.py` |
| Practical Validation provider context service helper | `app/services/backtest_practical_validation_provider_context.py` |
| Practical Validation efficacy audit service | `app/services/backtest_validation_efficacy.py` |
| Data coverage audit service | `app/services/backtest_data_coverage_audit.py` |
| Backtest realism audit service | `app/services/backtest_realism_audit.py` |
| Backtest evidence read model service | `app/services/backtest_evidence_read_model.py` |
| Backtest Analysis | `app/web/backtest_analysis.py` |
| Practical Validation | `app/web/backtest_practical_validation.py` |
| Final Review | `app/web/backtest_final_review.py` |
| Selected Portfolio Dashboard | `app/web/final_selected_portfolio_dashboard.py` |
| Ingestion jobs | `app/jobs/ingestion_jobs.py` |
| DB schema | `finance/data/db/schema.py` |
| SEC Form 25 delisting collector | `finance/data/sec_delisting.py` |
| SEC CIK / ticker exchange crosscheck collector | `finance/data/sec_company_tickers.py` |
| Nasdaq Symbol Directory snapshot collector | `finance/data/symbol_directory.py` |
| Computed snapshot lifecycle collector | `finance/data/computed_lifecycle.py` |
| ETF provider ingestion | `finance/data/etf_provider.py` |
| Macro ingestion | `finance/data/macro.py` |
| Backtest result bundle runtime helper | `app/runtime/backtest_result_bundle.py` |
| Service contract tests | `tests/test_service_contracts.py` |

## Practical Validation Core Files

| File | Responsibility |
|---|---|
| `app/services/backtest_practical_validation.py` | Streamlit-free Practical Validation result build wrapper, source/result registry append, Practical Validation / Final Review handoff contract, provider gap row / collection plan / ingestion job orchestration |
| `app/services/backtest_practical_validation_source.py` | Streamlit-free validation profile / selection source builder / source component table helper |
| `app/services/backtest_practical_validation_curve_context.py` | Streamlit-free compact curve snapshot, result curve normalize, DB price proxy curve, component curve combination, window perturbation / monthly returns helper |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | Streamlit-free rolling validation, stress window, baseline challenge, sensitivity interpretation, correlation risk, market context, overfit audit, Robustness Lab board helper |
| `app/services/backtest_temporal_validation.py` | Streamlit-free benchmark-aligned temporal validation helper. Walk-forward rolling excess return, drawdown gap, curve source strength, and compact storage boundary evidence를 만든다 |
| `app/services/backtest_practical_validation_diagnostics.py` | Streamlit-free Practical Validation diagnostics orchestration, component context assembly, 12개 diagnostic result 생성, public compatibility export |
| `app/services/backtest_practical_validation_replay.py` | Streamlit-free Practical Validation replay service. source를 최신 DB 데이터 기준으로 다시 실행하거나 저장 기간 그대로 재현해 component / portfolio curve evidence 생성 |
| `app/services/backtest_practical_validation_curve.py` | Streamlit-free curve normalize, provenance, benchmark parity helper |
| `app/services/backtest_practical_validation_provider_context.py` | Streamlit-free provider / macro loader output to compact coverage, provenance, freshness, diagnostic evidence, and look-through board context adapter |
| `app/services/backtest_validation_efficacy.py` | Streamlit-free validation efficacy audit read model. Existing compact evidence를 읽어 runtime replay, period coverage, benchmark parity, walk-forward temporal validation, provider freshness, robustness, PIT / look-ahead, survivorship / universe, execution / storage boundary gap을 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_data_coverage_audit.py` | Streamlit-free data coverage audit read model. DB price window summary, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 compact `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/services/backtest_realism_audit.py` | Streamlit-free backtest realism audit read model. Existing result metadata와 compact validation evidence를 읽어 transaction cost, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary gap을 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 만든다 |
| `app/web/backtest_practical_validation.py` | Practical Validation UI render, profile input, recheck button, diagnostics board, look-through board, Robustness Lab board, provider gaps display, provider gap / replay service result session state handoff |
| `finance/data/etf_provider.py` | ETF source map discovery, operability / holdings / exposure snapshot 수집과 저장 |
| `finance/loaders/provider.py` | ETF provider snapshot read path |
| `finance/data/macro.py` | FRED macro series 수집 |
| `finance/loaders/macro.py` | macro market-context read path |

## Final Review / Selected Portfolio Evidence Files

| File | Responsibility |
|---|---|
| `app/services/backtest_evidence_read_model.py` | Streamlit-free final decision status, investability evidence packet / profile-aware gate policy snapshot / selected-route gate, saved decision table rows, shared evidence check rows, decision dossier markdown read model |
| `app/web/backtest_final_review.py` | Final Review screen render, investability packet display, look-through / Robustness Lab summary, final decision input, saved final decision review, decision dossier download |
| `app/web/backtest_final_review_helpers.py` | Final Review source selection, validation reuse, paper observation snapshot, investability packet wiring, save row construction |
| `app/web/final_selected_portfolio_dashboard.py` | Selected Portfolio Dashboard screen render, continuity check, Recheck Readiness, Symbol Freshness, Provider Evidence, Timeline / Review Signals / recheck comparison / allocation monitoring controls |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Dashboard table / component / continuity / timeline / recheck readiness / symbol freshness / provider evidence / recheck comparison / drift / alert display helpers |
| `app/runtime/final_selected_portfolios.py` | Read-only selected portfolio dashboard runtime model, Final Review -> Selected Dashboard continuity check, performance recheck readiness, symbol freshness, selected provider evidence, performance recheck, recheck comparison, drift check, alert preview, monitoring timeline |

## Backtest Workflow Boundary

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Selected Portfolio Dashboard
```

역할:

- Backtest Analysis는 후보 source를 만든다.
- Practical Validation은 source를 실전 투입 전 조건으로 검증하고 Provider / Look-through / Robustness Lab / Validation Efficacy / Data Coverage / Backtest Realism 근거를 compact하게 보여준다.
- Final Review는 Provider / Look-through / Robustness Lab / Validation Efficacy / Data Coverage / Backtest Realism 근거와 investability packet을 읽어 profile-aware gate policy로 selected-route 가능 여부를 판정하고, select / hold / reject / re-review 판단을 기록하며, 저장된 판단을 read-only dossier로 다시 보여준다.
- Selected Portfolio Dashboard는 선정 이후 성과와 read-only recheck readiness / symbol freshness / provider evidence / monitoring timeline / signal / recheck comparison을 확인한다.

## Data Boundary

| Data | Location | Commit Policy |
|---|---|---|
| Current / candidate / final decision registries | `.aiworkspace/note/finance/registries/*.jsonl` | 명시 요청 없이는 새 runtime 생성물 커밋 금지. 저장 경계는 `docs/data/STORAGE_GOVERNANCE.md` 기준 |
| Saved portfolio setup | `.aiworkspace/note/finance/saved/*.jsonl` | 보존 대상. validation / approval record가 아니라 reusable setup |
| Backtest result reports | `.aiworkspace/note/finance/reports/backtests/` | 사람이 읽는 결과/근거 문서. JSONL source-of-truth 대체 금지 |
| Backtest run history | `.aiworkspace/note/finance/run_history/*.jsonl` | local runtime artifact, 보통 커밋 금지 |
| Run artifacts | `.aiworkspace/note/finance/run_artifacts/` | local runtime artifact, 보통 커밋 금지 |
| Playwright output | `.playwright-mcp/` | generated artifact, 커밋 금지 |

Code resolves these paths through `app/workspace_paths.py`; app/runtime and app/jobs should not recreate legacy `.note/finance` paths directly.

## Where To Look

| Situation | Start Here |
|---|---|
| Backtest UI 수정 | `app/web/pages/backtest.py`, 관련 `app/web/backtest_*.py` |
| UI-engine boundary 수정 | `app/services/*`, 호출하는 `app/web/backtest_*.py`, 관련 `app/runtime/*` |
| Service contract 회귀 검증 | `tests/test_service_contracts.py`, `.aiworkspace/note/finance/docs/runbooks/README.md` |
| Practical Validation P2 수정 | `app/web/backtest_practical_validation*.py`, `finance/data/etf_provider.py`, `finance/loaders/provider.py`, `finance/data/macro.py`, `finance/loaders/macro.py` |
| DB schema 변경 | `finance/data/db/schema.py` |
| Ingestion job 변경 | `app/jobs/ingestion_jobs.py`, `finance/data/*` |
| Strategy runtime 변경 | `finance/engine.py`, `finance/strategy.py`, `finance/transform.py`, `finance/performance.py` |
| 제품 방향 / 벤치마킹 리서치 | `.aiworkspace/note/finance/researches/README.md`, `.aiworkspace/note/finance/researches/active/<research-id>/` |
| Backtest report 작성 / 정리 | `.aiworkspace/note/finance/reports/backtests/INDEX.md` |
| 문서 / AI workspace 체계 변경 | `.aiworkspace/note/finance/tasks/active/doc-system-rebuild/`, `.aiworkspace/note/finance/tasks/active/ai-workspace-migration/` |

## Detailed Documentation Maps

| Need | Start Here |
|---|---|
| script별 책임 지도 | `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` |
| backtest runtime / result bundle 흐름 | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` |
| data / DB / loader 코드 흐름 | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` |
| Backtest UI / Final Review / Selected Dashboard 화면 흐름 | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` |
| Portfolio Selection V2 사용자 흐름 | `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` |
| helper script / automation 사용법 | `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md` |
