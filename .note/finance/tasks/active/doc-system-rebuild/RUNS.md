# RUNS - Finance Documentation System Rebuild

Status: Active
Last Updated: 2026-05-12

## 2026-05-12 - Inventory

Command:

```bash
find .note/finance -maxdepth 2 -type f | sort
```

Result:

- 기존 root docs, `code_analysis`, `data_architecture`, `operations`, `research`, `support_tracks`, `phases`, `registries`, `saved`, `run_history` 확인
- `registries/`와 `saved/`는 보존 대상으로 확인

## 2026-05-12 - Skeleton Creation

Command:

```bash
mkdir -p .note/finance/docs/architecture .note/finance/docs/flows .note/finance/docs/data .note/finance/docs/runbooks .note/finance/phases/active .note/finance/phases/done .note/finance/tasks/active/practical-validation-v2 .note/finance/tasks/done .note/finance/agent
```

Result:

- 새 docs / phases / tasks / agent skeleton 생성
- 기존 문서 삭제 없음

## 2026-05-12 - First Work Verification

Command:

```bash
find .note/finance -maxdepth 3 -type d | sort
find .note/finance -maxdepth 3 -type f | sort
git status --short
git diff --stat
```

Result:

- 새 `docs/`, `phases/active`, `phases/done`, `tasks/active`, `tasks/done`, `agent` 파일 생성 확인
- `registries/`와 `saved/` 파일 목록 유지 확인
- `git diff --check` 통과
- 기존 dirty artifact는 그대로 남아 있으며 stage 대상에서 제외 예정

## 2026-05-12 - AGENTS Rewrite

Command:

```bash
sed -n '1,260p' AGENTS.md
sed -n '1,220p' .note/finance/docs/INDEX.md
sed -n '1,220p' .note/finance/docs/PROJECT_MAP.md
```

Result:

- 기존 `AGENTS.md`의 핵심 운영 규칙을 새 `.note/finance/docs/` read order 기준으로 축약
- legacy `.note/finance/code_analysis/`, `data_architecture/`, `operations/`, `research/`, root markdown 문서는 마이그레이션 완료 전 임시 reference로만 두도록 명시
- registry / saved 보존, generated artifact 커밋 금지, UX/workflow 승인 규칙 유지

## 2026-05-12 - Backtest Reports 1차 Migration

Command:

```bash
git mv .note/finance/backtest_reports/README.md .note/finance/reports/backtests/README.md
git mv .note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md .note/finance/reports/backtests/INDEX.md
git mv .note/finance/backtest_reports/strategies .note/finance/reports/backtests/strategies
git mv .note/finance/backtest_reports/phase* .note/finance/reports/backtests/archive/legacy_phase/
```

Result:

- 기존 83개 backtest report 파일을 삭제하지 않고 새 `.note/finance/reports/backtests/` 아래로 이동
- `strategies/`는 active strategy hub/log 영역으로 유지
- 기존 phase13~phase24 report는 `archive/legacy_phase/`에 임시 보관
- 새 `README.md`, `INDEX.md`, `TEMPLATE.md`, `LEGACY_MIGRATION.md`로 report 운영 기준 작성
- legacy report의 세부 재분류와 삭제 판단은 후속 단계로 분리
