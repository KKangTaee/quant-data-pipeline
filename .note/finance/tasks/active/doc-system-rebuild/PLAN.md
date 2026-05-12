# PLAN - Finance Documentation System Rebuild

Status: Draft
Created: 2026-05-12
Task Path: `.note/finance/tasks/active/doc-system-rebuild/`

## 1. Goal

`finance` 프로젝트의 문서 체계를 Notion의 Codex 문서 운영 가이드에 맞춰 다시 구성한다.

현재 `.note/finance/`는 장기 지식, phase 기록, task 기록, 코드 분석, 운영 메모, 연구 메모, runtime 산출물이 한 공간에 섞여 있다. 이 때문에 Codex가 작업 시작 시 무엇을 먼저 읽어야 하는지, 진행 중 발견한 내용을 어디에 기록해야 하는지, 완료 후 어떤 내용을 장기 문서로 승격해야 하는지 판단하기 어렵다.

이 작업의 목표는 다음과 같다.

- 장기 지식과 작업 중 기록을 분리한다.
- phase 작업과 non-phase task 작업을 분리한다.
- Main worktree와 Sub worktree의 역할을 문서 구조로 구분한다.
- Codex가 매번 읽고 갱신할 문서 경로를 단순화한다.
- 기존 문서 대부분을 제거하더라도 `registries/`와 `saved/` 데이터는 보존한다.

## 2. Success Criteria

완료 기준:

- `.note/finance/docs/`가 장기 지식의 기준 위치가 된다.
- `.note/finance/phases/`가 phase 단위 계획과 통합 기록의 기준 위치가 된다.
- `.note/finance/tasks/`가 개별 실행 task 기록의 기준 위치가 된다.
- `.note/finance/agent/`가 Codex 반복 실수, 교훈, 운영 팁의 기준 위치가 된다.
- `.note/finance/reports/backtests/`가 durable backtest report의 기준 위치가 된다.
- `.note/finance/registries/`와 `.note/finance/saved/`는 삭제하지 않고 유지한다.
- `AGENTS.md`는 새 문서 구조 기준으로 짧고 강한 작업 규칙 문서로 정리된다.
- 기존 문서 중 장기적으로 필요한 내용만 새 `docs/` 문서에 최소 승격된다.
- 삭제 또는 재배치 후 `find .note/finance -maxdepth 3`로 새 구조가 확인된다.
- 문서 재구성 변경은 하나의 coherent commit으로 남긴다.

## 3. Scope

작업 대상:

- `.note/finance/` 문서 구조
- `AGENTS.md`
- finance Codex 운영 문서
- 기존 `.note/finance` 문서의 삭제, 축약, 재배치

보존 대상:

- `.note/finance/registries/`
- `.note/finance/saved/`

새 기준 구조:

```text
.note/finance/
  docs/
    INDEX.md
    PRODUCT_DIRECTION.md
    ROADMAP.md
    PROJECT_MAP.md
    GLOSSARY.md
    architecture/
    flows/
    data/
    runbooks/

  phases/
    active/
    done/

  tasks/
    active/
    done/

  agent/
    GOTCHAS.md
    LESSONS.md

  reports/
    backtests/
      INDEX.md
      strategies/
      runs/
      candidates/
      validation/
      archive/

  registries/
  saved/
```

## 4. Out Of Scope

이 작업에서 하지 않을 것:

- finance 코드 기능 변경
- Practical Validation V2 기능 개발
- Backtest UI UX 개선
- registry JSONL 데이터 정리 또는 내용 수정
- saved portfolio JSONL 데이터 정리 또는 내용 수정
- run history / runtime artifact를 새 장기 문서로 승격

## 5. Source Principles

Notion 가이드에서 적용할 원칙:

