# Phase 9 Cost / Slippage / Liquidity Realism Design

Status: Active
Created: 2026-05-29

## Design Boundary

Phase 9는 backtest realism evidence를 강화한다.
사용자-facing 저장 기능을 늘리지 않고, 기존 source chain을 우선 사용한다.

```text
backtest result metadata / validation compact evidence
DB provider / price snapshots
  -> app.services.backtest_realism_audit
  -> Final Review investability packet / selected-route gate
```

## Evidence Classes

| Evidence | Meaning |
| --- | --- |
| cost assumption | 사용자가 넣었거나 profile에서 온 거래비용 가정 |
| cost applied proof | net curve / result metric에 비용이 실제 반영됐다는 근거 |
| turnover evidence | rebalance별 포지션 변화량 또는 최소한 cadence 기반 review evidence |
| liquidity evidence | AUM, ADV, dollar volume, bid-ask spread, provider freshness |
| capacity evidence | 포트폴리오 가상 투자금 대비 거래대금 / AUM / spread 부담 |
| slippage sensitivity | 비용 bps 변화에 대한 성과 민감도 |

## PASS / REVIEW Principle

| Case | Audit meaning |
| --- | --- |
| cost missing | NEEDS_INPUT |
| cost assumption only | REVIEW |
| cost applied to net curve | PASS candidate |
| turnover missing but rebalance cadence exists | REVIEW |
| liquidity provider stale / partial | REVIEW |
| liquidity missing | NEEDS_INPUT |
| sensitivity NOT_RUN | REVIEW or NEEDS_INPUT depending route |

## Storage Boundary

- Full price / provider / liquidity rows stay in DB.
- Practical Validation / Final Review rows keep compact evidence only.
- No new JSONL registry is introduced by default.
- No user memo / preset persistence is added.

## Tradeoff

Phase 9 will not build a full execution simulator.
The target is a defensible realism gate: if costs or liquidity are weakly evidenced, the system should say so and block or review practical selection rather than over-trusting gross backtest performance.
