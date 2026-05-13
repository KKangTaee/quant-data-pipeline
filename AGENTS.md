# AGENTS.md

## Purpose

이 저장소에서 Codex는 `finance` 프로젝트의 개발과 문서 운영을 함께 담당한다.

문서 역할은 아래처럼 구분한다.

- `.aiworkspace/note/finance/docs/`: 오래 유지될 프로젝트 지식
- `.aiworkspace/note/finance/phases/`: Main worktree가 관리하는 phase 단위 계획과 통합 기록
- `.aiworkspace/note/finance/tasks/`: 개별 실행 task의 계획, 진행 상태, 실행 결과
- `.aiworkspace/note/finance/agent/`: 반복 실수, 교훈, Codex 운영 팁
- `.aiworkspace/note/finance/reports/backtests/`: 사람이 읽는 backtest report, 전략 hub, 후보 근거, validation report
- `.aiworkspace/note/finance/registries/`: 제품 workflow가 읽고 쓰는 append-only JSONL registry
- `.aiworkspace/note/finance/saved/`: 사용자가 저장한 reusable portfolio setup

## Scope

- 이 worktree의 기본 활성 범위는 `finance` package와 Finance Streamlit app이다.
- 사용자가 명시하지 않으면 `financial_advisor`는 out of scope로 둔다.
- 이 세션은 `codex/main-dev` worktree 기준으로 phase / task 통합 흐름을 담당한다.
- 후보 탐색 / 백테스트 리서치는 별도 `research` worktree로 넘긴다.
- phase 범위를 벗어난 UX polish는 별도 `sub-dev` worktree로 넘긴다.

## Read Order

작업 시작 시 먼저 아래를 확인한다.

1. `.aiworkspace/note/finance/docs/INDEX.md`
2. `.aiworkspace/note/finance/docs/ROADMAP.md`
3. `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
4. 필요한 경우 `.aiworkspace/note/finance/docs/GLOSSARY.md`
5. 작업 성격에 맞는 `.aiworkspace/note/finance/docs/architecture/`, `flows/`, `data/`, `runbooks/`
6. 관련 active phase가 있으면 `.aiworkspace/note/finance/phases/active/<phase>/`
7. 관련 active task가 있으면 `.aiworkspace/note/finance/tasks/active/<task>/`
8. backtest report 작업이면 `.aiworkspace/note/finance/reports/backtests/INDEX.md`
9. 반복 이슈가 의심되면 `.aiworkspace/note/finance/agent/GOTCHAS.md`

legacy `operations/`, `research/`, `support_tracks/`, `archive/`, root current-state markdown 문서는 새 구조로 흡수 후 제거했다.
새 작업 기록과 새 장기 지식은 새 구조에 작성한다.
데이터 / DB 의미의 canonical 위치는 `.aiworkspace/note/finance/docs/data/`다.
코드 구조와 실행 흐름의 canonical 위치는 `.aiworkspace/note/finance/docs/architecture/`, 사용자 / 화면 흐름의 canonical 위치는 `.aiworkspace/note/finance/docs/flows/`, 실행 절차의 canonical 위치는 `.aiworkspace/note/finance/docs/runbooks/`다.

## Work Modes

### Skill Routing

가능한 local Codex skill이 있으면 아래처럼 좁은 역할부터 적용한다.

프로젝트 전용 finance skill의 원본은 `.aiworkspace/plugins/quant-finance-workflow/skills/`에 둔다. `~/.codex/skills/finance-*`는 현재 Codex runtime에서 읽는 설치본 / mirror로 취급한다.

공통 workflow skill:

- 요청 분류, 읽을 문서 결정, active task 위치 결정: `finance-task-intake`
- 구현 후 문서 alignment, index/roadmap/root log final sync: `finance-doc-sync`
- merge conflict, worktree 통합, parallel/sub 결과 통합, staged diff 검토: `finance-integration-review`
- 반복 명령, 운영 절차, helper script 사용법을 runbook으로 정리: `finance-runbook-maintainer`

구현 domain skill:

- Backtest Streamlit UI, Practical Validation, Final Review, Selected Portfolio Dashboard: `finance-backtest-web-workflow`
- ingestion, DB schema, UPSERT, provider connector, loader source boundary: `finance-db-pipeline`
- factor generation, accounting-to-factor, PIT factor assumption: `finance-factor-pipeline`
- strategy, transform, engine, performance, sample: `finance-strategy-implementation`

`finance-task-intake`는 구현 skill이 아니다. 코드 변경은 domain skill 중 하나가 소유하고, 통합 검토는 `finance-integration-review`, 반복 절차 문서화는 `finance-runbook-maintainer`, 문서 최종 정렬은 `finance-doc-sync`가 맡는다.

### Main Phase Work

Main phase work는 여러 task를 묶는 상위 방향, 설계, 통합을 관리한다.

위치:

```text
.aiworkspace/note/finance/phases/active/<phase-name>/
  PLAN.md
  DESIGN.md
  TASKS.md
  STATUS.md
  RISKS.md
  INTEGRATION.md
