# Data Provenance / PIT Evidence Contract Plan

Status: Active
Started: 2026-06-09

## Goal

Practical Validation / Final Review / Portfolio Monitoring evidence가 source, freshness, current snapshot, PIT, look-ahead, survivorship, proxy 상태를 같은 compact contract로 읽을 수 있게 한다.

## 이걸 하는 이유?

제품 흐름은 Backtest -> Practical Validation -> Final Review -> Portfolio Monitoring까지 이어졌지만, evidence row마다 "현재 snapshot인지", "decision-time에 알 수 있었던 정보인지", "proxy / stale / current-only라 pass로 보면 안 되는지"가 한 schema로 보이지 않는다. 이 task는 raw provider / macro / holdings row를 JSONL로 옮기지 않고도, 판단에 쓰는 compact evidence가 provenance risk를 숨기지 않게 만든다.

## 1차 / 2차 / 3차 Roadmap

| 차수 | 목적 | 바뀔 화면 / 파일 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차: provenance 흐름 감사 | provider / macro / lifecycle / price / robustness evidence metadata와 저장 경계 확인 | task docs 중심, code audit | 새 DB schema 필요 여부와 최소 contract 위치 결정 | 2차 contract builder / tests |
| 2차: 최소 contract 구현 | 기존 compact evidence에서 `data_provenance_summary`를 생성하고 Practical Validation result / Final Review packet에 붙임 | `app/services/*`, focused tests | stale / proxy / current-only / NOT_RUN이 pass처럼 숨지 않음 | 3차 UI/docs/검증 |
| 3차: UI / docs / 검증 연결 | Practical Validation / Final Review에서 provenance summary를 읽고 durable docs를 맞춤 | `app/web/*`, finance docs, root logs | focused tests, compile, diff check, commit 완료 | 다음 후보는 broader DB migration 또는 monitoring snapshot provenance 확장 |

## Scope

- Existing loader metadata를 읽어 compact provenance rows를 만든다.
- Provider / holdings / exposure / macro / price window / lifecycle / robustness run-set evidence를 우선 포함한다.
- Practical Validation result와 Final Review investability packet에 summary를 연결한다.
- UI는 기존 audit / packet 상세 expander에 추가한다.
- Durable docs는 data/storage/flow 중심으로 최소 갱신한다.

## Out Of Scope

- 새 DB migration system.
- 모든 table column 추가.
- 새 JSONL registry 생성.
- registry / saved JSONL rewrite.
- full holdings, full macro series, raw provider response JSONL 저장.
- UI-side provider / FRED fetch.
- live approval, broker order, account sync, auto rebalance.

## Stop Condition

- 최소 provenance contract가 문서화되고, 주요 validation / Final Review evidence에 `data_provenance_summary`가 붙는다.
- current snapshot / stale / proxy / PIT-risk row가 `decision_effect.treat_as_pass=True`로 숨지 않는다.
- focused tests와 compile/diff checks가 통과하고 coherent commit을 만든다.
