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
| `candidates/point_in_time/` | ready | 후보 선택 근거를 시점 기준으로 정리할 위치 |
| `validation/runtime/` | ready | 코드/runtime smoke report 위치 |
| `validation/ui_replay/` | ready | UI replay smoke report 위치 |
| `archive/legacy_phase/` | migration_pending | 기존 phase별 report 임시 보관 위치 |

## Strategy Hubs

| Strategy | Hub | Log |
|---|---|---|
| GTAA | [GTAA.md](./strategies/GTAA.md) | [GTAA_BACKTEST_LOG.md](./strategies/GTAA_BACKTEST_LOG.md) |
| Equal Weight | [EQUAL_WEIGHT.md](./strategies/EQUAL_WEIGHT.md) | [EQUAL_WEIGHT_BACKTEST_LOG.md](./strategies/EQUAL_WEIGHT_BACKTEST_LOG.md) |
| Quality Strict Annual | [QUALITY_STRICT_ANNUAL.md](./strategies/QUALITY_STRICT_ANNUAL.md) | [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](./strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md) |
| Value Strict Annual | [VALUE_STRICT_ANNUAL.md](./strategies/VALUE_STRICT_ANNUAL.md) | [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](./strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md) |
| Quality + Value Strict Annual | [QUALITY_VALUE_STRICT_ANNUAL.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL.md) | [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](./strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md) |

## Current Candidate Notes

현재 candidate one-pager는 아직 `strategies/` root에 남겨 둔다. 후속 migration에서 `candidates/point_in_time/`로 옮길지, 전략별 hub에 흡수할지 결정한다.

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

## Legacy Phase Archive

기존 phase별 report는 아래 위치로 1차 이동했다.

| Legacy Folder | Files | Status |
|---|---:|---|
| `archive/legacy_phase/phase13/` | 15 | pending_classification |
| `archive/legacy_phase/phase14/` | 2 | pending_classification |
| `archive/legacy_phase/phase15/` | 15 | pending_classification |
| `archive/legacy_phase/phase16/` | 5 | pending_classification |
| `archive/legacy_phase/phase17/` | 4 | pending_classification |
| `archive/legacy_phase/phase18/` | 3 | pending_classification |
| `archive/legacy_phase/phase21/` | 5 | pending_classification |
| `archive/legacy_phase/phase22/` | 3 | pending_classification |
| `archive/legacy_phase/phase23/` | 2 | pending_classification |
| `archive/legacy_phase/phase24/` | 3 | pending_classification |

후속 단계에서는 각 문서를 `runs/`, `candidates/`, `validation/`, `strategies/` 중 하나로 흡수하거나, 중복이면 삭제한다.