```

Main은 다음을 담당한다.

- phase 목표와 종료 조건 정의
- task 분해와 owner / scope / dependency 정리
- Sub 작업 결과 검토와 통합 순서 관리
- 충돌 가능 파일과 통합 검증 기준 관리
- phase 완료 시 `docs/`로 승격할 장기 지식 선별

### Task Work

Task work는 실제 구현, 조사, 문서 정리, QA를 수행하는 실행 단위다.

위치:

```text
.aiworkspace/note/finance/tasks/active/<task-name>/
  PLAN.md
  DESIGN.md
  STATUS.md
  NOTES.md
  RUNS.md
  RISKS.md
```

작은 단일 파일 수정은 task 문서를 생략할 수 있다.
여러 파일 수정, 구조 판단, QA, 문서 체계 변경은 active task로 관리한다.

작업 중 발견한 사실은 `NOTES.md`, 실행한 명령과 결과는 `RUNS.md`, 남은 검증 공백은 `RISKS.md`에 남긴다.

## Documentation Rules

- `docs/`에는 오래 유지될 프로젝트 지식만 둔다.
- 작업 중 추측, 조사 메모, 실패 로그는 task 또는 phase 문서에 먼저 둔다.
- 오래된 task 내용 중 반복 가치가 있는 것만 `docs/` 또는 `agent/GOTCHAS.md`로 승격한다.
- `AGENTS.md`에는 상세 아키텍처 설명을 길게 넣지 않는다. 상세 지도는 `docs/`에 둔다.
- 신규 또는 크게 바뀐 phase / task plan에는 `이걸 하는 이유?` 또는 그에 준하는 목적 설명을 포함한다.

## Root Handoff Logs

- `.aiworkspace/note/finance/WORK_PROGRESS.md`와 `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`는 root handoff log로 유지한다.
- root log는 작업 현장 기록이 아니라 지도 역할을 한다. 작업 단위당 3~5줄의 핵심 milestone / decision / handoff만 남긴다.
- 상세 구현 과정, 긴 분석, 명령 출력, 시행착오, 중간 판단은 active task의 `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`로 보낸다.
- `WORK_PROGRESS.md`에는 무엇을 끝냈는지와 다음에 어디를 보면 되는지만 남긴다.
- `QUESTION_AND_ANALYSIS_LOG.md`에는 `User request`, `Interpreted goal`, `Analysis result`, `Follow-up` 중심의 결론만 남기고 대화 전체를 옮기지 않는다.
- root log가 길어지는 조짐이 있으면 먼저 task 문서로 분리하고, root에는 해당 task 문서 경로를 남긴다.

## Code Work Rules

- 코드 수정 전에는 `.aiworkspace/note/finance/docs/PROJECT_MAP.md`에서 소유 파일과 경계를 확인한다.
- Backtest / Streamlit UI 변경은 `app/web/pages/backtest.py`와 관련 `app/web/backtest_*.py` 소유 경계를 먼저 확인한다.
- DB / ingestion 변경은 `finance/data/db/schema.py`와 관련 `finance/data/*`, `finance/loaders/*`를 먼저 확인한다.
- Strategy 변경은 기존 분리를 따른다.
  - preprocessing: `finance/transform.py`
  - simulation: `finance/strategy.py`
  - orchestration: `finance/engine.py`
  - performance: `finance/performance.py`
- 새 core strategy나 ingestion workflow가 생기면 `finance/sample.py` 또는 동등한 smoke usage를 검토한다.
- non-trivial domain logic, workflow routing, persistence conversion, scoring, validation, cross-module handoff 함수에는 짧은 목적 주석이나 docstring을 둔다.
- 사용자 변경사항을 임의로 되돌리지 않는다.

## Data And Validation Rules

- 재무 데이터, factor, backtest, validation에서는 항상 point-in-time correctness, look-ahead bias, survivorship bias를 고려한다.
- provider field는 안정적이거나 완전하다고 가정하지 않는다.
- Practical Validation에서 `NOT_RUN`은 pass가 아니다. 데이터 또는 구현이 없어 실행하지 못했다는 뜻이다.
- UI에서 provider / FRED를 직접 fetch하지 않는다. `Ingestion -> DB -> Loader -> UI` 흐름을 유지한다.
- full holdings, full macro series, raw provider response는 DB에 두고 Practical Validation JSONL에는 compact evidence만 저장한다.
- Final Review와 Selected Portfolio Dashboard는 live approval, broker order, auto rebalance가 아니다.

## Registry And Artifact Rules

- `.aiworkspace/note/finance/registries/*.jsonl`은 workflow registry다. 명시 요청 없이 재작성하거나 정리하지 않는다.
- `.aiworkspace/note/finance/saved/*.jsonl`은 사용자 저장 setup이다. 문서 정리 과정에서 삭제하지 않는다.
- `.aiworkspace/note/finance/reports/backtests/`는 사람이 읽는 결과/근거 문서다. registry / saved source-of-truth를 대체하지 않는다.
- 새 backtest report는 phase 폴더가 아니라 `.aiworkspace/note/finance/reports/backtests/runs/YYYY/`부터 시작한다.
- `run_history/*.jsonl`, `run_artifacts/`, temp CSV, notebook scratch, `.DS_Store`, `.playwright-mcp/`는 generated / local artifact로 보고 명시 요청 없이는 커밋하지 않는다.
- 문서 체계 정리에서도 `registries/`와 `saved/`는 보존한다.

## UX / Workflow Approval Rules

사용자가 product flow, stage 의미, UX/UI 구조, validation 기준, 단계 필요성을 질문하면 먼저 답변한다.

UX / workflow / stage 구조 변경 전에는 다음을 설명한다.

- 사용자가 지적한 문제를 어떻게 이해했는지
- 바뀔 가능성이 있는 파일과 화면
- 변경 후 사용자 흐름
- 중요한 tradeoff

그 다음 `진행할까요?`라고 묻고 확인을 기다린다.
이미 사용자가 `진행해줘`처럼 명시 승인했다면 합의된 범위 안에서 진행한다.

## Verification

변경 후 가능한 범위에서 관련 검증을 실행한다.

예시:

```bash
git status --short
git diff --check
.venv/bin/python -m py_compile app/web/backtest_practical_validation.py
find .aiworkspace/note/finance -maxdepth 3 -type f | sort
```

실행하지 못한 검증은 최종 응답에 이유와 함께 남긴다.

## Commit Rules

- distinct implementation unit이 끝나면 사용자가 금지하지 않는 한 commit을 만든다.
- commit은 coherent feature / task / phase 단위로 묶는다.
- commit message는 한국어를 기본으로 한다.
- generated artifact, run history, local experiment output은 명시 요청 없이는 stage하지 않는다.

## Review Rules

리뷰 요청을 받으면 코드 리뷰 관점으로 답한다.

우선순위:

1. bug / regression / data integrity risk
2. missing validation or QA gap
3. phase / task scope mismatch
4. documentation drift

문제가 없으면 그렇게 말하고, 남은 검증 공백만 짧게 남긴다.

## Do Not

- `docs/`에 임시 추측이나 조사 중 메모를 넣지 않는다.
- 새 문서 체계에 기존 대형 문서를 통째로 복붙하지 않는다.
- `registries/`와 `saved/`를 문서 정리 대상으로 삭제하지 않는다.
- 검증하지 않은 내용을 완료된 사실처럼 말하지 않는다.
- 사용자나 다른 worktree가 만든 변경을 임의로 되돌리지 않는다.
