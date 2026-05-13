# RUNS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## 1차 stale path scan

Command:

```bash
rg -n "FINANCE_COMPREHENSIVE_ANALYSIS|FINANCE_DOC_INDEX|MASTER_PHASE_ROADMAP|FINANCE_TERM_GLOSSARY|code_analysis|data_architecture|backtest_reports|operations/|research/|support_tracks|phases/phase|phase<N>|phase\\*/|finance-phase-management" /Users/taeho/.codex/skills/finance-* plugins/quant-finance-workflow/skills/finance-backtest-candidate-refinement
```

Result:

- 수정 전 legacy path가 여러 finance skill에 남아 있었다.
- 수정 후 출력 없음.

## 1차 skill inventory

Result after removal:

```text
/Users/taeho/.codex/skills/finance-backtest-web-workflow/SKILL.md
/Users/taeho/.codex/skills/finance-db-pipeline/SKILL.md
/Users/taeho/.codex/skills/finance-doc-sync/SKILL.md
/Users/taeho/.codex/skills/finance-factor-pipeline/SKILL.md
/Users/taeho/.codex/skills/finance-strategy-implementation/SKILL.md
/Users/taeho/.codex/skills/quant-strategy-creation/SKILL.md
```

## 1차 skill validation

Command:

```bash
for d in /Users/taeho/.codex/skills/finance-backtest-web-workflow \
  /Users/taeho/.codex/skills/finance-db-pipeline \
  /Users/taeho/.codex/skills/finance-doc-sync \
  /Users/taeho/.codex/skills/finance-factor-pipeline \
  /Users/taeho/.codex/skills/finance-strategy-implementation; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d"
done
```

Result:

- 5개 finance skill 모두 `Skill is valid!`
- system Python은 `yaml` module이 없어 실패했으므로 repo `.venv/bin/python`으로 검증했다.

## 2차 skill creation

Command:

```bash
.venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/init_skill.py finance-task-management --path /Users/taeho/.codex/skills --interface display_name="Finance Task Management" --interface short_description="Classify finance requests and manage active task documents." --interface default_prompt="Classify this finance request and update the right active task documents."
```

Result:

- `/Users/taeho/.codex/skills/finance-task-management/` 생성
- `SKILL.md`와 `agents/openai.yaml` 생성 후 `SKILL.md`를 새 workflow 기준으로 재작성

## 2차 skill validation

Command:

```bash
for d in /Users/taeho/.codex/skills/finance-task-management \
  /Users/taeho/.codex/skills/finance-backtest-web-workflow \
  /Users/taeho/.codex/skills/finance-db-pipeline \
  /Users/taeho/.codex/skills/finance-doc-sync \
  /Users/taeho/.codex/skills/finance-factor-pipeline \
  /Users/taeho/.codex/skills/finance-strategy-implementation; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- 6개 finance skill 모두 `Skill is valid!`

Additional checks:

- `rg --files /Users/taeho/.codex/skills | rg '/finance-[^/]+/SKILL\\.md$' | sort`
  - `finance-task-management` 포함 6개 finance skill 확인
- `rg -n "finance-phase-management|phase<N>|phases/phase|FINANCE_COMPREHENSIVE_ANALYSIS|FINANCE_DOC_INDEX|MASTER_PHASE_ROADMAP|FINANCE_TERM_GLOSSARY|code_analysis|data_architecture|backtest_reports" /Users/taeho/.codex/skills/finance-* AGENTS.md`
  - 출력 없음
- `git diff --check`
  - 출력 없음

## 3차 repo-local skill source / references split

Actions:

- Added repo-local source skills under `plugins/quant-finance-workflow/skills/`:
  - `finance-task-management`
  - `finance-backtest-web-workflow`
  - `finance-db-pipeline`
  - `finance-factor-pipeline`
  - `finance-strategy-implementation`
  - `finance-doc-sync`
- Split long domain rules into each skill's `references/` directory.
- Synced global installed mirrors:

```bash
for skill in finance-task-management finance-backtest-web-workflow finance-db-pipeline finance-factor-pipeline finance-strategy-implementation finance-doc-sync; do
  rm -rf "/Users/taeho/.codex/skills/$skill"
  cp -R "plugins/quant-finance-workflow/skills/$skill" "/Users/taeho/.codex/skills/$skill"
done
```

Validation commands:

```bash
for d in plugins/quant-finance-workflow/skills/finance-task-management \
  plugins/quant-finance-workflow/skills/finance-backtest-web-workflow \
  plugins/quant-finance-workflow/skills/finance-db-pipeline \
  plugins/quant-finance-workflow/skills/finance-factor-pipeline \
  plugins/quant-finance-workflow/skills/finance-strategy-implementation \
  plugins/quant-finance-workflow/skills/finance-doc-sync; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- repo-local 6개 finance skill 모두 `Skill is valid!`
- global mirror 6개 finance skill 모두 `Skill is valid!`
- 기존 repo-local `finance-backtest-candidate-refinement`도 `Skill is valid!`
- `plugins/quant-finance-workflow/.codex-plugin/plugin.json` JSON parse 성공
- stale legacy path grep 출력 없음
- `git diff --check` 출력 없음
