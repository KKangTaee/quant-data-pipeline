# Legacy Backtest Report Migration

Status: Active
Last Verified: 2026-05-12

## Purpose

기존 `.note/finance/backtest_reports/phase*/` 구조는 phase 진행 기록과 backtest 결과 report가 강하게 묶여 있었다.

앞으로는 report를 phase 번호가 아니라 사용 목적에 따라 찾을 수 있게 정리한다.

## 1차 처리 결과

2026-05-12 기준으로 기존 report는 삭제하지 않고 아래 위치로 이동했다.

- 기존: `.note/finance/backtest_reports/`
- 신규: `.note/finance/reports/backtests/`
- legacy phase archive: `.note/finance/reports/backtests/archive/legacy_phase/`

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
| `phase13/` | 15 | strategy search / candidate evidence | pending |
| `phase14/` | 2 | candidate refresh | pending |
| `phase15/` | 15 | candidate improvement / strategy search | pending |
| `phase16/` | 5 | downside refinement / candidate search | pending |
| `phase17/` | 4 | weighting / defensive sleeve tests | pending |
| `phase18/` | 3 | next-ranked fill tests | pending |
| `phase21/` | 5 | portfolio bridge validation / rerun | pending |
| `phase22/` | 3 | portfolio candidate pack / weight alternative | pending |
| `phase23/` | 2 | quarterly contract smoke validation | pending |
| `phase24/` | 3 | runtime / UI replay validation | pending |

## 후속 작업 순서

1. `phase24`, `phase23`처럼 validation 성격이 분명한 문서를 먼저 `validation/`으로 흡수한다.
2. `phase13`~`phase18`의 search report는 전략 hub/log와 중복 여부를 확인한다.
3. 현재 후보 판단에 남길 근거만 `candidates/point_in_time/`로 승격한다.
4. hub/log에 이미 충분히 반영된 raw report는 삭제 후보로 표시한다.
5. `archive/legacy_phase/`가 비게 되면 폴더를 제거한다.

## Guardrails

- legacy 문서를 삭제하기 전에 현재 `registries/` 또는 `strategies/*_BACKTEST_LOG.md`에 핵심 근거가 남아 있는지 확인한다.
- `registries/`와 `saved/`는 이 migration의 정리 대상이 아니다.
- 후속 정리 중에도 새 report는 phase 폴더가 아니라 `runs/YYYY/`부터 시작한다.
