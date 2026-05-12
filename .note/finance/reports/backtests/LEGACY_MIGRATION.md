# Legacy Backtest Report Migration

Status: Complete
Last Verified: 2026-05-12

## Purpose

기존 `.note/finance/backtest_reports/phase*/` 구조는 phase 진행 기록과 backtest 결과 report가 강하게 묶여 있었다.

앞으로는 report를 phase 번호가 아니라 사용 목적에 따라 찾을 수 있게 정리한다.

## 1차 처리 결과

2026-05-12 기준으로 기존 report는 삭제하지 않고 아래 위치로 이동했다.

- 기존: `.note/finance/backtest_reports/`
- 신규: `.note/finance/reports/backtests/`
- legacy phase archive: `.note/finance/reports/backtests/archive/legacy_phase/`

이 archive는 3차 처리에서 모두 비웠고 제거했다.

## Classification Rules

| 분류 | 이동 대상 |
|---|---|
| `runs/YYYY/` | 특정 날짜 또는 세션의 원본성 backtest 결과 |
| `candidates/point_in_time/` | 후보 선택, near-miss, hold/reject 근거로 다시 읽을 문서 |
| `validation/runtime/` | backtest engine/runtime smoke 검증 |
| `validation/ui_replay/` | Streamlit UI replay / saved replay 검증 |
| `strategies/` | 전략 family의 장기 hub 또는 누적 log에 흡수할 내용 |
| 삭제 | 같은 내용이 hub/log/registry에 이미 흡수되어 원본 유지 가치가 낮은 중복 문서 |

## Legacy Inventory

| Folder | Files | Likely Classification | Status |
|---|---:|---|---|
| `phase13/` | 14 reports, README removed | strategy search / candidate evidence | moved_to_runs_2026_strategy_search |
| `phase14/` | 1 report, README removed | candidate refresh | moved_to_runs_2026_strategy_search |
| `phase15/` | 14 reports, README removed | candidate improvement / strategy search | moved_to_runs_2026_strategy_search |
| `phase16/` | 4 reports, README removed | downside refinement / candidate search | moved_to_runs_2026_strategy_search |
| `phase17/` | 3 reports, README removed | weighting / defensive sleeve tests | moved_to_runs_2026_strategy_search |
| `phase18/` | 2 reports, README removed | next-ranked fill tests | moved_to_runs_2026_strategy_search |
| `phase21/` | 4 reports, README removed | portfolio bridge validation / rerun | moved_to_validation_and_candidate_evidence |
| `phase22/` | 2 reports, README removed | portfolio candidate pack / weight alternative | moved_to_portfolio_candidate_evidence |
| `phase23/` | 1 report, README removed | quarterly contract smoke validation | moved_to_validation_runtime |
| `phase24/` | 2 reports, README removed | runtime / UI replay validation | moved_to_validation_runtime_and_ui_replay |

## 2차 처리 결과

2026-05-12 기준으로 성격이 분명한 개발 검증 report를 먼저 흡수했다.

| Original | New Location | Reason |
|---|---|---|
| `phase23/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md` | `validation/runtime/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md` | quarterly contract가 DB-backed runtime과 result meta에 전달되는지 확인한 runtime smoke report |
| `phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md` | `validation/runtime/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md` | 신규 전략 core/runtime이 result bundle까지 생성되는지 확인한 runtime smoke report |
| `phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md` | `validation/ui_replay/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md` | 신규 전략이 single/compare/history/saved replay UI 흐름에 연결되는지 확인한 UI replay smoke report |

`phase23/README.md`, `phase24/README.md`는 archive index 역할만 하던 문서라서 핵심 설명을 `validation/` README에 반영하고 제거했다.

## 3차 처리 결과

2026-05-12 기준으로 남아 있던 legacy archive를 모두 비웠다.

| Original | New Location | Reason |
|---|---|---|
| `phase13`~`phase18` search / refinement reports | `runs/2026/strategy_search/` | 전략 탐색과 개선 과정의 원본성 backtest run report |
| `phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` | `validation/runtime/` | weighted portfolio 저장 / replay workflow 검증 |
| `phase21` family별 anchor / alternative rerun reports | `candidates/point_in_time/strategy_candidates/` | current anchor와 alternative 판단을 시점 기준 후보 근거로 읽는 문서 |
| `phase22` portfolio candidate pack / weight alternative reports | `candidates/point_in_time/portfolio_candidates/` | portfolio-level baseline과 weight alternative 판단 근거 |

각 phase별 `README.md`는 archive index 역할만 하던 문서라 제거했다. 현재 구조의 색인은 각 새 위치의 README와 `INDEX.md`가 담당한다.

## Final State

- `archive/legacy_phase/`는 비었고 제거됐다.
- 새 report는 `runs/YYYY/`부터 시작한다.
- 후보 판단 근거는 `candidates/point_in_time/`에 둔다.
- runtime/UI 검증은 `validation/`에 둔다.
- 전략 family 장기 해석은 `strategies/` hub/log에 둔다.

## Remaining Follow-Up

- `strategies/` hub/log와 `runs/2026/strategy_search/` 사이의 중복 해석은 나중에 정리할 수 있다.
- 현재는 원문 보존을 우선해 raw report를 삭제하지 않았다.

## Guardrails

- legacy 원문을 삭제하기 전에 현재 `registries/` 또는 `strategies/*_BACKTEST_LOG.md`에 핵심 근거가 남아 있는지 확인한다.
- `registries/`와 `saved/`는 이 migration의 정리 대상이 아니다.
- 후속 정리 중에도 새 report는 phase 폴더가 아니라 `runs/YYYY/`부터 시작한다.
