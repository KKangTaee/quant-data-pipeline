# NOTES - Finance Documentation System Rebuild

Status: Active
Last Updated: 2026-05-12

## Inventory Summary

현재 `.aiworkspace/note/finance/`에는 아래 성격의 문서가 섞여 있었다.

| Group | Existing Examples | Migration Decision |
|---|---|---|
| root current-state docs | `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, `MASTER_PHASE_ROADMAP.md` | 핵심만 새 `docs/`로 재작성 |
| code flow docs | `docs/architecture/*`, `docs/flows/*`, `docs/runbooks/*` | 기존 `code_analysis/*`를 문서 성격별로 흡수 |
| data architecture docs | `docs/data/*` | 기존 `data_architecture/*` 상세 문서를 `docs/data/`로 흡수 |
| operations guides | `operations/*` | 필요한 운영 경계만 `docs/runbooks/README.md`와 `PROJECT_MAP.md`에 축약 |
| research docs | `research/*` | 당장 필요한 Practical Validation 개념만 승격. 상세 research는 삭제 후보 |
| backtest reports | `backtest_reports/*` | 삭제가 아니라 `.aiworkspace/note/finance/reports/backtests/`로 이관. phase별 원본은 legacy archive에서 후속 분류 |
| phase docs | `phases/phase*/` | 새 구조에서는 `phases/active/`, `phases/done/`로 요약 관리 |
| task docs | 없음 또는 흩어진 planning docs | 새 구조에서는 `tasks/active/<task>/` 기준 |
| registry data | `registries/*.jsonl` | 보존 |
| saved setup | `saved/*.jsonl` | 보존 |
| runtime/generated | `run_history/`, `run_artifacts/`, `.DS_Store`, `.playwright-mcp/` | 장기 문서 아님. 커밋/보존 대상에서 제외 |

## Decisions

- 장기 지식 위치는 `.aiworkspace/note/finance/docs/`로 한다.
- 현재 Practical Validation V2는 phase가 아니라 active task로 관리한다.
- 기존 phase1~phase36 상세 문서는 현재 구현과 맞지 않는 legacy history로 보고 3차에서 제거한다.
- 새 문서에는 기존 상세 내용을 복붙하지 않고, 다음 세션이 작업을 재개할 수 있는 최소 기준만 남긴다.
- backtest report는 phase 문서와 달리 분석 근거로 재사용될 가능성이 높으므로 삭제하지 않고 새 `reports/backtests/` 구조로 먼저 이동한다.
- `archive/legacy_phase/`는 영구 위치가 아니라 후속 흡수/삭제 판단 전 staging 영역이며, 3차에서 제거했다.
- legacy report 중 개발 검증 성격이 분명한 `phase23`, `phase24`는 먼저 `validation/`으로 흡수한다.
- legacy `phase13`~`phase18`은 원본성 전략 탐색 report로 보고 `runs/2026/strategy_search/`에 둔다.
- legacy `phase21`~`phase22`는 runtime validation과 point-in-time candidate evidence로 나눠 둔다.
- legacy `data_architecture/`는 archive를 만들지 않고 `docs/data/`로 전체 마이그레이션했다.
- legacy `code_analysis/`는 archive를 만들지 않고 문서 성격별로 흡수했다.
  - current-state code map: `docs/architecture/`
  - user / screen flow: `docs/flows/`
  - helper script usage: `docs/runbooks/`
  - Practical Validation V2 planning: `tasks/active/practical-validation-v2/`
- legacy root / operations / research / support 문서는 2차에서 아래처럼 흡수 기준을 확정했다.
  - root current-state docs: `docs/INDEX.md`, `docs/PROJECT_MAP.md`, `docs/ROADMAP.md`, `docs/GLOSSARY.md`로 대체
  - registry guide docs: `.aiworkspace/note/finance/registries/README.md`에 current V2 / legacy compatibility 기준으로 흡수
  - runtime artifact hygiene / data collection UI / config externalization: `docs/runbooks/README.md`에 운영 원칙만 흡수
  - Practical Validation investment diagnostics research: `tasks/active/practical-validation-v2/DESIGN.md`에 진단 설계로 흡수
  - static stress window JSON: `docs/data/practical_validation_stress_windows_v1.json`로 이동하고 runtime path 갱신
  - Playwright / market research playbook: `docs/runbooks/README.md`의 external research 원칙으로 축약
  - support track docs: `AGENTS.md`, `docs/runbooks/AUTOMATION_SCRIPTS.md`, `agent/GOTCHAS.md`, `agent/LESSONS.md`로 필요한 원칙만 흡수

## Open Questions

- 기존 phase 문서를 전부 삭제해도 되는지 최종 승인 필요
- strategy hub/log와 raw strategy search report 사이의 중복 삭제 여부 결정 필요
- `run_history/`와 `run_artifacts/`를 working tree에서 삭제할지, gitignore / local cleanup으로 둘지 최종 승인 필요

## 2차 삭제 후보 판단

3차에서 삭제한 legacy 문서:

| Legacy Area | 2차 판단 |
|---|---|
| root `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, `MASTER_PHASE_ROADMAP.md`, `FINANCE_TERM_GLOSSARY.md` | 새 `docs/`와 앱 reference path로 대체됨 |
| `operations/*.md` | registry / runbook / flow 기준으로 핵심 흡수 완료. 상세 세션 기록은 삭제 후보 |
| `research/*.md` | Practical Validation 설계 / external research 원칙으로 핵심 흡수 완료. JSON reference data는 `docs/data/`로 이동 |
| `support_tracks/*.md` | Codex 운영 / helper script 원칙만 새 구조로 흡수 완료. 상세 과거 support plan은 삭제 후보 |
| `archive/*.md` | 과거 snapshot. 현재 새 구조에 직접 필요하지 않음 |

3차 삭제 후 유지한 것:

- `WORK_PROGRESS.md`와 `QUESTION_AND_ANALYSIS_LOG.md`는 현재 hygiene helper와 handoff log가 보고 있으므로 바로 삭제하지 않는다.
- `PHASE_PLAN_TEMPLATE.md`, `PHASE_TEST_CHECKLIST_TEMPLATE.md`는 helper script가 읽는 source file이므로 `.aiworkspace/note/finance/docs/runbooks/templates/`로 이동하고 `bootstrap_finance_phase_bundle.py` 경로를 갱신했다.
- 기존 `phases/phase1` ~ `phases/phase36` 상세 문서는 새 docs / reports / task 구조에 필요한 내용을 흡수한 뒤 제거했다.
- `registries/`와 `saved/`는 삭제 대상이 아니다.
- `run_history/`, `run_artifacts/`, `.DS_Store`, `.playwright-mcp/`는 generated / local artifact다. 커밋 대상이 아니다.