- `docs/`는 오래 유지될 프로젝트 지식만 둔다.
- `tasks/active/<task>/`는 현재 작업의 계획, 분석, 진행 상태, 실행 결과를 둔다.
- 작업 완료 후 `tasks/` 내용 중 오래 남길 가치가 있는 것만 `docs/` 또는 `agent/GOTCHAS.md`로 승격한다.
- 모든 작업에 문서 작성을 강제하지 않는다. 큰 작업, 조사, 여러 파일 수정 작업에만 task 문서를 만든다.
- Main은 phase 설계와 통합을 담당하고, Sub는 phase에서 분리된 task를 수행한다.
- Main은 `phases/`를 관리하고, Sub는 `tasks/active/`를 관리한다.
- `AGENTS.md`는 상세 아키텍처 설명을 담지 않고, Codex가 문서를 읽고 갱신하는 규칙만 담는다.

## 6. Proposed Migration Steps

### Step 1 - Inventory

- [x] 현재 `.note/finance/` 폴더와 파일 목록을 저장한다.
- [x] 삭제 대상, 보존 대상, 승격 후보를 분류한다.
- [x] 이미 생성된 local runtime artifact와 generated file을 별도 표시한다.

완료 조건:

- 삭제해도 되는 문서와 새 구조에 반영할 핵심 정보가 구분된다.

### Step 2 - Create New Skeleton

- [x] `.note/finance/docs/` 생성
- [x] `.note/finance/docs/INDEX.md` 생성
- [x] `.note/finance/docs/PRODUCT_DIRECTION.md` 생성
- [x] `.note/finance/docs/ROADMAP.md` 생성
- [x] `.note/finance/docs/PROJECT_MAP.md` 생성
- [x] `.note/finance/docs/GLOSSARY.md` 생성
- [x] `.note/finance/docs/architecture/README.md` 생성
- [x] `.note/finance/docs/flows/README.md` 생성
- [x] `.note/finance/docs/data/README.md` 생성
- [x] `.note/finance/docs/runbooks/README.md` 생성
- [x] `.note/finance/phases/active/`, `.note/finance/phases/done/` 생성
- [x] `.note/finance/tasks/active/`, `.note/finance/tasks/done/` 생성
- [x] `.note/finance/agent/GOTCHAS.md`, `.note/finance/agent/LESSONS.md` 생성

완료 조건:

- 새 문서 구조만 봐도 장기 지식, phase 기록, task 기록, Codex 운영 팁의 위치가 구분된다.

### Step 3 - Minimal Knowledge Promotion

기존 문서를 모두 그대로 옮기지 않는다. 아래 정보만 새 문서에 최소 승격한다.

- [x] 현재 product goal과 non-goal
- [x] 현재 Backtest / Ingestion / Practical Validation / Final Review / Selected Portfolio Dashboard의 큰 제품 흐름
- [x] 주요 코드 entrypoint와 module responsibility
- [x] 주요 DB / registry / saved data boundary
- [x] Practical Validation V2의 현재 task 위치와 다음 작업 방향
- [x] phase와 non-phase task를 구분하는 운영 규칙
- [x] registry / saved / generated artifact commit 정책

완료 조건:

- 새 `docs/` 문서만 읽어도 다음 Codex 세션이 프로젝트의 현재 상태와 작업 시작점을 파악할 수 있다.

### Step 4 - Rewrite AGENTS.md

- [x] 현재 긴 `AGENTS.md`를 새 문서 구조 기준으로 축약한다.
- [x] 필수 read order를 명확히 한다.
- [x] Main phase work와 Sub task work의 차이를 명확히 한다.
- [x] 삭제/커밋 금지 파일 규칙을 남긴다.
- [x] UX flow 승인 규칙처럼 프로젝트 운영에 꼭 필요한 규칙만 유지한다.

완료 조건:

- `AGENTS.md`는 작업 규칙과 문서 읽는 순서를 빠르게 전달한다.
- 상세 시스템 설명은 `.note/finance/docs/`로 이동한다.

### Step 5 - Migrate / Remove Old Documentation Tree

재배치 대상:

