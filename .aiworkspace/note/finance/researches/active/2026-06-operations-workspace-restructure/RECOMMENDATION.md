# Recommendation

## One-Line Recommendation

Keep `Selected Portfolio Dashboard` under `Operations`, but restructure Operations so it reads as an operating console with clear lanes: `Portfolio Monitoring`, `System/Data Health`, `Archive/Recovery`, and eventually `Reports`.

## Why This Direction

The current placement is conceptually right. A selected portfolio is no longer in the "build/test a strategy" phase; it is in the "observe, recheck, compare, and decide whether review is needed" phase. That belongs outside `Workspace > Backtest`.

The problem is not location. The problem is hierarchy. `Ops Review`, `Selected Portfolio Dashboard`, `Backtest Run History`, and `Candidate Library` are presented as peers, but only two are real primary Operations surfaces:

- `Selected Portfolio Dashboard`: user-facing portfolio monitoring.
- `Ops Review`: system/data/run health.

The other two should remain, but as secondary archive/recovery tools:

- `Backtest Run History`: reproduce old backtest runs, restore forms, resend to validation.
- `Candidate Library`: inspect saved current/pre-live candidates and rebuild result curves.

Do not delete legacy tools yet. They carry audit, reproducibility, and migration value. Instead, demote them visually and semantically.

## Recommended 1st Build Scope

### Step 1. Label The Operating Model

- Treat `Workspace` as "build and validate".
- Treat `Operations` as "monitor selected outcomes and system health".
- Treat `Reference` as "explain meaning and workflow".
- Keep Selected Dashboard in Operations.
- Add copy/guidance that Run History and Candidate Library are archive/recovery, not primary candidate selection stages.

### Step 2. Add Operations Overview

- Create one landing surface that answers "what should I check now?"
- Show lanes for Portfolio Monitoring, System/Data Health, Archive/Recovery, and Reference/Reports.
- Put Selected Portfolio Dashboard as the first Portfolio Monitoring action.
- Put Backtest Run History and Candidate Library under Archive/Recovery.
- Do not delete pages in the first slice.
- Do not change registry/saved schemas.

## Recommended Next Phase After 1st Build

| Phase | Output | Why |
| --- | --- | --- |
| Portfolio Monitoring V2 | Stronger Selected Dashboard status cockpit | Makes the correct primary Operations surface more useful. |
| Archive Demotion | Navigation or Overview cards lower Run History / Candidate Library prominence | Preserves legacy replay while reducing workflow confusion. |
| Data/System Health Alignment | Better bridge between Ops Review and Ingestion health | Clarifies where to inspect vs where to execute collection. |
| Report Export | Manual selected portfolio monitoring snapshots | Adds durable human-readable operations output after semantics stabilize. |

## What Not To Do Yet

- Do not move Selected Dashboard back to Workspace/Backtest.
- Do not delete Backtest Run History or Candidate Library immediately.
- Do not add broker/account/order/auto-rebalance behavior.
- Do not rewrite registries or saved setup.
- Do not begin with a full React/API migration.

## Decision Rules

Proceed when:

- The user agrees Operations should remain the post-selection + system-health area.
- The user agrees Run History and Candidate Library should be kept but demoted.
- The first implementation is limited to IA/read-model/UI copy, not data schema or live-trading scope.

## Final Recommendation

Approve a narrow `Operations Overview / IA V1` design task before implementation.

The first implementation should not remove pages. It should make the current system legible:

```text
Operations = Portfolio Monitoring + System/Data Health + Archive/Recovery
```

After that lands and feels right, run a second pass on Selected Dashboard monitoring summaries and a third pass on archive demotion. This keeps useful legacy tools available while shifting the user's center of gravity from "old backtest artifacts" to "selected portfolio operations".

## 2026-06-07 Updated Recommendation

`Operations Overview / IA V1`은 현재 구현되어 있으므로, 다음 승인 후보는 `Operations Cockpit V2`로 좁히는 것이 맞다.

### Updated One-Line Recommendation

Keep the current Operations structure, but redesign the Overview around three operating questions:

1. 내 selected portfolio monitoring 상태가 지금 어떤가?
2. 이 상태를 판단할 데이터 / 실행 근거가 신뢰 가능한가?
3. 과거 run / candidate를 복구해야 하는 예외 상황인가?

### Recommended Next Build Scope

1차 `Operations Cockpit Cleanup`

- `Operations Overview`의 개발 이력 / surface audit 중심 정보를 낮추거나 Reference/docs로 이동한다.
- Today's Operations Queue를 portfolio-first로 다시 정렬한다.
- Archive metrics는 보조 drawer로 낮춘다.
- no-live boundary는 유지하되, 과하게 반복되는 개발용 문구는 정리한다.

2차 `Portfolio Monitoring First Summary`

- Operations Overview에서 Portfolio Monitoring의 compact summary를 더 강하게 보여준다.
- stale scenario, blocked/missing selected reference, open review item, next review date, target snapshot freshness를 우선 지표로 삼는다.
- Portfolio Monitoring 본 화면은 계속 상세 cockpit 역할을 맡는다.

3차 `Archive / Recovery Decision`

- `Archive: Backtest Runs`와 `Archive: Candidates`는 삭제하지 않고, top navigation 노출 방식만 조정할 수 있는지 검토한다.
- 제거는 registry read path, history restore, Practical Validation handoff, candidate replay 대체 경로가 확인된 뒤에만 한다.

### What Should Not Be Done Now

- Portfolio Monitoring을 Backtest로 되돌리지 않는다.
- Archive screens를 즉시 삭제하지 않는다.
- Operations에서 broker account sync, 주문, 자동 리밸런싱, scheduler-owned monitoring log write를 만들지 않는다.
- 새 탭을 늘리는 방식으로 정체성 문제를 덮지 않는다. 먼저 기존 Overview와 Portfolio Monitoring의 목적을 날카롭게 만든다.

### Approval Checkpoint

구현으로 넘어가려면 사용자가 아래 범위를 승인해야 한다.

- 이번 차수는 `Operations Cockpit V2`로 제한한다.
- 1차에서는 삭제보다 화면 위계 / copy / summary 개선을 한다.
- archive 도구는 보존하되 primary workflow처럼 보이지 않게 낮춘다.
