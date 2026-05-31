# Phase 11 Portfolio Construction Risk Controls Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8은 data / lifecycle evidence를 강화했고, Phase 9는 cost / liquidity realism을 강화했으며, Phase 10은 walk-forward / OOS / regime validation efficacy를 강화했다.
그래도 실전 후보로 보기에는 포트폴리오 구성 자체의 위험이 남아 있다.

좋은 component를 모아도 실제 포트폴리오는 특정 ETF, sector, top holding, factor, risk source에 과도하게 몰릴 수 있다.
50:50 비중처럼 보여도 변동성 기준 risk contribution은 한쪽 component가 대부분을 차지할 수 있고, 여러 전략을 섞었지만 실제로는 같은 성장주 / 기술주 / 금리 민감 자산에 반복 노출될 수 있다.

Phase 11의 목적은 Backtest -> Practical Validation -> Final Review 흐름에서 portfolio construction 자체의 집중도, 중복, 상관, 위험기여, component role / weight discipline을 검증 가능한 compact evidence로 만들고, selected-route gate에서 필요한 경우 review 또는 blocker로 드러내는 것이다.
이 phase는 사용자 메모, preset, 임의 JSONL 저장을 늘리는 작업이 아니라 기존 DB / loader / compact validation evidence를 더 엄격하게 읽는 작업이다.

## Phase Goal

Practical Validation, Final Review, selected-route gate가 아래 질문에 답할 수 있게 만든다.

- 특정 component나 asset class에 target weight가 과도하게 몰려 있지 않은가?
- ETF를 여러 개 섞었지만 top holding / sector / theme overlap이 높은 것은 아닌가?
- component return 상관과 volatility 때문에 risk contribution이 한쪽으로 쏠리지 않는가?
- component를 하나 제거하거나 weight를 조금 바꾸면 portfolio thesis가 쉽게 무너지는가?
- profile별 risk budget에 비해 equity, growth, sector, leveraged / inverse exposure가 과도하지 않은가?
- component role / hedge role / diversifier role이 실제 evidence와 맞는가?

## Scope

포함한다.

- Phase 11 official board 생성
- current Practical Validation / Look-through Board / Robustness Lab / Final Review gate의 construction risk source map 확인
- concentration / overlap / exposure construction risk contract 설계
- correlation / risk contribution / drop-one dependency evidence 설계
- component role / target weight discipline evidence 설계
- Practical Validation / Final Review evidence와 selected-route gate 연결 설계
- integrated QA / closeout

포함하지 않는다.

- 새 JSONL registry
- user memo / preset persistence
- broker order, live approval, auto rebalance
- UI direct provider / holdings fetch
- paid data source 우선 도입
- full optimizer / portfolio construction engine replacement
- raw full holdings / full return matrix artifact를 workflow JSONL에 저장하는 방식

## Storage Boundary

Phase 11은 우선 기존 selection source, result curve, DB provider / holdings / exposure loader, compact validation evidence를 읽는다.
새 데이터가 필요하면 `Ingestion -> DB -> Loader -> UI` 흐름을 따르고, 검증 효력을 높이는 DB-backed evidence로만 다룬다.
사용자의 코멘트, 시간 기록, 프리셋, 메모성 저장 기능은 추가하지 않는다.

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 11-0 | Phase 11 board open / scope and task split | Complete |
| 11-1 | Current construction risk source map / gap audit | Complete |
| 11-2 | Concentration / overlap / exposure contract | Complete |
| 11-3 | Correlation / risk contribution contract | Complete |
| 11-4 | Component role / weight discipline contract | Complete |
| 11-5 | Practical Validation / Final Review construction risk gate integration | Complete |
| 11-6 | Phase 11 integrated QA / closeout | Complete |

## Done Criteria

- Concentration / overlap / exposure evidence가 compact validation read model로 표시된다.
- Correlation / risk contribution / drop-one dependency evidence가 component return matrix 기준으로 표시된다.
- component role / weight discipline이 profile-aware review 또는 blocker 근거로 표시된다.
- `NOT_RUN`, insufficient holdings coverage, missing component return matrix, proxy-only construction evidence는 pass로 처리하지 않는다.
- Final Review selected-route gate가 construction risk gap을 block 또는 review-required로 표시한다.
- 새 raw artifact나 user memo 저장 없이 기존 DB / loader / compact evidence boundary를 유지한다.
- 관련 service contract test와 compile / diff check가 통과한다.

## Carry Forward To Later Phases

- Phase 12: selected monitoring / recheck operations를 정리한다.
- Phase 13: 전체 1차 hardening cycle closeout을 진행한다.