- `.note/finance/backtest_reports/` -> `.note/finance/reports/backtests/`
- `.note/finance/backtest_reports/strategies/` -> `.note/finance/reports/backtests/strategies/`
- `.note/finance/backtest_reports/phase*/` -> 1차 임시 archive -> 최종적으로 `runs/`, `candidates/`, `validation/`으로 분류

삭제 후보:

- `.note/finance/archive/`
- `.note/finance/code_analysis/`
- `.note/finance/data_architecture/` -> `.note/finance/docs/data/`로 마이그레이션 후 제거
- `.note/finance/operations/`
- `.note/finance/research/`
- `.note/finance/support_tracks/`
- 기존 `.note/finance/phases/phase*/`
- 기존 root markdown 문서
- `.note/finance/run_history/`
- `.note/finance/run_artifacts/`
- `.note/finance/.DS_Store`

보존:

- `.note/finance/registries/`
- `.note/finance/saved/`
- 새 `.note/finance/docs/`
- 새 `.note/finance/reports/backtests/`
- 새 `.note/finance/phases/`
- 새 `.note/finance/tasks/`
- 새 `.note/finance/agent/`

완료 조건:

- 오래된 문서 구조가 새 구조와 섞여 남지 않는다.
- backtest report는 삭제하지 않고 새 report 구조로 이동한다.
- legacy phase archive는 후속 정리 전 임시 보관 위치로만 사용하고, 최종적으로 비운다.
- runtime/generated artifact가 장기 문서처럼 남지 않는다.

### Step 6 - Verification

- [ ] `find .note/finance -maxdepth 3 -type d | sort`
- [ ] `find .note/finance -maxdepth 3 -type f | sort`
- [ ] `git status --short`
- [ ] `git diff --stat`
- [ ] 새 `AGENTS.md` read order가 실제 경로와 일치하는지 확인
- [ ] `registries/`와 `saved/`가 남아 있는지 확인

완료 조건:

- 새 문서 구조가 의도한 형태로만 남는다.
- 보존 대상 데이터가 삭제되지 않았다.
- 삭제된 문서는 Git history에서 복구 가능하다는 전제 아래 정리된다.

## 7. Risks

### Risk 1 - 기존 문서의 중요한 맥락 손실

대응:

- 삭제 전에 최소 승격 목록을 먼저 만든다.
- 장기 지식으로 필요한 것만 `docs/`에 짧게 재작성한다.
- 세부 과거 문서는 Git history에서 복구할 수 있다는 점을 전제로 한다.

### Risk 2 - AGENTS.md가 다시 길어짐

대응:

- AGENTS.md는 read order, work mode, commit/document safety 규칙만 둔다.
- 시스템 설명은 `.note/finance/docs/`로 이동한다.

### Risk 3 - phase와 task가 다시 섞임

대응:

- phase는 `.note/finance/phases/active/<phase>/`
- task는 `.note/finance/tasks/active/<task>/`
- phase가 여러 task를 묶고, task가 실제 실행 단위라는 원칙을 `AGENTS.md`와 `docs/INDEX.md`에 반복해서 명시한다.

### Risk 4 - registry / saved 데이터 손상

대응:

- 삭제 명령 전후로 `registries/`와 `saved/` 파일 목록을 확인한다.
- registry JSONL과 saved JSONL 내용은 이 작업에서 수정하지 않는다.

## 8. Approval Gate

이 문서 작성 이후 바로 대량 삭제를 진행하지 않는다.

다음 작업 전에 사용자에게 확인할 것:

- 새 구조가 맞는지
- 기존 문서 중 반드시 보존해야 할 폴더가 추가로 있는지
- 기존 phase 문서를 모두 삭제해도 되는지
- run history / run artifacts를 삭제해도 되는지
- 새 `AGENTS.md`를 어느 정도까지 축약할지

사용자가 승인하면 Step 1부터 실제 마이그레이션을 진행한다.
