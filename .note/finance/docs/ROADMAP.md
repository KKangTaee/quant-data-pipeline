# Finance Roadmap

Status: Active
Last Verified: 2026-05-12

## Current Work

| Track | Status | Notes |
|---|---|---|
| Documentation System Rebuild | Active | `.note/finance/tasks/active/doc-system-rebuild/` |
| Backtest Report Migration | Active | `.note/finance/reports/backtests/`, legacy phase archive 정리 중 |
| Practical Validation V2 | Active | `.note/finance/tasks/active/practical-validation-v2/` |
| Phase 36 Selected Portfolio Dashboard | Implementation complete before doc rebuild | 기존 phase 문서는 새 구조 정리 후 필요 시 `phases/done/`에 요약만 남긴다 |

## Practical Validation V2 Roadmap

| Step | Goal | Status |
|---|---|---|
| P0 | 최신 runtime 재검증 보강 | Completed before this doc rebuild |
| P1 | Practical Validation V2 기본 진단 구조 | Completed before this doc rebuild |
| P2 | proxy / NOT_RUN 중심 진단을 provider / macro / stress evidence로 정상화 | In practical closeout |
| P3 | QA, Final Review handoff, selected monitoring 연결 정리 | Planned |

## P2 Scope Reminder

P2의 핵심은 provider connector 자체가 아니라,
12개 Practical Validation 진단 중 미완성 진단을 정상 검증 가능한 상태로 만드는 것이다.

P2에서 정상화하는 주요 진단:

| No | Diagnostic |
|---:|---|
| 2 | Asset Allocation Fit |
| 3 | Concentration / Overlap / Exposure |
| 5 | Regime / Macro Suitability |
| 6 | Sentiment / Risk-On-Off Overlay |
| 7 | Stress / Scenario Diagnostics |
| 9 | Leveraged / Inverse ETF Suitability |
| 10 | Operability / Cost / Liquidity |
| 11 | Robustness / Sensitivity / Overfit |

## Phase / Task Model

앞으로 큰 작업은 두 층으로 관리한다.

| Layer | Location | Meaning |
|---|---|---|
| Phase | `.note/finance/phases/active/<phase>/` | 여러 task를 묶는 상위 방향, 설계, 통합 단위 |
| Task | `.note/finance/tasks/active/<task>/` | 실제 구현, 문서 정리, 조사, QA를 수행하는 실행 단위 |

현재 Practical Validation V2는 phase가 아니라 별도 active task로 관리한다.

## Next Decisions

- backtest legacy phase archive를 `runs/`, `candidates/`, `validation/`, `strategies/`로 후속 분류할지 결정한다.
- 문서 재구성 다음 작업에서 기존 `.note/finance` 문서 tree를 삭제하고 새 구조만 남긴다.
- Practical Validation V2는 P2 QA 여부를 확인한 뒤 P3로 넘어갈지, P2를 closeout할지 결정한다.
