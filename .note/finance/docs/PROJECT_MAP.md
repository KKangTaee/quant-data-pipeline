# Finance Project Map

Status: Active
Last Verified: 2026-05-12

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
| `app/web/` | Streamlit Finance Console 화면과 runtime glue |
| `app/jobs/` | Ingestion console에서 실행하는 job wrapper |
| `.note/finance/docs/` | 장기 프로젝트 지식 |
| `.note/finance/tasks/active/` | 현재 실행 task 기록 |
| `.note/finance/phases/active/` | phase 단위 계획과 통합 기록 |
| `.note/finance/registries/` | workflow JSONL registry |
| `.note/finance/saved/` | reusable saved portfolio setup |

## Main Entry Points

| Area | Entry Point |
|---|---|
| Finance Console | `app/web/streamlit_app.py` |
| Backtest page | `app/web/pages/backtest.py` |
| Backtest Analysis | `app/web/backtest_analysis.py` |
| Practical Validation | `app/web/backtest_practical_validation.py` |
| Final Review | `app/web/backtest_final_review.py` |
| Selected Portfolio Dashboard | `app/web/final_selected_portfolio_dashboard.py` |
| Ingestion jobs | `app/jobs/ingestion_jobs.py` |
| DB schema | `finance/data/db/schema.py` |
| ETF provider ingestion | `finance/data/etf_provider.py` |
| Macro ingestion | `finance/data/macro.py` |

## Practical Validation Core Files

| File | Responsibility |
|---|---|
| `app/web/backtest_practical_validation.py` | Practical Validation UI render, profile input, recheck button, diagnostics board, provider gaps |
| `app/web/backtest_practical_validation_helpers.py` | 12개 diagnostic result 생성, validation profile, save / Final Review handoff |
| `app/web/backtest_practical_validation_connectors.py` | provider / macro loader output을 diagnostic evidence로 변환 |
| `app/web/backtest_practical_validation_replay.py` | source를 최신 DB 데이터 기준으로 다시 실행하거나 저장 기간 그대로 재현 |
| `app/web/backtest_practical_validation_curve.py` | curve normalize, provenance, benchmark parity |
| `finance/data/etf_provider.py` | ETF source map discovery, operability / holdings / exposure snapshot 수집과 저장 |
| `finance/loaders/provider.py` | ETF provider snapshot read path |
| `finance/data/macro.py` | FRED macro series 수집 |
| `finance/loaders/macro.py` | macro market-context read path |

## Backtest Workflow Boundary

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Selected Portfolio Dashboard
```

역할:

- Backtest Analysis는 후보 source를 만든다.
- Practical Validation은 source를 실전 투입 전 조건으로 검증한다.
- Final Review는 select / hold / reject / re-review 판단을 기록한다.
- Selected Portfolio Dashboard는 선정 이후 성과와 monitoring signal을 확인한다.

## Data Boundary

| Data | Location | Commit Policy |
|---|---|---|
| Current / candidate / final decision registries | `.note/finance/registries/*.jsonl` | 명시 요청 없이는 새 runtime 생성물 커밋 금지 |
| Saved portfolio setup | `.note/finance/saved/*.jsonl` | 보존 대상 |
| Backtest run history | `.note/finance/run_history/*.jsonl` | local runtime artifact, 보통 커밋 금지 |
| Run artifacts | `.note/finance/run_artifacts/` | local runtime artifact, 보통 커밋 금지 |
| Playwright output | `.playwright-mcp/` | generated artifact, 커밋 금지 |

## Where To Look

| Situation | Start Here |
|---|---|
| Backtest UI 수정 | `app/web/pages/backtest.py`, 관련 `app/web/backtest_*.py` |
| Practical Validation P2 수정 | `app/web/backtest_practical_validation*.py`, `finance/data/etf_provider.py`, `finance/loaders/provider.py`, `finance/data/macro.py`, `finance/loaders/macro.py` |
| DB schema 변경 | `finance/data/db/schema.py` |
| Ingestion job 변경 | `app/jobs/ingestion_jobs.py`, `finance/data/*` |
| Strategy runtime 변경 | `finance/engine.py`, `finance/strategy.py`, `finance/transform.py`, `finance/performance.py` |
| 문서 체계 변경 | `.note/finance/tasks/active/doc-system-rebuild/` |
