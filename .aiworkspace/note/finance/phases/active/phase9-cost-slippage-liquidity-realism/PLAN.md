# Phase 9 Cost / Slippage / Liquidity Realism Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8은 lifecycle / survivorship evidence가 약해서 투자 가능 판단이 과대해질 수 있는 문제를 보강했다.
다음 큰 약점은 backtest 성과가 실제 체결 비용, slippage, turnover, liquidity, capacity를 충분히 반영하지 못할 수 있다는 점이다.

Phase 9의 목적은 "좋아 보이는 백테스트"를 "실제로 사고팔 수 있는 후보"에 더 가깝게 만드는 것이다.
새 사용자 메모나 preset 저장을 늘리는 phase가 아니라, 기존 Backtest -> Practical Validation -> Final Review 흐름에서 비용 / 체결 가능성 evidence를 더 엄격하게 읽고 필요한 경우 blocker / review로 남기는 phase다.

## Phase Goal

Backtest Realism Audit과 selected-route gate가 비용 / 회전율 / 유동성 / capacity evidence를 더 구체적으로 판단하도록 만든다.

완료 상태는 아래와 같다.

- cost assumption이 단순 metadata인지, net curve에 실제 반영됐는지 분리한다.
- turnover / rebalance cadence가 비용 민감도와 연결된다.
- ETF / ticker liquidity evidence가 DB provider / price snapshot 기반으로 compact하게 읽힌다.
- slippage / cost sensitivity가 `NOT_RUN`일 때 pass로 숨겨지지 않는다.
- Final Review selected-route가 realism gap을 더 정확히 block / review로 처리한다.

## Scope

포함한다.

- Phase 9 official board 생성
- current Backtest Realism Audit / runtime metadata source map 확인
- cost model evidence contract 정리
- turnover / rebalance evidence 보강
- liquidity / capacity evidence read model 보강
- cost / slippage sensitivity read-only audit 보강
- selected-route gate policy refinement
- integrated QA / closeout

포함하지 않는다.

- broker 연결, 주문 지시, auto rebalance
- 새 user memo / preset persistence
- 새 JSONL registry
- UI direct provider fetch
- 세금 최적화 엔진
- full market microstructure simulator

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 9-0 | Phase 9 board open / scope and task split | Complete |
| 9-1 | Cost model source contract review | Complete |
| 9-2 | Turnover / rebalance evidence read model | Complete |
| 9-3 | Net cost curve application proof | Complete |
| 9-4 | Liquidity / capacity evidence refinement | Complete |
| 9-5 | Cost / slippage sensitivity audit | Pending |
| 9-6 | Backtest Realism gate policy refinement | Pending |
| 9-7 | Phase 9 integrated QA / closeout | Pending |

## Done Criteria

- Backtest Realism Audit이 cost, turnover, liquidity, net performance, sensitivity gap을 더 분명히 보여준다.
- `NOT_RUN`, assumption-only, stale / partial liquidity evidence는 pass로 처리하지 않는다.
- 새 raw/full evidence는 workflow JSONL이 아니라 DB / loader / compact audit evidence 경계에 남는다.
- 관련 service contract test와 compile / diff check가 통과한다.

## Carry Forward To Later Phases

- Phase 10: walk-forward / out-of-sample / regime split 검증을 강화한다.
- Phase 11: portfolio construction risk controls를 강화한다.
- Phase 12: selected monitoring / recheck operations를 정리한다.
- Phase 13: 전체 1차 hardening cycle closeout을 진행한다.
