# Finance Document Governance Alignment V1 Plan

## Goal

핵심 문서의 새 역할과 작업 지침·스킬·phase 자동화·상태 판정 규칙을 하나의 운영 계약으로 정렬한다.

## 이걸 하는 이유?

현재 문서 본문은 간결해졌지만 갱신 지침이 과거 패턴을 유지하면 다음 작업부터 다시 중복과 상태 충돌이
쌓인다. 사람이 읽어도 현재 상태와 이력의 위치가 분명하고, AI가 작업 종류에 따라 필요한 문서만
갱신하도록 만드는 것이 목적이다.

## Scope

- `AGENTS.md`
- finance task intake/doc sync/integration review/backtest workflow skill과 reference
- phase bootstrap 및 hygiene checker
- phase/runbook/template/script-map 문서
- task README, status manifest, 필요한 최소 root pointer
- 관련 unit/service contract 테스트
- repo skill source와 runtime mirror 동기화

## Execution

### Task 1. 현재 계약을 테스트로 고정

- [x] `tests/test_finance_document_workflow.py`를 추가한다.
- [x] 새 phase bundle이 canonical 여섯 파일만 계획하는지 테스트한다.
- [x] 일반 task/phase closeout이 INDEX·root log 갱신 경고를 만들지 않는지 테스트한다.
- [x] 테스트가 기존 구현에서 실패하는 것을 확인한다.

검증:

```bash
.venv/bin/python -m unittest -v tests.test_finance_document_workflow
```

### Task 2. phase 자동화 교정

- [x] bootstrap 입력을 `<phase-id>` 중심으로 바꾼다.
- [x] `PLAN.md`, `DESIGN.md`, `TASKS.md`, `STATUS.md`, `RISKS.md`, `INTEGRATION.md`를 생성한다.
- [x] 상태 skeleton에 정규화된 `State:` 값을 포함한다.
- [x] hygiene checker가 모든 `phases/active/<phase-id>/*.md`를 인식하도록 바꾼다.
- [x] `CURRENT_CHAPTER_TODO`, INDEX, root log 의무 검사를 제거한다.
- [x] generated artifact와 strategy 안전 검사는 보존한다.

검증:

```bash
.venv/bin/python -m unittest -v tests.test_finance_document_workflow
.venv/bin/python -m py_compile \
  .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py \
  .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

### Task 3. 지침과 runbook 교정

- [x] `AGENTS.md`에 네 canonical 문서 역할, 갱신 trigger, 상태 우선순위를 명시한다.
- [x] phase shape와 task status 계약을 맞춘다.
- [x] phase/runbook/template/script-map의 과거 numbered-phase 전제를 제거한다.
- [x] `agent/GOTCHAS.md`의 latest/current pointer 동기화 규칙을 역할 기반 규칙으로 바꾼다.

### Task 4. finance skill 교정

- [x] `finance-task-intake`가 Product Direction과 역할별 first read를 선택하도록 바꾼다.
- [x] task document contract에 정규화된 상태 모델과 source-of-truth를 추가한다.
- [x] `finance-doc-sync` matrix를 change-based update matrix로 교체한다.
- [x] `finance-integration-review`가 canonical 문서에 이력을 합치지 않도록 바꾼다.
- [x] `finance-backtest-web-workflow` closeout 안내를 역할 기반 doc sync로 연결한다.

### Task 5. 현재 포인터와 서비스 계약 교정

- [x] task README/manifest 상단을 Active 없음, Paused 1건, Verification-Only 2건으로 맞춘다.
- [x] 필요한 최소 root Active Pointer만 현재 상태로 맞춘다.
- [x] Roadmap/root log 특정 문구에 의존하는 테스트를 집중 flow/task 상태 문서 기준으로 바꾼다.
- [x] registry/saved/run-history/generated artifact가 diff에 포함되지 않았는지 확인한다.

### Task 6. mirror, 최종 검증, closeout

- [x] 변경한 repo skill source를 runtime mirror에 동일하게 반영한다.
- [x] 변경한 각 skill source와 mirror에 `quick_validate.py`를 실행한다.
- [x] source/mirror가 동일한지 확인한다.
- [x] targeted unittest, compile, dry-run, hygiene JSON, `git diff --check`를 실행한다.
- [x] task `STATUS.md`, `RUNS.md`, `RISKS.md`를 closeout 상태로 갱신한다.
- [x] coherent unit별로 commit한다.

## Stop Condition

- 문서 역할과 갱신 trigger가 AGENTS/skills/runbooks에서 일관된다.
- phase 자동화가 현재 여섯 파일 계약을 생성한다.
- 평범한 closeout이 INDEX/ROADMAP/root log 갱신을 강제하지 않는다.
- 현재 task 상태 포인터가 Roadmap과 일치한다.
- 집중 테스트와 skill validation이 통과한다.
- 사용자 소유 registry/saved/run-history/QA artifact는 건드리거나 stage하지 않는다.
