# Backtest Reports

Status: Active
Last Verified: 2026-05-12

## Purpose

이 폴더는 `finance` 프로젝트에서 생성되는 durable backtest report를 보관한다.

여기서 report는 코드 구현 기록이 아니라, 다음 질문에 답하는 문서다.

- 어떤 전략이나 포트폴리오 후보를 검증했는가?
- 어떤 기간, universe, benchmark, 설정으로 실행했는가?
- 결과는 무엇이고, 어떤 판단으로 이어졌는가?
- 나중에 같은 후보를 다시 볼 때 어떤 근거를 먼저 확인해야 하는가?

## What Goes Here

| 위치 | 용도 |
|---|---|
| `strategies/` | 전략 family별 hub, backtest log, 현재 후보 one-pager |
| `runs/YYYY/` | 새 분석 세션에서 받은 원본성 backtest report |
| `candidates/point_in_time/` | 특정 시점 후보의 선택 근거, near-miss, 재검토 근거 |
| `validation/` | runtime smoke, UI replay, validation 결과 보고 |
| `archive/legacy_phase/` | 기존 phase별 report를 안전하게 임시 보관하는 legacy staging 영역 |

## What Does Not Go Here

| 대상 | 기준 위치 | 이유 |
|---|---|---|
| 현재 후보 / 최종 판단 JSONL | `.note/finance/registries/` | 제품 workflow가 읽는 append-only source-of-truth |
| 사용자가 저장한 portfolio setup | `.note/finance/saved/` | 재사용 가능한 사용자 입력 데이터 |
| task 진행 로그 | `.note/finance/tasks/active/<task>/` | 현재 작업 실행 기록 |
| phase 계획 / QA / 완료 문서 | `.note/finance/phases/active/` 또는 `done/` | phase 단위 관리 기록 |
| local run history / temp artifact | `.note/finance/run_history/`, `.note/finance/run_artifacts/` | 보통 커밋하지 않는 runtime 산출물 |

## Operating Rules

- 새 분석 세션에서 받은 결과 report는 먼저 `runs/YYYY/`에 둔다.
- 전략 family 단위로 반복 확인할 가치가 있으면 `strategies/*_BACKTEST_LOG.md`에 요약 entry를 추가한다.
- 최종 후보 판단에 쓰이는 핵심 근거는 `candidates/point_in_time/`로 승격한다.
- runtime/UI 검증 문서는 `validation/`으로 분리한다.
- `archive/legacy_phase/`는 영구 정답 위치가 아니다. 후속 migration에서 `runs/`, `candidates/`, `validation/`, `strategies/`로 흡수하거나 삭제한다.

## Read Order

1. [INDEX.md](./INDEX.md)
2. [strategies/README.md](./strategies/README.md)
3. [LEGACY_MIGRATION.md](./LEGACY_MIGRATION.md)
4. 필요한 경우에만 `archive/legacy_phase/`의 원본 report
