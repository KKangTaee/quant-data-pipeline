# Backtest Report Index

Status: Active
Last Verified: 2026-05-12

## Read First

| 목적 | 문서 |
|---|---|
| report 폴더 운영 기준 | [README.md](./README.md) |
| 새 report 작성 형식 | [TEMPLATE.md](./TEMPLATE.md) |
| 전략별 hub와 log | [strategies/README.md](./strategies/README.md) |
| legacy phase report 정리 계획 | [LEGACY_MIGRATION.md](./LEGACY_MIGRATION.md) |

## Current Structure

| 위치 | 상태 | 설명 |
|---|---|---|
| `strategies/` | active | 전략 family별 hub, log, current-candidate one-pager |
| `runs/2026/` | ready | 앞으로 새 backtest report를 받는 기본 위치 |
| `validation/runtime/` | ready | 코드/runtime smoke report 위치 |
| `validation/ui_replay/` | ready | UI replay smoke report 위치 |

## Run Reports

| Type | Location | Notes |
|---|---|---|
| Legacy strategy search raw reports | [runs/2026/strategy_search/](./runs/2026/strategy_search/README.md) | phase13~phase18에서 생성된 원본성 전략 탐색 report 38개 |

## Strategy Hubs

| Strategy | Hub | Log |
|---|---|---|
| GTAA | [GTAA.md](./strategies/GTAA.md) | [GTAA_BACKTEST_LOG.md](./strategies/GTAA_BACKTEST_LOG.md) |
| Equal Weight | [EQUAL_WEIGHT.md](./strategies/EQUAL_WEIGHT.md) | [EQUAL_WEIGHT_BACKTEST_LOG.md](./strategies/EQUAL_WEIGHT_BACKTEST_LOG.md) |
| Quality Strict Annual | [QUALITY_STRICT_ANNUAL.md](./strategies/QUALITY_STRICT_ANNUAL.md) | [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](./strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md) |
| Value Strict Annual | [VALUE_STRICT_ANNUAL.md](./strategies/VALUE_STRICT_ANNUAL.md) | [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](./strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md) |
| Quality + Value Strict Annual | [QUALITY_VALUE_STRICT_ANNUAL.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL.md) | [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md) |

## Current Candidate Notes

현재 candidate one-pager는 `strategies/` root에 둔다. 장기적으로 반복 확인할 전략 후보 근거는 별도 candidate 폴더가 아니라 전략별 hub / backtest log에 흡수한다.

- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](./strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](./strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](./strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- [VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md](./strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md)
- [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](./strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](./strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)

## Validation Reports

| Type | Report |
|---|---|
| Runtime | [WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md](./validation/runtime/WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md) |
| Runtime | [QUARTERLY_CONTRACT_RUNTIME_SMOKE.md](./validation/runtime/QUARTERLY_CONTRACT_RUNTIME_SMOKE.md) |
| Runtime | [GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md](./validation/runtime/GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md) |
| UI Replay | [GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md](./validation/ui_replay/GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md) |

## Candidate Evidence Handling

과거 후보 rerun report는 현재 후보 폴더로 따로 보관하지 않는다.

| Evidence | Current Home | Notes |
|---|---|---|
| Value / Quality / Quality + Value rerun 판단 | `strategies/*_BACKTEST_LOG.md` | 전략별 log에 내용 중심 entry로 흡수 |
| Weighted portfolio baseline / weight alternative 판단 | `validation/runtime/WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md` | portfolio candidate가 아니라 replay / weighted builder smoke evidence로 정리 |

## Legacy Migration Status

기존 `archive/legacy_phase/`는 2026-05-12 3차 migration에서 비웠고 제거했다.

분류 이력은 [LEGACY_MIGRATION.md](./LEGACY_MIGRATION.md)에 남긴다.
