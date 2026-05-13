# AI Workspace

`.aiworkspace/`는 Codex / AI 작업자가 `quant-data-pipeline`의 finance 프로젝트를 일관되게 이해하고 작업하기 위한 운영 workspace다.

제품 코드는 repo root의 `app/`, `finance/`에 둔다. 이 폴더에는 AI 작업 문서, task 기록, backtest report, registry, saved setup, repo-local Codex skill / helper script source를 둔다.

## 구조

```text
.aiworkspace/
  README.md
  note/
    finance/
      docs/                  # 장기 프로젝트 지식
      tasks/                 # active / done task 기록
      phases/                # phase 단위 통합 계획
      reports/               # 사람이 읽는 report
      agent/                 # Codex 운영 팁 / gotchas
      registries/            # workflow JSONL registry
      saved/                 # 사용자 저장 setup
      run_history/           # 로컬 실행 이력
      run_artifacts/         # 로컬 실행 산출물
      WORK_PROGRESS.md
      QUESTION_AND_ANALYSIS_LOG.md
  plugins/
    quant-finance-workflow/
      .codex-plugin/
      skills/
      scripts/
```

## 먼저 볼 곳

| 상황 | 시작 문서 |
|---|---|
| 프로젝트 전체 방향 확인 | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` |
| 현재 작업 흐름 확인 | `.aiworkspace/note/finance/docs/ROADMAP.md` |
| 코드 / 문서 위치 확인 | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` |
| finance 문서 목록 확인 | `.aiworkspace/note/finance/docs/INDEX.md` |
| 용어 확인 | `.aiworkspace/note/finance/docs/GLOSSARY.md` |
| 반복 명령 / 절차 확인 | `.aiworkspace/note/finance/docs/runbooks/README.md` |
| 현재 실행 task 확인 | `.aiworkspace/note/finance/tasks/active/` |

## Finance Note 영역

| Path | 역할 |
|---|---|
| `note/finance/docs/` | 오래 유지될 제품 / 구조 / 데이터 / 흐름 / runbook 문서 |
| `note/finance/tasks/active/` | 현재 실행 중인 task의 계획, 상태, 실행 결과, 리스크 |
| `note/finance/phases/active/` | 여러 task를 묶는 phase 단위 방향과 통합 기록 |
| `note/finance/reports/backtests/` | backtest 결과 report, 전략 hub, validation report |
| `note/finance/agent/` | 반복 실수, 운영 팁, Codex 작업 gotcha |
| `note/finance/registries/` | 제품 workflow가 읽고 쓰는 append-only JSONL registry |
| `note/finance/saved/` | 사용자가 저장한 reusable portfolio setup |
| `note/finance/run_history/` | 로컬 실행 이력. 보통 커밋하지 않음 |
| `note/finance/run_artifacts/` | 로컬 실행 산출물. 보통 커밋하지 않음 |
| `note/finance/WORK_PROGRESS.md` | root handoff용 핵심 milestone log |
| `note/finance/QUESTION_AND_ANALYSIS_LOG.md` | user question / design decision 요약 log |

## Skill / Plugin 영역

프로젝트 전용 finance skill의 원본은 `plugins/quant-finance-workflow/skills/`다.

`~/.codex/skills/finance-*`는 Codex runtime에서 읽는 mirror / 설치본으로 취급한다. skill을 수정하면 repo-local source를 먼저 바꾸고, 필요한 경우 global mirror를 동기화한다.

### Workflow Skills

| Skill | 역할 |
|---|---|
| `finance-task-intake` | 요청을 분류하고 읽을 문서, active task 위치, 담당 skill을 결정 |
| `finance-doc-sync` | 구현 / 분석 후 durable docs, index, roadmap, root logs 정렬 |
| `finance-integration-review` | merge conflict, worktree 통합, sub 결과 통합, staged diff 검토 |
| `finance-runbook-maintainer` | 반복 명령 / 운영 절차 / helper script 사용법을 runbook으로 정리 |

### Domain Skills

| Skill | 역할 |
|---|---|
| `finance-backtest-web-workflow` | Backtest / Practical Validation / Final Review / Selected Dashboard UI |
| `finance-db-pipeline` | ingestion, DB schema, provider connector, loader source boundary |
| `finance-strategy-implementation` | strategy / engine / transform / performance |
| `finance-factor-pipeline` | factor, financial statements, PIT accounting logic |

## 운영 원칙

- 장기 지식은 `note/finance/docs/`에 둔다.
- 작업 중 상태, 시행착오, 실행 결과는 `note/finance/tasks/active/<task>/`에 둔다.
- root logs는 상세 기록이 아니라 handoff map으로 유지한다.
- registry JSONL, saved setup, run history, run artifacts는 문서가 아니라 workflow / runtime data다.
- `registries/`와 `saved/`는 문서 정리 과정에서 삭제하거나 재작성하지 않는다.
- `run_history/`, `run_artifacts/`, temp CSV, `.DS_Store`, Playwright output은 명시 요청 없이는 커밋하지 않는다.
- 후보 탐색 / 백테스트 리서치 성격의 작업은 별도 `research` worktree로 넘긴다.
- phase 범위를 벗어난 UX polish는 별도 `sub-dev` worktree로 넘긴다.

## 변경 시 확인

`.aiworkspace/` 구조나 skill / plugin을 바꿨다면 최소한 아래를 확인한다.

```bash
python3 -m json.tool .aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
for d in .aiworkspace/plugins/quant-finance-workflow/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
git diff --check
```

global mirror를 동기화했다면 repo-local source와 `~/.codex/skills/finance-*`가 일치하는지도 확인한다.
