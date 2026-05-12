# Architecture Notes

Status: Active
Last Verified: 2026-05-13

## Current Architecture

```text
External Sources
  -> finance/data/*
  -> finance/data/db/*
  -> finance/loaders/*
  -> finance/engine.py / strategy.py / transform.py
  -> app/web/runtime/*
  -> app/web Streamlit UI
```

## Layer Responsibilities

| Layer | Responsibility |
|---|---|
| Data Collection | yfinance, issuer pages, NYSE, EDGAR, FRED 등에서 데이터 수집 |
| Persistence | MySQL table schema와 UPSERT 기반 저장 |
| Loader | DB 데이터를 runtime / validation이 읽을 수 있는 형태로 변환 |
| Strategy Runtime | 전략 계산, 리밸런싱, 성과 curve 생성 |
| Web Runtime | UI payload와 strategy runtime / registry / saved setup 연결 |
| Streamlit UI | 사용자가 후보 생성, 검증, 최종 판단, 운영 대시보드를 사용하는 화면 |

## Architecture Rules

- UI에서 provider / FRED를 직접 fetch하지 않는다.
- 수집은 `finance/data/*`와 `app/jobs/ingestion_jobs.py`를 통해 수행한다.
- Practical Validation은 loader를 통해 provider context를 읽는다.
- JSONL registry에는 full raw provider response를 저장하지 않는다.
- full holdings, macro series, raw-ish provider row는 DB에 둔다.
- live approval, broker order, auto rebalance는 현재 architecture 범위 밖이다.

## Decision Notes

중요한 설계 결정을 새로 만들 때는 필요하면 `architecture/decisions/ADR-XXXX.md` 형태로 추가한다.
아직 이 재구성 단계에서는 기존 긴 결정 문서를 모두 옮기지 않는다.

## Detailed Maps

| Need | Document |
|---|---|
| 어떤 script가 어떤 책임을 갖는지 빠르게 확인 | [SCRIPT_STRUCTURE_MAP.md](./SCRIPT_STRUCTURE_MAP.md) |
| UI payload에서 strategy runtime과 result bundle까지의 흐름 확인 | [BACKTEST_RUNTIME_FLOW.md](./BACKTEST_RUNTIME_FLOW.md) |
| data collection, DB persistence, loader read path 확인 | [DATA_DB_PIPELINE_FLOW.md](./DATA_DB_PIPELINE_FLOW.md) |
| 새 strategy family 추가 / 변경 절차 확인 | [STRATEGY_IMPLEMENTATION_FLOW.md](./STRATEGY_IMPLEMENTATION_FLOW.md) |
