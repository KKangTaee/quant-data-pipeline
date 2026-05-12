# NOTES - Finance Documentation System Rebuild

Status: Active
Last Updated: 2026-05-12

## Inventory Summary

현재 `.note/finance/`에는 아래 성격의 문서가 섞여 있었다.

| Group | Existing Examples | Migration Decision |
|---|---|---|
| root current-state docs | `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, `MASTER_PHASE_ROADMAP.md` | 핵심만 새 `docs/`로 재작성 |
| code flow docs | `code_analysis/*` | 세부 문서는 삭제 후보. 핵심 entrypoint만 `docs/PROJECT_MAP.md`로 승격 |
| data architecture docs | `docs/data/*` | 기존 `data_architecture/*` 상세 문서를 `docs/data/`로 흡수 |
| operations guides | `operations/*` | 필요한 운영 경계만 `docs/runbooks/README.md`와 `PROJECT_MAP.md`에 축약 |
| research docs | `research/*` | 당장 필요한 Practical Validation 개념만 승격. 상세 research는 삭제 후보 |
| backtest reports | `backtest_reports/*` | 삭제가 아니라 `.note/finance/reports/backtests/`로 이관. phase별 원본은 legacy archive에서 후속 분류 |
| phase docs | `phases/phase*/` | 새 구조에서는 `phases/active/`, `phases/done/`로 요약 관리 |
| task docs | 없음 또는 흩어진 planning docs | 새 구조에서는 `tasks/active/<task>/` 기준 |
| registry data | `registries/*.jsonl` | 보존 |
| saved setup | `saved/*.jsonl` | 보존 |
| runtime/generated | `run_history/`, `run_artifacts/`, `.DS_Store`, `.playwright-mcp/` | 장기 문서 아님. 커밋/보존 대상에서 제외 |

## Decisions

- 장기 지식 위치는 `.note/finance/docs/`로 한다.
- 현재 Practical Validation V2는 phase가 아니라 active task로 관리한다.
- 기존 phase36 등 과거 phase 문서는 다음 마이그레이션에서 필요한 summary만 남기는 방향으로 정리한다.
- 새 문서에는 기존 상세 내용을 복붙하지 않고, 다음 세션이 작업을 재개할 수 있는 최소 기준만 남긴다.
- backtest report는 phase 문서와 달리 분석 근거로 재사용될 가능성이 높으므로 삭제하지 않고 새 `reports/backtests/` 구조로 먼저 이동한다.
- `archive/legacy_phase/`는 영구 위치가 아니라 후속 흡수/삭제 판단 전 staging 영역이며, 3차에서 제거했다.
- legacy report 중 개발 검증 성격이 분명한 `phase23`, `phase24`는 먼저 `validation/`으로 흡수한다.
- legacy `phase13`~`phase18`은 원본성 전략 탐색 report로 보고 `runs/2026/strategy_search/`에 둔다.
- legacy `phase21`~`phase22`는 runtime validation과 point-in-time candidate evidence로 나눠 둔다.
- legacy `data_architecture/`는 archive를 만들지 않고 `docs/data/`로 전체 마이그레이션했다.

## Open Questions

- 기존 phase 문서를 전부 삭제해도 되는지 최종 승인 필요
- strategy hub/log와 raw strategy search report 사이의 중복 삭제 여부 결정 필요
- `run_history/`와 `run_artifacts/` 삭제 여부 최종 승인 필요
- `AGENTS.md` 축약 수준 최종 확인 필요
