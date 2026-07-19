# Architecture Notes

Status: Active
Last Verified: 2026-07-08

## Current Architecture

```text
External Sources
  -> finance/data/*
  -> finance/data/db/*
  -> finance/loaders/*
  -> finance/engine.py / strategy.py / transform.py / swing.py
  -> app/runtime/*
  -> app/services/*
  -> app/web Streamlit UI
```

Layer ownership과 storage / surface boundary를 먼저 판정해야 하면 [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)를 기준으로 한다.

## Layer Responsibilities

| Layer | Responsibility |
|---|---|
| Data Collection | yfinance, issuer pages, NYSE, EDGAR, FRED 등에서 데이터 수집 |
| Persistence | MySQL table schema와 UPSERT 기반 저장 |
| Loader | DB 데이터를 runtime / validation이 읽을 수 있는 형태로 변환 |
| Strategy Runtime | 전략 계산, 리밸런싱, 성과 curve 생성 |
| App Runtime | UI payload와 strategy runtime / registry / saved setup 연결 |
| App Services | Streamlit-free execution dispatch, read model, error normalization, evidence interpretation |
| Streamlit UI | 사용자가 시장 context 확인, 후보 생성, 검증, 최종 판단, 운영 대시보드를 사용하는 화면 |

## Architecture Rules

- UI에서 provider / FRED를 직접 fetch하지 않는다.
- 수집은 `finance/data/*`와 `app/jobs/ingestion_jobs.py`를 통해 수행한다. `Workspace > Overview`의 bounded refresh는 `app/jobs/overview_actions.py` facade를 통해서만 이 경계를 넘는다.
- Practical Validation은 loader를 통해 provider context를 읽는다.
- Overview Sentiment / Futures / Why It Moved도 context surface로 유지하고, validation gate나 trading signal로 승격하지 않는다.
- JSONL registry에는 full raw provider response를 저장하지 않는다.
- full holdings, macro series, raw-ish provider row는 DB에 둔다.
- live approval, broker order, auto rebalance는 현재 architecture 범위 밖이다.

## Current Surface Notes

- `Workspace > Overview`의 current primary tabs는 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events`다. Market Context visible path는 Shiller/S&P index earnings/SEP/SPX-SPY DB evidence를 읽는 React S&P 500 valuation surface다. `Futures Monitor`와 `Sector / Industry` standalone tab은 current primary surface가 아니며, 선물/sector evidence는 Futures Macro와 Market Movers가 읽는다.
- Futures Macro의 Streamlit-free 계산 경계는 `app/services/futures_macro_pattern.py`와 `app/services/futures_macro_pattern_validation.py`다. 전자는 stored daily candle의 point-in-time 1D / 5D / 20D feature와 현재 regime / transition을 만들고, 후자는 as-of volatility, 독립 episode spacing, chronological Brier / calibration publication gate와 stepwise 2D analog-path error / baseline / middle-50% coverage를 계산한다. 공개 경로는 현재 좌표에 유사 episode의 표준화된 중앙 이동을 더한 5D / 20D 조건부 경로이며, probability와 path status 중 더 보수적인 상태를 사용한다. Streamlit helper는 DB/provider 계산을 소유하지 않고 finite-number payload 연결, unavailable suppression, refresh dispatch, native fallback만 담당한다.
- Backtest strict Quality / Value family는 statement shadow factor path와 `PIT Monthly Snapshot Universe`를 visible contract로 사용한다. Static Managed Research / Historical Dynamic PIT는 saved payload와 old run replay compatibility path다.
- Practical Validation은 5-flow 화면으로 읽고, Flow 3은 검증 결론, Flow 4는 카테고리별 검증 결과와 해결 guide를 소유한다. Flow 3 / Flow 4는 Final Review 전용 `REVIEW` metadata를 현재 보강해야 할 문제처럼 노출하지 않는다.

## Decision Notes

중요한 설계 결정을 새로 만들 때는 필요하면 `architecture/decisions/ADR-XXXX.md` 형태로 추가한다.
아직 이 재구성 단계에서는 기존 긴 결정 문서를 모두 옮기지 않는다.

## Detailed Maps

| Need | Document |
|---|---|
| layer / storage / product surface 경계 판정 | [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md) |
| 어떤 script가 어떤 책임을 갖는지 빠르게 확인 | [SCRIPT_STRUCTURE_MAP.md](./SCRIPT_STRUCTURE_MAP.md) |
| UI payload에서 strategy runtime과 result bundle까지의 흐름 확인 | [BACKTEST_RUNTIME_FLOW.md](./BACKTEST_RUNTIME_FLOW.md) |
| data collection, DB persistence, loader read path 확인 | [DATA_DB_PIPELINE_FLOW.md](./DATA_DB_PIPELINE_FLOW.md) |
| 새 strategy family 추가 / 변경 절차 확인 | [STRATEGY_IMPLEMENTATION_FLOW.md](./STRATEGY_IMPLEMENTATION_FLOW.md) |
