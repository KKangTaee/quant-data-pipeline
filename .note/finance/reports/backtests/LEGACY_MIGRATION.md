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
| `strategies/*_BACKTEST_LOG.md` | 전략별 current anchor, near-miss, hold/reject 근거로 다시 읽을 요약 |
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
| `phase23/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md` | `validation/runtime/QUARTERLY_CONTRACT_RUNTIME_SMOKE.md` | quarterly contract가 DB-backed runtime과 result meta에 전달되는지 확인한 runtime smoke report |
| `phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md` | `validation/runtime/GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md` | 신규 전략 core/runtime이 result bundle까지 생성되는지 확인한 runtime smoke report |
| `phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md` | `validation/ui_replay/GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md` | 신규 전략이 single/compare/history/saved replay UI 흐름에 연결되는지 확인한 UI replay smoke report |

`phase23/README.md`, `phase24/README.md`는 archive index 역할만 하던 문서라서 핵심 설명을 `validation/` README에 반영하고 제거했다.

## 3차 처리 결과

2026-05-12 기준으로 남아 있던 legacy archive를 모두 비웠다.

| Original | New Location | Reason |
|---|---|---|
| `phase13`~`phase18` search / refinement reports | `runs/2026/strategy_search/` | 전략 탐색과 개선 과정의 원본성 backtest run report |
| `phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` | `validation/runtime/WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md` | weighted portfolio 저장 / replay workflow 검증 |
| `phase21` family별 anchor / alternative rerun reports | `strategies/*_BACKTEST_LOG.md` | current anchor와 alternative 판단을 전략별 누적 log에 흡수 |
| `phase22` portfolio candidate pack / weight alternative reports | `validation/runtime/WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md` | portfolio 후보가 아니라 weighted builder / saved replay smoke evidence로 재정리 |

## 4차 내용 중심 재분류

2026-05-12 추가 검토에서 `candidates/point_in_time/` 구조는 현재 workflow와 맞지 않는다고 판단했다.

이유:

- 현재 후보 source-of-truth는 `registries/`와 Final Review decision이다.
- `candidates/`라는 폴더명은 과거 rerun report를 현재 후보처럼 보이게 만든다.
- 유용한 내용은 이미 전략별 log 또는 weighted portfolio replay 검증 문서로 흡수할 수 있다.

처리:

| 대상 | 처리 |
|---|---|
| strategy candidate rerun report 3개 | 각 전략별 `*_BACKTEST_LOG.md`에 유지된 rerun entry로 흡수하고 원본 파일 제거 |
| portfolio candidate report 2개 | `WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md`로 내용 중심 재작성 후 원본 파일 제거 |
| `candidates/` 폴더 | 현재 후보 폴더로 오해되지 않도록 제거 |

각 phase별 `README.md`는 archive index 역할만 하던 문서라 제거했다. 현재 구조의 색인은 각 새 위치의 README와 `INDEX.md`가 담당한다.

## Final State

- `archive/legacy_phase/`는 비었고 제거됐다.
- 새 report는 `runs/YYYY/`부터 시작한다.
- 후보 판단 근거는 별도 `candidates/` 폴더에 두지 않고, registry source-of-truth와 전략별 log / validation report에 나눠 둔다.
- runtime/UI 검증은 `validation/`에 둔다.
- 전략 family 장기 해석은 `strategies/` hub/log에 둔다.

## Remaining Follow-Up

- `strategies/` hub/log와 `runs/2026/strategy_search/` 사이의 중복 해석은 나중에 정리할 수 있다.
- 현재는 전략별 log와 validation report에 흡수되지 않은 raw search report만 `runs/2026/strategy_search/`에 남겨 둔다.

## Guardrails

- legacy 원문을 삭제하기 전에 현재 `registries/` 또는 `strategies/*_BACKTEST_LOG.md`에 핵심 근거가 남아 있는지 확인한다.
- `registries/`와 `saved/`는 이 migration의 정리 대상이 아니다.
- 후속 정리 중에도 새 report는 phase 폴더가 아니라 `runs/YYYY/`부터 시작한다.
