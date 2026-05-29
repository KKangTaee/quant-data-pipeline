# Phase 10 Walk-forward / OOS / Regime Validation Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8은 lifecycle / survivorship evidence를 강화했고, Phase 9는 cost / slippage / turnover / liquidity realism을 강화했다.
그래도 좋은 백테스트가 특정 기간, 특정 시장 국면, 특정 in-sample 튜닝에만 맞은 결과일 가능성은 아직 충분히 남아 있다.

Phase 10의 목적은 전략이 한 번의 전체기간 성과표만으로 선택되지 않게 만들고, walk-forward, out-of-sample, regime split 기준에서도 투자 후보로 볼 수 있는지 확인하는 것이다.
이 phase는 새 사용자 메모, preset, 임의 JSONL 저장을 늘리는 작업이 아니라, 기존 Backtest -> Practical Validation -> Final Review 흐름에서 검증 효력을 더 강하게 읽는 작업이다.

## Phase Goal

Practical Validation, Final Review, selected-route gate가 아래 질문에 답할 수 있게 만든다.

- 전략이 in-sample 구간에만 과적합된 것은 아닌가?
- out-of-sample holdout 구간에서도 최소한의 성과 / 리스크 기준을 유지하는가?
- 상승장, 하락장, 고변동성, 금리 / 인플레이션 regime에서 특정 조건에만 의존하지 않는가?
- walk-forward window를 바꿔도 selection 근거가 크게 무너지지 않는가?
- `NOT_RUN`, 기간 부족, benchmark / regime evidence 부족을 pass처럼 숨기지 않는가?

## Scope

포함한다.

- Phase 10 official board 생성
- current Practical Validation / Robustness Lab / replay / result metadata source map 확인
- walk-forward split contract 설계
- out-of-sample holdout validation contract 설계
- regime split / market condition robustness read model 설계
- Practical Validation / Final Review evidence와 selected-route gate 연결
- integrated QA / closeout

포함하지 않는다.

- 새 JSONL registry
- user memo / preset persistence
- broker order, live approval, auto rebalance
- UI direct provider / FRED fetch
- paid data source 우선 도입
- full ML hyperparameter optimization platform
- raw full split result artifact를 workflow JSONL에 저장하는 방식

## Storage Boundary

Phase 10은 우선 기존 result bundle, DB price / macro loader, compact validation evidence를 읽는다.
새 데이터가 필요하면 `Ingestion -> DB -> Loader -> UI` 흐름을 따르고, 검증 효력을 높이는 DB-backed evidence로만 다룬다.
사용자의 코멘트, 시간 기록, 프리셋, 메모성 저장 기능은 추가하지 않는다.

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 10-0 | Phase 10 board open / scope and task split | Complete |
| 10-1 | Current validation source map / gap audit | Next |
| 10-2 | Walk-forward split contract | Planned |
| 10-3 | Out-of-sample holdout validation contract | Planned |
| 10-4 | Regime split / market condition robustness | Planned |
| 10-5 | Practical Validation / Final Review gate integration | Planned |
| 10-6 | Phase 10 integrated QA / closeout | Planned |

## Done Criteria

- Walk-forward / out-of-sample / regime evidence가 compact validation read model로 표시된다.
- `NOT_RUN`, insufficient period, missing regime source, in-sample-only evidence는 pass로 처리하지 않는다.
- Final Review selected-route gate가 overfit / OOS / regime gap을 block 또는 review-required로 표시한다.
- 새 raw artifact나 user memo 저장 없이 기존 DB / loader / compact evidence boundary를 유지한다.
- 관련 service contract test와 compile / diff check가 통과한다.

## Carry Forward To Later Phases

- Phase 11: portfolio construction risk controls를 강화한다.
- Phase 12: selected monitoring / recheck operations를 정리한다.
- Phase 13: 전체 1차 hardening cycle closeout을 진행한다.
