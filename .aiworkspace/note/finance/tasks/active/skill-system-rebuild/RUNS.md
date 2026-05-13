# RUNS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## 1차 stale path scan

Command:

```bash
rg -n "FINANCE_COMPREHENSIVE_ANALYSIS|FINANCE_DOC_INDEX|MASTER_PHASE_ROADMAP|FINANCE_TERM_GLOSSARY|code_analysis|data_architecture|backtest_reports|operations/|research/|support_tracks|phases/phase|phase<N>|phase\\*/|finance-phase-management" /Users/taeho/.codex/skills/finance-* .aiworkspace/plugins/quant-finance-workflow/skills/finance-backtest-candidate-refinement
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

- Added repo-local source skills under `.aiworkspace/plugins/quant-finance-workflow/skills/`:
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
  cp -R ".aiworkspace/plugins/quant-finance-workflow/skills/$skill" "/Users/taeho/.codex/skills/$skill"
done
```

Validation commands:

```bash
for d in .aiworkspace/plugins/quant-finance-workflow/skills/finance-task-management \
  .aiworkspace/plugins/quant-finance-workflow/skills/finance-backtest-web-workflow \
  .aiworkspace/plugins/quant-finance-workflow/skills/finance-db-pipeline \
  .aiworkspace/plugins/quant-finance-workflow/skills/finance-factor-pipeline \
  .aiworkspace/plugins/quant-finance-workflow/skills/finance-strategy-implementation \
  .aiworkspace/plugins/quant-finance-workflow/skills/finance-doc-sync; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- repo-local 6개 finance skill 모두 `Skill is valid!`
- global mirror 6개 finance skill 모두 `Skill is valid!`
- 기존 repo-local `finance-backtest-candidate-refinement`도 `Skill is valid!`
- `.aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json` JSON parse 성공
- stale legacy path grep 출력 없음
- `git diff --check` 출력 없음

## 3차 post-migration hardening

Actions:

- Repo-local `finance-backtest-candidate-refinement`를 새 `.aiworkspace` 문서 체계에 맞게 다시 정리했다.
- 오래된 `phase report + active phase TODO` 중심 표현을 제거하고, `registry-backed candidate evidence`, strategy hub/log, backtest report, root handoff log 중심으로 수정했다.
- 7개 repo-local skill의 `agents/openai.yaml` default prompt가 `$skill-name`을 명시하도록 정리했다.
- 활성 6개 finance skill은 repo-local source에서 global `~/.codex/skills/finance-*` mirror로 다시 동기화했다.

Validation:

```bash
for d in .aiworkspace/plugins/quant-finance-workflow/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- repo-local 7개 finance skill 모두 `Skill is valid!`

```bash
for d in /Users/taeho/.codex/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- global mirror 6개 finance skill 모두 `Skill is valid!`

Additional checks:

- 6개 활성 finance skill repo-local source와 global mirror `diff -qr` 일치
- `.aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json` JSON parse 성공

## 4차 plugin placeholder / trigger path validation

Actions:

- `.aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json`에서 공개 배포용 placeholder와 존재하지 않는 component 참조를 제거했다.
- `.agents/plugins/marketplace.json`의 `quant-finance-workflow` source path를 `./.aiworkspace/plugins/quant-finance-workflow`로 보정했다.
- repo-local plugin source는 7개 skill을 보관하고, global runtime mirror는 활성 6개 finance skill을 보관하는 구조로 확정했다.

Validation:

```bash
python3 -m json.tool .aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

Result:

- plugin manifest와 marketplace JSON parse 성공.

```bash
python3 - <<'PY'
import json
from pathlib import Path
root = Path(".")
market = json.loads(Path(".agents/plugins/marketplace.json").read_text())
entry = next(p for p in market["plugins"] if p["name"] == "quant-finance-workflow")
plugin_root = root / entry["source"]["path"]
manifest = json.loads((plugin_root / ".codex-plugin/plugin.json").read_text())
skills = sorted(p.parent.name for p in (plugin_root / manifest["skills"]).glob("*/SKILL.md"))
print(entry["source"]["path"])
print(manifest["name"])
print(len(skills))
PY
```

Result:

- marketplace path: `./.aiworkspace/plugins/quant-finance-workflow`
- manifest name: `quant-finance-workflow`
- plugin source skill count: `7`

```bash
for d in .aiworkspace/plugins/quant-finance-workflow/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- repo-local 7개 finance skill 모두 `Skill is valid!`

```bash
for d in /Users/taeho/.codex/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- global mirror 6개 finance skill 모두 `Skill is valid!`

Additional checks:

- 활성 6개 finance skill repo-local source와 global mirror `diff -qr` 일치
- placeholder grep 출력 없음
- `git diff --check` 출력 없음

## 5차 final taxonomy correction

Actions:

- `finance-task-management`를 `finance-task-intake`로 rename했다.
- `finance-integration-review`와 `finance-runbook-maintainer`를 추가했다.
- `finance-backtest-candidate-refinement`를 repo-local plugin source에서 제거했다.
- domain skill과 `finance-doc-sync`, `AGENTS.md`, plugin manifest, roadmap, root logs를 새 4 workflow + 4 domain 구조에 맞게 보정했다.
- global `~/.codex/skills/finance-*` mirror를 repo-local source와 다시 동기화했다.

Validation:

```bash
for d in .aiworkspace/plugins/quant-finance-workflow/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- repo-local 8개 finance skill 모두 `Skill is valid!`

```bash
for d in /Users/taeho/.codex/skills/finance-*; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

Result:

- global mirror 8개 finance skill 모두 `Skill is valid!`

Additional checks:

- repo-local 8개 source와 global mirror `diff -qr` 일치
- marketplace path는 `./.aiworkspace/plugins/quant-finance-workflow`
- plugin source skill count는 `8`
- `git diff --check` 출력 없음
